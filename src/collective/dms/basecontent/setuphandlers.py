def setup_documentviewer(portal):
    from collective.documentviewer.settings import GlobalSettings

    dv_settings = GlobalSettings(portal)
    dv_settings.auto_layout_file_types = ("pdf", "ppt", "word", "rft")
    dv_settings.auto_convert = True
    dv_settings.show_sidebar = False
    dv_settings.show_search = False


def setup_externaleditor(portal):
    from plone import api

    enabled_types = api.portal.get_registry_record(
        'externaleditor.externaleditor_enabled_types',
        default=[u'File', u'Image'],
    )

    if u'dmsappendixfile' not in enabled_types:
        enabled_types.append(u'dmsappendixfile')
        api.portal.set_registry_record(
            'externaleditor.externaleditor_enabled_types',
            enabled_types,
        )

    if u'dmsmainfile' not in enabled_types:
        enabled_types.append(u'dmsmainfile')
        api.portal.set_registry_record(
            'externaleditor.externaleditor_enabled_types',
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
