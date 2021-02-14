from django.contrib import admin

from core.apps.app.models import City, State, MedicineStore, Product, Region

admin.site.register(City)
admin.site.register(State)
admin.site.register(MedicineStore)
admin.site.register(Product)
admin.site.register(Region)
