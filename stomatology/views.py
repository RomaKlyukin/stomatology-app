from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity, SearchVector

from .forms import DoctorForm
from .models import Doctor


def index(request):
    return render(request, 'main/index.html')

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

class DoctorAdd(CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctors/doctor_add.html'
    success_url = reverse_lazy('doctors')

class DoctorEdit(UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctors/doctor_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('doctors')

class DoctorDelete(DeleteView):
    model = Doctor
    template_name = 'doctors/doctor_delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('doctors')
