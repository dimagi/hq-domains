import sys, re
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db import transaction
from django.db.models import Count
from django.db.models.query import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.http import urlquote

import address_book.models as ABM
import address_book.forms as ABF
import django_tables as tables
from domain.decorators import login_and_domain_required

from common_code.debug_client import console_msg as cm

########################################################################################################


class PatientTable(tables.ModelTable):
    domain_membership = tables.Column(sortable=False, visible=False)

    # Custom cols - properties are defined in the Patient model.
    # Limitation of django-tables: custom cols aren't sortable. Mark them
    # as such explicitly, so that we don't render them as sortable in the browser.
    email_count= tables.Column(name='Email addresses?', sortable=False)
    phone_count= tables.Column(name='Phone #s?', sortable=False)
    
    class Meta: 
        model = ABM.Patient
        
class EmailTable(tables.ModelTable):
    id = tables.Column(sortable=False, visible=False)
    patient = tables.Column(sortable=False, visible=False)
    class Meta:
        model = ABM.Email   
         
class PhoneTable(tables.ModelTable):
    id = tables.Column(sortable=False, visible=False)
    patient = tables.Column(sortable=False, visible=False)
    class Meta:
        model = ABM.Phone

########################################################################################################
#
# Reused by all views that render a patient list
#
# sort_vars is a dictionary of the params that get appended to the HREF attached to each sortable column's header. 
# This lets the originating view regenerate the query on the request for each page - this is used only by the 
# search function at the moment (basic patient_list doesn't use it)

def patient_list_paging(request, queryset, sort_vars=None):
    # django_table checks to see if sort field is allowable - won't raise an error if the field isn't present
    # (unlike filtering of a raw queryset)
    
    order_by=request.GET.get('sort', 'last_name')
    patient_table = PatientTable(queryset, order_by)
    
    paginator = Paginator(patient_table.rows, 20, orphans=2)

    # Code taken from Django dev docs explaining pagination

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        patients = paginator.page(page)
    except (EmptyPage, InvalidPage):
        patients = paginator.page(paginator.num_pages)
     
    return render_to_response('address_book/patient_list.html', 
                              { 'columns': patient_table.columns, 'rows':patients, 'sort':order_by, 'sort_vars':sort_vars}, 
                              context_instance = RequestContext(request))   

########################################################################################################
           
@login_and_domain_required
def patient_list(request):
    # Need for 'distinct' in the annotations was pointed out here:
    # http://stackoverflow.com/questions/1265190/django-annotate-multiple-times-causes-wrong-answers
    # I didn't take time to study how/why it works, though.
    
    # Split over two lines, simply for readability
    queryset = ABM.Patient.objects.filter(domain_membership__domain = request.user.selected_domain, domain_membership__is_active = True)
    queryset = queryset.annotate(Count('email', distinct=True)).annotate(Count('phone', distinct=True))

    return patient_list_paging(request, queryset)
    
########################################################################################################

@login_and_domain_required
def patient_detail(request, patient_id):
    
    # Note that we query on patient domain_membership here, always - this keeps users from viewing patients that aren't in
    # their selected_domain
    selected_domain = request.user.selected_domain
    patient_queryset = ABM.Patient.objects.filter(id = patient_id, domain_membership__domain = selected_domain, domain_membership__is_active = True)
    email_queryset = ABM.Email.objects.filter(patient__id = patient_id, patient__domain_membership__domain = selected_domain, patient__domain_membership__is_active = True)
    phone_queryset = ABM.Phone.objects.filter(patient__id = patient_id, patient__domain_membership__domain = selected_domain, patient__domain_membership__is_active = True)
    emails = EmailTable(email_queryset, order_by=request.GET.get('email_sort', 'email'))
    phones = PhoneTable(phone_queryset, order_by=request.GET.get('phone_sort', 'phone'))
    
    return render_to_response('address_book/patient_detail.html', 
                              {'patient':patient_queryset[0],'email_table': emails, 'phone_table': phones}, 
                              context_instance = RequestContext(request))   
    
