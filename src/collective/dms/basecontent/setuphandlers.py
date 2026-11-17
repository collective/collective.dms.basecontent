try:
    from collective.documentviewer.settings import GlobalSettings
except ImportError:  # collective.documentviewer is not available on Plone 6.2
    GlobalSettings = None


def setup_documentviewer(portal):
    if GlobalSettings is None:
        return
    dv_settings = GlobalSettings(portal)
    dv_settings.auto_layout_file_types = ("pdf", "ppt", "word", "rft")
    dv_settings.auto_convert = True
    dv_settings.show_sidebar = False
    dv_settings.show_search = False


def setup_externaleditor(portal):
    from plone import api

    enabled_types = api.portal.get_registry_record(
        "externaleditor.externaleditor_enabled_types",
        default=["File", "Image"],
    )

    if "dmsappendixfile" not in enabled_types:
        enabled_types.append("dmsappendixfile")
        api.portal.set_registry_record(
            "externaleditor.externaleditor_enabled_types",
            enabled_types,
        )

    if "dmsmainfile" not in enabled_types:
        enabled_types.append("dmsmainfile")
        api.portal.set_registry_record(
            "externaleditor.externaleditor_enabled_types",
            enabled_types,
        )


def importFinalSteps(context):
    """Import all final steps."""
    marker = context.readDataFile("collective_dms_basecontent_marker.txt")
    if marker is None:
        return

    site = context.getSite()
    setup_documentviewer(site)
    setup_externaleditor(site)
