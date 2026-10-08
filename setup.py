#! -*- coding: utf8 -*-
from setuptools import find_packages
from setuptools import setup


version = "3.0.0.dev0"

long_description = (
    open("README.rst").read() + "\n" + "Contributors\n"
    "============\n" + "\n" + open("CONTRIBUTORS.rst").read() + "\n" + open("CHANGES.rst").read() + "\n"
)

setup(
    name="collective.dms.basecontent",
    version=version,
    description="Base content types for document management system",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.2",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="document management system dms viewer",
    author="Ecreall, Entrouvert, IMIO",
    project_urls={
        "PyPI": "https://pypi.org/project/collective.dms.basecontent",
        "Source": "https://github.com/collective/collective.dms.basecontent",
    },
    license="gpl",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "z3c.table>=2.2",
        "collective.externaleditor",
        "collective.iconifiedcategory",
        "dexterity.localrolesfield",
        "imio.actionspanel",
        "imio.annex",
        "imio.helpers>=0.42",
        "plone.api",
        "plone.app.contenttypes",
        "plone.app.dexterity",
        "plone.app.relationfield",
        "plone.namedfile",
        "setuptools",
    ],
    extras_require={
        "test": ["plone.app.testing", "ecreall.helpers.testing", "plone.app.vocabularies"],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