########################################################################################################

# regex patterns are global so that they only compile once per process execution
email_pattern = re.compile(ur'(\d+)-email')
phone_pattern = re.compile(ur'(\d+)-phone') 

# Get the set of numeric prefixes that distinguish each email/phone input element
def submitted_form_copy_prefixes( form_vars, pattern):
    return [y.group(1) for y in [pattern.match(x) for x in form_vars] if y is not None]

@login_and_domain_required
@transaction.commit_manually
def new_patient(request):

    # Multiple models in one form:
    # http://collingrady.wordpress.com/2008/02/18/editing-multiple-objects-in-django-with-newforms/

    if request.method == 'POST': # If the form has been submitted...
        patient_form = ABF.PatientForm(request.POST) # A form bound to the POST data
        
        # We don't know how many email/phone addresses the user sent in, so we have to count, and we have to use
        # the same prefixes that were sent in (else django forms won't automatically copy over POST vars)
        # Prune null email submissions here, too
        prefixes = submitted_form_copy_prefixes(request.POST.keys(), email_pattern)
        email_forms = [y for y in [ABF.EmailForm(request.POST, prefix=str(x)) for x in prefixes] if y['email'].data!='']
        prefixes = submitted_form_copy_prefixes(request.POST.keys(), phone_pattern)
        phone_forms = [y for y in [ABF.PhoneForm(request.POST, prefix=str(x)) for x in prefixes] if (y['phone'].data!='' or y['description'].data!='')]
                                 
        if patient_form.is_valid() and all(x.is_valid() for x in email_forms) and all(x.is_valid() for x in phone_forms): 
            # Special handling for ModelForms with hidden fields - right out of  the Django dev docs
            try:                               
                new_patient = patient_form.save(commit=False)                
                new_patient.save()
                # New objects through GenericRelation fields must be created, not initialized and saved.
                # Don't know why this is - just know that save isn't in the GenericRelation maanger.
                # Need to do further research.
                #
                # This can only be called after the new patient has been created/saved once;
                # needs to have the patient id available.
                new_patient.domain_membership.create(domain=request.user.selected_domain, is_active=True)            
                
                for email_form in email_forms:
                    new_email = email_form.save(commit=False)
                    new_email.patient = new_patient
                    new_email.save()
                        
                for phone_form in phone_forms:
                    new_phone = phone_form.save(commit=False)
                    new_phone.patient = new_patient
                    new_phone.save()
            except:
                transaction.rollback()
                vals = {'error_msg':'There was a problem with your request',
                        'error_details':sys.exc_info(),
                        'show_homepage_link': 1 }
                return render_to_response('error.html', vals, context_instance = RequestContext(request))                   
            else:
                transaction.commit()
                                       
            return render_to_response('address_book/new_patient_success.html', 
                                      {'first_name':new_patient.first_name, 'last_name':new_patient.last_name},
                                      context_instance = RequestContext(request))   
        # Form didn't validate. Make sure we have at least one email and phone field available - we might've wiped them all
        # out if all were submitted blank and there was a problem with the patient form
        else: 
            if not email_forms:
                email_forms = [ABF.EmailForm(prefix=str(0))]
            if not phone_forms:
                phone_forms = [ABF.PhoneForm(prefix=str(0))]                
                 
    else:
        patient_form = ABF.PatientForm() # An unbound form
        email_forms = [ABF.EmailForm(prefix=str(0))]
        phone_forms = [ABF.PhoneForm(prefix=str(0))]        
    
    return render_to_response('address_book/new_patient.html', 
                              {'patient_form':patient_form, 'email_forms':email_forms, 'phone_forms':phone_forms},
                              context_instance = RequestContext(request))   

########################################################################################################    

comma_or_ws = re.compile('[\s,]+')

