from django import forms
from django.contrib.auth.models import User

import django_tables as tables
from common_code.debug_client import console_msg as cm

########################################################################################################
#
# From http://www.peterbe.com/plog/automatically-strip-whitespace-in-django-forms
#
# I'll put this in each app, so they can be standalone, but it should really go in some centralized 
# part of the distro

class _BaseForm(object):
    def clean(self):
        for field in self.cleaned_data:
            if isinstance(self.cleaned_data[field], basestring):
                self.cleaned_data[field] = self.cleaned_data[field].strip()
        return self.cleaned_data

########################################################################################################

class UpdateSelfForm(_BaseForm, forms.Form):
    first_name  =  forms.CharField(label='First name', max_length=User._meta.get_field('first_name').max_length)
    last_name   =  forms.CharField(label='Last (family) name', max_length=User._meta.get_field('last_name').max_length)
    email       =  forms.EmailField(label ='Email address', max_length=User._meta.get_field('email').max_length)

########################################################################################################                                   

class UpdateSelfTable(tables.Table):
    property = tables.Column(verbose_name="Property")
    old_val= tables.Column(verbose_name="Old value")
    new_val= tables.Column(verbose_name="New value")