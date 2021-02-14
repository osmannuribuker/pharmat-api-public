from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from core.apps.app.views import *

urlpatterns = [
    path('', home, name='home'),
]