from collective.documentviewer.browser.views import DocumentViewerView
from collective.externaleditor.browser.views import ExternalEditorEnabledView as BaseExternalEditorEnabledView
from plone.base.utils import human_readable_size
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

import json
import os


class VersionViewerView(DocumentViewerView):
    def index(self):
        self.table = self.context.restrictedTraverse('@@iconifiedcategory_table')
        return super(VersionViewerView, self).index()

    def get_obj_size(self, context):
        size = context.get_size()
        return human_readable_size(size)

    def get_content_type(self, context):
        if not context.file:
            return ""
        return context.file.contentType


class JSONVersionViewerView(DocumentViewerView):
    def index(self):
        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(self.dv_data())


class DmsDocumentView(DefaultView):
    def update(self):
        super(DmsDocumentView, self).update()
        self.portal_url = getMultiAdapter((self.context, self.request), name="plone_portal_state").portal_url()
        self.dvstatic = "%s/++resource++dv.resources" % (self.portal_url)

    def legend_extra(self, group):
        return u""


class DmsDocumentEdit(DefaultEditForm):
    template = ViewPageTemplateFile("templates/dmsdocument_edit.pt")

    def update(self):
        super(DmsDocumentEdit, self).update()
        self.portal_url = getMultiAdapter((self.context, self.request), name="plone_portal_state").portal_url()
        self.dvstatic = "%s/++resource++dv.resources" % (self.portal_url)


class ExternalEditorEnabledView(BaseExternalEditorEnabledView):
    def available(self, bypasslock=False):
        if self.context.file is None:
            return False

        ext = os.path.splitext(self.context.file.filename)[-1].lower()
        if ext in (u".pdf", u".jpg", ".jpeg"):
            return False

        return super(ExternalEditorEnabledView, self).available(bypasslock=bypasslock)
