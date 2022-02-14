# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------
import os

import rubrix as rb

project = "Rubrix"
copyright = "2021, Recognai"
author = "Recognai"

# Normally the full version, including alpha/beta/rc tags.
# But since rtd changes some files during the build process, the scm version becomes dirty,
# so we just want to display the major and minor version in the tab title of the browser.
release = ".".join(rb.__version__.split(".")[0:2])

# If on the master branch, set release and version to 'master'
if "origin/master" in os.popen("git log -n 1 --oneline --decorate").read():
    release = "master"

# The short X.Y version
version = release


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "nbsphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxext.opengraph",
]

# Do not execute the notebooks when building the docs
nbsphinx_execute = "never"

# Hide input/output prompts (cell counts)
nbsphinx_prolog = """
.. raw:: html

    <script>require=requirejs;</script>
    <script>
        window.PlotlyConfig = {MathJaxConfig: 'local'}
        requirejs.config({
            paths: {
                'plotly': ['https://cdn.plot.ly/plotly-latest.min']
            },
        });
        if(!window.Plotly) {
            {
                require(['plotly'], function(plotly) {window.Plotly=plotly;});
            }
        }
    </script>

    <style>
        .nbinput .prompt,
        .nboutput .prompt {
            display: none;
        }
    </style>
"""

autodoc_typehints = "description"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# Theme options
html_logo = "_static/images/logo.svg"
html_favicon = "_static/images/favicon.ico"
# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = ["css/custom.css"]
html_theme_options = {"logo_only": True}

# Open graph meta
ogp_image = "https://repository-images.githubusercontent.com/362500938/02330f7b-922b-4534-9e8d-895a00f10057"

ogp_custom_meta_tags = [
    '<meta name="twitter:card" content="summary_large_image" />',
]
