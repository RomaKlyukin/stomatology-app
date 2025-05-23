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

    path('patients/', views.patients_get, name='patients'),
    path('patient/add/', views.PatientAdd.as_view(), name='patient_add'),
    path('patient/<int:pk>/edit', views.PatientEdit.as_view(), name='patient_edit'),
    path("patient/<int:pk>/delete/", views.PatientDelete.as_view(), name="patient_delete"),

]
