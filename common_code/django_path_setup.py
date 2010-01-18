# This is run out of site-packages; storing a copy in common_code so it's
# source controlled

import sys, os

def set_path():
    web_dirs_root = '/Users/ross/web'
    subdirs_to_add = ('', 'apache', 'sites', 'apps')
    for d in subdirs_to_add:
        d = os.path.normpath(os.path.join(web_dirs_root, d))
        if d not in sys.path:
            sys.path.append(d)

