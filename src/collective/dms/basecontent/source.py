from collective.iconifiedcategory.vocabularies import CategoryVocabulary as BaseCategoryVocabulary
from plone import api
from plone.namedfile import NamedBlobImage
from plone.protect.interfaces import IDisableCSRFProtection
from zope.globalrequest import getRequest
from zope.interface import alsoProvides

import os


class CategoryVocabulary(BaseCategoryVocabulary):

    def _get_categories(self, context, only_enabled=True):
        try:
            categories = super(CategoryVocabulary, self)._get_categories(context, only_enabled=only_enabled)
        except ValueError:
            categories = [self.create_default_category()]
        return categories

    def create_default_category(self):
        """Create a default category if none exists."""
        # created when a file add form is opened (GET): not a write of the user (plone.protect auto CSRF)
        request = getRequest()
        if request is not None:
            alsoProvides(request, IDisableCSRFProtection)
        portal = api.portal.get()
        ccc = api.content.create(
            container=portal,
            id='contentcategory-configuration',
            title='Content Category Configuration',
            type="ContentCategoryConfiguration",
            exclude_from_nav=True,
            safe_id=True,
        )

        ccg = api.content.create(
            type="ContentCategoryGroup",
            title="Default Category Group",
            container=ccc,
            id="default-category-group",
            safe_id=True,
        )

        with open(os.path.join(os.path.dirname(__file__), "tests", "icon.png"), "rb") as fl:
            icon = NamedBlobImage(fl.read(), filename=u"icon.png")
        cc = api.content.create(
            type="ContentCategory",
            title="Default Category",
            icon=icon,
            container=ccg,
            id="default-category",
            safe_id=True,
        )

        return cc
