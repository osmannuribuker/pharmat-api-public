from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from core.apps.services.views import *

from rest_framework_swagger.views import get_swagger_view

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


schema_view = get_swagger_view(title='Django API')

urlpatterns = [
    path('', schema_view, name='schema_view'),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerify.as_view(), name='token_verify'),
    path('socket/verify', TokenVerifyView.as_view(), name='socket_verify'),
    path('cities', GetCities.as_view(), name='get_cities'),
    path('states/<int:city_id>', GetStates.as_view(), name='get_states'),
    path('medicine_stores', GetMedicineStores.as_view(), name='get_medicine_store'),
    path('product', ProductCreate.as_view(), name='create_product'),
    path('products', ProductList.as_view(), name='get_all_product'),
    path('product/<int:pk>', ProductDetail.as_view(), name='single_product'),
    path('group', GroupCreate.as_view(), name='create_group'),
    path('groups', GroupList.as_view(), name='get_all_group'),
    path('group/<int:pk>', GroupDetail.as_view(), name='single_group'),
    path('pharmacy', PharmacyCreate.as_view(), name='create_pharmacy'),
    path('pharmacies', PharmacyList.as_view(), name='get_all_pharmacy'),
    path('pharmacy/<int:pk>', PharmacyDetail.as_view(), name='single_pharmacy'),
    path('pharmacy_msi', PharmacyMSICreate.as_view(), name='create_pharmacy_msi'),
    path('pharmacy_msies', PharmacyMSIList.as_view(), name='get_all_pharmacy_msi'),
    path('pharmacy_msi/<int:pk>', PharmacyMSIDetail.as_view(), name='single_pharmacy_msi'),
]