"""Results of the default profile (profiles/default)."""

from collective.dms.basecontent.dmsdocument import DmsDocument
from collective.dms.basecontent.dmsfile import DmsAppendixFile
from collective.dms.basecontent.dmsfile import DmsFile
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from collective.dms.basecontent.tests.base import add_file
from collective.dms.basecontent.tests.base import LETTER
from collective.dms.basecontent.tests.base import PLAN
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer

import unittest

FILE_BEHAVIORS = (
    "plone.app.content.interfaces.INameFromTitle",
    "plone.app.dexterity.behaviors.metadata.IOwnership",
    "collective.iconifiedcategory.behaviors.iconifiedcategorization.IIconifiedCategorization",
)


class TestDefaultProfile(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.types = self.portal.portal_types
        self.doc = createContentInContainer(self.portal, "dmsdocument", title="Doc 1")

    def object_buttons(self, obj):
        return [
            a["id"]
            for a in self.portal.portal_actions.listFilteredActionsFor(obj)[
                "object_buttons"
            ]
        ]

    def check_file_actions(self, obj):
        """FTI actions of dms files."""
        fti = self.types[obj.portal_type]
        self.assertEqual(
            sorted([a.id for a in fti.listActions()]),
            ["download", "edit", "view", "view_element"],
        )
        download = fti.getActionObject("object_buttons/download")
        self.assertEqual(
            download.getActionExpression(), "string:${object/absolute_url}/@@download"
        )
        self.assertEqual(download.condition.text, "python:object.show_download()")
        self.assertEqual(download.link_target, "_blank")
        self.assertEqual(download.permissions, ("View",))
        view_element = fti.getActionObject("object_buttons/view_element")
        self.assertEqual(
            view_element.getActionExpression(), "string:${object/absolute_url}/view"
        )
        self.assertEqual(view_element.permissions, ("Manage portal",))
        self.assertEqual(fti.getMethodAliases()["(Default)"], "@@display-file")
        buttons = self.object_buttons(obj)
        self.assertIn("download", buttons)
        self.assertIn("view_element", buttons)
        setRoles(self.portal, TEST_USER_ID, ["Editor"])
        self.assertIn("download", self.object_buttons(obj))
        self.assertNotIn("view_element", self.object_buttons(obj))
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_actions(self):
        action = self.portal.portal_actions.object_buttons.external_edit
        self.assertEqual(action.title, "Edit with external application")
        self.assertEqual(action.url_expr, "string:${object_url}/@@external_edit")
        # Plone 6: the image is no longer at the portal root (resolved in test_actionspanel)
        self.assertEqual(
            action.icon_expr,
            "string:${portal_url}/++resource++imio.actionspanel/extedit_icon.png",
        )
        # Plone 6: object/externalEditorEnabled traverses to the view (truthy) instead of calling the skin script
        self.assertEqual(
            action.available_expr, "object/@@externalEditorEnabled/available"
        )
        self.assertEqual(action.permissions, ("Modify portal content",))
        self.assertTrue(action.visible)

    def test_catalog(self):
        catalog = self.portal.portal_catalog
        for name in ("treating_groups", "recipient_groups"):
            index = catalog._catalog.getIndex(name)
            self.assertEqual(index.meta_type, "KeywordIndex")
            self.assertEqual(list(index.getIndexSourceNames()), [name])
            self.assertIn(name, catalog.schema())

    def test_metadata(self):
        setup_tool = self.portal.portal_setup
        self.assertEqual(
            setup_tool.getLastVersionForProfile("collective.dms.basecontent:default"),
            ("4",),
        )
        # the dependencies (collective.documentviewer: see test_documentviewer; collective.z3cform.select2 replaced)
        for profile in (
            "plone.app.dexterity:default",
            "plone.app.relationfield:default",
            "collective.iconifiedcategory:default",
            "imio.actionspanel:default",
            "collective.externaleditor:default",
        ):
            self.assertNotEqual(
                setup_tool.getLastVersionForProfile(profile), "unknown", profile
            )

    def test_registry(self):
        # Plone 4 propertiestool.xml
        self.assertFalse(api.portal.get_registry_record("plone.exposeDCMetaTags"))
        types_not_searched = api.portal.get_registry_record("plone.types_not_searched")
        use_view_action = api.portal.get_registry_record(
            "plone.types_use_view_action_in_listings"
        )
        for portal_type in ("dmsmainfile", "dmsappendixfile"):
            self.assertIn(portal_type, types_not_searched)
            self.assertIn(portal_type, use_view_action)
            # navtree metaTypesNotToList: not a type displayed in the navigation
            self.assertNotIn(
                portal_type, api.portal.get_registry_record("plone.displayed_types")
            )
        # not purged
        self.assertIn("Image", use_view_action)
        self.assertIn("Plone Site", types_not_searched)

    def test_rolemap(self):
        permission = "collective.dms.basecontent: Add DmsFile"
        roles = [
            r["name"]
            for r in self.portal.rolesOfPermission(permission)
            if r["selected"]
        ]
        self.assertEqual(
            set(roles),
            {
                "Owner",
                "Manager",
                "Contributor",
                "Editor",
                "Reviewer",
                "Site Administrator",
            },
        )
        self.assertTrue(self.portal.acquiredRolesAreUsedBy(permission))
        # a member, contributor of a document (not the owner of both documents)
        other = createContentInContainer(self.portal, "dmsdocument", title="Doc 2")
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        for doc in (self.doc, other):
            doc.manage_delLocalRoles([TEST_USER_ID])
        self.doc.manage_setLocalRoles(TEST_USER_ID, ["Contributor"])
        self.assertTrue(api.user.has_permission(permission, obj=self.doc))
        self.assertFalse(api.user.has_permission(permission, obj=other))

    def test_types(self):
        for name in ("dmsdocument", "dmsmainfile", "dmsappendixfile"):
            self.assertEqual(self.types[name].meta_type, "Dexterity FTI")

    def test_type_dmsdocument(self):
        fti = self.types.dmsdocument
        self.assertEqual(
            fti.klass, "collective.dms.basecontent.dmsdocument.DmsDocument"
        )
        self.assertEqual(fti.schema_policy, "schema_policy_dmsdocument")
        self.assertEqual(
            fti.behaviors,
            (
                "plone.app.content.interfaces.INameFromTitle",
                "plone.app.dexterity.behaviors.metadata.IDublinCore",
            ),
        )
        self.assertEqual(
            fti.icon_expr, "string:${portal_url}/++resource++dmsdocument_icon.png"
        )
        self.assertTrue(
            self.portal.restrictedTraverse("++resource++dmsdocument_icon.png")
        )
        self.assertEqual(fti.add_permission, "cmf.AddPortalContent")
        self.assertTrue(fti.global_allow)
        self.assertEqual(fti.default_view, "view")
        self.assertEqual(fti.view_methods, ("view",))
        self.assertTrue(fti.filter_content_types)
        self.assertEqual(
            fti.allowed_content_types,
            (
                "dmsmainfile",
                "dmsappendixfile",
                "information",
                "opinion",
                "task",
                "validation",
            ),
        )
        self.assertEqual([a.id for a in fti.listActions()], ["view", "edit"])
        # a document blocks the local roles inheritance and contains its files
        self.assertIsInstance(self.doc, DmsDocument)
        self.assertTrue(self.doc.__ac_local_roles_block__)
        self.assertEqual(
            sorted([t.getId() for t in self.doc.allowedContentTypes()]),
            ["dmsappendixfile", "dmsmainfile"],
        )

    def test_type_dmsmainfile(self):
        fti = self.types.dmsmainfile
        self.assertEqual(fti.klass, "collective.dms.basecontent.dmsfile.DmsFile")
        self.assertEqual(fti.schema_policy, "schema_policy_dmsfile")
        self.assertEqual(fti.behaviors, FILE_BEHAVIORS)
        self.assertEqual(
            fti.icon_expr, "string:${portal_url}/++resource++dmsmainfile_icon.png"
        )
        self.assertTrue(
            self.portal.restrictedTraverse("++resource++dmsmainfile_icon.png")
        )
        self.assertEqual(fti.add_permission, "collective.dms.basecontent.dmsfile.add")
        self.assertFalse(fti.global_allow)
        self.assertEqual(fti.default_view, "view")
        self.assertIn("view", fti.view_methods)
        self.assertNotIn(
            "dmsmainfile", [t.getId() for t in self.portal.allowedContentTypes()]
        )
        mainfile = add_file(self.doc, "dmsmainfile", "letter.html", LETTER, title="1")
        self.assertIsInstance(mainfile, DmsFile)
        self.assertTrue(mainfile.__ac_local_roles_block__)
        self.check_file_actions(mainfile)

    def test_type_dmsappendixfile(self):
        fti = self.types.dmsappendixfile
        self.assertEqual(
            fti.klass, "collective.dms.basecontent.dmsfile.DmsAppendixFile"
        )
        self.assertEqual(fti.schema_policy, "schema_policy_dmsappendixfile")
        self.assertEqual(
            fti.behaviors,
            FILE_BEHAVIORS[:1]
            + ("plone.app.dexterity.behaviors.metadata.IBasic",)
            + FILE_BEHAVIORS[1:],
        )
        self.assertEqual(
            fti.icon_expr, "string:${portal_url}/++resource++dmsappendixfile_icon.png"
        )
        self.assertTrue(
            self.portal.restrictedTraverse("++resource++dmsappendixfile_icon.png")
        )
        self.assertEqual(fti.add_permission, "cmf.AddPortalContent")
        self.assertFalse(fti.global_allow)
        self.assertEqual(fti.view_methods, ("view",))
        appendix = add_file(
            self.doc, "dmsappendixfile", "plan.html", PLAN, title="Plan"
        )
        self.assertIsInstance(appendix, DmsAppendixFile)
        self.assertTrue(appendix.__ac_local_roles_block__)
        self.check_file_actions(appendix)

    def test_workflows(self):
        workflow_tool = self.portal.portal_workflow
        for portal_type in ("dmsmainfile", "dmsappendixfile"):
            # explicitly bound to no workflow
            self.assertEqual(workflow_tool._chains_by_type[portal_type], ())
        self.assertNotIn("dmsdocument", workflow_tool._chains_by_type)
