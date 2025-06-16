from collective.dms.basecontent import _
from collective.dms.basecontent.browser.listing import DmsAppendixTable
from collective.dms.basecontent.browser.listing import VersionsTable
from collective.dms.basecontent.browser.table import TableViewlet
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from zope.viewlet.interfaces import IViewletManager


class IDmsAboveContent(IViewletManager):
    """A viewlet manager that sits above the content area"""


class IDmsBelowContent(IViewletManager):
    """A viewlet manager that sits below the content area"""


class BaseViewlet(TableViewlet):

    __table__ = VersionsTable

    def contentFilter(self):
        return {
            "portal_type": self.portal_type,
        }


APPENDIX_FILTER = {"portal_type": "dmsappendixfile", "sort_on": "getObjPositionInParent", "sort_order": "ascending"}


class VersionsViewlet(BaseViewlet):
    portal_type = "dmsmainfile"
    label = _(u"Versions")
    noresult_message = _(u"There is no version note for this document.")

    def contentFilter(self):
        return {"portal_type": self.portal_type, "sort_on": "getObjPositionInParent", "sort_order": "descending"}

    def first_appendix(self):
        if len(self.table.values) > 0:
            return None
        values = api.portal.get_tool("portal_catalog").searchResults(
            path="/".join(self.context.getPhysicalPath()), **APPENDIX_FILTER
        )
        if values:
            return values[0]
        return None


class AppendixViewlet(BaseViewlet):
    portal_type = "dmsappendixfile"
    label = _(u"Appendix")
    noresult_message = _(u"There is no appendix for this document.")
    __table__ = DmsAppendixTable

    def contentFilter(self):
        return APPENDIX_FILTER


class ChangeTitleViewlet(ViewletBase):
    def render(self):
        return u"""
<script type="text/javascript">
  (function ($) {
    $(document).ready(function () {
      $("body.template-dmsincomingmail label[for='form-widgets-IDublinCore-title']").text('Objet');
      $("body.template-dmsoutgoingmail label[for='form-widgets-IDublinCore-title']").text('Objet');
      $("body.template-edit.portaltype-dmsincomingmail label[for='form-widgets-IDublinCore-title']").text('Objet');
      $("body.template-edit.portaltype-dmsoutgoingmail label[for='form-widgets-IDublinCore-title']").text('Objet');
    });
  })(jQuery);
</script>"""
