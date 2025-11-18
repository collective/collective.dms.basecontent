from collective.iconifiedcategory.vocabularies import CategoryVocabulary as BaseCategoryVocabulary
from plone import api
from plone.namedfile import NamedBlobImage
from plone.principalsource.source import PrincipalSource
from plone.principalsource.source import PrincipalSourceBinder
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory

import os


# By default, we list groups and we can search for users in ajax
class PrincipalSource(PrincipalSource):
    def search_principals(self, groups_first=False, **kw):
        if kw:
            results = self.acl_users.searchPrincipals(groups_first=True, **kw)
        else:
            # if no kw, we have been called from source __iter__ because
            # of Chosen widget populate_select attribute is set to True
            results = self.acl_users.searchGroups()
        return [r for r in results if r.get("groupid", None) != "AuthenticatedUsers"]

    @property
    def _search(self):
        if self.users and self.groups:
            # return self.acl_users.searchPrincipals
            return self.search_principals
        elif self.users:
            return self.acl_users.searchUsers
        elif self.groups:
            return self.acl_users.searchGroups


class PrincipalSourceBinder(PrincipalSourceBinder):
    def __call__(self, context):
        return PrincipalSource(context, self.users, self.groups)


@implementer(IVocabularyFactory)
class PrincipalsVocabularyFactory(object):
    """Vocabulary for principals"""

    def __call__(self, context):
        principals = PrincipalSourceBinder(users=True, groups=True)
        return principals(context)


@implementer(IVocabularyFactory)
class TreatingGroupsVocabulary(object):
    """Vocabulary for treating groups"""

    def __call__(self, context):
        principals = PrincipalSourceBinder(users=True, groups=True)
        #        principals = queryUtility(IVocabularyFactory, name=u'plone.principalsource.Principals')
        return principals(context)


@implementer(IVocabularyFactory)
class RecipientGroupsVocabulary(object):
    """Vocabulary for recipient groups"""

    def __call__(self, context):
        # principals = queryUtility(IVocabularyFactory, name=u'plone.principalsource.Principals')
        principals = PrincipalSourceBinder(users=True, groups=True)
        return principals(context)


class CategoryVocabulary(BaseCategoryVocabulary):

    def _get_categories(self, context, only_enabled=True):
        try:
            categories = super(CategoryVocabulary, self)._get_categories(context, only_enabled=only_enabled)
        except ValueError:
            categories = [self.create_default_category()]
        return categories

    def create_default_category(self):
        """Create a default category if none exists."""
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
