# CODE GENERER PAR IA POUR PEUPLER LA BASE DE DONNEE


"""
    GENERE UNE LISTE DE 20 EMPLOYEE ET LE REPARTI PAR DEPARTEMENTS
"""

# --- Start Copy from here ---

from datetime import date

from django.db import IntegrityError

from employee.models import Employee, Position, Department

# Mot de passe par défaut pour tous les utilisateurs créés (À CHANGER EN PRODUCTION !)
DEFAULT_PASSWORD = "password123"

# --- Création des Départements (si non existants) ---
department_names = [
    "Production & Transport",
    "Ressources Humaines & Administration",
    "Finances & Commercial",
    "Technique & Ingénierie",
    "Support & Logistique"
]
department_objects = {}
for dept_name in department_names:
    dept, created = Department.objects.get_or_create(name=dept_name, defaults={'description': f'Département de {dept_name}'})
    department_objects[dept_name] = dept
    if created:
        print(f"Département '{dept_name}' créé.")

# --- Création des Postes (réduit à 6 postes hiérarchiques) ---
position_names = [
    "Directeur Général Adjoint", # Poste de haute direction
    "Directeur de Département",  # Managers de haut niveau (incluant RH)
    "Chef de Service",           # Managers intermédiaires
    "Ingénieur / Spécialiste",   # Experts techniques
    "Technicien / Agent",        # Rôles opérationnels
    "Assistant Administratif"    # Rôles de support
]

position_objects = {}
for pos_name in position_names:
    pos, created = Position.objects.get_or_create(title=pos_name, defaults={'description': f'Description du poste {pos_name}'})
    position_objects[pos_name] = pos
    if created:
        print(f"Poste '{pos_name}' créé.")


