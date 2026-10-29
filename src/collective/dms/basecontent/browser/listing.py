from collective.dms.basecontent import _
from collective.dms.basecontent.browser import column
from collective.dms.basecontent.browser.table import Table as BaseTable
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.browser.tabview import CategorizedContent
from collective.iconifiedcategory.browser.tabview import TitleColumn
from plone.base.utils import safe_text
from zope.i18nmessageid import MessageFactory

import html

PMF = MessageFactory("plone")


class VersionsTable(BaseTable):
    cssClasses = {"table": "listing nosort dv iconified-listing"}

    @property
    def values(self):
        if not getattr(self, "_v_stored_values", []):
            sort_on = "getObjPositionInParent"
            data = [
                CategorizedContent(self.context, content)
                for content in utils.get_categorized_elements(
                    self.context,
                    result_type="dict",
                    portal_type=self.portal_type,
                    sort_on=sort_on,
                )
            ]
            self._v_stored_values = data[::-1]
        return self._v_stored_values


class DmsAppendixTable(VersionsTable):
    def setUpColumns(self):
        columns = super().setUpColumns()
        return [column for column in columns if column.__name__ != "dms.state"]


class VersionsTitleColumn(TitleColumn):
    def renderCell(self, content):
        pattern = (
            '<a class="version-link" href="{link}" alt="{title}" title="{title}">'
            '<img src="{icon}" alt="{category}" title="{category}" />'
            ' {title}</a><p class="discreet">{description}</p>'
        )
        url = content.getURL()
        return pattern.format(
            link=url,
            title=html.escape(safe_text(getattr(content, self.attrName))),
            icon=content.icon_url,
            category=html.escape(safe_text(content.category_title)),
            description=html.escape(safe_text(content.Description)),
        )


class UpdateColumn(column.DateColumn):
    header = PMF("listingheader_modified")
    attribute = "modified"
    weight = 40
    cssClasses = {"th": "th_header_modified", "td": "td_cell_modified"}


class StateColumn(column.StateColumn):
    # before the author column (50): the Python 2 adapter order placed it there
    weight = 45


class VersionLabelColumn(column.LabelColumn):
    attribute = "label"
    header = _("Label")
    weight = 15
