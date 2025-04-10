# coding=utf-8
from BTrees.Length import Length
from collective.dms.basecontent import _
from imio.annex.content.annex import Annex
from imio.annex.content.annex import IAnnex
from plone.autoform import directives as form
from plone.dexterity.schema import DexteritySchemaPolicy
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_unicode
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def titleDefaultValue(container):
    annotations = IAnnotations(container)
    if "higher_version" not in annotations:
        version_number = 1
    else:
        version_number = annotations["higher_version"].value + 1
    return safe_unicode(version_number)


class IDmsFile(IAnnex):
    """Schema for DmsFile"""

    title = schema.TextLine(title=_(u"Version number"), required=False, defaultFactory=titleDefaultValue)

    form.mode(label="hidden")
    label = schema.TextLine(
        title=_(u"Label"),
        required=False,
    )

    form.mode(description="hidden")


@implementer(IDmsFile)
class DmsFile(Annex):
    """DmsFile"""

    __ac_local_roles_block__ = True

    incomingmail = False

    def Title(self):
        if self.incomingmail:
            return _(u"Incoming mail")
        elif base_hasattr(self, "signed") and self.signed:
            return _(u"Signed version")
        else:
            return self.title


class DmsFileSchemaPolicy(DexteritySchemaPolicy):
    """Schema Policy for DmsFile"""

    def bases(self, schemaName, tree):
        return (IDmsFile,)


class IDmsAppendixFile(IAnnex):
    """Schema for DmsAppendixFile"""
    form.mode(title="hidden")
    form.mode(description="hidden")


@implementer(IDmsAppendixFile)
class DmsAppendixFile(Annex):
    """DmsAppendixFile"""

    __ac_local_roles_block__ = True


class DmsAppendixFileSchemaPolicy(DexteritySchemaPolicy):
    """Schema Policy for DmsAppendixFile"""

    def bases(self, schemaName, tree):
        return (IDmsAppendixFile,)


def update_higher_version(context, event):
    """Stores the higher version number in a file parent annotation.

    data transfer: ✅"""
    container = context.getParentNode()
    annotations = IAnnotations(container)
    if "higher_version" not in annotations:
        annotations["higher_version"] = Length()
    annotations["higher_version"].change(1)
