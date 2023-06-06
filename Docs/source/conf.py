# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.
import pathlib
import sys
sys.path.insert(0,str('../../Src/pyPLUTO/'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyPLUTO'
copyright = '2023, G. Mattia, D. Crocco'
author = 'G. Mattia D. Crocco'
release = '0.7.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.autosectionlabel','numpydoc'
]
intersphinx_mapping = {
  'python': ('https://docs.python.org/3', None),
  }

templates_path = ['_templates']
exclude_patterns = []
autoclass_content = 'both'

numpydoc_show_class_members = False
html_show_sourcelink = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "agogo"

#html_theme = "pydata_sphinx_theme"
