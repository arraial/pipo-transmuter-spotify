# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import importlib.metadata

project = "pipo_transmuter_spotify"
copyright = "2024, Tiago Gonçalves"
author = "Tiago Gonçalves, André Gonçalves, Miguel Peixoto"

try:
    release = importlib.metadata.version(project)
except importlib.metadata.PackageNotFoundError:
    release = "latest"

version = release

nitpicky = True

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx_immaterial",
]

master_doc = "index"
templates_path = ["_templates"]
exclude_patterns = ["_build", "_templates"]
show_authors = True
add_function_parentheses = False
language = "en"

# -- Options for autoapi ----------------------------------------------
autoapi_dirs = ["../pipo_transmuter_spotify"]

# -- Options for napoleon ----------------------------------------------
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = False
napoleon_preprocess_types = True
napoleon_attr_annotations = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_immaterial"
html_extra_path = []
html_static_path = ["_static"]
html_theme_options = {
    "source_repository": f"https://github.com/arraial/{project}",
    "source_branch": "main",
    "source_directory": "docs/",
}
html_baseurl = f"https://arraial.github.io/{project}"

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration
todo_include_todos = True
