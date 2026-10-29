from collective.dms.basecontent.dmsfile import DmsAppendixFileSchemaPolicy
from collective.dms.basecontent.dmsfile import DmsFileSchemaPolicy
from collective.dms.basecontent.dmsfile import IDmsAppendixFile
from collective.dms.basecontent.dmsfile import IDmsFile
from collective.dms.basecontent.dmsfile import titleDefaultValue
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from collective.dms.basecontent.tests.base import add_file
from collective.dms.basecontent.tests.base import LETTER
from collective.dms.basecontent.tests.base import PLAN
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

import unittest


class DmsFileTestCase(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(self.portal, "dmsdocument", title="Doc 1")

    def add_form(self, portal_type):
        form = self.doc.restrictedTraverse("++add++%s" % portal_type).form_instance
        form.update()
        return form


class TestDmsFile(DmsFileTestCase):

    def test_Title(self):
        mainfile = add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        self.assertEqual(mainfile.Title(), "1")
        # the scan of an incoming mail
        mainfile.incomingmail = True
        self.assertEqual(mainfile.Title(), "Incoming mail")
        # a version signed with the iconified "signed" action
        mainfile.incomingmail = False
        mainfile.signed = True
        self.assertEqual(mainfile.Title(), "Signed version")
        mainfile.signed = False
        self.assertEqual(mainfile.Title(), "1")


class TestDmsFileSchemaPolicy(DmsFileTestCase):

    def test_bases(self):
        self.assertEqual(DmsFileSchemaPolicy().bases("dmsmainfile", None), (IDmsFile,))
        schema = getUtility(IDexterityFTI, name="dmsmainfile").lookupSchema()
        self.assertTrue(schema.isOrExtends(IDmsFile))
        # the add form shows the version number, hides the label and the description
        form = self.add_form("dmsmainfile")
        self.assertEqual(form.widgets["title"].label, "Version number")
        self.assertEqual(form.widgets["label"].mode, "hidden")
        self.assertEqual(form.widgets["description"].mode, "hidden")
        self.assertEqual(form.widgets["file"].mode, "input")


class TestDmsAppendixFileSchemaPolicy(DmsFileTestCase):

    def test_bases(self):
        self.assertEqual(
            DmsAppendixFileSchemaPolicy().bases("dmsappendixfile", None),
            (IDmsAppendixFile,),
        )
        schema = getUtility(IDexterityFTI, name="dmsappendixfile").lookupSchema()
        self.assertTrue(schema.isOrExtends(IDmsAppendixFile))
        self.assertFalse(schema.isOrExtends(IDmsFile))
        # the title of the schema is hidden, the IBasic behavior one is shown
        form = self.add_form("dmsappendixfile")
        self.assertEqual(form.widgets["title"].mode, "hidden")
        self.assertEqual(form.widgets["description"].mode, "hidden")
        self.assertEqual(form.widgets["IBasic.title"].mode, "input")


class TestDmsfile(DmsFileTestCase):
    """Module functions"""

    def test_titleDefaultValue(self):
        # fixed on Plone 6 (Plone 4 bug: the @default_value adapter was not grokked and returned an int)
        form = self.add_form("dmsmainfile")
        self.assertEqual(form.widgets["title"].value, "1")
        self.assertEqual(titleDefaultValue(self.doc), "1")
        # the add form validates the default of the title field
        IDmsFile["title"].bind(self.doc).validate(titleDefaultValue(self.doc))
        add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        self.assertEqual(titleDefaultValue(self.doc), "2")
        self.assertEqual(self.add_form("dmsmainfile").widgets["title"].value, "2")
        # an appendix is not a version
        add_file(self.doc, "dmsappendixfile", "plan.html", PLAN, title="Plan")
        self.assertEqual(titleDefaultValue(self.doc), "2")

    def test_update_higher_version(self):
        annotations = IAnnotations(self.doc)
        self.assertNotIn("higher_version", annotations)
        first = add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        self.assertEqual(annotations["higher_version"].value, 1)
        add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="2")
        self.assertEqual(annotations["higher_version"].value, 2)
        add_file(self.doc, "dmsappendixfile", "plan.html", PLAN, title="Plan")
        self.assertEqual(annotations["higher_version"].value, 2)
        # a deleted version keeps its number used
        self.doc.manage_delObjects([first.getId()])
        self.assertEqual(annotations["higher_version"].value, 2)
