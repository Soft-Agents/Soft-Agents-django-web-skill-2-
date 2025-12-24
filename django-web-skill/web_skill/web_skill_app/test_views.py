
from functools import wraps
from django.shortcuts import render, redirect # ⬅️ ADDED 'render'
from django.contrib import messages
from bson.objectid import ObjectId # (Usually not needed in a Django view unless you're using MongoDB)

def test_views(request):
    """
    Renders the test.html template for a GET request.
    This is a basic Django view function.
    """
    # Django's 'render' function takes the request object, 
    # the template path, and an optional context dictionary.
    return render(request, 'web_skill_app/test.html')