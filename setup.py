from setuptools import setup

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rubrix",
    # other arguments omitted
    description="Open-source tool for tracking, exploring and labelling data for AI projects.",
    long_description=long_description,
    author="recognai",
    author_email="contact@recogn.ai",
    maintainer="recognai",
    maintainer_email="contact@recogn.ai",
    url="https://recogn.ai",
    license="Apache-2.0",
    keywords="data-science natural-language-processing artificial-intelligence knowledged-graph developers-tools human-in-the-loop mlops",
    long_description_content_type="text/markdown",
    use_scm_version=True,
)
