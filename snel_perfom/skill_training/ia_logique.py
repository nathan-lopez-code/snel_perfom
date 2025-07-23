import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
from django.db.models import Q  # Pour des requêtes complexes
from django.conf import settings
from skill_training.models import Skill, TrainingCourse, EmployeeSkill, RecommendedTraining, SkillGapAnalysis, EmployeeTraining
from employee.models import Employee


def prepare_data_for_recommendation():
    """
    Prépare les données des compétences et des formations dans un format adapté à l'IA.
    """
    # Récupérer toutes les compétences et leurs descriptions
    skills_data = Skill.objects.all().values('id', 'name', 'description', 'is_critical_for_snel')
    df_skills = pd.DataFrame(list(skills_data))

    # Récupérer toutes les formations et leurs compétences couvertes
    courses_data = []
    for course in TrainingCourse.objects.all():
        skills_covered_names = [skill.name for skill in course.skills_covered.all()]
        courses_data.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'provider': course.provider,
            'duration_hours': course.duration_hours,
            'cost': float(course.cost) if course.cost else 0.0,  # Convertir DecimalField en float
            'skills_covered_names': skills_covered_names,
        })
    df_courses = pd.DataFrame(courses_data)

    if df_skills.empty or df_courses.empty:
        return None, None, None, None

    # Appliquer TF-IDF sur les descriptions des compétences
    # et les titres/descriptions des formations pour une analyse sémantique
    vectorizer = TfidfVectorizer(stop_words=['french'])

    # Concaténer description et nom pour les compétences
    df_skills['text_features'] = df_skills['name'] + " " + df_skills['description'].fillna('')
    skill_features = vectorizer.fit_transform(df_skills['text_features'])

    # Concaténer titre, description et compétences couvertes pour les formations
    df_courses['text_features'] = df_courses['title'] + " " + \
                                  df_courses['description'].fillna('') + " " + \
                                  df_courses['skills_covered_names'].apply(lambda x: ' '.join(x))
    course_features = vectorizer.transform(df_courses['text_features'])  # Utiliser le même vectorizer

    return df_skills, df_courses, skill_features, course_features, vectorizer


def get_skill_gap_for_employee(employee: Employee):
    """
    Identifie les lacunes en compétences pour un employé donné.
    Les lacunes sont les compétences critiques que l'employé ne possède pas
    ou dont le niveau de maîtrise est faible.
    """
    employee_current_skills_qs = EmployeeSkill.objects.filter(employee=employee)
    employee_skill_ids = set(es.skill.id for es in employee_current_skills_qs)

    # Récupérer les compétences critiques pour la SNEL
    critical_skills = Skill.objects.filter(is_critical_for_snel=True)
    critical_skill_ids = set(s.id for s in critical_skills)

    # Identifier les compétences critiques manquantes ou avec un faible niveau de maîtrise
    # Pour un niveau de maîtrise faible, on peut définir un seuil (ex: < 3)
    low_proficiency_skills = set(
        es.skill.id for es in employee_current_skills_qs
        if es.proficiency_level < 5  # Exemple: considérer une lacune si niveau < Intermédiaire
    )

    gaps_ids = (critical_skill_ids - employee_skill_ids) | low_proficiency_skills
    return Skill.objects.filter(id__in=list(gaps_ids))


def calculate_similarity_and_recommendations(employee: Employee, df_skills, df_courses, skill_features, course_features,
                                             vectorizer):
    """
    Calcule la similarité entre les compétences de l'employé et les formations.
    Génère des recommandations basées sur les lacunes et la pertinence des formations.
    """
    if df_skills is None or df_courses is None or skill_features is None or course_features is None:
        return []

    # 1. Identifier les lacunes en compétences de l'employé
    gaps_qs = get_skill_gap_for_employee(employee)
    if not gaps_qs.exists():
        # Si aucune lacune critique, on peut chercher à améliorer les compétences existantes
        # ou recommander des formations d'enrichissement. Pour l'instant, on se concentre sur les lacunes.
        print(f"DEBUG: Aucune lacune critique identifiée pour {employee.username}.")
        # Fallback: Recommander des formations générales ou de niveau supérieur
        # Pour cet exemple, on arrête ici si pas de lacunes clairement identifiées
        return []

    identified_gap_skills_names = [s.name for s in gaps_qs]

    # Convertir les noms des compétences manquantes en features pour la similarité
    gap_skill_text_features = ' '.join(identified_gap_skills_names)
    gap_features_vector = vectorizer.transform([gap_skill_text_features])

    # Calculer la similarité cosinus entre les lacunes de l'employé et les formations
    # Ici, nous comparons le vecteur des lacunes avec les vecteurs des formations
    cosine_sim = cosine_similarity(gap_features_vector, course_features).flatten()

    # Combiner les scores de similarité avec les informations des formations
    df_courses['similarity_score'] = cosine_sim

    # Filtrer les formations déjà recommandées ou suivies par l'employé
    already_recommended_courses = RecommendedTraining.objects.filter(employee=employee,
                                                                     status__in=['En attente', 'Acceptée',
                                                                                 'Inscrite']).values_list(
        'training_course_id', flat=True)
    already_completed_courses = EmployeeTraining.objects.filter(employee=employee, status='Terminé').values_list(
        'course_id', flat=True)

    df_filtered_courses = df_courses[
        (~df_courses['id'].isin(list(already_recommended_courses))) &
        (~df_courses['id'].isin(list(already_completed_courses)))
        ]

    # Trier par score de similarité (décroissant)
    # On peut aussi ajouter d'autres facteurs ici: coût, durée, type...
    df_recommendations = df_filtered_courses.sort_values(by='similarity_score', ascending=False)

    # Limiter le nombre de recommandations
    top_n_recommendations = df_recommendations.head(1)  # Recommander les 5 meilleures

    recommendations_list = []
    for index, row in top_n_recommendations.iterrows():
        # Générer un raisonnement simple pour la recommandation
        reasoning = f"Cette formation est recommandée car elle couvre des compétences ({', '.join(row['skills_covered_names'])}) qui peuvent aider à combler vos lacunes identifiées en {', '.join(identified_gap_skills_names)}."

        # Le score de confiance peut être le score de similarité lui-même, normalisé si nécessaire.
        confidence = round(float(row['similarity_score']), 2)


        if confidence*100 > 40 :

            recommendations_list.append({
                'employee': employee,
                'training_course_id': row['id'],
                'ai_reasoning': reasoning,
                'confidence_score': confidence * 100,
                'identified_gaps_qs': gaps_qs  # Passer le QuerySet des lacunes
            })

    return recommendations_list


