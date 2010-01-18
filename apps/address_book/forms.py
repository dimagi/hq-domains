import re
from django import forms
from address_book.models import Patient, Phone, Email

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

class PatientForm(_BaseForm, forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ('domain_membership',)

########################################################################################################
        
class EmailForm(_BaseForm, forms.ModelForm):
#    Was using this to allow null email fields to be passed in as valid,
#    but I still had to filter out the null values before they went into the
#    database. Now I just filter out null forms before even trying to validate 
#    them, so there's no need to monkey with the basic form definition.

#    def __init__(self, *args, **kwargs):
#        super(EmailForm, self).__init__(*args, **kwargs)
#        self.fields['email'].required = False
                
    class Meta:
        model = Email
        exclude = ('patient',)

########################################################################################################
        
class PhoneForm(_BaseForm, forms.ModelForm):
    class Meta:
        model = Phone
        exclude = ('patient',)        

########################################################################################################
#
# Dynamically specify search field validation type - helps us reuse search code
#
# Doesn't need to be a _BaseForm - data's stripped before searching, and we aren't putting it in the DB

comma_or_ws = re.compile('[\s,]+')

class SearchForm(forms.Form):
    searchText = forms.CharField(label="Search text", max_length=256)    
    def __init__(self, kind, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        assert(kind=='text' or kind=='id')         
        self.kind = kind
        if kind == 'id':
            self.fields['searchText'].label = 'IDs'

    # Custom validation - the id search must be a list of whitespace or comma-separated integers
    #
    # Example taken straight from Python docs
    def clean_searchText(self):
        data = self.cleaned_data['searchText'].strip()
        if self.kind == 'id':
            splitTxt = comma_or_ws.split(data)
            toInt = []
            try:
                # No list comprhension here - need the bad value to raise in the error msg
                for x in splitTxt:
                    toInt.append(int(x))
            except ValueError:
                raise forms.ValidationError("Search string has a non-integer id: " + x)

        # No need to return the int-converted vals; the textual representation of the ids will be
        # converted to ints in the query code 
        
        # Always return the cleaned data, whether you have changed it or not
        return data

########################################################################################################
    