# --- Données des Employés ---
# 20 employés avec 2 HR et 5 Managers, tous is_staff=False, is_superuser=False
# Les postes sont maintenant mappés aux 6 nouveaux postes réduits.
employees_data = [
    # HR - is_hr=True, is_manager=False (Note: Fatou est Directrice de Département RH, Esther est Spécialiste/Conseillère)
    {
        "first_name": "Fatou", "last_name": "Diallo", "email": "fatou.diallo@snel.cd",
        "department": "Ressources Humaines & Administration", "position": "Directeur de Département",
        "hire_date": "2010-01-20", "is_hr": True, "is_manager": False
    },
    {
        "first_name": "Esther", "last_name": "Kibonge", "email": "esther.kibonge@snel.cd",
        "department": "Ressources Humaines & Administration", "position": "Ingénieur / Spécialiste",
        "hire_date": "2011-04-20", "is_hr": True, "is_manager": False
    },
    # Managers  (5 managers)
    {
        "first_name": "Jean-Luc", "last_name": "Kabongo", "email": "jeanluc.kabongo@snel.cd",
        "department": "Production & Transport", "position": "Directeur de Département",
        "hire_date": "2005-03-15", "is_hr": False, "is_manager": True
    },
    {
        "first_name": "Chantal", "last_name": "Mbuyi", "email": "chantal.mbuyi@snel.cd",
        "department": "Finances & Commercial", "position": "Directeur de Département",
        "hire_date": "2013-09-01", "is_hr": False, "is_manager": True
    },
    {
        "first_name": "Didier", "last_name": "Ngoy", "email": "didier.ngoy@snel.cd",
        "department": "Support & Logistique", "position": "Chef de Service", # Chef de Service est aussi un type de manager
        "hire_date": "2016-02-15", "is_hr": False, "is_manager": True
    },
    {
        "first_name": "Bruno", "last_name": "Mutombo", "email": "bruno.mutombo@snel.cd",
        "department": "Support & Logistique", "position": "Chef de Service",
        "hire_date": "2008-08-01", "is_hr": False, "is_manager": True
    },
    {
        "first_name": "Samuel", "last_name": "Kazadi", "email": "samuel.kazadi@snel.cd",
        "department": "Technique & Ingénierie", "position": "Chef de Service",
        "hire_date": "2014-03-25", "is_hr": False, "is_manager": True
    },
    # Employés réguliers (13 employés)
    {
        "first_name": "Marc", "last_name": "Dupont", "email": "marc.dupont@snel.cd",
        "department": "Technique & Ingénierie", "position": "Technicien / Agent",
        "hire_date": "2018-07-01", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Sophie", "last_name": "Nzuzi", "email": "sophie.nzuzi@snel.cd",
        "department": "Finances & Commercial", "position": "Ingénieur / Spécialiste",
        "hire_date": "2012-11-10", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Olivier", "last_name": "Lumu", "email": "olivier.lumu@snel.cd",
        "department": "Technique & Ingénierie", "position": "Ingénieur / Spécialiste",
        "hire_date": "2015-06-01", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Nathalie", "last_name": "Luzolo", "email": "nathalie.luzolo@snel.cd",
        "department": "Ressources Humaines & Administration", "position": "Assistant Administratif",
        "hire_date": "2019-01-05", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Christian", "last_name": "Maniema", "email": "christian.maniema@snel.cd",
        "department": "Technique & Ingénierie", "position": "Ingénieur / Spécialiste",
        "hire_date": "2017-03-10", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Marie", "last_name": "Kabasele", "email": "marie.kabasele@snel.cd",
        "department": "Finances & Commercial", "position": "Ingénieur / Spécialiste",
        "hire_date": "2014-05-22", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Patrick", "last_name": "Kimwenza", "email": "patrick.kimwenza@snel.cd",
        "department": "Production & Transport", "position": "Technicien / Agent",
        "hire_date": "2007-09-01", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Grace", "last_name": "Banza", "email": "grace.banza@snel.cd",
        "department": "Ressources Humaines & Administration", "position": "Assistant Administratif",
        "hire_date": "2020-02-01", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Kevin", "last_name": "Nzita", "email": "kevin.nzita@snel.cd",
        "department": "Technique & Ingénierie", "position": "Technicien / Agent",
        "hire_date": "2016-04-10", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Sarah", "last_name": "Kabamba", "email": "sarah.kabamba@snel.cd",
        "department": "Production & Transport", "position": "Ingénieur / Spécialiste",
        "hire_date": "2019-08-20", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Alexandre", "last_name": "Mabiala", "email": "alexandre.mabiala@snel.cd",
        "department": "Support & Logistique", "position": "Technicien / Agent",
        "hire_date": "2015-11-05", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Laura", "last_name": "Lukusa", "email": "laura.lukusa@snel.cd",
        "department": "Finances & Commercial", "position": "Assistant Administratif",
        "hire_date": "2017-06-12", "is_hr": False, "is_manager": False
    },
    {
        "first_name": "Emma", "last_name": "Kamwanga", "email": "emma.kamwanga@snel.cd",
        "department": "Production & Transport", "position": "Ingénieur / Spécialiste",
        "hire_date": "2021-01-15", "is_hr": False, "is_manager": False
    }
]

# --- Création des Employés ---
created_employees_count = 0
for emp_data in employees_data:
    try:
        # Récupérer les objets ForeignKey
        department_obj = department_objects.get(emp_data["department"])
        position_obj = position_objects.get(emp_data["position"])

        # Utiliser l'email comme identifiant unique
        employee, created = Employee.objects.get_or_create(
            email=emp_data["email"], # L'email est le USERNAME_FIELD
            defaults={
                'first_name': emp_data["first_name"],
                'last_name': emp_data["last_name"],
                'department': department_obj,
                'position': position_obj,
                'hire_date': date.fromisoformat(emp_data["hire_date"]),
                'is_staff': False,          # Tous à False
                'is_superuser': False,      # Tous à False
                'is_hr': emp_data["is_hr"],
                'is_manager': emp_data["is_manager"]
            }
        )

        if created:
            employee.set_password(DEFAULT_PASSWORD)
            employee.save() # La méthode save() du modèle générera l'employee_id ici
            created_employees_count += 1
            print(f"Employé '{employee.full_name}' créé avec l'email : {employee.email}")
        else:
            # Si l'employé existe déjà, le mettre à jour avec les nouveaux rôles et département/poste.
            employee.first_name = emp_data["first_name"]
            employee.last_name = emp_data["last_name"]
            employee.department = department_obj
            employee.position = position_obj
            employee.hire_date = date.fromisoformat(emp_data["hire_date"])
            employee.is_staff = False
            employee.is_superuser = False
            employee.is_hr = emp_data["is_hr"]
            employee.is_manager = emp_data["is_manager"]
            employee.save()
            print(f"Employé '{employee.full_name}' (Email: {employee.email}) mis à jour.")

    except IntegrityError:
        print(f"Erreur: L'employé avec l'email '{emp_data['email']}' existe déjà et ne peut être mis à jour (problème d'unicité). skipping.")
    except Exception as e:
        print(f"Erreur inattendue lors de la création/mise à jour de l'employé {emp_data.get('email', emp_data.get('first_name'))}: {e}")

