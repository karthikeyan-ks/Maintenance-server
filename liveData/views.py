from django.shortcuts import render

# Create your views here.
def index(request): 
    return render(request, 'liveData.html', {}) 

def admin_login(request):
    # Logic to handle the request, if needed
    return render(request, 'admin_login.html')