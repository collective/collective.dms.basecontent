from collective.dms.basecontent.setuphandlers import setup_externaleditor
from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from plone import api

import unittest

RECORD = "externaleditor.externaleditor_enabled_types"


class TestSetuphandlers(unittest.TestCase):

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_setup_externaleditor(self):
        # done at install
        self.assertEqual(
            api.portal.get_registry_record(RECORD),
            ["File", "Image", "dmsappendixfile", "dmsmainfile"],
        )
        api.portal.set_registry_record(RECORD, ["File", "dmsmainfile"])
        setup_externaleditor(self.portal)
        self.assertEqual(
            api.portal.get_registry_record(RECORD),
            ["File", "dmsmainfile", "dmsappendixfile"],
        )
        # no duplicate
        setup_externaleditor(self.portal)
        self.assertEqual(
            api.portal.get_registry_record(RECORD),
            ["File", "dmsmainfile", "dmsappendixfile"],
        )

    def test_importFinalSteps(self):
        api.portal.set_registry_record(RECORD, ["File"])
        setup_tool = self.portal.portal_setup
        # the step does nothing for another profile (no marker file)
        setup_tool.runImportStepFromProfile(
            "profile-collective.dms.basecontent:testing",
            "collective.dms.basecontent-final",
            run_dependencies=False,
        )
        self.assertEqual(api.portal.get_registry_record(RECORD), ["File"])
        setup_tool.runImportStepFromProfile(
            "profile-collective.dms.basecontent:default",
            "collective.dms.basecontent-final",
            run_dependencies=False,
        )
        self.assertEqual(
            api.portal.get_registry_record(RECORD),
            ["File", "dmsappendixfile", "dmsmainfile"],
        )
