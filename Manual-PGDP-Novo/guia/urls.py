from django.urls import path
from . import views

app_name = "guia"

urlpatterns = [
    path("", views.home, name="home"),
    path("procedimento/<slug:slug>/", views.procedimento_detail, name="procedimento_detail"),
    path("procedimento/<slug:slug>/pdf/", views.procedimento_pdf, name="procedimento_pdf"),
]
