from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity, SearchVector


from .forms import *
from .models import Doctor


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
        doctors = Doctor.objects.all()
            
    if request.headers.get('HX-Request'):  # Проверка на AJAX (HTMX)
        html = render_to_string('doctors/doctor_search.html', {'doctors': doctors})
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
