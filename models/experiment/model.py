"""
Model describing a specific experiment
"""
from __future__ import annotations

from invenio_i18n import lazy_gettext as _
from oarepo_model.api import model
from oarepo_model.customizations import AddMetadataExport, PatchIndexPropertyMapping
from oarepo_model.datatypes.registry import from_yaml
from oarepo_rdm.model.presets import rdm_basic_preset
from oarepo_rdm.model.presets import rdm_minimal_preset
from oarepo_rdm.model.presets.rdm.resources.records.exports import RDMCompleteExportsPreset

from .datatypes import PathSafeObjectDataType
from .serializers import DataCiteJSONSerializer

# TODO: Consider letting users add an image/icon for the model,
# so that the deposit model selection page is more visually appealing.
experiment_model = model(
    "experiment",
    version="1.0.0",
    description="Model describing a specific experiment",
    presets=[

        # NOTE: Switched from rdm_basic_preset to rdm_minimal_preset, according to the docs
        #       some features may not work (for example I had to fix citations), don't know
        #       how much functionality is online due to me not resetting the whole database
        rdm_minimal_preset,


        # Import all exports from the RDM Complete preset.
        # This, among other things, fixes citation generation.
        RDMCompleteExportsPreset

    ],
    types=[
        from_yaml("metadata.yaml", __file__),
        # Overrides the built-in `object` datatype (see datatypes.py) so that
        # facets of the nested `metadata.metadata.*` subtree get correct paths.
        {"object": PathSafeObjectDataType},
    ],
    metadata_type="Metadata",
    customizations=[
        # Add your customizations here, such as custom exports and class mixins. 
        # The list of available extensions is at https://github.com/oarepo/oarepo-model.
        # If you do not find a customization that suits your needs or need a
        # help with using customizations, please contact us at support@cesnet.cz and
        # specify the keyword "Invenio repository development" inside the subject or
        # mail body of the request.

        # Export for datacite
        # RDMCompleteExportsPreset only includes export for datacite+xml
        AddMetadataExport(
            code="datacite",
            name=_("Datacite export"),
            mimetype="application/vnd.datacite.datacite+json",
            serializer=DataCiteJSONSerializer()
        ),

        # `metadata.metadata.provenance` is a free-form dump from the extraction service.
        # This makes it so that opensearch doesn't even try to index it, as it kept throwing errors.
        PatchIndexPropertyMapping(
            "metadata.metadata.provenance",
            {"type": "object", "enabled": False},
        ),
    ],
    configuration={
        "ui_blueprint_name": "experiment_ui"
    }
)
