from django.shortcuts import render

DOCUMENTATION_DIR = "documentation"

# Create your views here.
def index(request):
    return render(request, DOCUMENTATION_DIR + "/index.html")
