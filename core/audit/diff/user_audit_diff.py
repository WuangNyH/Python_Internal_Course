from typing import Any, Mapping

from core.audit.diff.audit_diff import AuditDiff, diff_snapshots
from core.audit.snapshots.user_snapshot import USER_AUDIT_FIELDS


def diff_user_for_audit(
    *,
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    password_changed: bool = False,
    include_changes: bool = True,
) -> AuditDiff:
    # Khử bớt các noise-field như timestamp
    allow_fields = [f for f in USER_AUDIT_FIELDS if f not in {"created_at", "updated_at"}]

    base = diff_snapshots(
        before=before,
        after=after,
        allow_fields=allow_fields,
        include_changes=include_changes,
    )

    if not password_changed:
        return base

    # password semantic event (không log hash)
    changed_fields = list(base.changed_fields)
    changes = dict(base.changes)

    changed_fields.append("password")
    if include_changes:
        changes["password"] = {"from": "***", "to": "***"}

    after_patch: dict[str, Any] = {"changed_fields": changed_fields}
    if include_changes:
        after_patch["changes"] = changes

    return AuditDiff(
        changed_fields=changed_fields,
        changes=changes,
        after_patch=after_patch
    )
