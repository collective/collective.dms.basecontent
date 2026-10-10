# -*- coding: utf8 -*-
from plone import api
from plone.app.robotframework.content import Content
from plone.app.robotframework.remote import RemoteLibraryLayer
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.robotframework.utils import disableCSRFProtection
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneWithPackageLayer
from plone.testing.zope import WSGI_SERVER_FIXTURE
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
    # externalEditLink_ of the external editor (Zope imports every product in an instance, Plone 4 PLONE_FIXTURE did)
    additional_z2_products=("Products.ExternalEditor",),
    gs_profile_id="collective.dms.basecontent:testing",
    name="DMS_TESTS_PROFILE",
)

DMS_TESTS_PROFILE_FUNCTIONAL = FunctionalTesting(bases=(DMS_TESTS_PROFILE,), name="DMS_TESTS_PROFILE_FUNCTIONAL")


class CSRFSafeContent(Content):
    """Set field value is aborted by plone.protect on Plone 6 otherwise (Create content disables the check)"""

    def set_field_value(self, uid, field, value, field_type):
        disableCSRFProtection()
        return super(CSRFSafeContent, self).set_field_value(uid, field, value, field_type)


REMOTE_LIBRARY_FIXTURE = RemoteLibraryLayer(
    bases=(PLONE_FIXTURE,),
    libraries=tuple(
        CSRFSafeContent if lib is Content else lib for lib in REMOTE_LIBRARY_BUNDLE_FIXTURE.libraryBases[1:]
    ),
    name="RemoteLibraryBundle:RobotRemote",
)

ACCEPTANCE = FunctionalTesting(
    bases=(DMS_TESTS_PROFILE, REMOTE_LIBRARY_FIXTURE, WSGI_SERVER_FIXTURE), name="ACCEPTANCE"
)
