import sys
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.simple import direct_to_template


admin.autodiscover()

#
# After much reading, I discovered that Django matches URLs derived from the environment
# variable PATH_INFO. This is set by your webserver, so any misconfiguration there will
# mess this up. In Apache, the WSGIScriptAliasMatch pulls off the mount point directory,
# and puts everything that follows it into PATH_INFO. Those (mount-point-less) paths are
# what is matched in urlpatterns.
#
urlpatterns = patterns( '',
                        url(r'^$', 'HQTest.views.homepage', name='homepage'),
                        url(r'^tos/$', direct_to_template, {'template': 'tos.html'}, name='tos'),

                        # apps
                        url(r'^address_book/', include('address_book.urls')),                                                
                        url(r'^domain/', include('domain.urls')),                        
                                                
                        # our pages (not a contrib app) for users to update their own accounts
                        url(r'^accounts/admin_own/$', 'HQTest.views.admin_own_account_main', name='admin_own_account_main'),
                        url(r'^accounts/admin_own/update/$', 'HQTest.views.admin_own_account_update', name='admin_own_account_update'),
                        
                        # user registration - customization of django_registration's default backend
                        (r'^accounts/', include('domain.user_registration_backend.urls')),

                        # django's admin pages (not specifically our users or domains)
                        (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                        (r'^admin/', include(admin.site.urls)),
                        )


# All of these auth functions have custom templates in registration/, with the default names they expect.
#
# Django docs on password reset are weak. See these links instead:
#
# http://streamhacker.com/2009/09/19/django-ia-auth-password-reset/
# http://www.rkblog.rk.edu.pl/w/p/password-reset-django-10/
# http://blog.montylounge.com/2009/jul/12/django-forgot-password/
#
# Note that the provided password reset function raises SMTP errors if there's any
# problem with the mailserver. Catch that more elegantly with a simple wrapper.

def exception_safe_password_reset(request, *args, **kwargs):
    try:
        return password_reset(request, *args, **kwargs)                
    except: 
        vals = {'error_msg':'There was a problem with your request',
                'error_details':sys.exc_info(),
                'show_homepage_link': 1 }
        return render_to_response('error.html', vals, context_instance = RequestContext(request))   


# auth templates are normally in 'registration,'but that's too confusing a name, given that this app has
# both user and domain registration. Move them somewhere more descriptive.

def auth_pages_path(page):
    return {'template_name':'login_and_password/' + page}

urlpatterns += patterns( 'django.contrib.auth.views',
                        url('^accounts/login/$', 'login', auth_pages_path('login.html'), name='login'),          
                        # If you want to have an intermediate logout page, comment out the next line
                        # and uncomment the line after that. The redirect-to-login view knows where to
                        # redirect to because of the delayed setting of LOGIN_URL at the bottom of the page.
                        url(r'^accounts/logout/$', 'logout_then_login', name='logout'), # no template with this view - see Django docs
                        #url(r'^accounts/logout/$', logout, name='logout'),
                        url(r'^accounts/password_change/$', 'password_change', auth_pages_path('password_change_form.html'), name='password_change'),
                        url(r'^accounts/password_change_done/$', 'password_change_done', auth_pages_path('password_change_done.html') ),                                                
                        url(r'^accounts/password_reset_email/$', exception_safe_password_reset, auth_pages_path('password_reset_form.html'), name='password_reset_email'),
                        url(r'^accounts/password_reset_email/done/$', 'password_reset_done', auth_pages_path('password_reset_done.html') ),
                        url(r'^accounts/password_reset_confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', auth_pages_path('password_reset_confirm.html') ),
                        url(r'^accounts/password_reset_confirm/done/$', 'password_reset_complete', auth_pages_path('password_reset_complete.html') ) 
                        )

# Can't call reverse('login') and the like until all URLConfs are setup. Placing them immediately after 
# urlpatterns definition is the earliest we can set them up
if settings.LOGIN_URL is None:
    settings.LOGIN_URL = reverse('login') 
    
if settings.LOGIN_REDIRECT_URL is None:
    settings.LOGIN_REDIRECT_URL = reverse('homepage') 

if settings.DOMAIN_SELECT_URL is None:
    settings.DOMAIN_SELECT_URL = reverse('domain_select') 
        