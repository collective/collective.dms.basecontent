# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.dms.basecontent.browser.listing import VersionsTable
from collective.dms.basecontent.browser.viewlets import VersionsViewlet
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from collective.dms.basecontent.tests.base import add_file
from collective.dms.basecontent.tests.base import LETTER
from collective.iconifiedcategory.interfaces import ICategorizedApproved
from collective.iconifiedcategory.interfaces import ICategorizedPrint
from collective.iconifiedcategory.interfaces import ICategorizedSigned
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer

import datetime
import unittest


class TableTestCase(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(self.portal, "dmsdocument", title="Building permit")
        self.version = add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")

    def viewlet(self, doc):
        return VersionsViewlet(doc, self.request, doc.restrictedTraverse("@@view"), None)

    def table(self):
        table = VersionsTable(self.doc, self.request)
        table.portal_type = "dmsmainfile"
        table.update()
        return table


class TestTableViewlet(TableTestCase):

    def test_update(self):
        viewlet = self.viewlet(self.doc)
        viewlet.update()
        self.assertIsInstance(viewlet.table, VersionsTable)
        self.assertEqual(viewlet.table.portal_type, "dmsmainfile")
        self.assertIs(viewlet.table.viewlet, viewlet)
        self.assertEqual([row[0][0].getObject() for row in viewlet.table.rows], [self.version])

    def test__prepare_table_render(self):
        viewlet = self.viewlet(self.doc)
        viewlet.update()
        for interface in (ICategorizedPrint, ICategorizedSigned, ICategorizedApproved):
            self.assertFalse(interface.providedBy(viewlet.table))
        # the outgoing mails (collective.dms.mailcontent type based on dmsdocument) show the print/sign/approve columns
        fti = DexterityFTI("dmsoutgoingmail")
        fti.klass = self.portal.portal_types.dmsdocument.klass
        fti.schema_policy = "schema_policy_dmsdocument"
        self.portal.portal_types._setObject("dmsoutgoingmail", fti)
        outgoing_mail = createContentInContainer(self.portal, "dmsoutgoingmail", title="Reply")
        viewlet = self.viewlet(outgoing_mail)
        viewlet.update()
        for interface in (ICategorizedPrint, ICategorizedSigned, ICategorizedApproved):
            self.assertTrue(interface.providedBy(viewlet.table))


class TestTable(TableTestCase):

    def test_translation_service(self):
        self.assertIs(aq_base(self.table().translation_service), aq_base(self.portal.translation_service))

    def test_wtool(self):
        self.assertIs(aq_base(self.table().wtool), aq_base(self.portal.portal_workflow))

    def test_format_date(self):
        table = self.table()
        self.assertEqual(table.format_date(None), "")
        self.assertEqual(table.format_date(datetime.date(2026, 10, 10)), "Oct 10, 2026")
        self.assertEqual(table.format_date(datetime.datetime(2026, 10, 10, 14, 30)), "Oct 10, 2026")
        self.assertEqual(
            table.format_date(datetime.datetime(2026, 10, 10, 14, 30), long_format=True), "Oct 10, 2026 02:30 PM"
        )
        self.assertEqual(table.format_date(datetime.datetime(2026, 10, 10, 14, 30), time_only=True), "02:30 PM")
        self.assertEqual(table.format_date(DateTime("2026/10/10 14:30")), "Oct 10, 2026")

    def test_renderRow(self):
        self.portal.portal_workflow.setChainForPortalTypes(("dmsmainfile",), ("simple_publication_workflow",))
        self.version = add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="2")
        table = self.table()
        rendered = table.render()
        self.assertIn('\n    <tr class="even">', rendered)
        self.assertIn('<td class="td_cell_dms.state"></td>', rendered)
        # Plone 4 bug: the categorized elements have no review_state, so no state class nor state title
        self.assertNotIn("row-state", rendered)
        # with catalog brains (the state column only), the row gets the state class
        brain = self.portal.portal_catalog(UID=self.version.UID())[0]
        row = [(brain, column, colspan) for item, column, colspan in table.rows[0] if column.__name__ == "dms.state"]
        rendered = table.renderRow(row, "even")
        self.assertTrue(rendered.startswith('\n    <tr class="even row-state-private">'))
        self.assertIn('<td class="td_cell_dms.state">Private</td>', rendered)
        # the selected rows
        table.cssClassSelected = "selected"
        table.selectedItems = [brain]
        rendered = table.renderRow(row)
        self.assertTrue(rendered.startswith('\n    <tr class="selected row-state-private">'))