@login_and_domain_required
def search( request, kind ):
    
    assert(kind=='text' or kind=='id')
    # Unlike some forms, we don't care if this form is submitted via GET or POST, because resorting a displayed
    # table will submit the searchText variable via GET. The distinguishing question is - do we have searchText?
    
    if request.REQUEST.has_key('searchText'): 
        # A form bound to the union of GET and POST data
        form = ABF.SearchForm(kind, request.REQUEST)              
        if form.is_valid(): # All validation rules pass
            rawTxt = form.cleaned_data['searchText']
            splitTxt = comma_or_ws.split( rawTxt )
            
            # OR together all the serach terms we care about
            # 
            # This seem bad for a few reasons:
            #
            # - Need a way to identify the columsn that are searchable at the model level; it's not good
            #   to have to make those decisions here, in code
            # - Likely to be slow - lots of ORs. Really, we want a pattern-matching "in" form, but I suspect
            #   this is quite database-specific (if it exists)
            #
            # Note double underscores with "columns names" of email and phone - we're chasing links to a child model
            
            qset = None
            if kind == 'text':
                cols_we_care_about = ['first_name', 'last_name', 'email__email', 'phone__phone']
            else:
                cols_we_care_about = ['id']
            for term in splitTxt:
                exp = None
                for col in cols_we_care_about:
                    # Use **kwargs feature to dynamically construct filter fieldnames
                    if kind == 'text': 
                        kwargs = {col+"__icontains":term}
                    else:
                        kwargs = {col+"__exact":term}
                    q = Q(**kwargs)
                    if exp is None:
                        exp = q
                    else:
                        exp |= q    
                if qset is None:
                    qset = exp
                else:
                    qset = qset | exp
                     
            # The query doc section titled "Spanning multi-valued relationships" indicates that chained filters on multivalued
            # relationships don't work quite as expected; they don't successivly filter. Rather, they return the union of values
            # that would be returned by each filter clause alone. To get a query that does an interesection (an AND), we have to
            # get all filtering terms into a single call to filter.
            #
            # I have tested this, and it turns out to not make a difference in this case. I think that's because each patient
            # currently only belongs to one domain, so it's not a many-to-many relationship, but haven't tested to confirm that.
            # In any case, putting both conditions in one filter call doesn't hurt (and may help in the future, when patients can
            # be in multiple domains).
            queryset = ABM.Patient.objects.filter(qset, domain_membership__domain = request.user.selected_domain, domain_membership__is_active=True)               
            queryset = queryset.annotate(Count('email', distinct=True)).annotate(Count('phone', distinct=True))
            
            # Returned result depends on number returned - 0 gives a "sorry", 1 takes righ to the patient detail
            # page, and more than one gives the full list view
            n = len(queryset)
            if n == 0:
                vals = {'error_msg':"No patients found for the search string \"" +rawTxt + "\"",
                        'back':urlquote(request.get_full_path()),
                        'show_homepage_link': 0 }
                return render_to_response('error.html', vals, context_instance = RequestContext(request))    
            elif n == 1:
                return patient_detail(request, queryset[0].id)
            else:
                return patient_list_paging(request, queryset, dict(searchText=rawTxt))
    else:
        form = ABF.SearchForm(kind) # An unbound form

    if kind == 'text':
        vals = { 'instructions_1':['Search for patients via text of names, email, and phone numbers'],
                 'instructions_2':["Words and numbers separated by spaces or commas will be OR'd together"],
                 'search_type':'Full-text search' }
    else:
        vals = { 'instructions_1':['Search for patients by ID'],
         'instructions_2':["IDs separated by spaces or commas will be OR'd together"],
         'search_type':'Search' }
    
    vals['action'] = urlquote(request.get_full_path())
    vals['form'] = form
    
    return render_to_response('address_book/search.html', vals, context_instance = RequestContext(request))    

########################################################################################################


