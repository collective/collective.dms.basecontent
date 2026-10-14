"""Robot suites of tests/robot, run with the layer of their file name.

ROBOT_PLONE_MAJOR selects the UI keywords (ui_plone6.robot): robotsuite passes the
ROBOT_* environment variables to the suites as robot variables.
"""

from collective.dms.basecontent.testing import ACCEPTANCE
from importlib.metadata import version
from plone.app.testing import ROBOT_TEST_LEVEL
from plone.testing import layered

import os
import robotsuite
import unittest

try:
    import collective.documentviewer  # noqa: F401
except ImportError:  # replaced on Plone 6
    SKIPPED_SUITES = ("test_documentviewer.robot",)
else:
    SKIPPED_SUITES = ()


# suites needing an optional integration layer, e.g. {'test_facetednav.robot': ADDONS_ACCEPTANCE}
SUITE_LAYERS = {}


def test_suite():
    os.environ.setdefault(
        "ROBOT_PLONE_MAJOR", version("Products.CMFPlone").split(".")[0]
    )
    suite = unittest.TestSuite()
    robot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "robot")
    for name in sorted(os.listdir(robot_dir)):
        if (
            name.startswith("test_")
            and name.endswith(".robot")
            and name not in SKIPPED_SUITES
        ):
            robot_suite = robotsuite.RobotTestSuite(os.path.join("robot", name))
            # not run by a plain bin/test: bin/test --all -t robot
            robot_suite.level = ROBOT_TEST_LEVEL
            suite.addTests(
                [layered(robot_suite, layer=SUITE_LAYERS.get(name, ACCEPTANCE))]
            )
    return suite
