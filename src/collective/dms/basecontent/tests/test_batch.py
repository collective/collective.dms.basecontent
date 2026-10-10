# -*- coding: utf-8 -*-
from collective.dms.basecontent.browser.batch import BootstrapPloneBatchProvider
from collective.dms.basecontent.browser.batch import PloneBatchProvider
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.batching import Batch
from plone.dexterity.utils import createContentInContainer
from z3c.table.interfaces import IBatchProvider
from z3c.table.table import Table
from zope.component import getMultiAdapter

import unittest


class DocumentsTable(Table):
    """A table listing documents in a Plone batch."""

    batchProviderName = "plonebatch"
    values = None


class BatchTestCase(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request.form.clear()
        self.request["ACTUAL_URL"] = "http://nohost/plone/documents"
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        for i in range(5):
            createContentInContainer(self.portal, "dmsdocument", title="Doc %d" % i)

    def table(self, size=2, start=0):
        table = DocumentsTable(self.portal, self.request)
        brains = self.portal.portal_catalog(portal_type="dmsdocument", sort_on="sortable_title")
        table.values = Batch(brains, size, start)
        return table


class TestPloneBatchProvider(BatchTestCase):

    def test_render(self):
        table = self.table(start=2)
        provider = getMultiAdapter((self.portal, self.request, table), IBatchProvider, name="plonebatch")
        self.assertIsInstance(provider, PloneBatchProvider)
        self.assertEqual(
            provider.render(),
            '<div class="listingBar">\n'
            '<a href="http://nohost/plone/documents?b_start:int=0" class="previous">&laquo;</a>\n'
            '<a href="http://nohost/plone/documents?b_start:int=4" class="next">&raquo;</a>\n'
            '<a href="http://nohost/plone/documents?b_start:int=0">1</a>\n'
            '<span class="current">2</span>\n'
            '<a href="http://nohost/plone/documents?b_start:int=4">3</a>\n'
            "</div>",
        )
        # one page (5 / 10 is 0 with the Python 2 integer division)
        self.assertEqual(PloneBatchProvider(self.portal, self.request, self.table(size=5)).render(), "")
        self.assertEqual(PloneBatchProvider(self.portal, self.request, self.table(size=10)).render(), "")
        # the last page
        rendered = PloneBatchProvider(self.portal, self.request, self.table(size=1, start=4)).render()
        self.assertIn('<a href="http://nohost/plone/documents?b_start:int=0" class="first">1</a>\n', rendered)
        self.assertIn('<span class="current">5</span>\n</div>', rendered)
        self.assertNotIn('class="next"', rendered)

    def test_renderCurrentBatchLink(self):
        provider = PloneBatchProvider(self.portal, self.request, self.table())
        self.assertEqual(provider.renderCurrentBatchLink(2, "current"), '<span class="current">2</span>')

    def test_renderBatchLink(self):
        provider = PloneBatchProvider(self.portal, self.request, self.table())
        self.assertEqual(
            provider.renderBatchLink(3, "next", text="&raquo;"),
            '<a href="http://nohost/plone/documents?b_start:int=4" class="next">&raquo;</a>',
        )
        # the request parameters are kept (in any order)
        self.request.form["SearchableText"] = "permit"
        self.request.form["b_size"] = "2"
        link = provider.renderBatchLink(3)
        self.assertTrue(link.startswith('<a href="http://nohost/plone/documents?'))
        self.assertTrue(link.endswith('">3</a>'))
        self.assertEqual(
            sorted(link[len('<a href="http://nohost/plone/documents?') : -len('">3</a>')].split("&")),
            ["SearchableText=permit", "b_size=2", "b_start:int=4"],
        )
        # or only the batch form keys, as data-query
        provider.batchformkeys = ["SearchableText", "sort_on"]
        link = provider.renderBatchLink(1)
        self.assertTrue(link.startswith('<a data-query="'))
        query = link[len('<a data-query="') : -len('">1</a>')]
        self.assertEqual(sorted(query.split("&")), ["SearchableText=permit", "b_start:int=0"])


class TestBootstrapPloneBatchProvider(BatchTestCase):

    def test_renderBatchLink(self):
        provider = BootstrapPloneBatchProvider(self.portal, self.request, self.table())
        self.assertEqual(
            provider.renderBatchLink(2, "next", text="&raquo;"),
            '<li class="next"><a href="http://nohost/plone/documents?b_start:int=2">&raquo;</a></li>',
        )
        self.assertEqual(
            provider.render(),
            '<div class="pagination"><ul class="pager">\n'
            '<li class="active"><a href="#">1</a></li>\n'
            '<li><a href="http://nohost/plone/documents?b_start:int=2">2</a></li>\n'
            '<li><a href="http://nohost/plone/documents?b_start:int=4">3</a></li>\n'
            '<li class="next"><a href="http://nohost/plone/documents?b_start:int=2">&raquo;</a></li>\n'
            "</ul></div>",
        )

    def test_renderCurrentBatchLink(self):
        provider = BootstrapPloneBatchProvider(self.portal, self.request, self.table())
        self.assertEqual(provider.renderCurrentBatchLink(2, "active"), '<li class="active"><a href="#">2</a></li>')
