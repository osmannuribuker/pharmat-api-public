from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F

import json
from core.apps.app.models import Product, City, State, MedicineStore
from core.apps.authentication.models import Group, User, Pharmacy, PharmacyMSI
from core.apps.services.serializers import ProductSerializer, GroupSerializer, PharmacySerializer, PharmacyMSISerializer
from core.apps.services.exception import AcceptableException
from django.http.response import JsonResponse

class TokenVerify(APIView):
    def get(self, request):
        user = request.user
        pharmacy = user.pharmacy
        p = Pharmacy.objects.get(id=pharmacy.id)
        if pharmacy:
            return Response({
                "username": user.username,
                "email": user.email,
                "name": user.get_full_name(),
                "id": user.id,
                "pharmacy": {
                    "id": pharmacy.id,
                    "name": pharmacy.name,
                    "state_id": pharmacy.state.id,
                    "city_id": pharmacy.state.city_id,
                    "groups": list(pharmacy.groups.all().values("id", "name"))
                }
            })
        else:
            return Response({
                "username": user.username,
                "email": user.email,
                "name": user.get_full_name(),
            })
    permission_classes =[IsAuthenticated]

class GetCities(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            return JsonResponse(list(City.objects.all().values("id", "name")), safe=False)
        except Exception as e:
            raise AcceptableException(detail={"error": "Şehir bilgileri çekilirken bir sorun oluştu"})

class GetStates(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, city_id):
        try:
            return JsonResponse(list(State.objects.filter(city_id=city_id).values("id", "name")), safe=False)
        except Exception as e:
            raise AcceptableException(detail={"error": "Şehir bilgileri çekilirken bir sorun oluştu"})

class GetMedicineStores(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            return JsonResponse(list(MedicineStore.objects.all().values("id", "name")), safe=False)
        except Exception as e:
            raise AcceptableException(detail={"error": "Ecza deposu bilgileri çekilirken bir sorun oluştu"})

class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class ProductCreate(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class GroupList(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

class GroupCreate(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        raise AcceptableException(detail={"error": "Bu işlemi yapmak için yetkiniz yoktur. Grup silmek için lütfen sistem yöneticisi ile iletişime geçin"})

class PharmacyList(generics.ListAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    permission_classes = [IsAuthenticated]

class PharmacyCreate(generics.CreateAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    permission_classes = [IsAuthenticated]

class PharmacyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        raise AcceptableException(detail={"error": "Bu işlemi yapmak için yetkiniz yoktur. Eczane silmek için lütfen sistem yöneticisi ile iletişime geçin"})

class PharmacyMSIList(generics.ListAPIView):
    queryset = PharmacyMSI.objects.all()
    serializer_class = PharmacyMSISerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            pharmacy_msies = PharmacyMSI.objects.filter(pharmacy=request.user.pharmacy).values("pharmacy_code", "username", "password", "ms", "pharmacy", "id", "ms__name")
            if len(pharmacy_msies) > 0:
                return JsonResponse(list(pharmacy_msies), safe=False)
            else:
                return Response({"error": "Şimdiye kadar herhangi bir ecza deposuna ait bilgi oluşturmadınız"})
        except Exception as e:
            raise AcceptableException(detail={"error": "Hatalı işlem"})

class PharmacyMSICreate(generics.CreateAPIView):
    queryset = PharmacyMSI.objects.all()
    serializer_class = PharmacyMSISerializer
    permission_classes = [IsAuthenticated]

class PharmacyMSIDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PharmacyMSI.objects.all()
    serializer_class = PharmacyMSISerializer
    permission_classes = [IsAuthenticated]
    message = None

    def check_ownership(self, user, pharmacy_msi):
        try:
            pharmacyMsi = PharmacyMSI.objects.get(id=pharmacy_msi)
            if user.pharmacy == pharmacyMsi.pharmacy:
                return True
            else:
                self.message = {"error": "Sahibi olmadığınız eczanenin ilaç deposu bilgilerini görüntüleyemez/silemezsiniz"}
                raise Exception
        except Exception as e:
            if self.message:
                raise Exception
            else:
                self.message = {"error": "Girdiğiniz eczaneye ait ilaç deposu bilgisi yok veya eczaneniz yok"}
                raise Exception    

    def get(self, request, pk):
        try:
            user = request.user
            self.check_ownership(user, pk)
            queryset = self.get_queryset()
            serializer = PharmacyMSISerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            if self.message:
                raise AcceptableException(detail=self.message)
            else:
                raise AcceptableException(detail={"error": str(e)})

    def delete(self, request, pk):
        try:
            user = request.user
            self.check_ownership(user, pk)
            msi = PharmacyMSI.objects.get(id=pk)
            msi.delete()
            return Response({'success': "İlaç deposu bilgileri başarıyla silindi"})
        except Exception as e:
            if self.message:
                raise AcceptableException(detail=self.message)
            else:
                raise AcceptableException(detail={"error": str(e)})
