from collective.dms.basecontent.dmsdocument import IDmsDocument
from OFS.interfaces import IItem
from plone.indexer import indexer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from ZODB.POSException import ConflictError
import six


@indexer(IDmsDocument)
def document_dynamic_searchable_text_indexer(obj):
    indexed_elements = [obj.title]

    # if there is no path to text/plain, do nothing
    transforms = getToolByName(obj, 'portal_transforms')

    had_version = False
    for child in reversed(list(obj.values())):
        if child.portal_type in ('dmsmainfile', 'dmsappendixfile'):
            if not child.file or child.file.getSize() == 0:
                continue

            if not transforms._findPath(child.file.contentType, 'text/plain'):
                continue

            # only index the latest version
            if child.portal_type == 'dmsmainfile' and had_version:
                continue
            had_version = True

            # convert it to text/plain
            try:
                datastream = transforms.convertTo(
                    'text/plain', child.file.data, mimetype=child.file.contentType,
                    filename=child.file.filename)
                indexed_elements.append(six.text_type(datastream.getData(), 'utf-8'))
            except (ConflictError, KeyboardInterrupt):
                raise

    return u' '.join(indexed_elements)


@indexer(IItem)
def treating_groups_indexer(obj):
    # skip acquisition for contained elements. None is considered as ()
    if base_hasattr(obj, 'treating_groups'):
        return obj.treating_groups


@indexer(IItem)
def recipient_groups_indexer(obj):
    # skip acquisition for contained elements. None is considered as ()
    if base_hasattr(obj, 'recipient_groups'):
        return obj.recipient_groups