def run_ai_recommendation_process():
    """
    Fonction principale pour exécuter le processus de recommandation pour tous les employés.
    """
    print("Lancement du processus de recommandation IA...")
    df_skills, df_courses, skill_features, course_features, vectorizer = prepare_data_for_recommendation()

    if df_skills is None or df_courses is None:
        print("Données insuffisantes pour la recommandation.")
        return False

    employees = Employee.objects.all().exclude(is_superuser=True)
    new_recommendations_count = 0

    for employee in employees:
        print(f"Analyse pour l'employé : {employee.username}")
        # Étape 1: Exécuter l'analyse des lacunes et l'enregistrer
        gaps = get_skill_gap_for_employee(employee)
        if gaps.exists():
            gap_analysis_reason = f"Lacunes identifiées basées sur les compétences critiques SNEL et/ou le faible niveau de maîtrise. Compétences manquantes ou faibles : {', '.join([s.name for s in gaps])}"
            skill_gap_analysis, created = SkillGapAnalysis.objects.get_or_create(
                employee=employee,
                # On peut ajouter une logique pour éviter des doublons si l'analyse est trop fréquente
                # Par exemple, vérifier si une analyse similaire existe depuis moins d'une semaine
                defaults={
                    'recommendation_reason': gap_analysis_reason,
                }
            )
            if not created:
                # Mettre à jour si elle existe déjà et est pertinente
                skill_gap_analysis.analysis_date = pd.Timestamp.now()
                skill_gap_analysis.recommendation_reason = gap_analysis_reason
                skill_gap_analysis.save()

            # Mettre à jour les compétences identifiées comme lacunes
            skill_gap_analysis.identified_gaps.set(gaps)
        else:
            skill_gap_analysis = None
            print(f"Aucune lacune significative identifiée pour {employee.username}. Pas d'analyse enregistrée.")
            continue  # Si pas de lacune, pas de recommandation basée sur les lacunes pour l'instant

        # Étape 2: Générer les recommandations de formation basées sur l'analyse
        recommendations = calculate_similarity_and_recommendations(
            employee, df_skills, df_courses, skill_features, course_features, vectorizer
        )

        for rec_data in recommendations:
            training_course = TrainingCourse.objects.get(id=rec_data['training_course_id'])

            # Créer ou mettre à jour la recommandation
            # On utilise get_or_create pour éviter les doublons si la même recommandation est faite à nouveau
            recommended_training, created = RecommendedTraining.objects.get_or_create(
                employee=employee,
                training_course=training_course,
                defaults={
                    'reasoning': rec_data['ai_reasoning'],
                    'confidence_score': rec_data['confidence_score'],
                    'originating_gap_analysis': skill_gap_analysis  # Lien vers l'analyse de lacune
                }
            )
            if created:
                new_recommendations_count += 1
                print(f"  + Nouvelle recommandation pour {employee.username}: {training_course.title}")
            else:
                # Si elle existe déjà et n'est pas en "acceptée" ou "inscrite", on peut la mettre à jour
                if recommended_training.status not in ['Acceptée', 'Inscrite', 'Terminée']:
                    recommended_training.reasoning = rec_data['ai_reasoning']
                    recommended_training.confidence_score = rec_data['confidence_score']
                    recommended_training.originating_gap_analysis = skill_gap_analysis
                    recommended_training.save()
                    print(f"  ~ Recommandation existante mise à jour pour {employee.username}: {training_course.title}")

    return True

