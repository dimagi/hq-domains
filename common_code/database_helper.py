#!/usr/bin/env python

import sys, os, glob, tempfile
from django.core.management import execute_manager, setup_environ

# We typically softlink the reset, restore, and dump scripts from some common directory to
# the root directory of a site (where the settings.py file lives). By adding the path in 
# which the interpreter is invoked to sys.path, we'll pick up settings.py
sys.path.append(os.getcwd())

import settings # Assumed to be in the current working dir
setup_environ(settings)

DUMP_FORMAT = 'yaml'
CONTRIB_APPS_WE_CARE_ABOUT = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sites']

###############################################################################################
#
# Override this as you like; all of my apps are in ~/web/apps. 
#

def apps_we_care_about():
    return ['domain','address_book', 'django_granular_permissions', 'user_registration']

###############################################################################################

def dump():
    [dump_app(app) for app in CONTRIB_APPS_WE_CARE_ABOUT + apps_we_care_about()]

###############################################################################################

def reset():
    # We don't reset() CONTRIB_APPS_WE_CARE_ABOUT because that tends to not work 
    # (django-admin.py doesn't seem to call SET FOREIGN_KEY_CHECKS = 0 before resetting
    # tables). We'll call flush after we reset our own apps, to clear out those 
    # preinstalled tables.

    L = [get_app_name_dir(app)[0] for app in apps_we_care_about()]

    # Can't make reset() work because of FK, and not just on the contrib apps
    # So, we'll just flush() instead.
#    args = [sys.argv[0], 'reset', '--noinput'] + L
#    print "ARGS: ", args
#    execute_manager(settings, args)

    args = [sys.argv[0], 'flush', '--noinput'] 
    execute_manager(settings, args)

    # Put contrib apps first in the restore path, so all apps that depend on the existence of users
    # will not fail to load due to FK problems
    return  [get_app_name_dir(app)[0] for app in CONTRIB_APPS_WE_CARE_ABOUT] + L

###############################################################################################

def restore():
    L = [x + '.fixture.' + DUMP_FORMAT for x in reset()]
    # Do apps one at a time, in case one of them has a corrupt database dump. 
    # execute_manager chokes if any of them fail when passed simultaneously.
    for x in L:
        args = [sys.argv[0], 'loaddata',x]
        execute_manager(settings, args)

###############################################################################################

def dump_app(app):
    # Get app's name and directory
    (app_name, app_dir) = get_app_name_dir(app)
    
    # Make sure the fixture dir exists and that we can write to it
    try:
        fixture_dir = os.path.join(app_dir, 'fixtures')
        if not os.path.exists(fixture_dir):
            print "Creating fixture directory: ",fixture_dir
            os.mkdir(fixture_dir)
        f = tempfile.TemporaryFile(dir=fixture_dir)
    except OSError:
        # Almost certainly can't write to it
        fixture_dir = settings.FIXTURE_DIRS[0]

    print "Exporting", app_name, "in", fixture_dir    
    active_fixture_name = rename_existing_fixtures(app_name, fixture_dir)
    saveout = sys.stdout
    with open(active_fixture_name, 'w') as active_fixture_file:
        sys.stdout = active_fixture_file
        args = [sys.argv[0], 'dumpdata', app_name, '--indent', '2', '--format', DUMP_FORMAT]
        execute_manager(settings, args)
        sys.stdout = saveout

###############################################################################################

def get_app_name_dir(app):
    exec("import " + app + " as tmp")
    app_dir = os.path.dirname(tmp.__file__)
    app_name = app.split('.')[-1]
    return (app_name, app_dir)

###############################################################################################

def rename_existing_fixtures(app_name, fixture_dir):
    
    # Format of per-app fixture names is:
    # fixturedir/appname.fixture.SERIAL_NUMBER.DUMP_FORMAT
    # where SERIAL_NUMBER is a three-digit number that increments
    #
    # HOWEVER...a numberless version (what would otherwise be 000) is always the 
    # latest one.

    active_fixture_basename = os.path.join(fixture_dir, app_name + '.fixture')
    existing_fixtures = glob.glob(active_fixture_basename + '.???')
    next_num = 1
    if existing_fixtures: 
        existing_fixtures.sort()
        last_file = existing_fixtures[-1]
        next_num = int(last_file.split('.')[-1]) + 1
        assert next_num <= 999

    active_fixture_name = active_fixture_basename + '.' + DUMP_FORMAT
    if os.path.exists(active_fixture_name):
        # No DUMP_FORMAT suffix on the renamed files, so the loaddata command doesn't try to load them
        os.rename( active_fixture_name, 
                   active_fixture_basename + '.{0:03d}'.format(next_num))

    return active_fixture_name

###############################################################################################
def main():
    print "No-op on this module"

if __name__ == '__main__':
    main()

###############################################################################################
