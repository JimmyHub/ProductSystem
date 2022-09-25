from django.urls import path
from . import views

urlpatterns=[
    path('/<str:pattern>/<str:browser>/<str:keyword>', views.ProductView.as_view()),
]