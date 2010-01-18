from django.contrib import admin
from address_book.models import Patient, Email, Phone

admin.site.register(Patient)
admin.site.register(Email)
admin.site.register(Phone)
