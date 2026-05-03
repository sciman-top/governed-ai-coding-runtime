from __future__ import annotations

from typing import Final


MANAGEMENT_MODE_REPLACE: Final = "replace"
MANAGEMENT_MODE_JSON_MERGE: Final = "json_merge"
MANAGEMENT_MODE_BLOCK_ON_DRIFT: Final = "block_on_drift"

ALLOWED_MANAGEMENT_MODES: Final = {
    MANAGEMENT_MODE_REPLACE,
    MANAGEMENT_MODE_JSON_MERGE,
    MANAGEMENT_MODE_BLOCK_ON_DRIFT,
}


def managed_file_mode_error_text() -> str:
    return (
        "replace (legacy fail-closed alias; blocks existing target drift), "
        "json_merge, or block_on_drift"
    )


def managed_file_mode_contract(management_mode: str) -> dict[str, str]:
    if management_mode == MANAGEMENT_MODE_JSON_MERGE:
        return {
            "mode_status": "active",
            "overwrite_policy": "json_merge_overlay_preserve_target_local_keys",
        }
    if management_mode == MANAGEMENT_MODE_BLOCK_ON_DRIFT:
        return {
            "mode_status": "active",
            "overwrite_policy": "create_missing_block_existing_drift",
        }
    if management_mode == MANAGEMENT_MODE_REPLACE:
        return {
            "mode_status": "legacy_fail_closed",
            "overwrite_policy": "create_missing_block_existing_drift",
        }
    return {
        "mode_status": "unsupported",
        "overwrite_policy": "unknown",
    }


def managed_file_drift_recommended_action(*, management_mode: str, verifier: str) -> str:
    tail = (
        "then rerun consistency verification"
        if verifier == "consistency"
        else "then rerun apply"
    )
    if management_mode == MANAGEMENT_MODE_REPLACE:
        return (
            "replace is a legacy fail-closed alias and does not silently overwrite target drift; "
            "diff target file against source, integrate target-local fixes into the control-repo source "
            f"or explicitly retire the target change, {tail}"
        )
    return (
        "diff target file against source, integrate target-local fixes into the control-repo source "
        f"or explicitly retire the target change, {tail}"
    )
