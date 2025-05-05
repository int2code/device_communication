# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# pylint: skip-file
import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath("../src"))

from device_communication._version import __version__ as release

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "device-communication"
copyright = f"{date.today().year}, int2code"
author = "int2code"

version = release = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinxcontrib.programoutput",
    "myst_parser",
]
autosummary_generate = True

# uncomment when _templates won't be empty
# templates_path = ['._templates']
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
# uncomment when static content is added
# html_static_path = ['_static']

# suppress warning from release notes and readme markdown files
suppress_warnings = ["myst.header"]
