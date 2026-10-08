from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent

import unittest


class TestRelatedDocsWidget(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc1 = createContentInContainer(self.portal, "dmsdocument", title="Doc 1")
        self.doc2 = createContentInContainer(self.portal, "dmsdocument", title="Doc 2")
        self.doc3 = createContentInContainer(self.portal, "dmsdocument", title="Doc 3")
        # doc1 refers to doc2, doc3 refers to doc1
        intids = getUtility(IIntIds)
        self.doc1.related_docs = [RelationValue(intids.getId(self.doc2))]
        notify(ObjectModifiedEvent(self.doc1))
        self.doc3.related_docs = [RelationValue(intids.getId(self.doc1))]
        notify(ObjectModifiedEvent(self.doc3))

    def _widget(self, doc):
        view = doc.restrictedTraverse("@@view")
        view.update()
        return view.widgets["related_docs"]

    def test_tuples(self):
        # its references, then its back references
        self.assertEqual(
            self._widget(self.doc1).tuples(),
            [(self.doc2.absolute_url(), "Doc 2"), (self.doc3.absolute_url(), "Doc 3")],
        )
        self.assertEqual(self._widget(self.doc2).tuples(), [(self.doc1.absolute_url(), "Doc 1")])

    def test_render(self):
        rendered = self._widget(self.doc2).render()
        self.assertIn('<a href="%s">Doc 1</a>' % self.doc1.absolute_url(), rendered)

    def test_view(self):
        # the back reference is displayed in the document view, although the field of doc2 is empty
        rendered = self.doc2.restrictedTraverse("@@view")()
        self.assertIn('<a href="%s">Doc 1</a>' % self.doc1.absolute_url(), rendered)