print(f"\nProcessus terminé. {created_employees_count} nouveaux employés créés (des existants peuvent avoir été mis à jour).")
print(f"Vérifiez les rôles RH et Manager en consultant les employés dans l'interface d'administration.")

# --- End Copy here ---






"""
    Genere les competences et les attribuent a des employee en s'assurant que 60% d'entre eux manque
    de compentences clef.
"""

# --- Start Copy from here ---

from employee.models import Employee
from skill_training.models import SkillCategory, Skill, EmployeeSkill
import random

# --- Création des Catégories de Compétences (si non existantes) ---
skill_category_names = [
    "Compétences Techniques Électriques",
    "Compétences Managériales",
    "Compétences Informatiques",
    "Compétences Administratives",
    "Compétences de Sécurité",
    "Compétences Commerciales"
]
skill_category_objects = {}
for cat_name in skill_category_names:
    category, created = SkillCategory.objects.get_or_create(name=cat_name)
    skill_category_objects[cat_name] = category
    if created:
        print(f"Catégorie de compétence '{cat_name}' créée.")

# --- Création des Compétences (14 au total, dont 9 critiques) avec descriptions spécifiques ---
critical_skills_data = [
    {"name": "Sécurité Électrique BT/HT", "category": "Compétences Techniques Électriques",
     "is_critical_for_snel": True,
     "description": "Maîtrise des normes et procédures de sécurité pour les installations Basse et Haute Tension."},
    {"name": "Gestion de Projet Agile", "category": "Compétences Managériales", "is_critical_for_snel": True,
     "description": "Application des méthodologies Agile pour la planification et l'exécution de projets complexes."},
    {"name": "Cybersécurité des Systèmes Industriels", "category": "Compétences Informatiques",
     "is_critical_for_snel": True,
     "description": "Protection des systèmes de contrôle industriel (SCADA/DCS) contre les menaces cybernétiques."},
    {"name": "Réglementation et Conformité SNEL", "category": "Compétences Administratives",
     "is_critical_for_snel": True,
     "description": "Connaissance approfondie des lois, décrets et directives régissant les activités de la SNEL."},
    {"name": "Maintenance des Transformateurs", "category": "Compétences Techniques Électriques",
     "is_critical_for_snel": True,
     "description": "Diagnostic, réparation et entretien préventif/curatif des transformateurs de puissance."},
    {"name": "Analyse Financière Avancée", "category": "Compétences Commerciales", "is_critical_for_snel": True,
     "description": "Évaluation complexe de la santé financière des projets et de l'entreprise."},
    {"name": "Gestion des Crises et Continuité d'Activité", "category": "Compétences de Sécurité",
     "is_critical_for_snel": True,
     "description": "Mise en place de plans pour faire face aux incidents majeurs et assurer la reprise des opérations."},
    {"name": "Systèmes SCADA/DCS", "category": "Compétences Informatiques", "is_critical_for_snel": True,
     "description": "Opération et configuration des systèmes de contrôle et d'acquisition de données."},
    {"name": "Négociation Commerciale Internationale", "category": "Compétences Commerciales",
     "is_critical_for_snel": True,
     "description": "Conduite de négociations complexes avec des partenaires et fournisseurs étrangers."},
]

