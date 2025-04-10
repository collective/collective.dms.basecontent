# -*- coding: utf-8 -*-
from collective.dms.basecontent import _
from collective.dms.basecontent.browser import column
from collective.dms.basecontent.browser.table import Table
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

    cssClasses = {"table": "listing nosort dv"}


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
