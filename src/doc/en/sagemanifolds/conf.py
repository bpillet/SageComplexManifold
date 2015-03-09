# -*- coding: utf-8 -*-
#
# Sage documentation build configuration file, created by
# sphinx-quickstart on Thu Aug 21 20:15:55 2008.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys, os
sys.path.append(os.environ['SAGE_DOC'])
from common.conf import *

# General information about the project.
project = u"SageManifolds Reference Manual"
name = 'sagemanifolds_ref'
release = "0.6"

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = project + " v" + release
copyright = "2014, Michal Bejger and Eric Gourgoulhon"

# Output file base name for HTML help builder.
htmlhelp_basename = name

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [
  ('index', name+'.tex', u'SageManifolds Reference Manual',
   u'Michal Bejger and Eric Gourgoulhon', 'manual'),
]
