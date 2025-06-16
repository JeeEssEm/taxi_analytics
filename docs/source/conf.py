# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os
from pathlib import Path
import django
import inspect

project = 'Сервис такси'
copyright = '2025, JeeEssEm, umarnurmatov'
author = 'JeeEssEm, umarnurmatov'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add your project directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Django settings setup (replace 'taxi_analytics' with your settings module)
os.environ['DJANGO_SETTINGS_MODULE'] = 'taxi_analytics.settings'
django.setup()

extensions = [
    'sphinx.ext.autodoc',
]

autodoc_default_options = {
    'undoc-members': False,
    'special-members': False,
    'private-members': False,
    'inherited-members': False,
}

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


def filter(app, what, name, obj, skip, options):
    if what in ['module', 'class', 'functions']:
        return True
    return False

def setup(app):
    app.connect('autodoc-skip-member', filter)