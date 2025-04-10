# -*- coding: utf8 -*-

from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneWithPackageLayer

import collective.dms.basecontent


DMS = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=collective.dms.basecontent,
    gs_profile_id="collective.dms.basecontent:testing",
    name="DMS",
)

DMS_TESTS_PROFILE = PloneWithPackageLayer(
    bases=(DMS,),
    zcml_filename="testing.zcml",
    zcml_package=collective.dms.basecontent,
    gs_profile_id="collective.dms.basecontent:testing",
    name="DMS_TESTS_PROFILE",
)

DMS_TESTS_PROFILE_FUNCTIONAL = FunctionalTesting(bases=(DMS_TESTS_PROFILE,), name="DMS_TESTS_PROFILE_FUNCTIONAL")