non_critical_skills_data = [
    {"name": "Communication Interpersonnelle", "category": "Compétences Managériales", "is_critical_for_snel": False,
     "description": "Capacité à interagir efficacement avec des collègues et des partenaires."},
    {"name": "Maîtrise d'Excel Avancé", "category": "Compétences Administratives", "is_critical_for_snel": False,
     "description": "Utilisation experte des fonctions avancées d'Excel pour l'analyse de données."},
    {"name": "Sensibilisation Environnementale", "category": "Compétences de Sécurité", "is_critical_for_snel": False,
     "description": "Compréhension des enjeux environnementaux liés à l'activité industrielle."},
    {"name": "Base de Données SQL", "category": "Compétences Informatiques", "is_critical_for_snel": False,
     "description": "Compétences de base en écriture et interprétation de requêtes SQL."},
    {"name": "Premiers Secours en Milieu Industriel", "category": "Compétences de Sécurité",
     "is_critical_for_snel": False,
     "description": "Connaissance des gestes qui sauvent en cas d'accident sur site industriel."},
]

all_skills_data = critical_skills_data + non_critical_skills_data
skill_objects = {}

for s_data in all_skills_data:
    category_obj = skill_category_objects.get(s_data["category"])
    skill, created = Skill.objects.get_or_create(
        name=s_data["name"],
        defaults={
            'description': s_data['description'],  # Utilisation de la description spécifique
            'category': category_obj,
            'is_critical_for_snel': s_data["is_critical_for_snel"]
        }
    )
    skill_objects[s_data["name"]] = skill
    if created:
        print(f"Compétence '{s_data['name']}' créée (Critique: {s_data['is_critical_for_snel']}).")

# --- Définition des Compétences Essentielles par Département/Poste ---
# Mapper les départements et postes aux compétences "essentielles"
# et une liste de compétences communes (non essentielles mais utiles)
department_essential_skills = {
    "Production & Transport": [
        skill_objects["Sécurité Électrique BT/HT"],
        skill_objects["Maintenance des Transformateurs"],
        skill_objects["Systèmes SCADA/DCS"]
    ],
    "Technique & Ingénierie": [
        skill_objects["Cybersécurité des Systèmes Industriels"],
        skill_objects["Systèmes SCADA/DCS"],
        skill_objects["Gestion de Projet Agile"]
    ],
    "Finances & Commercial": [
        skill_objects["Analyse Financière Avancée"],
        skill_objects["Négociation Commerciale Internationale"],
        skill_objects["Maîtrise d'Excel Avancé"]
    ],
    "Ressources Humaines & Administration": [
        skill_objects["Réglementation et Conformité SNEL"],
        skill_objects["Gestion de Projet Agile"],
        skill_objects["Communication Interpersonnelle"]
    ],
    "Support & Logistique": [
        skill_objects["Gestion des Crises et Continuité d'Activité"],
        skill_objects["Premiers Secours en Milieu Industriel"],
        skill_objects["Maîtrise d'Excel Avancé"]
    ]
}

# Compétences communes ou générales que beaucoup d'employés pourraient avoir
common_skills = [
    skill_objects["Communication Interpersonnelle"],
    skill_objects["Maîtrise d'Excel Avancé"],
    skill_objects["Sensibilisation Environnementale"],
]

# --- Attribution des Compétences aux Employés ---
employees = Employee.objects.all().exclude(is_superuser=True)
# Shuffle employees to randomly select 60% for missing skills
random_employees = list(employees)
random.shuffle(random_employees)

# Calculate 60% of employees
num_employees_to_have_gaps = int(len(random_employees) * 0.60)
employees_with_gaps = random_employees[:num_employees_to_have_gaps]
employees_without_gaps = random_employees[num_employees_to_have_gaps:]

print(
    f"\nAttribution des compétences aux employés ({len(employees_with_gaps)} auront des lacunes, {len(employees_without_gaps)} auront toutes les compétences essentielles)...")

