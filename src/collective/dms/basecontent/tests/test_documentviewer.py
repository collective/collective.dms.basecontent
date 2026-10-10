# -*- coding: utf-8 -*-
"""Tests needing collective.documentviewer (replaced on Plone 6.2: skipped when it is not installed)."""
from collective.dms.basecontent.browser import views
from collective.dms.basecontent.browser.views import ExternalEditorEnabledView
from collective.dms.basecontent.setuphandlers import setup_documentviewer
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from collective.dms.basecontent.tests.base import add_file
from collective.dms.basecontent.tests.base import LETTER
from collective.dms.basecontent.tests.base import PLAN
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile

import json
import unittest


try:
    from collective.documentviewer.interfaces import ILayer
    from collective.documentviewer.settings import GlobalSettings
except ImportError:  # replaced on Plone 6.2
    ILayer = GlobalSettings = None


@unittest.skipIf(GlobalSettings is None, "collective.documentviewer is not installed")
class DocumentViewerTestCase(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(self.portal, "dmsdocument", title="Building permit")
        self.version1 = add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        self.version2 = add_file(self.doc, "dmsmainfile", "reply.html", PLAN, title="2")


class TestSetuphandlers(DocumentViewerTestCase):

    def test_setup_documentviewer(self):
        settings = GlobalSettings(self.portal)
        # done at install
        self.assertEqual(settings.auto_layout_file_types, ("pdf", "ppt", "word", "rft"))
        self.assertTrue(settings.auto_convert)
        self.assertFalse(settings.show_sidebar)
        self.assertFalse(settings.show_search)
        settings.auto_layout_file_types = ["pdf"]
        settings.show_sidebar = True
        setup_documentviewer(self.portal)
        self.assertEqual(settings.auto_layout_file_types, ("pdf", "ppt", "word", "rft"))
        self.assertFalse(settings.show_sidebar)


class TestDefaultProfile(DocumentViewerTestCase):

    def test_metadata(self):
        self.assertNotEqual(
            self.portal.portal_setup.getLastVersionForProfile("collective.documentviewer:default"), "unknown"
        )

    def test_type_dmsmainfile(self):
        self.assertEqual(self.portal.portal_types.dmsmainfile.view_methods, ("view", "documentviewer"))
        # the documentviewer view of a version (html file, not convertible)
        rendered = self.version2.restrictedTraverse("@@documentviewer")()
        self.assertIn("The file is not a supported document type.", rendered)
        self.assertNotIn('id="DV-container"', rendered)


class TestVersionViewerView(DocumentViewerTestCase):

    def test_index(self):
        view = self.version2.restrictedTraverse("@@versionviewer")
        self.assertIsInstance(view, views.VersionViewerView)
        rendered = view()
        # Plone 4 bug: the ZCML template replaces the index method, so view.table is never set
        self.assertFalse(hasattr(view, "table"))
        self.assertEqual(view.dvstatic, "http://nohost/plone/++resource++dv.resources")
        self.assertFalse(view.enabled)
        self.assertIn('<div id="DV-container">', rendered)
        self.assertIn("window.documentData = ", rendered)
        self.assertIn('"pdf": "%s"' % self.version2.absolute_url(), rendered)
        # a fragment, not a page
        self.assertNotIn("<html", rendered)


class TestJSONVersionViewerView(DocumentViewerTestCase):

    def test_index(self):
        view = self.version1.restrictedTraverse("@@dvdata")
        self.assertIsInstance(view, views.JSONVersionViewerView)
        data = json.loads(view())
        self.assertEqual(self.request.response.getHeader("Content-Type"), "application/json")
        self.assertEqual(data["id"], self.version1.UID())
        self.assertEqual(data["title"], "1")
        self.assertIsNone(data["pages"])
        self.assertEqual(data["resources"]["pdf"], self.version1.absolute_url())
        self.assertEqual(data["canonical_url"], self.version1.absolute_url() + "/view")


class TestVersionsViewlet(DocumentViewerTestCase):

    def test_render(self):
        add_file(self.doc, "dmsappendixfile", "plan.html", PLAN, title="Ground floor plan")
        rendered = self.doc.restrictedTraverse("@@view")()
        # the versions listing, the latest first, and the viewer of the latest version
        self.assertLess(rendered.index(self.version2.absolute_url()), rendered.index(self.version1.absolute_url()))
        self.assertIn('class="listing nosort dv iconified-listing"', rendered)
        self.assertIn('<div id="DV-container">', rendered)
        self.assertIn('"pdf": "%s"' % self.version2.absolute_url(), rendered)
        self.assertNotIn('"pdf": "%s"' % self.version1.absolute_url(), rendered)
        self.assertNotIn("There is no version note for this document.", rendered)


class TestExternalEditorEnabledView(DocumentViewerTestCase):

    def test_available(self):
        # registered for the documentviewer layer, used by the external_edit action
        self.assertTrue(ILayer.providedBy(self.request))
        self.assertIsInstance(self.version2.restrictedTraverse("@@externalEditorEnabled"), ExternalEditorEnabledView)
        api.user.get_current().setMemberProperties({"ext_editor": True})
        api.portal.set_registry_record("externaleditor.ext_editor", True)
        self.version2.file = NamedBlobFile(LETTER, filename="reply.odt")
        buttons = self.portal.portal_actions.listFilteredActionsFor(self.version2)["object_buttons"]
        self.assertIn("external_edit", [action["id"] for action in buttons])
        self.version2.file = NamedBlobFile(LETTER, filename="reply.pdf")
        buttons = self.portal.portal_actions.listFilteredActionsFor(self.version2)["object_buttons"]
        self.assertNotIn("external_edit", [action["id"] for action in buttons])
