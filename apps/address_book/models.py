from django.contrib.contenttypes import generic
from django.db import models
from domain.models import Membership


###################

class Patient(models.Model):
    domain_membership = generic.GenericRelation( Membership, 
                                                 content_type_field='member_type', 
                                                 object_id_field='member_id' )    
    first_name  = models.CharField(max_length = 30)
    last_name = models.CharField(max_length = 30)

    # Creating a custom column by defining a property
    # derived from an associated set of many-to-one 
    # contained objects
    #
    # Alas, doing this stupidly, by following the contained email and phone sets,
    # leads to one (or more) SQL calls per object; it's fast to develop, but grossly inefficient 
    # to run on big data sets.
    # 
    # The way to do this as a group is via a nested SELECT:
    #
    # select p.id, p.first_name, p.last_name, foo._cnt from 
    # (select count(e.patient_id) _cnt , p.id _id from address_book_email e right outer join  address_book_patient p on p.id = e.patient_id group by p.id) as foo, 
    # address_book_patient p where p.id = foo._id and p.domain_id = 1;
    #
    # This is more or less what Django's aggregation functions (here, we use annotate())
    # do. Unfortunately, django-tables won't look in __dict__ to get the aggregated values;
    # it only picks up formally-defined properties. So, we have to wrap the djangoe-computed
    # vals in trivial properties. 
    #
    # NOTE THAT THE NAME HAS TO BE DIFFERENT, else python throws errors. I've pulled out one
    # of the underscores - django val has two, and property has one.


    @property
    def email_count(self):
        return self.__getattribute__('email__count')

    @property
    def phone_count(self):
        return self.__getattribute__('phone__count')

    def __unicode__(self):
        return self.first_name + u' ' + self.last_name
    
###################    

class Email(models.Model):
    patient = models.ForeignKey(Patient)
    email = models.EmailField()

    def __unicode__(self):
        return self.email

###################

class Phone(models.Model):
    patient = models.ForeignKey(Patient)
    phone = models.CharField(max_length = 30)
    description = models.CharField(max_length = 20)
    
    def __unicode__(self):
        return self.phone

###################

