from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q, Case, When, Value, CharField, Func, F
from django.db.models.functions import Cast, Greatest
from django.contrib.postgres.search import TrigramSimilarity, SearchVector


from .forms import *
from .models import Doctor, Patient, Schedule, Service, Reception


def index(request):
    context = {
        'title': 'IT-Стоматология',
        'content_name': 'IT-Стоматология',
        'content': 'грамотное лечение ваших зубов'
    }
    return render(request, 'main/index.html', context=context)

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
    FIELDS = ["full_name", "phone_number", "office_number"]
    search = request.GET.get('q')
    if search:
        doctors = Doctor.objects.annotate(
            search=SearchVector(*FIELDS),
            similarity_full_name=TrigramSimilarity('full_name', search),
            similarity_phone_number=TrigramSimilarity('phone_number', search)
        ).filter(
            Q(search=search) |
            Q(similarity_full_name__gt=0.1) |
            Q(similarity_phone_number__gt=0.25)
        ).distinct('id').order_by('id')
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
    FIELDS = ["full_name", "phone_number", "patient_address"]
    search = request.GET.get('q')
    
    if search:
        search_vector = SearchVector(*FIELDS)
        
        similarity_full_name = TrigramSimilarity('full_name', search)
        similarity_phone_number = TrigramSimilarity('phone_number', search)
        similarity_patient_address = TrigramSimilarity('patient_address', search)

        patients = Patient.objects.annotate(
            search=search_vector,
            similarity=Greatest(
                similarity_full_name,
                similarity_phone_number,
                similarity_patient_address
            )
        ).filter(
            Q(search=search) | 
            Q(full_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(patient_address__icontains=search) |
            Q(similarity__gt=0.6) 
        ).distinct('id').order_by('id')
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
    FIELDS = ['doctor__full_name', 'day_week', 'start_reception', 'end_reception']
    search = request.GET.get('q')

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
        search_vector = SearchVector(*FIELDS)
        similarity_doctor = TrigramSimilarity('doctor__full_name', search)
        similarity_day_week = TrigramSimilarity(Case(
            *[When(day_week=k, then=Value(v)) for k, v in DAY_WEEK.items()],
            output_field=CharField()
        ), search)

        schedules = Schedule.objects.annotate(
            search=search_vector,
            similarity=Greatest(
                similarity_doctor,
                similarity_day_week
            )
        ).filter(
            Q(search=search) |
            Q(similarity__gt=0.2)
        )
    else:
        schedules = Schedule.objects.all().order_by('id')
            
    if request.headers.get('HX-Request'):
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

def services_get(request):
    FIELDS = ['service_name', 'cost']
    search = request.GET.get('q')
    
    if search:
        search_vector = SearchVector(*FIELDS)
        similarity_service_name = TrigramSimilarity('service_name', search)

        # Попробуем преобразовать строку поиска в число для поиска по стоимости
        try:
            cost_search = float(search)
            services = Service.objects.annotate(
                search=search_vector,
                similarity=similarity_service_name
            ).filter(
                Q(search=search) |
                Q(similarity__gt=0.25) |
                Q(cost=cost_search)  # Поиск по стоимости
            )
        except ValueError:
            services = Service.objects.annotate(
                search=search_vector,
                similarity=similarity_service_name
            ).filter(
                Q(search=search) |
                Q(similarity__gt=0.25)
            )
    else:
        services = Service.objects.all().order_by('id')
            
    if request.headers.get('HX-Request'):
        html = render(request, 'services/service_search.html', {'services': services})
        return HttpResponse(html)

    return render(request, 'services/service_main.html', {'services': services})

class ServiceAdd(CreateView, PermissionRequiredMixin):
    model = Service
    form_class = ServiceForm
    template_name = 'services/service_add.html'
    success_url = reverse_lazy('services')
    permission_required = 'stomatology.add_service'

class ServiceEdit(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'services/service_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('services')
    permission_required = 'stomatology.change_service'

class ServiceDelete(DeleteView):
    model = Service
    template_name = 'services/service_delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('services')
    permission_required = 'stomatology.delete_service'

def service_rendereds_get(request):
    FIELDS = ["service__service_name", "number_reception__id", "quantity"]
    search = request.GET.get('q')
    
    if search:
        search_vector = SearchVector(*FIELDS)
        similarity_service_name = TrigramSimilarity('service__service_name', search)
        similarity_number_reception = TrigramSimilarity(Cast('number_reception__id', CharField()), search)
        similarity_quantity = TrigramSimilarity(Cast('quantity', CharField()), search)

        services_rendered = Service_rendered.objects.annotate(
            search=search_vector,
            similarity_service=similarity_service_name,
            similarity_number_reception=similarity_number_reception,

        ).filter(
            Q(search=search) |
            Q(similarity_service__gt=0.25) |
            Q(similarity_number_reception__gt=0.1) 
        ).distinct('id').order_by('id')
        services_rendered = Service_rendered.objects.annotate(
            search=search_vector,
            similarity_service=similarity_service_name,
            similarity_number_reception=similarity_number_reception,
            similarity_quantity=similarity_quantity
        ).filter(
            Q(search=search) |
            Q(similarity_service__gt=0.25) |
            Q(similarity_number_reception__gt=0.25) |
            Q(similarity_quantity__gt=0.25)
        ).distinct('id').order_by('id')
    else:
        services_rendered = Service_rendered.objects.all().order_by('id')
            
    if request.headers.get('HX-Request'):
        html = render(request, 'services_rendered/service_rendered_search.html', {'services_rendered': services_rendered})
        return HttpResponse(html)

    return render(request, 'services_rendered/service_rendered_main.html', {'services_rendered': services_rendered})

class Service_renderedAdd(CreateView, PermissionRequiredMixin):
    model = Service_rendered
    form_class = Service_renderedForm
    template_name = 'services_rendered/service_rendered_add.html'
    success_url = reverse_lazy('services_rendered')
    permission_required = 'stomatology.add_service_rendered'

class Service_renderedEdit(UpdateView):
    model = Service_rendered
    form_class = Service_renderedForm
    template_name = 'services_rendered/service_rendered_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('services_rendered')
    permission_required = 'stomatology.change_service_rendered'

class Service_renderedDelete(DeleteView):
    model = Service_rendered
    template_name = 'services_rendered/service_rendered_delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('services_rendered')
    permission_required = 'stomatology.delete_service_rendered'

def receptions_get(request):
    FIELDS = ['doctor__full_name', 'patient__full_name', 'date_reception', 'time_reception']
    search = request.GET.get('q')

    class DateFormat(Func):
        function = 'TO_CHAR'
        template = "%(function)s(%(expressions)s, 'DD Month YYYY \"г.\"')"

    if search:
        search_vector = SearchVector(*FIELDS)
        similarity_doctor = TrigramSimilarity('doctor__full_name', search)
        similarity_patient = TrigramSimilarity('patient__full_name', search)
        similarity_date_reception = TrigramSimilarity(DateFormat(F('date_reception')), search)
        similarity_time_reception = TrigramSimilarity(Cast('time_reception', CharField()), search)

        receptions = Reception.objects.annotate(
            search=search_vector,
            similarity=Greatest(
                similarity_doctor,
                similarity_patient,
                similarity_date_reception,
                similarity_time_reception
            )
        ).filter(
            Q(search=search) |
            Q(similarity__gt=0.4)
        )
    else:
        receptions = Reception.objects.all().order_by('id')
            
    if request.headers.get('HX-Request'):
        html = render(request, 'receptions/reception_search.html', {'receptions': receptions})
        return HttpResponse(html)

    return render(request, 'receptions/reception_main.html', {'receptions': receptions})

class ReceptionAdd(CreateView, PermissionRequiredMixin):
    model = Reception
    form_class = ReceptionForm
    template_name = 'receptions/reception_add.html'
    success_url = reverse_lazy('receptions')
    permission_required = 'stomatology.add_reception'

class ReceptionEdit(UpdateView):
    model = Reception
    form_class = ReceptionForm
    template_name = 'receptions/reception_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('receptions')
    permission_required = 'stomatology.change_reception'

class ReceptionDelete(DeleteView):
    model = Reception
    template_name = 'receptions/reception_delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('receptions')
    permission_required = 'stomatology.delete_reception'