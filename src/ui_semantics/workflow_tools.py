"""Interfaces for evidence expansion, preparation, observation and validation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Mapping

if TYPE_CHECKING:
    from .contracts import ObservedValueFlowSet, UiApiTrace, V2RuntimeReadyMaterialSet
    from .current_protocols import CurrentProtocolExecution
    from .m11b_materializer import RouteSM11bMaterializationResult
    from .proposal_run import DetailRegion, ProposalCallSpec
    from .v2_proposer import V2FrozenInput


def expand(
    frozen: V2FrozenInput,
    *,
    normalized_decisions: tuple[dict[str, Any], ...],
    first_call_order: int,
    detail_max_requests: int,
    detail_max_rendered_utf8_bytes: int,
    call_prototype: ProposalCallSpec,
) -> tuple[tuple[DetailRegion, ProposalCallSpec], ...]:
    """Construct the existing bounded detail views from screening decisions."""
    from .proposal_run import derive_detail_regions

    return derive_detail_regions(
        frozen,
        normalized_decisions=normalized_decisions,
        first_call_order=first_call_order,
        detail_max_requests=detail_max_requests,
        detail_max_rendered_utf8_bytes=detail_max_rendered_utf8_bytes,
        call_prototype=call_prototype,
    )


def prepare(
    material_set: V2RuntimeReadyMaterialSet,
    *,
    trace: UiApiTrace,
    value_flows: ObservedValueFlowSet,
    binding_plan: Mapping[str, Any],
    scientific_pins: Mapping[str, str],
    output_level: str,
    recording_trace: Mapping[str, Any] | None = None,
    recording_material_aliases: tuple[dict[str, Any], ...] = (),
    authenticated_actor_identity_paths: Mapping[str, str] | None = None,
    observed_catalog_requests: Mapping[str, Mapping[str, Any]] | None = None,
    observed_catalog_operations: Mapping[str, Mapping[str, Any]] | None = None,
) -> RouteSM11bMaterializationResult:
    """Reconstruct prerequisites and bindings with the existing materializer."""
    from .m11b_materializer import materialize_current_route_s_inputs

    return materialize_current_route_s_inputs(
        material_set,
        trace=trace,
        value_flows=value_flows,
        binding_plan=binding_plan,
        scientific_pins=scientific_pins,
        output_level=output_level,
        recording_trace=recording_trace,
        recording_material_aliases=recording_material_aliases,
        authenticated_actor_identity_paths=authenticated_actor_identity_paths,
        observed_catalog_requests=observed_catalog_requests,
        observed_catalog_operations=observed_catalog_operations,
    )


def observe(
    material: Any,
    runtime: Any,
    *,
    protocol_kind: str,
    artifact_writer: Callable[[str, bytes], None],
    output_level: str,
) -> tuple[Any, Any, Any]:
    """Collect observations using the selected execution pattern."""
    from .current_protocols import collect_current_protocol_observations

    return collect_current_protocol_observations(
        material,
        runtime,
        protocol_kind=protocol_kind,
        artifact_writer=artifact_writer,
        output_level=output_level,
    )


def read_observation(
    runtime: Any,
    context: Any,
    slot: str,
) -> tuple[dict[str, Any], dict[str, bytes]]:
    """Read one observation through the prepared runtime implementation."""
    return runtime._observe(context, slot, slot)


def validate(
    material: Any,
    runtime: Any,
    *,
    artifact_writer: Callable[[str, bytes], None],
    output_level: str,
) -> CurrentProtocolExecution:
    """Execute the validation plan with the existing protocol dispatcher."""
    from .current_protocols import execute_current_protocol

    return execute_current_protocol(
        material,
        runtime,
        artifact_writer=artifact_writer,
        output_level=output_level,
    )


__all__ = ["expand", "prepare", "observe", "validate"]
