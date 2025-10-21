from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.postgres.indexes import GinIndex

class Doctor(models.Model):
    full_name = models.CharField("ФИО", max_length=100)
    phone_number = PhoneNumberField("Номер телефона", region="RU")
    office_number = models.CharField("Номер кабинета", max_length=10)

    class Meta:
        db_table = 'doctor'
        verbose_name = 'Врача'
        verbose_name_plural = 'Врачи'
        indexes = [
            GinIndex(fields=['full_name', 'phone_number', 'office_number']),
        ]

    def __str__(self):
        return self.full_name

class Patient(models.Model):
    full_name = models.CharField("ФИО", max_length=100)
    phone_number = PhoneNumberField("Номер телефона", region="RU")
    patient_address = models.CharField("Адрес проживания", max_length=100)

    class Meta:
        db_table = 'patient'
        verbose_name = 'Пациента'
        verbose_name_plural = 'Пациенты'
        indexes = [
            GinIndex(fields=['full_name', 'phone_number', 'patient_address']),
        ]

    def __str__(self):
        return self.full_name

class Reception(models.Model):
    date_reception = models.DateField("Дата")
    time_reception = models.TimeField("Время")
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, verbose_name="Пациент")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, verbose_name="Врач")

    class Meta:
        db_table = 'reception'
        verbose_name = 'Прием'
        verbose_name_plural = 'Приемы'
        ordering = ['-id']
        indexes = [
            GinIndex(fields=['date_reception', 'time_reception', 'patient', 'doctor']),
        ]

    def __str__(self):
        return f"{str(self.id)} ({self.date_reception} {self.time_reception})"

class Service(models.Model):
    service_name = models.CharField("Услуга", max_length=50)
    cost = models.FloatField("Стоимость")

    class Meta:
        db_table = 'service'
        verbose_name = 'Услугу'
        verbose_name_plural = 'Услуги'
        indexes = [
            GinIndex(fields=['service_name', 'cost']),
        ]

    def __str__(self):
        return f"{self.service_name}({self.cost}руб.)"

class Service_rendered(models.Model):
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, verbose_name="Услуга")
    number_reception = models.ForeignKey(
        Reception, on_delete=models.SET_NULL, null=True, verbose_name="Прием"
    )
    quantity = models.PositiveIntegerField("Количество", default=0)

    class Meta:
        db_table = 'service_rendered'
        verbose_name = 'Оказанную услугу'
        verbose_name_plural = 'Оказанные услуги'
        ordering = ['-id']
        indexes = [
            GinIndex(fields=['service', 'number_reception', 'quantity']),
        ]

    def __str__(self):
        return f"{str(self.id)} ({self.service} ({self.quantity}))"

class Schedule(models.Model):
    DAY_WEEK_CHOICES = [
        (1, "Понедельник"),
        (2, "Вторник"),
        (3, "Среда"),
        (4, "Четверг"),
        (5, "Пятница"),
        (6, "Суббота"),
        (7, "Воскресенье"),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, verbose_name="Врач")
    day_week = models.PositiveIntegerField("День недели", choices=DAY_WEEK_CHOICES, default=0)
    start_reception = models.TimeField("Начало приема")
    end_reception = models.TimeField("Конец приема")

    class Meta:
        db_table = 'shedule'
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание работы врачей'
        indexes = [
            GinIndex(fields=['doctor', 'day_week', 'start_reception', 'end_reception']),
        ]

    def __str__(self):
        return f"{self.doctor} - {self.get_day_week_display()}"
    