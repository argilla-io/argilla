#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
from datetime import datetime

try:
    import argilla as rg

    version_ = rg.__version__
except ModuleNotFoundError:
    version_ = os.environ.get("VERSION")
except AttributeError:
    version_ = os.environ.get("VERSION")

project = "Argilla"
copyright = f"{datetime.today().year}, Argilla.io"
author = "Argilla.io"

# Normally the full version, including alpha/beta/rc tags.
release = version_

# The short X.Y version
try:
    version = ".".join(release.split(".")[0:2])
    release = version
except:
    version = ""
    release = ""


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "nbsphinx",
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxext.opengraph",
    "sphinx_design",
    "sphinx_copybutton",
]

myst_enable_extensions = [
    "colon_fence",
    "substitution",
]

myst_substitutions = {
    "pipversion": "" if "dev" in release else "==" + release,
    "dockertag": "master" if "dev" in release else "v" + release,
}
myst_substitutions["dockercomposeyaml"] = """```yaml
# docker-compose.yaml
version: "3"

services:
 argilla:
   image: argilla/argilla-server:{}
   ports:
     - "80:80"
   environment:
     ARGILLA_ELASTICSEARCH: <elasticsearch-host_and_port>
     ARGILLA_AUTH_SECRET_KEY: Please generate a 32 character random string with: openssl rand -hex 32
   restart: unless-stopped
```""".format(myst_substitutions["dockertag"])
myst_substitutions["dockercomposeuseryaml"] = """```yaml
# docker-compose.yaml
services:
  argilla:
    image: argilla/argilla-server:{}
    ports:
      - "6900:80"
    environment:
      ARGILLA_ELASTICSEARCH: http://elasticsearch:9200
      ARGILLA_AUTH_SECRET_KEY: Please generate a 32 character random string with: openssl rand -hex 32
      ARGILLA_LOCAL_AUTH_USERS_DB_FILE: /config/.users.yaml

    volumes:
      # We mount the local file .users.yaml in remote container in path /config/.users.yaml
      - ${}/.users.yaml:/config/.users.yaml
  ...
```""".format(myst_substitutions["dockertag"], "PWD")

# Do not execute the notebooks when building the docs
nbsphinx_execute = "never"

# open html file as Python string
getting_started_html = open(
    "./_common/getting_started.html", "r", encoding="utf8"
).read()
next_steps_html = open("./_common/next_steps.html", "r", encoding="utf8").read()