for employee in employees:
    # Clear existing skills for clean re-run if needed
    EmployeeSkill.objects.filter(employee=employee).delete()

    # Get essential skills for their department
    employee_dept_skills = department_essential_skills.get(employee.department.name, [])

    # Add some common skills randomly
    current_employee_skills = set(random.sample(common_skills, random.randint(1, len(common_skills))))

    # Determine if this employee should miss essential skills
    if employee in employees_with_gaps:
        # For employees with gaps: assign only a subset of essential skills, or none.
        # Ensure they miss at least one critical skill for their department if possible.
        num_essential_to_keep = random.randint(0, max(0, len(employee_dept_skills) - 1))  # Keep 0 to N-1 essential skills
        skills_to_add = random.sample(employee_dept_skills, num_essential_to_keep)
        current_employee_skills.update(skills_to_add)
        print( f"- {employee.full_name}: Aura des lacunes intentionnelles. Compétences essentielles attribuées: {[s.name for s in skills_to_add]}.")
    else:
        # For employees without gaps: assign all essential skills for their department
        current_employee_skills.update(employee_dept_skills)
        print( f"- {employee.full_name}: Aura toutes les compétences essentielles de son département. Compétences essentielles attribuées: {[s.name for s in employee_dept_skills]}.")

    # Assign proficiency levels (e.g., 3-5 for acquired skills)
    for skill_obj in current_employee_skills:
        # Assign a random proficiency level between 3 (Intermédiaire) and 5 (Expert)
        proficiency = random.randint(3, 5)
        EmployeeSkill.objects.create( employee=employee, skill=skill_obj, proficiency_level=proficiency, assessed_by=None, assessment_method='AI' )

    if not current_employee_skills:  # Ensure at least one skill to avoid empty records for analysis
        # If by chance an employee ends up with no skills, assign a common one
        EmployeeSkill.objects.create( employee=employee, skill=random.choice(common_skills), proficiency_level=random.randint(2, 3), assessed_by=None, assessment_method='AI' )
        print( f"  (Note: Ajout d'une compétence de base pour {employee.full_name} car aucune n'a été attribuée initialement.)")

print("\nAttribution des compétences terminée.")
print("Vous pouvez maintenant lancer le script de recommandation IA.")

# --- End Copy here ---



""" 
    ENRICHIRE LA BASE DE DONNE ET SURTOUT LA TABLE EMPLOYEE
"""

from datetime import date, timedelta
import random
from employee.models import Employee, Department  # Assurez-vous que l'importation est correcte
from django.db import transaction


# Fonction utilitaire pour générer des données aléatoires
def generate_random_date_of_birth():
    today = date.today()
    start_date = today - timedelta(days=365 * 50)
    end_date = today - timedelta(days=365 * 22)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date


def generate_random_phone_number():
    # Format DRC: +243 8X XXX XXXX
    return f"+243 8{random.randint(1, 9)}{random.randint(100, 999)}{random.randint(1000, 9999)}"


def generate_random_address():
    streets = ["Avenue de la Victoire", "Boulevard du 30 Juin", "Avenue des Huileries", "Rue Lukusa", "Avenue Kabinda"]
    cities = ["Kinshasa"]  # Puisque SNEL est basé à Kinshasa
    return f"{random.randint(1, 999)} {random.choice(streets)}, {random.choice(cities)}"


def generate_random_salary(is_manager):
    if is_manager:
        return round(random.uniform(1500.00, 4000.00), 2)  # Salaire plus élevé pour les managers
    return round(random.uniform(500.00, 1500.00), 2)


