from django.utils import timezone
from django.db.models.functions import Lower

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status

from core.apps.app.models import Product
from core.apps.authentication.models import Group, Pharmacy, PharmacyMSI, User
from core.apps.services.exception import AcceptableException

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'created_date', 'updated_date']

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.updated_date = timezone.now()
        instance.save()

        return instance

    
class GroupSerializer(serializers.ModelSerializer):
    ##### RULES #####
    # Bir kullanıcı birden fazla grup oluşturabilir
    # Bir kullanıcı birden fazla gruba yönetici olabilir
    # Bir kullanıcı birden fazla gruba dahil olabilir
    # Oluşturulacak veya değiştirilicek grup adı benzersiz olmalıdır
    ##### EOF RULES #####
    message = None
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'administrators', 'created_by']
        read_only_fields = ("administrators", "created_by")

    def validation(self, name):
        try:
            lower_group_name = Group.objects.annotate(lower_name=Lower('name'))
            is_have = lower_group_name.filter(lower_name__iexact=name.lower())
            if len(is_have) > 0:
                self.message = "Belirttiğiniz grup adı daha önce oluşturulduğu için bu grup adını kullanamazsınız. Lütfen farklı bir grup adı giriniz."
                raise Exception
            else:
                return True
        except:
            if self.message:
                raise Exception
            else:
                self.message = {"error": "Bilinmeyen bir hata oluştu. Lütfen sistem yöneticisine bildiriniz"}
                raise Exception       

    def check_pharmacy(self, user):
        try:
            return user.pharmacy
        except:
            self.message = {"error": "Eczanesi olmayan kullanıcılar grup açamaz."}
            
    def create(self, validated_data):
        try:
            valid = self.validation(validated_data['name'])
            if valid:
                user = self.context['request'].user
                validated_data['created_by'] = user
                pharmacy = self.check_pharmacy(user)
                group = Group.objects.create(**validated_data)
                group.administrators.add(user.id)
                pharmacy.groups.add(group)
                return group

        except Exception as e:
            if self.message:
                raise AcceptableException(detail=self.message)
            else:
                raise AcceptableException(detail={"error": str(e)})
    
    def update(self, instance, validated_data):
        try:
            valid = self.validation(validated_data['name'])
            if valid:
                instance.name = validated_data['name']
                instance.updated_date = timezone.now()
                instance.updated_by = self.context['request'].user
                instance.save()
                return instance
        
        except Exception as e:
            if self.message:
                raise AcceptableException(detail=self.message)
            else:
                raise AcceptableException(detail={"error": e})
    
