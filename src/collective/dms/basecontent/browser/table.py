from collective.iconifiedcategory import _
from collective.iconifiedcategory.browser.tabview import CategorizedTable
from collective.iconifiedcategory.interfaces import ICategorizedApproved
from collective.iconifiedcategory.interfaces import ICategorizedPrint
from collective.iconifiedcategory.interfaces import ICategorizedSigned
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from zope.cachedescriptors.property import CachedProperty
from zope.i18nmessageid import MessageFactory
from zope.interface import alsoProvides

import datetime


PMF = MessageFactory("plone")


class TableViewlet(ViewletBase):
    __table__ = NotImplemented
    label = NotImplemented
    noresult_message = NotImplemented
    portal_type = NotImplemented

    def update(self):
        self.table = self.__table__(self.context, self.request)
        self.table.portal_type = self.portal_type
        self._prepare_table_render()
        self.table.viewlet = self
        self.table.update()

    def _prepare_table_render(self):
        if self.context.portal_type == "dmsoutgoingmail":
            alsoProvides(self.table, ICategorizedPrint)
            alsoProvides(self.table, ICategorizedSigned)
            alsoProvides(self.table, ICategorizedApproved)


class Table(CategorizedTable):
    cssClassEven = u'even'
    cssClassOdd = u'odd'

    @CachedProperty
    def translation_service(self):
        return api.portal.get_tool("translation_service")

    @CachedProperty
    def wtool(self):
        return api.portal.get_tool("portal_workflow")

    def format_date(self, date, long_format=None, time_only=None):
        if date is None:
            return u""

        # If date is a datetime object, isinstance(date, datetime.date)
        # returns True, so we use type here.
        if type(date) == datetime.date:
            date = date.strftime("%Y/%m/%d")
        elif type(date) == datetime.datetime:
            date = date.strftime("%Y/%m/%d %H:%M")

        return self.translation_service.ulocalized_time(
            date,
            long_format=long_format,
            time_only=time_only,
            context=self.context,
            domain="plonelocales",
            request=self.request,
        )

    def renderRow(self, row, cssClass=None):
        from .column import get_value
        from .column import StateColumn

        isSelected = self.isSelectedRow(row)
        if isSelected and self.cssClassSelected and cssClass:
            cssClass = "%s %s" % (self.cssClassSelected, cssClass)
        elif isSelected and self.cssClassSelected:
            cssClass = self.cssClassSelected
        cells = [self.renderCell(item, col, colspan) for item, col, colspan in row]

        state_column = [x for x in row if isinstance(x[1], StateColumn)]
        if state_column:
            state_column = state_column[0]
            state_value = get_value(state_column[0], "review_state")
            if state_value:
                cssClass += " row-state-%s" % state_value

        cssClass = self.getCSSClass("tr", cssClass)
        return u"\n    <tr%s>%s\n    </tr>" % (cssClass, u"".join(cells))
