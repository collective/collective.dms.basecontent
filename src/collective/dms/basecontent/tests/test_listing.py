from collective.dms.basecontent.browser.listing import DmsAppendixTable
from collective.dms.basecontent.browser.listing import StateColumn
from collective.dms.basecontent.browser.listing import UpdateColumn
from collective.dms.basecontent.browser.listing import VersionLabelColumn
from collective.dms.basecontent.browser.listing import VersionsTable
from collective.dms.basecontent.browser.listing import VersionsTitleColumn
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from collective.dms.basecontent.tests.base import add_file
from collective.dms.basecontent.tests.base import LETTER
from collective.dms.basecontent.tests.base import PLAN
from collective.iconifiedcategory.browser.tabview import CategorizedContent
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import unittest


class ListingTestCase(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(
            self.portal, "dmsdocument", title="Building permit"
        )
        self.version1 = add_file(
            self.doc, "dmsmainfile", "letter.html", LETTER, title="1"
        )
        self.appendix = add_file(
            self.doc, "dmsappendixfile", "plan.html", PLAN, title="Plan"
        )
        self.version2 = add_file(
            self.doc, "dmsmainfile", "letter.html", LETTER, title="2"
        )

    def table(self, klass=VersionsTable, portal_type="dmsmainfile"):
        """The table as its viewlet updates it."""
        table = klass(self.doc, self.request)
        table.portal_type = portal_type
        table.update()
        return table

    def column(self, table, name):
        return [column for column in table.columns if column.__name__ == name][0]


class TestVersionsTable(ListingTestCase):

    def test_values(self):
        table = self.table()
        # the latest version first
        self.assertEqual(
            [item.getObject() for item in table.values], [self.version2, self.version1]
        )
        self.assertIsInstance(table.values[0], CategorizedContent)
        self.assertEqual(
            table.cssClasses, {"table": "listing nosort dv iconified-listing"}
        )
        self.assertEqual(
            [
                item.getObject()
                for item in self.table(portal_type="dmsappendixfile").values
            ],
            [self.appendix],
        )
        # stored on the table
        add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="3")
        self.assertEqual(len(table.values), 2)
        self.assertEqual(len(self.table().values), 3)


class TestDmsAppendixTable(ListingTestCase):

    def test_setUpColumns(self):
        names = [
            "title-column",
            "last-modification-column",
            "dms.state",
            "author-column",
            "filesize-column",
            "action-column",
        ]
        # the iconifiedcategory category and creation date columns are removed
        self.assertEqual([column.__name__ for column in self.table().columns], names)
        names.remove("dms.state")
        self.assertEqual(
            [
                column.__name__
                for column in self.table(DmsAppendixTable, "dmsappendixfile").columns
            ],
            names,
        )


class TestVersionsTitleColumn(ListingTestCase):

    def test_renderCell(self):
        self.maxDiff = None
        table = self.table()
        self.version2.title = "2 <signed>"
        self.version2.description = "Sent & signed"
        notify(ObjectModifiedEvent(self.version2))
        item = self.table().values[0]
        # Plone 4 bug: not registered since the iconified table refactor, the iconifiedcategory title column is used
        self.assertNotIsInstance(
            self.column(table, "title-column"), VersionsTitleColumn
        )
        column = VersionsTitleColumn(self.doc, self.request, table)
        self.assertEqual(
            column.renderCell(item),
            '<a class="version-link" href="%s" alt="2 &lt;signed&gt;" title="2 &lt;signed&gt;">'
            '<img src="%s" alt="Default Category" title="Default Category" /> 2 &lt;signed&gt;</a>'
            '<p class="discreet">Sent &amp; signed</p>'
            % (self.version2.absolute_url(), item.icon_url),
        )


class TestUpdateColumn(ListingTestCase):

    def test_renderCell(self):
        self.version2.setModificationDate(DateTime("2026/09/15 14:30"))
        table = self.table()
        column = self.column(table, "last-modification-column")
        self.assertIsInstance(column, UpdateColumn)
        self.assertEqual(column.header, "listingheader_modified")
        self.assertEqual(column.renderCell(table.values[0]), "Sep 15, 2026")


class TestStateColumn(ListingTestCase):

    def test_renderCell(self):
        table = self.table()
        column = self.column(table, "dms.state")
        self.assertIsInstance(column, StateColumn)
        self.assertEqual(column.weight, 45)
        # the dms files have no workflow
        self.assertEqual(column.renderCell(table.values[0]), "")


class TestVersionLabelColumn(ListingTestCase):

    def test_renderCell(self):
        table = self.table()
        # Plone 4 bug: registered for tables providing VersionLabelColumn, the column is never displayed
        self.assertNotIn("dms.label", [column.__name__ for column in table.columns])
        column = VersionLabelColumn(self.doc, self.request, table)
        self.assertEqual(column.renderCell(table.values[0]), "")
        self.version2.label = "Sent version"
        self.assertEqual(column.renderCell(table.values[0]), "Sent version")
