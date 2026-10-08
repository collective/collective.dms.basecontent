from AccessControl import getSecurityManager
from plone.app.z3cform.widgets.relateditems import RelatedItemsWidget
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.interface import implementer
from zope.intid.interfaces import IIntIds


class RelatedDocsWidget(RelatedItemsWidget):
    """Related items widget also displaying the back references."""

    display_template = ViewPageTemplateFile("related-docs-display.pt")
    display_backrefs = True

    def render(self):
        if self.mode == DISPLAY_MODE:
            return self.display_template(self)
        return super(RelatedDocsWidget, self).render()

    def tuples(self):
        """(url, title) of the viewable related objects, then of the back references."""
        sm = getSecurityManager()
        objs = [rel.to_object for rel in getattr(self.context, self.field.__name__, None) or []]
        if self.display_backrefs:
            try:
                doc_intid = getUtility(IIntIds).getId(self.context)
            except KeyError:
                pass
            else:
                objs += [rel.from_object for rel in getUtility(ICatalog).findRelations({"to_id": doc_intid})]
        refs = []
        for obj in objs:
            if obj is None or not sm.checkPermission("View", obj):
                continue
            tp = (obj.absolute_url(), obj.Title())
            if tp not in refs:
                refs.append(tp)
        return refs


@implementer(IFieldWidget)
def RelatedDocsFieldWidget(field, request):
    return FieldWidget(field, RelatedDocsWidget(request))