def generate_emergency_contact_name():
    first_names = ["Mutombo", "Kazadi", "Kalala", "Mweze", "Mwamba", "Kanku", "Ngoy", "Lunda"]
    last_names = ["Georges", "Marie", "Bienvenu", "Julie", "Christian", "Rachel", "David", "Esther"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


# --- Début de la mise à jour des employés ---
print("Lancement de la mise à jour des informations complémentaires des employés...")

# Récupérer tous les employés et organiser les managers par département
# Cela optimise la recherche de managers pour les non-managers
all_employees = Employee.objects.all().exclude(is_superuser=True)
managers_by_department = {dept.name: [] for dept in Department.objects.all()}

for emp in all_employees:
    if emp.is_manager and emp.department:  # S'il est manager et a un département assigné
        managers_by_department[emp.department.name].append(emp)

updated_count = 0
for employee in all_employees:
    try:
        # Générer des informations aléatoires
        employee.date_of_birth = generate_random_date_of_birth()
        employee.gender = random.choice(['M', 'F'])
        employee.phone_number = generate_random_phone_number()
        employee.address = generate_random_address()
        employee.salary = generate_random_salary(employee.is_manager)
        employee.emergency_contact_name = generate_emergency_contact_name()
        employee.emergency_contact_phone = generate_random_phone_number()  # Peut réutiliser la fonction pour téléphone

        # Attribuer un manager si l'employé n'est pas un manager lui-même
        if not employee.is_manager:
            if employee.department and employee.department.name in managers_by_department:
                possible_managers = managers_by_department[employee.department.name]
                if possible_managers:
                    # Choisir un manager aléatoire du même département
                    # Assurer qu'un employé ne soit pas son propre manager
                    eligible_managers = [m for m in possible_managers if m != employee]
                    if eligible_managers:
                        employee.manager = random.choice(eligible_managers)
                    else:
                        employee.manager = None  # Pas de manager disponible dans le département
                        print(
                            f"  Avertissement: Aucun manager disponible dans le département '{employee.department.name}' pour {employee.full_name}.")
                else:
                    employee.manager = None  # Aucun manager dans ce département
                    print(
                        f"  Avertissement: Aucun manager trouvé dans le département '{employee.department.name}' pour {employee.full_name}.")
            else:
                employee.manager = None  # Pas de département ou département non trouvé
                print(
                    f"  Avertissement: Le département de {employee.full_name} n'est pas trouvé ou n'a pas de managers définis.")
        else:
            employee.manager = None  # Les managers n'ont pas de manager direct pour cette simulation

        # Sauvegarder les modifications dans la base de données
        employee.save(update_fields=[
            'date_of_birth', 'gender', 'phone_number', 'address', 'salary',
            'emergency_contact_name', 'emergency_contact_phone', 'manager'
        ])
        updated_count += 1
        print(
            f"  Employé {employee.full_name} ({employee.email}) mis à jour. Manager: {employee.manager.full_name if employee.manager else 'Aucun'}")

    except Exception as e:
        print(f"Erreur lors de la mise à jour de l'employé {employee.full_name} ({employee.email}): {e}")

# Open your Django shell by navigating to your project's root directory
# (where manage.py is located) and running:
# python manage.py shell

# --- Start Copy from here ---


"""
    GENER UNE LISTE DE 15 COURS COUVRANT DE COMPETENCES CLEF POUR LA SNEL 
"""


from skill_training.models import Skill, TrainingCourse
import random

# Récupérer toutes les compétences existantes
all_skills = Skill.objects.all()
skill_objects = {skill.name: skill for skill in all_skills}

# --- Données des 15 Cours de Formation (adaptées au modèle TrainingCourse) ---
courses_data = [
    {
        "title": "Formation Avancée en Sécurité Électrique (BT/HT)",
        "description": "Cours intensif sur les protocoles de sécurité, les risques et les mesures préventives pour les installations électriques Basse et Haute Tension. Essentiel pour le personnel technique.",
        "provider": "Institut National de l'Électricité",
        "duration_hours": 80,  # 10 jours * 8 heures
        "cost": 800.00,
        "skills_covered_names": ["Sécurité Électrique BT/HT", "Premiers Secours en Milieu Industriel",
                                 "Sensibilisation Environnementale"],
        "training_type": "En Présentiel",
        "url_link": None
    },
    {
        "title": "Maîtrise des Méthodologies de Gestion de Projet Agile",
        "description": "Apprenez à planifier, exécuter et livrer des projets en utilisant les cadres Scrum et Kanban pour une efficacité maximale dans tous les départements.",
        "provider": "PMI Congo",
        "duration_hours": 56,  # 7 jours * 8 heures
        "cost": 1200.00,
        "skills_covered_names": ["Gestion de Projet Agile", "Communication Interpersonnelle"],
        "training_type": "En Ligne",
        "url_link": "https://pmi-congo.org/agile-mastery"
    },
    {
        "title": "Cybersécurité Appliquée aux Systèmes Industriels (ICS/SCADA)",
        "description": "Protégez les infrastructures critiques de la SNEL en maîtrisant les techniques de défense contre les cybermenaces ciblant les systèmes industriels et réseaux opérationnels.",
        "provider": "CyberSec Solutions RDC",
        "duration_hours": 96,  # 12 jours * 8 heures
        "cost": 1500.00,
        "skills_covered_names": ["Cybersécurité des Systèmes Industriels", "Systèmes SCADA/DCS", "Base de Données SQL"],
        "training_type": "Mixte (En ligne et Présentiel)",
        "url_link": "https://cybersec-rdc.com/ics-scada-security"
    },
    {
        "title": "Réglementation et Cadre Légal de la SNEL et du Secteur Énergétique Congolais",
        "description": "Comprenez en profondeur le cadre réglementaire national et international qui régit les opérations de la SNEL, y compris les licences et conformités.",
        "provider": "Barreau de Kinshasa",
        "duration_hours": 40,  # 5 jours * 8 heures
        "cost": 600.00,
        "skills_covered_names": ["Réglementation et Conformité SNEL"],
        "training_type": "En Présentiel",
        "url_link": None
    },
    {
        "title": "Diagnostic et Maintenance Préventive des Transformateurs de Puissance",
        "description": "Formation pratique sur l'inspection, le diagnostic de panne et la maintenance préventive et corrective des transformateurs électriques pour prolonger leur durée de vie.",
        "provider": "Centre de Formation Électrique SNEL",
        "duration_hours": 64,  # 8 jours * 8 heures
        "cost": 950.00,
        "skills_covered_names": ["Maintenance des Transformateurs", "Sécurité Électrique BT/HT"],
        "training_type": "En Présentiel",
        "url_link": None
    },
    {
        "title": "Atelier Pratique d'Analyse Financière Avancée",
        "description": "Développez des compétences pour interpréter les états financiers, évaluer la rentabilité des projets et prendre des décisions d'investissement éclairées pour la SNEL.",
        "provider": "KPMG RDC",
        "duration_hours": 48,  # 6 jours * 8 heures
        "cost": 750.00,
        "skills_covered_names": ["Analyse Financière Avancée", "Maîtrise d'Excel Avancé"],
        "training_type": "En Ligne",
        "url_link": "https://kpmg.cd/financial-analysis"
    },
    {
        "title": "Gestion de Crise et Élaboration de Plan de Continuité d'Activité (PCA)",
        "description": "Élaborez et mettez en œuvre des stratégies robustes pour répondre efficacement aux crises (techniques, naturelles, etc.) et assurer la résilience opérationnelle de la SNEL.",
        "provider": "Resilience Consulting Group",
        "duration_hours": 72,  # 9 jours * 8 heures
        "cost": 1100.00,
        "skills_covered_names": ["Gestion des Crises et Continuité d'Activité", "Communication Interpersonnelle"],
        "training_type": "Mixte (En ligne et Présentiel)",
        "url_link": "https://resiliencegroup.com/crisis-bcp"
    },
    {
        "title": "Opération et Optimisation Avancée des Systèmes SCADA/DCS",
        "description": "Cours technique approfondi sur l'utilisation avancée, la configuration et l'optimisation des systèmes de contrôle et d'acquisition de données dans les infrastructures électriques complexes.",
        "provider": "Schneider Electric Academy",
        "duration_hours": 56,  # 7 jours * 8 heures
        "cost": 900.00,
        "skills_covered_names": ["Systèmes SCADA/DCS", "Cybersécurité des Systèmes Industriels"],
        "training_type": "En Présentiel",
        "url_link": None
    },
    {
        "title": "Stratégies de Négociation Commerciale Internationale B2B",
        "description": "Perfectionnez vos compétences en négociation pour conclure des accords complexes avec des partenaires et fournisseurs étrangers, maximisant la valeur pour la SNEL.",
        "provider": "International Business Institute",
        "duration_hours": 48,  # 6 jours * 8 heures
        "cost": 1300.00,
        "skills_covered_names": ["Négociation Commerciale Internationale", "Analyse Financière Avancée"],
        "training_type": "En Ligne",
        "url_link": "https://ibi-global.org/negotiation-strategies"
    },
    {
        "title": "Atelier de Communication Interpersonnelle et Gestion des Conflits",
        "description": "Améliorez vos compétences de communication pour favoriser un environnement de travail collaboratif, gérer les désaccords et renforcer la cohésion d'équipe.",
        "provider": "RH Consult RDC",
        "duration_hours": 24,  # 3 jours * 8 heures
        "cost": 400.00,
        "skills_covered_names": ["Communication Interpersonnelle"],
        "training_type": "En Présentiel",
        "url_link": None
    },
    {
        "title": "Maîtrise d'Excel pour l'Analyse de Données et le Reporting RH",
        "description": "Exploitez tout le potentiel d'Excel pour l'analyse de grandes quantités de données, la création de tableaux de bord et l'automatisation des tâches de reporting.",
        "provider": "Data Skills Africa",
        "duration_hours": 32,  # 4 jours * 8 heures
        "cost": 550.00,
        "skills_covered_names": ["Maîtrise d'Excel Avancé", "Base de Données SQL"],
        "training_type": "En Ligne",
        "url_link": "https://dataskills.africa/excel-hr-analytics"
    },
    {
        "title": "Sensibilisation et Bonnes Pratiques Environnementales en Industrie Énergétique",
        "description": "Comprenez les enjeux environnementaux de l'industrie énergétique et apprenez à identifier et réduire les impacts écologiques des opérations de la SNEL.",
        "provider": "Green DRC Initiatives",
        "duration_hours": 16,  # 2 jours * 8 heures
        "cost": 300.00,
        "skills_covered_names": ["Sensibilisation Environnementale"],
        "training_type": "Mixte (En ligne et Présentiel)",
        "url_link": "https://greendrc.org/environmental-awareness"
    },
    {
        "title": "Introduction aux Bases de Données Relationnelles et Requêtes SQL",
        "description": "Découvrez les principes fondamentaux des bases de données relationnelles et pratiquez l'écriture de requêtes SQL de base pour la manipulation des données.",
        "provider": "Tech Academy Kinshasa",
        "duration_hours": 40,  # 5 jours * 8 heures
        "cost": 650.00,
        "skills_covered_names": ["Base de Données SQL"],
        "training_type": "En Ligne",
        "url_link": "https://techacademy-khi.com/sql-intro"
    },
    {
        "title": "Premiers Secours Avancés en Milieu Industriel (Habilitation)",
        "description": "Formation certifiante aux gestes de premiers secours adaptés aux risques spécifiques rencontrés dans les installations industrielles de la SNEL, y compris les blessures électriques.",
        "provider": "Croix-Rouge RDC",
        "duration_hours": 24,  # 3 jours * 8 heures
        "cost": 450.00,
        "skills_covered_names": ["Premiers Secours en Milieu Industriel", "Sécurité Électrique BT/HT"],
        "training_type": "En Présentiel",
        "url_link": None
    },
    {
        "title": "Leadership Stratégique et Motivation d'Équipe",
        "description": "Développez des compétences de leadership pour définir une vision, motiver vos équipes et atteindre les objectifs stratégiques de la SNEL.",
        "provider": "Global Leadership Center",
        "duration_hours": 40,  # 5 jours * 8 heures
        "cost": 1000.00,
        "skills_covered_names": ["Gestion de Projet Agile", "Communication Interpersonnelle"],
        "training_type": "En Présentiel",
        "url_link": None
    },
]

print("Création des cours de formation en utilisant le modèle TrainingCourse...")

for course_data in courses_data:
    # Créer ou récupérer le cours
    course, created = TrainingCourse.objects.get_or_create(
        title=course_data["title"],
        defaults={
            'description': course_data["description"],
            'provider': course_data["provider"],
            'duration_hours': course_data["duration_hours"],
            'cost': course_data["cost"],
            'training_type': course_data["training_type"],
            'url_link': course_data["url_link"]
        }
    )

    if created:
        print(f"Cours '{course.title}' créé.")
    else:
        print(f"Cours '{course.title}' existe déjà. Mise à jour des informations si nécessaire.")
        # Mettre à jour les champs si le cours existait déjà
        course.description = course_data["description"]
        course.provider = course_data["provider"]
        course.duration_hours = course_data["duration_hours"]
        course.cost = course_data["cost"]
        course.training_type = course_data["training_type"]
        course.url_link = course_data["url_link"]
        course.save()

    # Associer les compétences au cours (via ManyToManyField)
    # Effacer les anciennes associations pour éviter les doublons en cas de réexécution
    course.skills_covered.clear()

    for skill_name in course_data["skills_covered_names"]:
        skill = skill_objects.get(skill_name)
        if skill:
            course.skills_covered.add(skill)
        else:
            print(f"  AVERTISSEMENT: Compétence '{skill_name}' non trouvée pour le cours '{course.title}'.")

print("\nCréation et association des cours terminées en utilisant TrainingCourse.")

# --- End Copy here ---