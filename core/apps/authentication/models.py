from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

class Base(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name='Oluşturan Kullanıcı',
        related_name="%(app_label)s_%(class)s_related_created",
        related_query_name="%(app_label)s_%(class)ssc",
        blank=True,
        null=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name='Güncelleyen Kullanıcı',
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_related_updated",
        related_query_name="%(app_label)s_%(class)ssp"
    )
    created_date = models.DateTimeField(default=timezone.now, verbose_name='Oluşturulma Tarihi')
    updated_date = models.DateTimeField(verbose_name='Güncellenme Tarihi', blank=True, null=True)

    class Meta:
        abstract = True

class Group(Base):
    name = models.CharField(max_length=50, verbose_name="Grup Adı")
    administrators = models.ManyToManyField('authentication.User', verbose_name="Yöneticiler")
    
    def __str__(self):
        return self.name

class Pharmacy(Base):
    name = models.CharField(max_length=50, verbose_name="Eczane Adı")
    first_phone = models.CharField(max_length=50, verbose_name="Birincil Telefon")
    second_phone = models.CharField(max_length=50, verbose_name="İkincil Telefon")
    address = models.CharField(max_length=77, verbose_name="Adres")
    tax_administration = models.CharField(max_length=50, verbose_name="Vergi Dairesi")
    tax_number = models.CharField(max_length=20, verbose_name="Vergi Numarası")
    identification_number = models.CharField(max_length=12, verbose_name="Yetkili TC Kimlik Numarası")
    gln_number = models.CharField(max_length=25, verbose_name="GLN Numarası")
    groups = models.ManyToManyField(Group, verbose_name="Bağlı olduğu gruplar", blank=True)
    state = models.ForeignKey('app.State', on_delete=models.CASCADE, related_name="state_for_pharmacy")

    def __str__(self):
        return self.name

class PharmacyMSI(Base):
    pharmacy_code = models.CharField(max_length=50, verbose_name="Eczane Kodu")
    username = models.CharField(max_length=50, verbose_name="Kullanıcı Adı")
    password = models.CharField(max_length=50, verbose_name="Şifre")
    ms = models.ForeignKey('app.MedicineStore', on_delete=models.CASCADE, related_name="ms_for_pharmacyMsi")
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="pharmacy_for_pharmacyMsi")

    def __str__(self):
        return self.pharmacy.name

class User(AbstractUser):
    pharmacy = models.OneToOneField(Pharmacy, on_delete=models.SET_NULL, related_name="pharmacy_for_user", blank=True, default="", null=True)
    
    class Meta:
        permissions = [
            ("test", "Test Yetki"),
        ]
    