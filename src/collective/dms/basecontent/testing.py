# -*- coding: utf8 -*-
from plone import api
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneWithPackageLayer
from zope.globalrequest import setLocal

import collective.dms.basecontent


DMS = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=collective.dms.basecontent,
    gs_profile_id="collective.dms.basecontent:testing",
    name="DMS",
)

# DMS_TESTS_PROFILE = PloneWithPackageLayer(
#     bases=(DMS,),
# )


class DmsLayer(PloneWithPackageLayer):

    def setUpPloneSite(self, portal):
        portal.portal_registration.addMember(id="siteadmin", password="SiteAdm!n0")
        api.group.add_user(groupname="Administrators", username="siteadmin")
        setLocal("request", portal.REQUEST)
        super(DmsLayer, self).setUpPloneSite(portal)


DMS_TESTS_PROFILE = DmsLayer(
    zcml_filename="testing.zcml",
    zcml_package=collective.dms.basecontent,
    # additional_z2_products=("Products.PythonScripts", "imio.dashboard", "imio.dms.mail", "Products.PasswordStrength"),
    gs_profile_id="collective.dms.basecontent:testing",
    name="DMS_TESTS_PROFILE",
)

DMS_TESTS_PROFILE_FUNCTIONAL = FunctionalTesting(bases=(DMS_TESTS_PROFILE,), name="DMS_TESTS_PROFILE_FUNCTIONAL")
