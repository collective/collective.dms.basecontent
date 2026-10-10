# -*- coding: utf-8 -*-
from collective.dms.basecontent.indexers import document_dynamic_searchable_text_indexer
from collective.dms.basecontent.indexers import recipient_groups_indexer
from collective.dms.basecontent.indexers import treating_groups_indexer
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from collective.dms.basecontent.tests.base import add_file
from collective.dms.basecontent.tests.base import LETTER
from collective.dms.basecontent.tests.base import PLAN
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer

import os
import unittest


class TestIndexers(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        self.pc = self.portal.portal_catalog
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(
            self.portal,
            "dmsdocument",
            title="Building permit",
            treating_groups=["Reviewers"],
            recipient_groups=["Site Administrators"],
        )

    def searchable_text(self):
        """The indexed text, whitespace normalized."""
        return " ".join(document_dynamic_searchable_text_indexer(self.doc, self.pc)().split())

    def test_document_dynamic_searchable_text_indexer(self):
        self.assertEqual(self.searchable_text(), "Building permit")
        # the latest version only
        add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        self.assertEqual(self.searchable_text(), "Building permit I request a building permit for my house.")
        add_file(self.doc, "dmsmainfile", "letter.html", PLAN, title="2")
        self.assertEqual(self.searchable_text(), "Building permit Ground floor plan of the house.")
        # the catalog uses this indexer, not the documentviewer one
        self.doc.reindexObject(idxs=["SearchableText"])
        self.assertEqual(len(self.pc(SearchableText="floor", portal_type="dmsdocument")), 1)
        self.assertEqual(len(self.pc(SearchableText="request", portal_type="dmsdocument")), 0)
        # empty files, files without path to text/plain and plain text files are not indexed
        add_file(self.doc, "dmsmainfile", "empty.html", b"", title="3")
        with open(os.path.join(os.path.dirname(__file__), "icon.png"), "rb") as fl:
            add_file(self.doc, "dmsappendixfile", "photo.png", fl.read(), title="Photo")
        # Plone 4 bug: _findPath returns [] (no transform needed) for text/plain, taken as "no path"
        add_file(self.doc, "dmsappendixfile", "note.txt", b"Neighbour agreement", title="Note")
        self.assertEqual(self.searchable_text(), "Building permit Ground floor plan of the house.")
        # Plone 4 bug: an indexed appendix added after the versions hides the latest version
        add_file(self.doc, "dmsappendixfile", "annex.html", LETTER, title="Annex")
        self.assertEqual(self.searchable_text(), "Building permit I request a building permit for my house.")

    def test_treating_groups_indexer(self):
        self.assertEqual(treating_groups_indexer(self.doc, self.pc)(), ["Reviewers"])
        self.assertEqual(self.pc(treating_groups="Reviewers")[0].getObject(), self.doc)
        self.assertEqual(self.pc(treating_groups="Reviewers")[0].treating_groups, ["Reviewers"])
        # contained files do not acquire the value
        mainfile = add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        self.assertIsNone(treating_groups_indexer(mainfile, self.pc)())
        self.assertEqual(len(self.pc(treating_groups="Reviewers")), 1)
        self.assertIsNone(self.pc(UID=mainfile.UID())[0].treating_groups)

    def test_recipient_groups_indexer(self):
        self.assertEqual(recipient_groups_indexer(self.doc, self.pc)(), ["Site Administrators"])
        self.assertEqual(self.pc(recipient_groups="Site Administrators")[0].getObject(), self.doc)
        self.assertEqual(self.pc(recipient_groups="Site Administrators")[0].recipient_groups, ["Site Administrators"])
        # contained files do not acquire the value
        mainfile = add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        self.assertIsNone(recipient_groups_indexer(mainfile, self.pc)())
        self.assertEqual(len(self.pc(recipient_groups="Site Administrators")), 1)
        self.assertIsNone(self.pc(UID=mainfile.UID())[0].recipient_groups)
