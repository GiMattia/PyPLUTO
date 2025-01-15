# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.
import pathlib
import sys

sys.path.insert(0, os.path.abspath("../../Src/pyPLUTO/"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "PyPLUTO"
copyright = "2024, G. Mattia, D. Crocco, D. Melon Fuksman, M. Bugli, V. Berta, E. Puzzoni, A. Mignone, B, Vaidya"
author = "G. Mattia D. Crocco, D. Melon Fuksman, M. Bugli, V. Berta, E. Puzzoni, A. Mignone, B, Vaidya"
release = "1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "numpydoc",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]
exclude_patterns = []
autoclass_content = "both"

numpydoc_show_class_members = False
html_show_sourcelink = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "agogo"

# html_theme = "pydata_sphinx_theme"

# Add 'qualname' to autodoc_default_options
# This enables the qualname option for autodoc directives
# autodoc_default_options = {
#    'members': True,
#    'undoc-members': True,
#   'private-members': True,
#   'special-members': True,
#   'qualname': True,  # Enable the qualname option
# }
