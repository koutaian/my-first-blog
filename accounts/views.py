from django.shortcuts import render
from .models import User, Class

def index(request):
    """user = User(username="dianman")
    user.set_password("12345")
    user.save()
    c = Class.objects.get(class_name="世界史")
    user.classes.add(c)"""
    return render(request, "registration/select.html")
