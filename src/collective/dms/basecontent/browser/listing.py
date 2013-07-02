from five import grok

from zope.interface import Interface
from zope.cachedescriptors.property import CachedProperty
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from collective.dms.basecontent import _
from collective.dms.basecontent.browser import column
from collective.dms.basecontent.browser.table import Table


grok.templatedir('templates')

PMF = MessageFactory('plone')


class BaseTable(Table):

    @CachedProperty
    def values(self):
        portal_type = self.viewlet.portal_type
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        query = {}
        query['path'] = {'query' : folder_path}
        query['portal_type'] = portal_type

        results = portal_catalog.searchResults(query)
        return results


class VersionsTable(BaseTable):
    pass


class TasksTable(BaseTable):
    pass


class BaseTitleColumn(column.TitleColumn):
    grok.name('dms.title')
    grok.adapts(Interface, Interface, BaseTable)


class VersionsTitleColumn(BaseTitleColumn):
    grok.adapts(Interface, Interface, VersionsTable)
    linkCSS = 'version-link'


class TaskTitleColumn(BaseTitleColumn):
    grok.adapts(Interface, Interface, TasksTable)
    linkCSS = 'overlay-comment-form'


class DownloadColumn(column.DownloadColumn):
    grok.name('dms.download')
    grok.adapts(Interface, Interface, VersionsTable)


class DeleteColumn(column.DeleteColumn):
    grok.name('dms.delete')
    grok.adapts(Interface, Interface, VersionsTable)


class AuthorColumn(column.PrincipalColumn):
    grok.name('dms.author')
    grok.adapts(Interface, Interface, VersionsTable)
    header = _(u"Author")
    weight = 30
    attribute = 'Creator'


class UpdateColumn(column.DateColumn):
    grok.name('dms.update')
    grok.adapts(Interface, Interface, VersionsTable)
    header = PMF(u"listingheader_modified")
    attribute = 'modification_date'
    weight = 40


class StateColumn(column.StateColumn):
    grok.name('dms.state')
    grok.adapts(Interface, Interface, BaseTable)
    weight = 50


class EnquirerColumn(column.PrincipalColumn):
    grok.name('dms.enquirer')
    grok.adapts(Interface, Interface, TasksTable)
    header = _(u"Enquirer")
    weight = 20
    attribute = 'enquirer'


class ResponsibleColumn(column.PrincipalColumn):
    grok.name('dms.responsible')
    grok.adapts(Interface, Interface, TasksTable)
    header = _(u"Responsible")
    weight = 30
    attribute = 'responsible'


class DeadlineColumn(column.DateColumn):
    grok.name('dms.deadline')
    grok.adapts(Interface, Interface, TasksTable)
    header = _(u"Deadline")
    attribute = 'deadline'
    weight = 60
