from django import forms
from django.forms import ModelForm, TextInput

from .models import Doctor


class DoctorForm(ModelForm):
    class Meta:
        model = Doctor
        fields = ["full_name", "phone_number", "office_number"]

        widgets = {
            "full_name": TextInput(
                attrs={"class": "form-control", "placeholder": "Иванов Иван Иванович"}
            ),
            "phone_number": TextInput(attrs={"class": "form-control", "placeholder": "+79616448504"}),
            "office_number": TextInput(
                attrs={"class": "form-control", "placeholder": "101"}
            ),
        }

        error_css_class = 'error-field'  # CSS-класс для поля с ошибкой

        # Кастомные сообщения об ошибках
        error_messages = {
            "phone_number": {
                "invalid": "Введите номер в формате +7XXXXXXXXXX!",
            },
        }


    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name")
        if full_name and len(full_name.split()) < 3:
            raise forms.ValidationError("Введите полное ФИО!")
        return full_name
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        
        # Если это редактирование существующего врача (instance - существует)
        if self.instance and self.instance.phone_number == phone_number:
            return phone_number  # Разрешаем оставить тот же номер

        # Проверка на уникальность телефона
        if phone_number and Doctor.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("Этот номер телефона уже используется")
        
        return phone_number