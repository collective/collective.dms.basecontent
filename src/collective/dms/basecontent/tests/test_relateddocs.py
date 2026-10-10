# -*- coding: utf-8 -*-
from collective.dms.basecontent.dmsdocument import IDmsDocument
from collective.dms.basecontent.relateddocs import RelatedDocsFieldWidget
from collective.dms.basecontent.relateddocs import RelatedDocsWidget
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.utils import createContentInContainer
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
from zope.security.management import endInteraction
from zope.security.management import newInteraction

import unittest


class RelatedDocsTestCase(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        # the publisher opens a security interaction, needed by the widget
        newInteraction()
        self.addCleanup(endInteraction)
        self.doc1 = createContentInContainer(self.portal, "dmsdocument", title="Doc 1")
        self.doc2 = createContentInContainer(self.portal, "dmsdocument", title="Doc 2")
        self.doc3 = createContentInContainer(self.portal, "dmsdocument", title="Doc 3")
        self.doc4 = createContentInContainer(self.portal, "dmsdocument", title="Doc 4")
        # doc1 refers to doc2, doc3 refers to doc1, as the edit form saves it
        self.relate(self.doc1, self.doc2)
        self.relate(self.doc3, self.doc1)

    def relate(self, source, *targets):
        intids = getUtility(IIntIds)
        source.related_docs = [RelationValue(intids.getId(target)) for target in targets]
        notify(ObjectModifiedEvent(source))

    def widget(self, doc, view_name="view"):
        """The related_docs widget of the document view or edit form."""
        view = doc.restrictedTraverse(view_name)
        view = getattr(view, "form_instance", view)
        view.update()
        return view.widgets["related_docs"]


class TestRelatedDocsWidget(RelatedDocsTestCase):

    def test_render(self):
        # display mode: the links, also for a document with only back references
        self.assertIsInstance(self.widget(self.doc1), RelatedDocsWidget)
        self.assertTrue(self.widget(self.doc1).display_backrefs)
        self.assertIn('<a href="%s">Doc 1</a>' % self.doc1.absolute_url(), self.widget(self.doc2).render())
        self.assertNotIn("<a ", self.widget(self.doc4).render())
        # input mode: the plone.app.z3cform related items widget, without back references
        widget = self.widget(self.doc2, "@@edit")
        self.assertIsInstance(widget, RelatedDocsWidget)
        self.assertIn("pat-relateditems", widget.render())
        self.assertNotIn("Doc 1", widget.render())

    def test_update(self):
        # display mode: no pattern class, mockup would hide the links behind an empty related items widget
        self.assertNotIn("pat-relateditems", self.widget(self.doc1).klass)
        self.assertNotIn("pat-relateditems", self.widget(self.doc1).render())
        # input mode: the pattern class
        self.assertIn("pat-relateditems", self.widget(self.doc1, "@@edit").klass)

    def test_tuples(self):
        # its references, then its back references
        self.assertEqual(
            self.widget(self.doc1).tuples(),
            [(self.doc2.absolute_url(), "Doc 2"), (self.doc3.absolute_url(), "Doc 3")],
        )
        self.assertEqual(self.widget(self.doc2).tuples(), [(self.doc1.absolute_url(), "Doc 1")])
        self.assertEqual(self.widget(self.doc4).tuples(), [])
        # a mutual reference is listed once
        self.relate(self.doc2, self.doc1)
        self.assertEqual(self.widget(self.doc2).tuples(), [(self.doc1.absolute_url(), "Doc 1")])
        # back references from documents the user cannot view are hidden (doc3 is private, as a workflow sets it)
        self.doc3.manage_permission("View", ["Manager"], acquire=False)
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, TEST_USER_NAME)
        self.assertEqual(self.widget(self.doc1).tuples(), [(self.doc2.absolute_url(), "Doc 2")])
        # the document view lists the links, although the field of doc2 is empty
        self.assertIn('<a href="%s">Doc 1</a>' % self.doc1.absolute_url(), self.doc2.restrictedTraverse("@@view")())


class TestRelateddocs(RelatedDocsTestCase):
    """Module functions"""

    def test_RelatedDocsFieldWidget(self):
        field = IDmsDocument["related_docs"]
        widget = RelatedDocsFieldWidget(field, self.request)
        self.assertIsInstance(widget, RelatedDocsWidget)
        self.assertEqual(widget.field, field)
        self.assertTrue(widget.display_backrefs)
