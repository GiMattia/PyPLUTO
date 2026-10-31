# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from importlib.metadata import version as _pkg_version

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.
sys.path.insert(0, os.path.abspath("../../Src/pyPLUTO/"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project: str = "PyPLUTO"
copyright: str = "2025, G. Mattia, D. Crocco, D. Melon Fuksman, M. Bugli, V. Berta, E. Puzzoni, A. Mignone, B, Vaidya"
author: str = "G. Mattia D. Crocco, D. Melon Fuksman, M. Bugli, V. Berta, E. Puzzoni, A. Mignone, B, Vaidya"
release: str = _pkg_version("py-pluto")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "numpydoc",
    "sphinx.ext.viewcode",
    "sphinx_gallery.gen_gallery",
]

# Two galleries: the scripts in Gallery/ are run and give their figures, and
# the methods they call collect them in a box of examples (backreferences);
# the PLUTO test problems in Examples/ are not run, and show the figure each
# script saves
sphinx_gallery_conf = {
    "examples_dirs": ["../../Gallery", "../../Examples"],
    "gallery_dirs": ["gallery", "pluto_tests"],
    "filename_pattern": r"/Gallery/",
    "within_subsection_order": "FileNameSortKey",
    "doc_module": ("pyPLUTO",),
    "backreferences_dir": "gen_modules/backreferences",
    "write_computation_times": False,
    "remove_config_comments": True,
    # The images depend on pyPLUTO too, so unchanged scripts run again
    "run_stale_examples": True,
}

# The gallery index repeats the heading of each topic page by design
suppress_warnings = ["autosectionlabel.gallery/index"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]
# exclude_patterns = []
autoclass_content = "both"

numpydoc_show_class_members = False
html_show_sourcelink = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = "agogo"

html_theme = "pydata_sphinx_theme"

html_title = "PyPLUTO"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "navbar_align": "left",
    "show_nav_level": 2,
    # All eight pages in the bar, with no "More" menu
    "header_links_before_dropdown": 8,
    # Search as an icon next to the color mode, like matplotlib
    "navbar_persistent": [],
    "navbar_end": ["search-button", "theme-switcher", "navbar-icon-links"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/GiMattia/PyPLUTO",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
}

# Add 'qualname' to autodoc_default_options
# This enables the qualname option for autodoc directives
# autodoc_default_options = {
#    'members': True,
#    'undoc-members': True,
#   'private-members': True,
#   'special-members': True,
#   'qualname': True,  # Enable the qualname option
# }
