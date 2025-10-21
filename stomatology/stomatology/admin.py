from django.contrib import admin
from .models import Doctor, Patient, Reception, Service, Service_rendered, Schedule

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Reception)
admin.site.register(Service)
admin.site.register(Service_rendered)
admin.site.register(Schedule)