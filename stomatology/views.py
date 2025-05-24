from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q, Case, When, Value, CharField
from django.db.models.functions import Cast
from django.contrib.postgres.search import TrigramSimilarity, SearchVector


from .forms import *
from .models import Doctor, Patient, Schedule


def index(request):
    return render(request, 'main/index.html')

class UserRegisterView(SuccessMessageMixin, CreateView):
    form_class = UserRegisterForm
    template_name = 'user_register.html'
    success_message = 'Вы успешно зарегистрировались!'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        login(self.request, user)
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

class UserLoginView(SuccessMessageMixin, LoginView):
    form_class = UserLoginForm
    template_name = 'user_login.html'
    next_page = 'home'
    success_url = reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context
    
    def get_success_message(self, cleaned_data):
        username = self.request.user.username
        return f"Вы уже зашли в систему как '{username}'!"

class UserLogoutView(LogoutView):
    next_page = 'home'


def doctors_get(request):
    FIELDS = [field.name for field in Doctor._meta.get_fields()]
    search = request.GET.get('q')
    if search:
        doctors = Doctor.objects.annotate(
            search=SearchVector(*FIELDS),
            similarity_phone_number=TrigramSimilarity('phone_number', search),
            similarity_full_name=TrigramSimilarity('full_name', search)
        ).filter(
            Q(search=search) |
            Q(similarity_phone_number__gt=0.25) |
            Q(similarity_full_name=0.1)
        )
    else:
        doctors = Doctor.objects.all().order_by('id')
            
    if request.headers.get('HX-Request'):  # Проверка на AJAX (HTMX)
        html = render(request, 'doctors/doctor_search.html', {'doctors': doctors})
        return HttpResponse(html)

    return render(request, 'doctors/doctor_main.html', {'doctors': doctors})

class DoctorAdd(CreateView, PermissionRequiredMixin):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctors/doctor_add.html'
    success_url = reverse_lazy('doctors')
    permission_required = 'stomatology.add_doctor'

class DoctorEdit(UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctors/doctor_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('doctors')
    permission_required = 'stomatology.change_doctor'

class DoctorDelete(DeleteView):
    model = Doctor
    template_name = 'doctors/doctor_delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('doctors')
    permission_required = 'stomatology.delete_doctor'


def patients_get(request):
    FIELDS = [field.name for field in Patient._meta.get_fields()]
    search = request.GET.get('q')
    if search:
        patients = Patient.objects.annotate(
            search=SearchVector(*FIELDS),
            similarity_phone_number=TrigramSimilarity('phone_number', search),
            similarity_full_name=TrigramSimilarity('full_name', search)
        ).filter(
            Q(search=search) |
            Q(similarity_phone_number__gt=0.25) |
            Q(similarity_full_name=0.1)
        )
    else:
        patients = Patient.objects.all().order_by('id')
            
    if request.headers.get('HX-Request'):  # Проверка на AJAX (HTMX)
        html = render(request, 'patients/patient_search.html', {'patients': patients})
        return HttpResponse(html)

    return render(request, 'patients/patient_main.html', {'patients': patients})

class PatientAdd(CreateView, PermissionRequiredMixin):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_add.html'
    success_url = reverse_lazy('patients')
    permission_required = 'stomatology.add_patient'

class PatientEdit(UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('patients')
    permission_required = 'stomatology.change_patient'

class PatientDelete(DeleteView):
    model = Patient
    template_name = 'patients/patient_delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('patients')
    permission_required = 'stomatology.delete_patient'

def schedules_get(request):
    FIELDS = ['doctor__full_name']
    search = request.GET.get('q')

    # Словарь соответствия номеров дней и их названий
    DAY_WEEK = {
        1: "понедельник",
        2: "вторник",
        3: "среда",
        4: "четверг",
        5: "пятница",
        6: "суббота",
        7: "воскресенье"
    }

    if search:
        schedules = Schedule.objects.annotate(
            day_name=Case(
                *[When(day_week=k, then=Value(v)) for k, v in DAY_WEEK.items()],
                output_field=CharField()
            ),
            search=SearchVector(*FIELDS),
            day_similarity=TrigramSimilarity('day_name', search),
            similarity_doctor=TrigramSimilarity('doctor__full_name', search),
            similarity_start_reception=TrigramSimilarity(Cast('start_reception', CharField()), search)
        ).filter(
            Q(search=search) |
            Q(day_similarity__gt=0.2) |
            Q(similarity_doctor=0.1) |
            Q(similarity_start_reception__gt=0.4)
        )
    else:
        schedules = Schedule.objects.all().order_by('id')
            
    if request.headers.get('HX-Request'):  # Проверка на AJAX (HTMX)
        html = render(request, 'schedules/schedule_search.html', {'schedules': schedules})
        return HttpResponse(html)

    return render(request, 'schedules/schedule_main.html', {'schedules': schedules})

class ScheduleAdd(CreateView, PermissionRequiredMixin):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedules/schedule_add.html'
    success_url = reverse_lazy('schedules')
    permission_required = 'stomatology.add_schedule'

class ScheduleEdit(UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedules/schedule_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('schedules')
    permission_required = 'stomatology.change_schedule'

class ScheduleDelete(DeleteView):
    model = Schedule
    template_name = 'schedules/schedule_delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('schedules')
    permission_required = 'stomatology.delete_schedule'
