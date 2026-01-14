from dataclasses import dataclass
from typing import Any, Mapping, Iterable


@dataclass(frozen=True)
class AuditDiff:
    """
    Result container used by AuditLog payload.
    - changed_fields: list of field names that changed
    - changes: per-field before/after
    - after_patch: fields to merge into "after" payload
    """
    changed_fields: list[str]
    changes: dict[str, dict[str, Any]]
    after_patch: dict[str, Any]


def diff_snapshots(
        *,
        before: Mapping[str, Any],
        after: Mapping[str, Any],
        allow_fields: Iterable[str],
        include_changes: bool = True,
) -> AuditDiff:
    changed_fields: list[str] = []
    changes: dict[str, dict[str, Any]] = {}

    for field in allow_fields:
        b = before.get(field)
        a = after.get(field)

        if b != a:
            changed_fields.append(field)
            if include_changes:
                changes[field] = {"from": b, "to": a}

    after_patch: dict[str, Any] = {"changed_fields": changed_fields}
    if include_changes:
        after_patch["changes"] = changes

    return AuditDiff(changed_fields=changed_fields, changes=changes, after_patch=after_patch)
