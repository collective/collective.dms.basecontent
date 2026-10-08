from collective.dms.basecontent.dmsfile import IDmsFile
from collective.dms.basecontent.dmsfile import titleDefaultValue
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestDmsFile(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(self.portal, "dmsdocument", title="Doc 1")
        # dms files are categorized: the categories vocabulary creates the config
        getUtility(IVocabularyFactory, "collective.iconifiedcategory.categories")(self.doc)

    def test_titleDefaultValue(self):
        self.assertEqual(titleDefaultValue(self.doc), u"1")
        createContentInContainer(self.doc, "dmsmainfile", title="1")
        self.assertEqual(titleDefaultValue(self.doc), u"2")
        # the add form validates the default of the title field
        IDmsFile["title"].bind(self.doc).validate(titleDefaultValue(self.doc))
