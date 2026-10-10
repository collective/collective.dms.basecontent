# -*- coding: utf-8 -*-
from collective.dms.basecontent.browser.actionspanel import DmsFileActionsPanelView
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from collective.dms.basecontent.tests.base import add_file
from collective.dms.basecontent.tests.base import LETTER
from collective.dms.basecontent.tests.base import PLAN
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile

import re
import unittest


class TestDmsFileActionsPanelView(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(self.portal, "dmsdocument", title="Building permit")

    def test___init__(self):
        mainfile = add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        appendix = add_file(self.doc, "dmsappendixfile", "plan.html", PLAN, title="Plan")
        for obj in (mainfile, appendix):
            view = obj.restrictedTraverse("@@actions_panel")
            self.assertIsInstance(view, DmsFileActionsPanelView)
            self.assertEqual(view.ACCEPTABLE_ACTIONS, ["edit", "external_edit", "delete", "download"])
            # the object buttons are filtered (no view_element, cut, copy, rename)
            self.assertEqual([action["id"] for action in view.listObjectButtonsActions()], ["delete", "download"])
            rendered = view()
            self.assertIn("%s/@@download" % obj.absolute_url(), rendered)
            self.assertIn("%s/edit" % obj.absolute_url(), rendered)
            self.assertIn("%s/delete_confirmation" % obj.absolute_url(), rendered)
            self.assertNotIn("%s/view" % obj.absolute_url(), rendered)
        # the action icons resolve (Plone 6: download icon name, external editor image of imio.actionspanel)
        api.user.get_current().setMemberProperties({"ext_editor": True})
        api.portal.set_registry_record("externaleditor.ext_editor", True)
        mainfile.file = NamedBlobFile(LETTER, filename="letter.odt")
        view = mainfile.restrictedTraverse("@@actions_panel")
        self.assertEqual(
            [action["id"] for action in view.listObjectButtonsActions()], ["delete", "external_edit", "download"]
        )
        icons = re.findall(r'class="apButtonAction_form_(\w+)"[^>]*>\s*<img src="([^"]+)"', view())
        portal_url = self.portal.absolute_url()
        self.assertEqual(
            icons,
            [
                ("delete", portal_url + "/++plone++bootstrap-icons/trash.svg"),
                ("external_edit", portal_url + "/++resource++imio.actionspanel/extedit_icon.png"),
                ("download", portal_url + "/++plone++bootstrap-icons/download.svg"),
            ],
        )
        for action_id, url in icons:
            self.assertTrue(self.portal.unrestrictedTraverse(url[len(portal_url) + 1 :]), action_id)
