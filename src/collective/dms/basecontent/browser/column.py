from Acquisition import aq_base  # noqa
from collective.dms.basecontent import _
from collective.eeafaceted.z3ctable.columns import BaseColumn
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory

import Missing


PMF = MessageFactory("plone")


def get_value(item, attribute, default=None):
    try:
        value = getattr(aq_base(item), attribute)
        if value is Missing.Value:
            return default
    except AttributeError:
        obj = item.getObject()
        value = getattr(obj, attribute, default)

    if callable(value):
        value = value()

    return value


class DateColumn(BaseColumn):
    attribute = NotImplemented

    def renderCell(self, item):
        value = get_value(item, self.attribute)
        return self.table.format_date(value)


class StateColumn(BaseColumn):
    header = PMF(u"State")
    weight = 50

    def renderCell(self, item):
        try:
            wtool = self.table.wtool
            portal_type = get_value(item, "portal_type")
            review_state = get_value(item, "review_state")
            if not review_state:
                return u""
            state_title = wtool.getTitleForStateOnType(review_state, portal_type)
            return translate(PMF(state_title), context=self.request)
        except WorkflowException:
            return u""


class LabelColumn(BaseColumn):
    attribute = NotImplemented

    def renderCell(self, item):
        value = get_value(item, self.attribute)
        if value is None:
            value = ""
        return value
