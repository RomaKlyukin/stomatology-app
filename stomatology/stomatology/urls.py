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

    path('schedules/', views.schedules_get, name='schedules'),
    path('schedule/add/', views.ScheduleAdd.as_view(), name='schedule_add'),
    path('schedule/<int:pk>/edit', views.ScheduleEdit.as_view(), name='schedule_edit'),
    path("schedule/<int:pk>/delete/", views.ScheduleDelete.as_view(), name="schedule_delete"),

    path('services/', views.services_get, name='services'),
    path('service/add/', views.ServiceAdd.as_view(), name='service_add'),
    path('service/<int:pk>/edit', views.ServiceEdit.as_view(), name='service_edit'),
    path("service/<int:pk>/delete/", views.ServiceDelete.as_view(), name="service_delete"),

    path('services_rendered/', views.service_rendereds_get, name='services_rendered'),
    path('service_rendered/add/', views.Service_renderedAdd.as_view(), name='service_rendered_add'),
    path('service_rendered/<int:pk>/edit', views.Service_renderedEdit.as_view(), name='service_rendered_edit'),
    path("service_rendered/<int:pk>/delete/", views.Service_renderedDelete.as_view(), name="service_rendered_delete"),
    
    path('receptions/', views.receptions_get, name='receptions'),
    path('reception/add/', views.ReceptionAdd.as_view(), name='reception_add'),
    path('reception/<int:pk>/edit', views.ReceptionEdit.as_view(), name='reception_edit'),
    path("reception/<int:pk>/delete/", views.ReceptionDelete.as_view(), name="reception_delete"),

]
