from AccessControl import getSecurityManager
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.formwidget.contenttree.widget import MultiContentTreeWidget
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from z3c.relationfield.interfaces import IRelationList
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zc.relation.interfaces import ICatalog
from zope.cachedescriptors.property import CachedProperty
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import implements
from zope.intid.interfaces import IIntIds


class IRelatedDocs(IRelationList):
    """"""


class RelatedDocsWidget(MultiContentTreeWidget):
    display_template = ViewPageTemplateFile("related-docs-display.pt")

    def __init__(self, display_backrefs, request):
        self.display_backrefs = display_backrefs
        super(RelatedDocsWidget, self).__init__(request)

    def get_url(self, v):
        return self.request.physicalPathToURL(v)

    def get_label(self, v):
        term = self.terms.getTermByToken(v)
        return term.title

    def update(self):
        super(RelatedDocsWidget, self).update()
        if self.mode == "display":
            if self.tuples and not self.value:
                # hack to not have the 'empty' class added to the field
                self.value = ["don't hide field"]

    @CachedProperty
    def tuples(self):
        refs = [(self.get_url(x), self.get_label(x)) for x in self.value]
        if self.display_backrefs:
            intids = getUtility(IIntIds)
            catalog = getUtility(ICatalog)
            try:
                doc_intid = intids.getId(self.context)
            except KeyError:
                pass
            else:
                sm = getSecurityManager()
                for ref in catalog.findRelations({"to_id": doc_intid}):
                    obj = ref.from_object
                    if not sm.checkPermission("View", obj):
                        continue
                    url = self.get_url(ref.from_path)
                    tp = (url, obj.Title())
                    if tp not in refs:
                        refs.append(tp)
        return refs


@adapter(IRelatedDocs, IFormLayer)
@implementer(IFieldWidget)
def RelatedDocsFieldWidget(field, request):
    return FieldWidget(field, RelatedDocsWidget(field.display_backrefs, request))


class RelatedDocs(RelationList):
    implements(IRelatedDocs)

    def __init__(self, portal_types=None, display_backrefs=False, object_provides=None, **kwargs):
        self.display_backrefs = display_backrefs
        kw = dict()
        if portal_types:
            kw["portal_type"] = portal_types
        if object_provides:
            kw["object_provides"] = object_provides
        RelationList.__init__(self, value_type=RelationChoice(title=u"", source=ObjPathSourceBinder(**kw)), **kwargs)
