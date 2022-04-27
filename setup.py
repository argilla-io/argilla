from setuptools import setup

version = {}
with open("src/rubrix/_version.py") as fp:
    exec(fp.read(), version)

setup(version=version["version"])
