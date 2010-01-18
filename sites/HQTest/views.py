from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.shortcuts import render_to_response
from django.template import RequestContext

from domain.decorators import login_and_domain_required
from domain.forms import clean_password
from HQTest.forms import UpdateSelfForm, UpdateSelfTable
from common_code.debug_client import console_msg as cm

########################################################################################################
# Monekypatch the built-in auth password change and reset forms so that they enforces the same password 
# restrictions defined in the domain app

PasswordChangeForm.clean_new_password1 = lambda self : clean_password(self.cleaned_data.get('new_password1'))
PasswordChangeForm.clean_new_password2 = lambda self : clean_password(self.cleaned_data.get('new_password2'))
SetPasswordForm.clean_new_password1 = lambda self : clean_password(self.cleaned_data.get('new_password1'))
SetPasswordForm.clean_new_password2 = lambda self : clean_password(self.cleaned_data.get('new_password2'))

########################################################################################################

@login_and_domain_required
def homepage(request):
    vals = dict()
    return render_to_response('homepage.html',  vals, context_instance = RequestContext(request))                              

########################################################################################################

@login_and_domain_required
def admin_own_account_main(request):
    return render_to_response('admin_own_account_main.html',  {}, context_instance = RequestContext(request))

########################################################################################################

@login_and_domain_required
def admin_own_account_update(request):
    if request.method == 'POST': # If the form has been submitted...
        form = UpdateSelfForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            user_from_db = User.objects.get(id = request.user.id)            
            table_vals = [ {'property':form.base_fields[x].label,
                            'old_val':user_from_db.__dict__[x],
                            'new_val':form.cleaned_data[x]} for x in form.cleaned_data.keys() ]

            table = UpdateSelfTable(table_vals, order_by=('Property',))              
                    
            user_from_db.__dict__.update(form.cleaned_data)
            user_from_db.save()
            return render_to_response('admin_own_account_update_done.html', dict(table=table), context_instance = RequestContext(request))
    else:
        initial_vals = {}
        for x in UpdateSelfForm.base_fields.keys():            
            initial_vals[x] = request.user.__dict__[x]
        form = UpdateSelfForm(initial=initial_vals) # An unbound form - can render, but it can't validate

    vals = dict(form=form)
    return render_to_response('admin_own_account_update_form.html', vals, context_instance = RequestContext(request))

########################################################################################################