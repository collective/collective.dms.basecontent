# -*- coding: utf-8 -*-
from collective.dms.basecontent.browser.column import DateColumn
from collective.dms.basecontent.browser.column import get_value
from collective.dms.basecontent.browser.column import LabelColumn
from collective.dms.basecontent.browser.column import StateColumn
from collective.dms.basecontent.browser.listing import VersionsTable
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from collective.dms.basecontent.tests.base import add_file
from collective.dms.basecontent.tests.base import LETTER
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer

import unittest


class ColumnTestCase(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.pc = self.portal.portal_catalog
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(self.portal, "dmsdocument", title="Building permit", notes="Urgent")
        self.version = add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        self.table = VersionsTable(self.doc, self.request)
        self.table.portal_type = "dmsmainfile"
        self.table.update()
        # the versions listing item
        self.item = self.table.values[0]

    def brain(self, obj):
        return self.pc(UID=obj.UID())[0]


class TestColumn(ColumnTestCase):
    """Module functions"""

    def test_get_value(self):
        brain = self.brain(self.doc)
        # catalog metadata
        self.assertEqual(get_value(brain, "portal_type"), "dmsdocument")
        # missing metadata value
        self.assertEqual(get_value(brain, "getRemoteUrl", "default"), "default")
        # not a metadata: from the object, called if callable
        self.assertEqual(get_value(brain, "notes"), "Urgent")
        self.assertEqual(get_value(brain, "absolute_url"), "http://nohost/plone/building-permit")
        self.assertEqual(get_value(brain, "unknown", "default"), "default")
        # categorized content
        self.assertEqual(get_value(self.item, "portal_type"), "dmsmainfile")
        self.assertEqual(get_value(self.item, "title"), "1")
        self.assertIsNone(get_value(self.item, "review_state"))


class TestDateColumn(ColumnTestCase):

    def test_renderCell(self):
        self.version.setModificationDate(DateTime("2026/09/15 14:30"))
        self.version.reindexObject(idxs=["modified"])
        column = DateColumn(self.doc, self.request, self.table)
        column.attribute = "modified"
        self.assertEqual(column.renderCell(self.item), "Sep 15, 2026")
        self.assertEqual(column.renderCell(self.brain(self.version)), "Sep 15, 2026")
        column.attribute = "unknown"
        self.assertEqual(column.renderCell(self.item), "")


class TestStateColumn(ColumnTestCase):

    def test_renderCell(self):
        column = StateColumn(self.doc, self.request, self.table)
        # no workflow
        self.assertEqual(column.renderCell(self.item), "")
        self.assertEqual(column.renderCell(self.brain(self.doc)), "")
        self.portal.portal_workflow.setChainForPortalTypes(("dmsdocument",), ("simple_publication_workflow",))
        doc = createContentInContainer(self.portal, "dmsdocument", title="Reply")
        self.assertEqual(column.renderCell(self.brain(doc)), "Private")


class TestLabelColumn(ColumnTestCase):

    def test_renderCell(self):
        column = LabelColumn(self.doc, self.request, self.table)
        column.attribute = "label"
        self.assertEqual(column.renderCell(self.item), "")
        self.version.label = "Sent version"
        self.assertEqual(column.renderCell(self.item), "Sent version")
