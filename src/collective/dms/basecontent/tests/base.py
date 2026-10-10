# -*- coding: utf-8 -*-
"""Helpers shared by the test modules."""
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


LETTER = b"<html><body><p>I request a building permit for my house.</p></body></html>"
PLAN = b"<html><body><p>Ground floor plan of the house.</p></body></html>"


def default_category(context):
    """Return the default category token (the vocabulary creates it with its config)."""
    vocabulary = getUtility(IVocabularyFactory, "collective.iconifiedcategory.categories")(context)
    return list(vocabulary)[0].token


def add_file(container, portal_type, filename, data, **kwargs):
    """Add a categorized dms file."""
    return createContentInContainer(
        container,
        portal_type,
        file=NamedBlobFile(data, filename=filename),
        content_category=default_category(container),
        **kwargs
    )
