import mechanize
from bs4 import BeautifulSoup
import urllib3
from http import cookiejar

cj = cookiejar.CookieJar()
br = mechanize.Browser()
br.set_cookiejar(cj)
br.open("http://webdepo.selcukecza.com.tr/Login.aspx")

br.select_form('form1')

br.form['txtEczaneKodu'] = 'x'
br.form['txtKullaniciAdi'] = 'y'
br.form['txtSifre']= 'z'
br.submit()

print(br.response().read())
print(cj.extract_cookies)