class PharmacySerializer(serializers.ModelSerializer):
    ##### RULES #####
    ### IMPORTANT -- Bir eczanenin sahibi birden fazla kullanıcı olamaz -- IMPORTANT ###
    # Her kullanıcı sadece bir eczaneye sahip olabilir
    # Bu doğrultuda, eğer eczane oluşturmaya çalışan kullanıcı, bir eczaneye sahipse hata mesajı alır.
    # Eczane oluşturmaya çalışan kullanıcı bir veya daha fazla grupta yönetici ise ilgili eczane hepsine üye olur
    # Eğer eczane oluşturmaya çalışan kullanıcı herhangi bir grupta yönetici değilse o eczane grupsuz oluşturulur.
    # Eğer girilen gln numarasına sahip bir eczane var ise eczane o gln numarası ile oluşturulamaz
    # Bir kullanıcı birden fazla eczaneye sahip olamaz ama aynı kişi birden fazla eczaneye sahip olabilir
    # Bunun için identification_number yani yetkili kişinin TC kimlik numarasını kontrol etmedim. Yani farklı bir kullanıcı oluşturup
    # o kullanıcı aracılığı ile başka bir eczanede yetkili olabilir o tc ye sahip kişi, aynı şekilde telefon numarası da
    # Bir kullanıcının eczaneyi güncelleyebilmesi için o eczanenin sahibi olması gerekir
    ##### EOF RULES #####
    message = None
    class Meta:
        model = Pharmacy
        fields = [
            'id',
            'name',
            'first_phone',
            'second_phone',
            'address',
            'tax_administration',
            'tax_number',
            'identification_number',
            'gln_number',
            'state']

    def check_pharmacy(self, user):
        try:
            print(user.pharmacy)
            if user.pharmacy:
                self.message = {"error": "Mevcut bir eczaneye sahip olduğunuz için eczane oluşturamazsınız"}
                raise Exception
            else:
                return True
        except Exception as e:
            if self.message:
                raise Exception
            else:
                self.message = {"error": "Bilinmeyen bir hata oluştu. Lütfen sistem yöneticisine bildiriniz"}
                raise Exception
        
    def check_gln(self, gln, pharmacy=None):
        try:
            is_have = Pharmacy.objects.filter(gln_number=gln)
            if len(is_have) > 0:
                if pharmacy:
                    this_pharmacy = Pharmacy.objects.filter(id=pharmacy, gln_number=gln)
                    if len(this_pharmacy) > 0:
                        return True
                    else:
                        self.message = {"error": "Girdiğiniz GLN numarasına ait bir eczane olduğu için bu gln numarası ile eczane oluşturamazsınız"}
                        raise Exception
                else:
                    self.message = {"error": "Girdiğiniz GLN numarasına ait bir eczane olduğu için bu gln numarası ile eczane oluşturamazsınız"}
                    raise Exception
            else:
                return True
        except Exception as e:
            if self.message:
                raise Exception
            else:
                self.message = {"error": "Bilinmeyen bir hata oluştu. Lütfen sistem yöneticisine bildiriniz"}
                raise Exception

    def check_group(self, user):
        try:
            groups = Group.objects.filter(administrators=user)
            if len(groups) > 0:
                return groups
            else:
                return False
        except:
            self.message = {"error": "Bilinmeyen bir hata oluştu. Lütfen sistem yöneticisine bildiriniz"}
            raise Exception

    def check_ownership(self, pharmacy_id, user_id):
        try:
            is_ownership = User.objects.filter(id=user_id, pharmacy_id=pharmacy_id)
            if len(is_ownership) > 0:
                return True
            else:
                self.message = {"error": "Sahibi olmadığınız eczaneyi güncelleyemezsiniz"}
                raise Exception
        except Exception as e:
            if self.message:
                raise Exception
            else:
                self.message = {"error": "Bilinmeyen bir hata oluştu. Lütfen sistem yöneticisine bildiriniz"}
                raise Exception

    def create(self, validated_data):
        try:
            user = self.context['request'].user
            self.check_pharmacy(user)
            self.check_gln(validated_data['gln_number'])
            #groups = self.check_group(user)
            validated_data['created_by'] = user
            pharmacy = Pharmacy.objects.create(**validated_data)
            '''
            # eczane oluşturulurken kullanıcının yonetici oldugu grup var ise gruba eklemesi için yazmışım ama bunu sildim.
            # CÜNKÜ ECZANESİ OLMAYAN GRUP OLUŞTURAMAZ
            if groups:
                for group in groups:
                    pharmacy.groups.add(group.id)
            '''
            User.objects.filter(id=user.id).update(pharmacy=pharmacy)
            return pharmacy
        except Exception as e:
            if self.message:
                raise AcceptableException(detail=self.message)
            else:
                print(e)
                raise AcceptableException(detail={"error": e})

    def update(self, instance, validated_data):
        try:
            user = self.context['request'].user
            self.check_ownership(instance.id, user.id)
            self.check_gln(validated_data['gln_number'], instance.id)
            instance.name = validated_data['name']
            instance.first_phone = validated_data['first_phone']
            instance.second_phone = validated_data['second_phone']
            instance.address = validated_data['address']
            instance.tax_administration = validated_data['tax_administration']
            instance.tax_number = validated_data['tax_number']
            instance.identification_number = validated_data['identification_number']
            instance.gln_number = validated_data['gln_number']
            instance.state = validated_data['state']
            instance.updated_by = user
            instance.updated_date = timezone.now()
            instance.save()
            return instance
        except Exception as e:
            if self.message:
                raise AcceptableException(detail=self.message)
            else:
                print(e)
                raise AcceptableException(detail={"error": e})

