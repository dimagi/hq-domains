from django.conf.urls.defaults import *

#
# After much reading, I discovered that Django matches URLs derived from the environment
# variable PATH_INFO. This is set by your webserver, so any misconfiguration there will
# mess this up. In Apache, the WSGIScriptAliasMatch pulls off the mount point directory,
# and puts everything that follows it into PATH_INFO. Those (mount-point-less) paths are
# what is matched in urlpatterns.
#

urlpatterns = patterns( 'address_book.views',
                        url(r'^patient_list/$', 'patient_list', name='patient_list'),
                        url(r'^patient_detail/(?P<patient_id>\d{1,10})/$', 'patient_detail', name='patient_detail'),
                        url(r'^new_patient/$', 'new_patient', name='new_patient'),
                        url(r'^search/text/$', 'search', kwargs=dict(kind='text'), name='search_text'),
                        url(r'^search/id/$', 'search', kwargs=dict(kind='id'), name='search_id'),
                        )


