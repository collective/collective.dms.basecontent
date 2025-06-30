.. image:: https://github.com/collective/collective.dms.basecontent/actions/workflows/main.yml/badge.svg?branch=master
    :target: https://github.com/collective/collective.dms.basecontent/actions/workflows/main.yml

.. image:: https://coveralls.io/repos/github/collective/collective.dms.basecontent/badge.svg
    :target: https://coveralls.io/github/collective/collective.dms.basecontent

.. image:: http://img.shields.io/pypi/v/collective.dms.basecontent.svg
   :alt: PyPI badge
   :target: https://pypi.org/project/collective.dms.basecontent

Introduction
============

Base content classes for document management system.

Features
--------

- Add dmsdocument type : base content type to handle metadata of a document
- Add dmsmainfile type : content type of the dematerialized file
- Add dmsappendixfile type : content type of an appendix file

The dmsdocument view is divided in 2 columns:

- left column displays metadata
- rigth column displays a documentviewer image of the dmsmailfile content

Migration
---------

* From 1.0 version, collective.z3cform.rolefield has been replaced by dexterity.localrolesfield.
    After the upgrade step, you have to manually define dexterity localroles field configuration.
    See `dexterity.localrolesfield page information <https://pypi.python.org/pypi/dexterity.localrolesfield>`_
