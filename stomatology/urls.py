from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('doctors/', views.doctors_get, name='doctors'),
    path('doctor/add/', views.DoctorAdd.as_view(), name='doctor_add'),
    path('doctor/<int:pk>/edit', views.DoctorEdit.as_view(), name='doctor_edit'),
    path("doctor/<int:pk>/delete/", views.DoctorDelete.as_view(), name="doctor_delete"),
]