# -- AUTODOC IMPORT MOCKS ---------------------------------------------------
autodoc_typehints = "description"
autodoc_mock_imports = [
    "cleanlab",
    "datasets",
    "huggingface_hub",
    "flair",
    "faiss",
    "flyingsquid",
    "pgmpy",
    "plotly",
    "snorkel",
    "spacy",
    "spacy_transformers",
    "sentence_transformers",
    "torch",
    "transformers",
    "evaluate",
    "seqeval",
    "setfit",
    "span_marker",
    "openai",
    "peft",
    "trl",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

if not os.getenv("READTHEDOCS"):
    notfound_urls_prefix = ""
else:
    lang, docs_version = (
        os.getenv("READTHEDOCS_LANGUAGE", "en"),
        os.getenv("READTHEDOCS_VERSION", "latest"),
    )

    notfound_urls_prefix = f"/{lang}/{docs_version}/"

docs_version = os.getenv("READTHEDOCS_VERSION", "latest")
if docs_version == "latest":
    branch = "main"
else:
    branch = docs_version.replace("-", "/")

nbsphinx_prolog = (
    """
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
    + f"""

.. raw:: html

    {getting_started_html}

"""
    + """

.. raw:: html

    <div class="open-in-colab__wrapper">
    <a href="https://colab.research.google.com/github/argilla-io/argilla/blob/"""
    + branch
    + """/docs/_source/{{ env.doc2path(env.docname, base=None) }}" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" style="display: inline; margin: 0" alt="Open In Colab"/></a> &nbsp;"""
    + """<a href="https://github.com/argilla-io/argilla/tree/"""
    + branch
    + """/docs/_source/{{ env.doc2path(env.docname, base=None) }}" target="_blank"><img src="https://img.shields.io/badge/github-view%20source-black.svg" style="display: inline; margin: 0" alt="View Notebook on GitHub"/></a>
    </div>
"""
)

# nbsphinx_epilog = f"""
# .. raw:: html

#     {next_steps_html}
# """

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# Theme options
html_favicon = "_static/images/favicon.ico"
# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = ["css/custom.css"]
html_js_files = ["js/githubStargazers.js", "js/sidebarScrollPosition.js"]
html_theme_options = {
    "top_of_page_button": None,
    "sidebar_hide_name": True,
    "light_logo": "images/logo-light-mode.svg",
    "dark_logo": "images/logo-dark-mode.svg",
    "light_css_variables": {
        "color-sidebar-background": "#FFFFFF",
        "color-sidebar-background-border": "#e9eaed",
        "color-sidebar-caption-text": "#484848",
        "color-sidebar-link-text": "#484848",
        "color-sidebar-link-text--top-level": "#484848",
        "color-sidebar-item-background--current": "transparent",
        "color-sidebar-item-background--hover": "transparent",
        "color-sidebar-item-expander-background": "transparent",
        "color-sidebar-item-expander-background--hover": "transparent",
        "color-sidebar-search-text": "#484848",
        "color-sidebar-search-background": "#FFFFFF",
        "color-sidebar-search-background--focus": "#FFFFFF",
        "color-sidebar-search-border": "#b9b9b9",
        "color-sidebar-search-border-focus": "#484848",
        "color-sidebar-current-text": "#ff675f",
        "color-content-foreground": "#484848",
        "color-toc-title": "#212529",
        "color-toc-item-text--hover": "#484848",
        "color-toc-item-text--active": "#484848",
        "color-table-header": "#FDDACA",
        "color-table-bg": "#FFE5D9",
        "color-table-row": "#FEEDE6",
        "color-link": "#ff675f",
        "color-link--hover": "#ff675f",
        "content-padding": "5em",
        "content-padding--small": "2em",
        "color-search-icon": "#484848",
        "color-search-placeholder": "#484848",
        "color-literal": "#FF675F",
        "toc-spacing-vertical": "3em",
        "color-page-info": "#646776",
        "toc-item-spacing-vertical": "1em",
        "color-img-background": "#ffffff",
        "sidebar-tree-space-above": "0",
        "sidebar-caption-space-above": "0",
        "color-card-bg": "#ffffff",
        "color-card-bg-hover": "#484848",
        "color-card-text": "#ffffff",
        "sd-color-card-border": "#dadada",
        "color-tuto-card-bg": "#ffffff",
        "color-tuto-card-bg-hover": "#ffffff",
        "color-tuto-card-text": "#484848",
        "sd-color-tabs-underline-active": "#FF675F",
        "sd-color-tabs-label-active": "#FF675F",
        "sd-color-tabs-label-inactive": "#6d6d6d",
        "sd-color-tabs-label-hover": "#6d6d6d",
        "sd-color-tabs-underline-hover": "#6d6d6d",
        "sd-fontsize-tabs-label": "0.9rem",
    },
    "dark_css_variables": {
        "color-sidebar-background": "#131416",
        "color-sidebar-background-border": "#303335",
        "color-sidebar-caption-text": "#FFFFFF",
        "color-sidebar-link-text": "#FFFFFF",
        "color-sidebar-link-text--top-level": "#FFFFFF",
        "color-sidebar-item-background--current": "none",
        "color-sidebar-item-background--hover": "none",
        "color-sidebar-item-expander-background": "transparent",
        "color-sidebar-item-expander-background--hover": "transparent",
        "color-sidebar-search-text": "#FFFFFF",
        "color-sidebar-search-background": "#131416",
        "color-sidebar-search-background--focus": "transparent",
        "color-sidebar-search-border": "#FFFFFF",
        "color-sidebar-search-border-focus": "#FFFFFF",
        "color-sidebar-search-foreground": "#FFFFFF",
        "color-sidebar-current-text": "#FFC2BF",
        "color-content-foreground": "#FFFFFF",
        "color-toc-title": "#FFFFFF",
        "color-toc-item-text--hover": "#FFFFFF",
        "color-toc-item-text--active": "#FFFFFF",
        "color-table-header": "#131416",
        "color-table-bg": "#232427",
        "color-table-row": "#444444",
        "color-link": "#FFC2BF",
        "color-link--hover": "#FFC2BF",
        "color-search-icon": "#FFFFFF",
        "color-search-placeholder": "#FFFFFF",
        "color-literal": "#F8C0A7",
        "color-page-info": "#FFFFFF",
        "color-img-background": "#18181a",
        "sidebar-tree-space-above": "0",
        "sidebar-caption-space-above": "0",
        "color-card-bg": "#27282a",
        "color-card-bg-hover": "#27282a",
        "color-card-text": "#ffffff",
        "sd-color-card-border": "#27282a",
        "color-tuto-card-bg": "#27282a",
        "color-tuto-card-bg-hover": "#3b3b3f",
        "color-tuto-card-text": "#ffffff",
    },
}
pygments_style = "material"
pygments_dark_style = "material"


# Open graph meta
ogp_image = "https://docs.v1.argilla.io/en/latest/_static/images/og-doc.png"

ogp_custom_meta_tags = [
    '<meta name="twitter:card" content="summary_large_image" />',
]
