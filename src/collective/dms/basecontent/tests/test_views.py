from collective.dms.basecontent.browser.views import DmsDocumentEdit
from collective.dms.basecontent.browser.views import DmsDocumentView
from collective.dms.basecontent.browser.views import ExternalEditorEnabledView
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from collective.dms.basecontent.tests.base import add_file
from collective.dms.basecontent.tests.base import LETTER
from collective.dms.basecontent.tests.base import PLAN
from collective.externaleditor.browser.views import (
    ExternalEditorEnabledView as BaseExternalEditorEnabledView,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.z3cform.widgets.select import Select2Widget
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile

import re
import unittest


class ViewsTestCase(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(
            self.portal,
            "dmsdocument",
            title="Building permit",
            description="Request of Mr Smith",
            notes="Urgent",
        )
        # the documents with versions are rendered in test_documentviewer (the versions viewlet shows the viewer)
        self.appendix = add_file(
            self.doc, "dmsappendixfile", "plan.html", PLAN, title="Ground floor plan"
        )


class TestDmsDocumentView(ViewsTestCase):

    def test_update(self):
        view = self.doc.restrictedTraverse("@@view")
        self.assertIsInstance(view, DmsDocumentView)
        rendered = view()
        self.assertEqual(view.portal_url, "http://nohost/plone")
        self.assertEqual(view.dvstatic, "http://nohost/plone/++resource++dv.resources")
        # collective.documentviewer replaced on Plone 6.2: no viewer resources
        self.assertNotIn("++resource++dv.resources", rendered)
        # fixed on Plone 6 (Plone 4 bug: the 4.3 description macro had no "inside" slot for the dms-description span)
        self.assertIn(
            '<span class="dms-description"><p class="lead">Request of Mr Smith</p>',
            rendered,
        )
        # the fields, without title and description
        self.assertIn('id="form-widgets-notes"', rendered)
        self.assertIn('id="form-widgets-treating_groups"', rendered)
        self.assertNotIn('id="form-widgets-IDublinCore-title"', rendered)
        self.assertNotIn('id="form-widgets-IDublinCore-description"', rendered)
        # the versions viewlet above, the appendix viewlet below
        self.assertIn("There is no version note for this document.", rendered)
        self.assertIn("Ground floor plan", rendered)
        self.assertLess(
            rendered.index('id="fieldset-versions"'), rendered.index('id="fields"')
        )
        self.assertLess(
            rendered.index('id="fields"'), rendered.index("Ground floor plan")
        )

    def test_legend_extra(self):
        view = self.doc.restrictedTraverse("@@view")
        view.update()
        self.assertEqual(
            [view.legend_extra(group) for group in view.groups], [""] * len(view.groups)
        )
        self.assertEqual(view.legend_extra(None), "")


class TestDmsDocumentEdit(ViewsTestCase):

    def test_update(self):
        view = self.doc.restrictedTraverse("@@dmsdocument-edit")
        self.assertIsInstance(view, DmsDocumentEdit)
        rendered = view()
        self.assertEqual(view.portal_url, "http://nohost/plone")
        self.assertEqual(view.dvstatic, "http://nohost/plone/++resource++dv.resources")
        for name in (
            "IDublinCore.title",
            "notes",
            "treating_groups",
            "recipient_groups",
            "related_docs",
        ):
            self.assertIn(name, view.widgets)
        # the IDublinCore fieldsets show the default fieldset label: the all-fields div is omitted
        self.assertTrue(view.groups)
        self.assertNotIn('id="all-fields"', rendered)
        self.assertIn('id="fieldset-default"', rendered)
        # collective.z3cform.select2 replaced by the plone.app.z3cform select2 widget
        self.assertIsInstance(view.widgets["recipient_groups"], Select2Widget)
        self.assertIn("pat-select2", view.widgets["recipient_groups"].klass)
        # the versions viewlet is in the form top, not a tab of the Plone 6 form tabbing (it would hide the fields)
        self.assertIn("There is no version note for this document.", rendered)
        self.assertIsNone(re.search(r'<form class="[^"]* pat-autotoc ', rendered))
        self.assertLess(
            rendered.index('id="fieldset-versions"'),
            rendered.index('id="fieldset-default"'),
        )


class TestExternalEditorEnabledView(ViewsTestCase):

    def test_available(self):
        mainfile = add_file(self.doc, "dmsmainfile", "letter.odt", LETTER, title="1")
        # enabled for the user and the site
        api.user.get_current().setMemberProperties({"ext_editor": True})
        api.portal.set_registry_record("externaleditor.ext_editor", True)
        self.assertTrue(
            BaseExternalEditorEnabledView(mainfile, self.request).available()
        )
        self.assertTrue(ExternalEditorEnabledView(mainfile, self.request).available())
        # not for pdf and jpeg files
        for filename in ("scan.pdf", "SCAN.PDF", "photo.jpg", "photo.jpeg"):
            mainfile.file = NamedBlobFile(LETTER, filename=filename)
            self.assertFalse(
                ExternalEditorEnabledView(mainfile, self.request).available(), filename
            )
        self.assertTrue(
            BaseExternalEditorEnabledView(mainfile, self.request).available()
        )
        # not without file
        mainfile.file = None
        self.assertFalse(ExternalEditorEnabledView(mainfile, self.request).available())
        # else the base conditions apply
        mainfile.file = NamedBlobFile(LETTER, filename="letter.odt")
        self.assertTrue(ExternalEditorEnabledView(mainfile, self.request).available())
        api.user.get_current().setMemberProperties({"ext_editor": False})
        self.assertFalse(ExternalEditorEnabledView(mainfile, self.request).available())
