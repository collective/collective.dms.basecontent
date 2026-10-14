.. image:: https://github.com/collective/collective.dms.basecontent/actions/workflows/meta.yml/badge.svg?branch=master
    :target: https://github.com/collective/collective.dms.basecontent/actions/workflows/meta.yml

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
- right column displays a documentviewer image of the dmsmailfile content

Migration
---------

* From 1.0 version, collective.z3cform.rolefield has been replaced by dexterity.localrolesfield.
    After the upgrade step, you have to manually define dexterity localroles field configuration.
    See `dexterity.localrolesfield page information <https://pypi.python.org/pypi/dexterity.localrolesfield>`_
