from collective.dms.basecontent.source import CategoryVocabulary
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.testing.zope import Browser
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import transaction
import unittest


class SourceTestCase(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = createContentInContainer(self.portal, "dmsdocument", title="Doc 1")


class TestCategoryVocabulary(SourceTestCase):

    def test__get_categories(self):
        factory = getUtility(
            IVocabularyFactory, "collective.iconifiedcategory.categories"
        )
        self.assertIsInstance(factory, CategoryVocabulary)
        # no config: a default category is created
        self.assertNotIn("contentcategory-configuration", self.portal)
        categories = CategoryVocabulary()._get_categories(self.doc)
        self.assertEqual(
            [c.absolute_url_path() for c in categories],
            [
                "/plone/contentcategory-configuration/default-category-group/default-category"
            ],
        )
        # the existing config is used
        self.assertEqual(CategoryVocabulary()._get_categories(self.doc), categories)
        self.assertEqual(
            self.portal["contentcategory-configuration"].objectIds(),
            ["default-category-group"],
        )
        vocabulary = getUtility(
            IVocabularyFactory, "collective.iconifiedcategory.categories"
        )(self.doc)
        self.assertEqual(
            [(t.token, t.title) for t in vocabulary],
            [
                (
                    "plone-contentcategory-configuration_-_default-category-group_-_default-category",
                    "Default Category",
                )
            ],
        )

    def test_create_default_category(self):
        category = CategoryVocabulary().create_default_category()
        config = self.portal["contentcategory-configuration"]
        self.assertEqual(config.portal_type, "ContentCategoryConfiguration")
        self.assertEqual(config.Title(), "Content Category Configuration")
        self.assertTrue(config.exclude_from_nav)
        group = config["default-category-group"]
        self.assertEqual(group.portal_type, "ContentCategoryGroup")
        self.assertEqual(group.Title(), "Default Category Group")
        self.assertEqual(category, group["default-category"])
        self.assertEqual(category.portal_type, "ContentCategory")
        self.assertEqual(category.Title(), "Default Category")
        self.assertEqual(category.icon.filename, "icon.png")
        self.assertEqual(category.icon.contentType, "image/png")
        # Plone 6: done by the GET of a file add form, not blocked by the plone.protect auto CSRF check
        api.content.delete(config)
        transaction.commit()
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )
        browser.open(self.doc.absolute_url() + "/++add++dmsmainfile")
        self.assertNotIn("Confirming User Action", browser.contents)
        self.assertIn('id="form-widgets-title"', browser.contents)
        self.assertIn(
            "default-category",
            self.portal["contentcategory-configuration"]["default-category-group"],
        )
