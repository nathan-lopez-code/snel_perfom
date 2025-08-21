from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.


@login_required(login_url='dashboard:login')
def dashboard(request):


    return render(request, 'dashboard_admin.html', context={})