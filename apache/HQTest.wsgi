# To create a new web app's .wsgi file, just copy this file to NEWAPPNAME.wsgi; no other changes
# are necessary.
#
# This file is boilerplate; the only reason we have to have one per Django instance is that the
# WSGI config file can't pass an arg to the script that starts Django; it can only call different
# filenames (which then must embed any optional info, such as the name of a web app).

import sys, os

# sys.stderr.write(os.getcwd() + '\n') writes to /var/log/apache2/error_log
# os.getcwd() = '/Library/WebServer', so we have to add paths to common code, apache config
# and sites

#
# Code that sets paths to apache, sites, and apps is centralized in a module located in Python's 
# site-packages directory. It's first called in the project's .wsgi file, and then again in a
# project's settings file. This is because the settings file is called standalone from manage.py,
# which needs to be able to find each app's model file(s). Since the apps don't necessarily live
# under the project dir, settings.py can't find all apps unless they're explicitly added to sys.path.
#
import django_path_setup
django_path_setup.set_path()

#from common_code.debug_client import console_msg 
#console_msg("In " + sys.argv[0])

# Monitor changes in module loaded in this Python process
import _wsgi_monitor
_wsgi_monitor.start(interval=1.0)
    
# __name__ is mod_wsgi, which presumably loads this file. To get the name of this file,
# we have to look in __file__
sitename = os.path.basename(__file__)
sitename = os.path.splitext(sitename)[0]

# Python eggs need to be unpacked in a dir that's writable by the apache user
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
os.environ['DJANGO_SETTINGS_MODULE'] = sitename + '.settings'

# Start the Django instance
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

