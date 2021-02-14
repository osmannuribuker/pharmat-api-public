#coding=utf-8

import os, sys, signal
import django
import requests
import json
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings.development'
django.setup()

from core.apps.app.models import Region, City, State

f = open('./city_state.json')
city_state = json.load(f)
regions = ["EGE", "MARMARA", "DOĞU ANADOLU", "KARADENİZ", "AKDENİZ", "GÜNEYDOĞU ANADOLU", "İÇ ANADOLU"]
for reg in regions:
    regi = Region.objects.create(name=reg, created_by_id=5)
    regi.save()
    
for data in city_state:
    region = Region.objects.get(name=data['bolge'])
    print("{} region created".format(region))
    is_have_city = City.objects.filter(name=data['il'])
    if len(is_have_city) > 0:
        active_city = City.objects.get(name=data['il'])
        state = State.objects.create(name=data['ilce'], city=city, created_by_id=5)
        state.save()
        print("{} state created".format(state))

    else:
        city = City.objects.create(name=data['il'], created_by_id=5, region=region)
        city.save()
        print("{} city created".format(city))
        state = State.objects.create(name=data['ilce'], city=city, created_by_id=5)
        state.save()
        print("{} state created".format(state))

    print(region.id)
    