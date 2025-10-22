# -*- coding: utf-8 -*-
from collective.dms.basecontent import _
from collective.dms.basecontent.browser import column
from collective.dms.basecontent.browser.table import Table
from collective.iconifiedcategory.browser.tabview import ApprovedColumn
from collective.iconifiedcategory.browser.tabview import PrintColumn
from collective.iconifiedcategory.browser.tabview import SignedColumn
from collective.iconifiedcategory.utils import get_category_object
from Products.CMFCore.utils import getToolByName
from zope.cachedescriptors.property import CachedProperty
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory


PMF = MessageFactory("plone")


class BaseTable(Table):
    @CachedProperty
    def values(self):
        portal_catalog = getToolByName(self, "portal_catalog")
        folder_path = "/".join(self.context.getPhysicalPath())
        query = {"path": {"query": folder_path}, "sort_on": "getObjPositionInParent", "sort_order": "ascending"}
        query.update(self.viewlet.contentFilter())
        results = portal_catalog.searchResults(query)
        return results


class VersionsTable(BaseTable):
    cssClasses = {"table": "listing nosort dv iconified-listing"}

    def _get_content_category_group(self, context):
        return get_category_object(context, context.content_category).get_category_group()

    def setUpColumns(self):
        columns = super(VersionsTable, self).setUpColumns()

        final_columns = []
        for col in columns:
            if isinstance(col, PrintColumn) and not any((self._get_content_category_group(v.getObject()).to_be_printed_activated for v in self.values)):
                continue
            elif isinstance(col, SignedColumn) and not any((self._get_content_category_group(v.getObject()).signed_activated for v in self.values)):
                continue
            elif isinstance(col, ApprovedColumn) and not any((self._get_content_category_group(v.getObject()).approved_activated for v in self.values)):
                continue
            final_columns.append(col)
        return final_columns

    def updateColumns(self):
        super(VersionsTable, self).updateColumns()
        self.columns = self.columns[:-3] + list(reversed(self.columns[-3:]))


class DmsAppendixTable(VersionsTable):
    def setUpColumns(self):
        columns = super(DmsAppendixTable, self).setUpColumns()
        return [column for column in columns if column.__name__ != "dms.state"]


class VersionsTitleColumn(column.TitleColumn):
    domain = "collective.dms.basecontent"
    linkCSS = "version-link"

    def getLinkContent(self, item):
        content = super(VersionsTitleColumn, self).getLinkContent(item)
        return translate(content, domain=self.domain, context=self.request)


class AuthorColumn(column.PrincipalColumn):
    header = _(u"Author")
    weight = 30
    attribute = "Creator"
    cssClasses = {"th": "th_header_author", "td": "td_cell_author"}


class UpdateColumn(column.DateColumn):
    header = PMF(u"listingheader_modified")
    attribute = "modified"
    weight = 40
    cssClasses = {"th": "th_header_modified", "td": "td_cell_modified"}


class StateColumn(column.StateColumn):
    weight = 50


class VersionLabelColumn(column.LabelColumn):
    attribute = "label"
    header = _(u"Label")
    weight = 15
