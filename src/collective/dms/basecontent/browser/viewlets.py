from five import grok

from collective.dms.basecontent.dmsdocument import IDmsDocument
from collective.dms.basecontent import _
from collective.dms.basecontent.browser.listing import FilesTable, TasksTable

from collective.dms.basecontent.browser.table import TableViewlet

grok.templatedir('templates')
grok.context(IDmsDocument)


class DmsBelowContentViewletManager(grok.ViewletManager):
    grok.name('dms.belowcontent')


class BaseViewlet(TableViewlet):
    grok.baseclass()
    grok.viewletmanager(DmsBelowContentViewletManager)
    __table__ = FilesTable

    def contentFilter(self):
        return {'portal_type': self.portal_type}


class FilesViewlet(BaseViewlet):
    grok.name('dms.files')
    grok.order(10)
    portal_type = 'dmsmainfile'
    label = _(u"Version notes")
    noresult_message = _(u"There is no version note for this document.")


class AppendixViewlet(BaseViewlet):
    grok.name('dms.appendix')
    grok.order(20)
    portal_type = 'dmsappendixfile'
    label = _(u"Appendix")
    noresult_message = _(u"There is no appendix for this document.")


class TasksViewlet(BaseViewlet):
    grok.name('dms.tasks')
    grok.order(30)
    portal_type = 'task'
    label = _(u"Tasks")
    noresult_message = _(u"There is no task for this document.")
    __table__ = TasksTable

class OpinionsViewlet(BaseViewlet):
    grok.name('dms.opinions')
    grok.order(40)
    portal_type = 'opinion'
    label = _(u"Opinion applications")
    noresult_message = _(u"There is no opinion applications for this document.")
    __table__ = TasksTable

class ValidationsViewlet(BaseViewlet):
    grok.name('dms.validations')
    grok.order(50)
    portal_type = 'validation'
    label = _(u"Validation applications")
    noresult_message = _(u"There is no validation applications for this document.")
    __table__ = TasksTable

class InformationsViewlet(BaseViewlet):
    grok.name('dms.informations')
    grok.order(60)
    portal_type = 'information'
    label = _(u"Informations")
    noresult_message = _(u"There is no informations for this document.")
    __table__ = TasksTable
