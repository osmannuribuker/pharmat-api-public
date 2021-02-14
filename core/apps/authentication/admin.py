from django.contrib import admin

from core.apps.authentication.models import User, Group, Pharmacy, PharmacyMSI

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Pharmacy)
admin.site.register(PharmacyMSI)