class PharmacyMSISerializer(serializers.ModelSerializer):
    ##### RULES #####
    ### IMPORTANT --- Detail Get methodu sadece kullanıcının sahip oldugu eczanenin bilgilerini versin ---- IMPORTANT ###
    # Bir eczanesi olmayan kişi ilaç deposu bilgisi oluşturamaz
    # Eczanesine ait ilaç deposu bilgisi girilen biri bu bilgiyi tekrar oluşturamaz
    # İlaç deposu bilgisini güncellemek için o eczanenin sahibi olmak gerekir
    ##### EOF RULES #####
    message = None

    class Meta:
        model = PharmacyMSI
        fields = [
            'pharmacy_code',
            'username',
            'password',
            'ms']

    def check_have(self, pharmacy, ms):
        try:
            is_have = PharmacyMSI.objects.filter(pharmacy=pharmacy, ms=ms)
            if len(is_have) > 0:
                self.message = {"error": "Seçtiğiniz depoya ait bilgileri daha önce oluşturduğunuz için yeniden bilgi oluşturamazsınız. İlaç deposu bilgilerinizde Değişiklik yapmak için güncelleme sayfasına gidiniz."}
                raise Exception
            return True
        except Exception as e:
            if self.message:
                raise Exception
            else:
                print("111",e)
                self.message = {"error": "Bilinmeyen bir hata oluştu. Lütfen sistem yöneticisine bildiriniz"}
                raise Exception

    def check_ownership(self, pharmacy_id, user_id):
        try:
            is_ownership = User.objects.filter(id=user_id, pharmacy_id=pharmacy_id)
            if len(is_ownership) > 0:
                return True
            else:
                self.message = {"error": "Sahibi olmadığınız eczaneye ait ilaç deposu bilgilerini güncelleyemez/görüntüleyemezsiniz"}
                raise Exception
        except Exception as e:
            if self.message:
                raise Exception
            else:
                self.message = {"error": "Bilinmeyen bir hata oluştu. Lütfen sistem yöneticisine bildiriniz"}

    def create(self, validated_data):
        try:
            user = self.context['request'].user
            if user.pharmacy:
                self.check_have(user.pharmacy, validated_data['ms'])
                validated_data['created_by'] = user
                validated_data['pharmacy'] = user.pharmacy
                return PharmacyMSI.objects.create(**validated_data)
            else:
                self.message = {"error": "Herhangi bir eczaneye sahip olmadığınız için ilaç deposu bilgisi oluşturamazsınız"}
                raise Exception
        except Exception as e:
            if self.message:
                raise AcceptableException(detail=self.message)
            else:
                raise AcceptableException(detail={"error": str(e)})

    def update(self, instance, validated_data):
        try:
            user = self.context['request'].user
            if user.pharmacy:
                self.check_ownership(instance.pharmacy.id, user.id)
                instance.pharmacy_code = validated_data['pharmacy_code']
                instance.username = validated_data['username']
                instance.password = validated_data['password']
                instance.updated_by = user
                instance.updated_date = timezone.now()
                instance.save()
                return instance
            else:
                self.message = {"error": "Herhangi bir eczaneye sahip olmadığınız için ilaç deposu bilgisini güncelleyemezsiniz"}
                raise Exception
        except Exception as e:
            if self.message:
                raise AcceptableException(detail=self.message)
            else:
                raise AcceptableException(detail={"error": str(e)})

# DESTROYU KONTROL ETMEYİ UNUTTUN HER SERİALİZER İÇİN SİLME İŞLLEMİNİ DE KONTROL ET YETKİYE BAĞLA RETRİWE DESTROY VS VS
    def destroy(self, validated_data):
        raise AcceptableException(detail={"error": "asdasdsad"})
