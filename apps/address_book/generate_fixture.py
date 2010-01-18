#!/usr/bin/env python

import random

###############################################################

def patient_list():
    fn = ['John', 'Paul', 'George', 'Ringo', 'Mick', 'Keith', 'Ronnie', 'Bill', 'Ann', 'Nancy', 'Eric', 'Jack', 'Ginger']
    ln = ['Lennon', 'McCartney', 'Harrison', 'Starr', 'Jagger', 'Richards', 'Wood', 'Wyman', 'Wilson', 'Clapton', 'Bruce', 'Baker']
    patients =  [(f,l) for f in fn for l in ln]
    random.shuffle(patients)
    return patients

###############################################################

def gen_patient(name, patient_pk):
    s = """- fields: {{first_name: {0}, last_name: {1}}}
  model: address_book.patient
  pk: {2}"""
    output = s.format(name[0], name[1], patient_pk)
    return output

###############################################################

email_pk = 1
def gen_email(name, patient_pk):
    s = """- fields: {{email: {0}, patient: {1}}}
  model: address_book.email
  pk: {2}"""
    global email_pk
    email_domains =  ['@gmail.com', '@hotmail.com', '@yahoo.com']
    random.shuffle(email_domains)
    outarray = []
    for n in range(0, random.randint(0,3)):
        email = name[0] + '.' + name[1] + email_domains[n]
        output = s.format(email, patient_pk, email_pk)
        outarray.append(output)
        email_pk += 1
    return outarray   
    
###############################################################

phone_pk = 1    
def gen_phone(patient_pk):
    s = """- fields: {{description: {0}, patient: {1}, phone: {2}}}
  model: address_book.phone
  pk: {3}"""
    global phone_pk
    desc = ['Home', 'Work', 'Mobile']
    random.shuffle(desc)
    prefix = ['617', '917', '212']
    random.shuffle(prefix)
    outarray = []
    for n in range(0, random.randint(0,3)):
        phone = '{0}-{1:03d}-{2:04d}'.format( prefix[n], random.randint(100, 999), random.randint(0, 9999))
        output = s.format(desc[n], patient_pk, phone, phone_pk)            
        outarray.append(output)
        phone_pk += 1
    return outarray

###############################################################
            
def main():
    random.seed(0) # Make this repeatable
    patient_array = []
    email_array = []
    phone_array = []
    for i, patient in enumerate(patient_list()):
        patient_pk = i + 1
        patient_array.append(gen_patient(patient, patient_pk))
        email_array.extend(gen_email(patient, patient_pk))
        phone_array.extend(gen_phone(patient_pk))
    print '\n'.join(patient_array)
    print '\n'.join(email_array)
    print '\n'.join(phone_array)
            
###############################################################

if __name__ == '__main__':
    main()
