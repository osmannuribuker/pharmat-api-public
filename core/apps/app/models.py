from django.db import models
from django.utils import timezone
from django.conf import settings

class Base(models.Model):
    # ilk migrations larda buradaki fk ları sil 
    # prod da fixle
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name='Oluşturan Kullanıcı',
        related_name="%(app_label)s_%(class)s_related_create",
        related_query_name="%(app_label)s_%(class)ssk",
        blank=True,
        null=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name='Güncelleyen Kullanıcı',
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_related_update",
        related_query_name="%(app_label)s_%(class)ssz"
    )
    created_date = models.DateTimeField(default=timezone.now, verbose_name='Oluşturulma Tarihi')
    updated_date = models.DateTimeField(verbose_name='Güncellenme Tarihi', blank=True, null=True)

    class Meta:
        abstract = True

class Region(Base):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class City(Base):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="region_for_city", blank=True, null=True)
    #change blank
    def __str__(self):
        return self.name

class State(Base):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="city_for_state")
    
    def __str__(self):
        return self.name

class MedicineStore(Base):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100, verbose_name="Ecza deposu servis url")

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return "{} - {}".format(str(self.id), self.title)