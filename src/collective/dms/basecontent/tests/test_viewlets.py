from collective.dms.basecontent.browser.listing import DmsAppendixTable
from collective.dms.basecontent.browser.listing import VersionsTable
from collective.dms.basecontent.browser.viewlets import AppendixViewlet
from collective.dms.basecontent.browser.viewlets import BaseViewlet
from collective.dms.basecontent.browser.viewlets import ChangeTitleViewlet
from collective.dms.basecontent.browser.viewlets import IDmsAboveContent
from collective.dms.basecontent.browser.viewlets import IDmsBelowContent
from collective.dms.basecontent.browser.viewlets import VersionsViewlet
from collective.dms.basecontent.browser.views import DocumentViewerView
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from collective.dms.basecontent.tests.base import add_file
from collective.dms.basecontent.tests.base import LETTER
from collective.dms.basecontent.tests.base import PLAN
from plone.app.layout.viewlets.interfaces import IHtmlHeadLinks
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager

import unittest


class ViewletsTestCase(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(
            self.portal, "dmsdocument", title="Building permit"
        )
        self.view = self.doc.restrictedTraverse("@@view")

    def viewlet(self, manager_name, name):
        """The viewlet as the document view gets it from its manager."""
        manager = getMultiAdapter(
            (self.doc, self.request, self.view), IViewletManager, name=manager_name
        )
        manager.update()
        return [viewlet for viewlet in manager.viewlets if viewlet.__name__ == name][0]


class TestBaseViewlet(ViewletsTestCase):

    def test_contentFilter(self):
        viewlet = BaseViewlet(self.doc, self.request, self.view, None)
        viewlet.portal_type = "dmsmainfile"
        self.assertEqual(viewlet.contentFilter(), {"portal_type": "dmsmainfile"})
        self.assertIs(BaseViewlet.__table__, VersionsTable)


class TestVersionsViewlet(ViewletsTestCase):

    def test_contentFilter(self):
        viewlet = self.viewlet("dms.abovecontent", "dms.files")
        self.assertIsInstance(viewlet, VersionsViewlet)
        self.assertTrue(IDmsAboveContent.providedBy(viewlet.manager))
        self.assertEqual(
            viewlet.contentFilter(),
            {
                "portal_type": "dmsmainfile",
                "sort_on": "getObjPositionInParent",
                "sort_order": "descending",
            },
        )

    def test_render(self):
        # with versions: see test_documentviewer (the latest version is shown in the viewer)
        viewlet = self.viewlet("dms.abovecontent", "dms.files")
        rendered = viewlet.render()
        self.assertIn(
            '<div id="fieldset-versions" style="float:right; width: 50%;">', rendered
        )
        self.assertIn("Versions", rendered)
        self.assertIn("There is no version note for this document.", rendered)
        self.assertNotIn("<table", rendered)
        # the versions script loads the selected version in collective.documentviewer (replaced on Plone 6.2)
        self.assertEqual(viewlet.has_viewer, DocumentViewerView is not None)
        self.assertEqual("DV.load" in rendered, viewlet.has_viewer)

    def test_first_appendix(self):
        viewlet = self.viewlet("dms.abovecontent", "dms.files")
        self.assertIsNone(viewlet.first_appendix())
        # without version, the first appendix (shown in the viewer instead of the latest version)
        first = add_file(
            self.doc, "dmsappendixfile", "plan.html", PLAN, title="Ground floor plan"
        )
        add_file(
            self.doc, "dmsappendixfile", "plan.html", PLAN, title="First floor plan"
        )
        viewlet = self.viewlet("dms.abovecontent", "dms.files")
        self.assertEqual(viewlet.first_appendix().getObject(), first)
        # none when there is a version
        add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        self.assertIsNone(
            self.viewlet("dms.abovecontent", "dms.files").first_appendix()
        )


class TestAppendixViewlet(ViewletsTestCase):

    def test_contentFilter(self):
        viewlet = self.viewlet("dms.belowcontent", "dms.appendix")
        self.assertIsInstance(viewlet, AppendixViewlet)
        self.assertTrue(IDmsBelowContent.providedBy(viewlet.manager))
        self.assertIsInstance(viewlet.table, DmsAppendixTable)
        self.assertEqual(
            viewlet.contentFilter(),
            {
                "portal_type": "dmsappendixfile",
                "sort_on": "getObjPositionInParent",
                "sort_order": "ascending",
            },
        )

    def test_render(self):
        # nothing without appendix
        self.assertEqual(
            self.viewlet("dms.belowcontent", "dms.appendix").render().strip(), ""
        )
        add_file(
            self.doc, "dmsappendixfile", "plan.html", PLAN, title="First floor plan"
        )
        add_file(
            self.doc, "dmsappendixfile", "plan.html", PLAN, title="Ground floor plan"
        )
        rendered = self.viewlet("dms.belowcontent", "dms.appendix").render()
        self.assertIn("<legend>Appendix</legend>", rendered)
        self.assertNotIn("th_header_dms.state", rendered)
        # the latest first, like the versions
        self.assertLess(
            rendered.index("Ground floor plan"), rendered.index("First floor plan")
        )


class TestChangeTitleViewlet(ViewletsTestCase):

    def test_render(self):
        rendered = ChangeTitleViewlet(self.doc, self.request, self.view, None).render()
        self.assertIn(
            "$(\"body.template-dmsincomingmail label[for='form-widgets-IDublinCore-title']\").text('Objet');",
            rendered,
        )
        # its registration is commented out
        manager = getMultiAdapter(
            (self.doc, self.request, self.view),
            IHtmlHeadLinks,
            name="plone.htmlhead.links",
        )
        self.assertIsNone(
            queryMultiAdapter(
                (self.doc, self.request, self.view, manager),
                IViewlet,
                name="dms.changetitle",
            )
        )
