"""Model-specific datatype overrides."""

from __future__ import annotations

import contextlib
from typing import Any, override

from oarepo_model.datatypes.collections import NoPropertiesError, ObjectDataType


class PathSafeObjectDataType(ObjectDataType):
    """Object datatype that builds facet paths correctly.

    ``ObjectDataType.get_facet`` skips a path level when the current path merely
    *ends* with the child key (``path.endswith(key)``). For the experiment model
    the metadata root has a child named ``metadata``, so the walk starts at
    ``path="metadata"`` and every nested facet silently loses that level,
    yielding e.g. ``metadata.simulation_setup.software`` instead of
    ``metadata.metadata.simulation_setup.software`` - facets with empty buckets.

    Only treat the path as already containing the key when it is a dotted
    suffix (an array item / wrapper case), so ``metadata`` + ``metadata``
    correctly becomes ``metadata.metadata``.
    """

    TYPE = "object"

    @override
    def get_facet(
        self,
        path: str,
        element: dict[str, Any],
        nested_facets: list[Any],
        facets: dict[str, list],
        path_suffix: str = "",
        ignored_keys: set[str] | None = None,
    ) -> Any:
        """Create facets for the object data type, appending the child key."""
        _ = path_suffix  # path suffix is not used for objects
        with contextlib.suppress(NoPropertiesError):
            properties = self._get_properties(element)
            for key, value in properties.items():
                if ignored_keys is not None and key in ignored_keys:
                    continue
                if path == "":
                    _path = key
                elif path.endswith(f".{key}"):
                    _path = path
                else:
                    _path = path + "." + key
                facets.update(
                    self._registry.get_type(value).get_facet(
                        _path, value, nested_facets, facets
                    )
                )

        return facets
