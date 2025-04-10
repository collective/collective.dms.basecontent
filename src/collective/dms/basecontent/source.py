from plone.principalsource.source import PrincipalSource
from plone.principalsource.source import PrincipalSourceBinder
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


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
