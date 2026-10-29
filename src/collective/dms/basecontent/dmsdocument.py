from collective.dms.basecontent import _
from collective.dms.basecontent.relateddocs import RelatedDocsFieldWidget
from dexterity.localrolesfield.field import LocalRolesField
from imio.helpers.content import object_values
from plone.app.z3cform.widgets.select import Select2Widget as BaseSelect2Widget
from plone.autoform import directives as form
from plone.dexterity.content import Container
from plone.dexterity.schema import DexteritySchemaPolicy
from plone.supermodel import model
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implementer


class Select2Widget(BaseSelect2Widget):
    """Select2 widget without its pattern in display mode."""

    def update(self):
        super().update()
        if self.mode == DISPLAY_MODE:
            # added in every mode by plone.app.z3cform: mockup would initialise select2 on the display span
            self.klass = " ".join(c for c in self.klass.split() if c != "pat-select2")


@implementer(IFieldWidget)
def Select2FieldWidget(field, request):
    return FieldWidget(field, Select2Widget(request))


class IDmsDocument(model.Schema):
    """Schema for DmsDocument"""

    notes = schema.Text(
        title=_("Notes"),
        required=False,
    )

    treating_groups = LocalRolesField(
        title=_("Treating groups"),
        required=False,
        value_type=schema.Choice(
            vocabulary="collective.dms.basecontent.treating_groups",
        ),
    )
    # form.widget(treating_groups=Select2FieldWidget)

    recipient_groups = LocalRolesField(
        title=_("Recipient groups"),
        required=False,
        value_type=schema.Choice(
            vocabulary="collective.dms.basecontent.recipient_groups"
        ),
    )
    form.widget(recipient_groups=Select2FieldWidget)

    related_docs = RelationList(
        title=_("Related documents"),
        # value_type=RelationChoice(title=u"", source=CatalogSource(portal_type="dmsdocument")),
        value_type=RelationChoice(
            title="", vocabulary="plone.app.vocabularies.Catalog"
        ),
        required=False,
    )
    form.widget("related_docs", RelatedDocsFieldWidget)


@implementer(IDmsDocument)
class DmsDocument(Container):
    """DmsDocument"""

    # disable local roles inheritance
    __ac_local_roles_block__ = True

    def get_mainfiles(self):
        return object_values(self, ["DmsFile"])


class DmsDocumentSchemaPolicy(DexteritySchemaPolicy):
    """DmsDocument schema policy"""

    def bases(self, schemaName, tree):
        return (IDmsDocument,)
