from pydantic import BaseModel, Field
from typing import Literal


SortDirection = Literal["asc", "desc"]


class SortSpec(BaseModel):
    """
    1 sort rule
    """
    field: str = Field(..., description="Field name to sort by")
    direction: SortDirection = Field(default="asc")

    @property
    def is_desc(self) -> bool:
        return self.direction == "desc"


def parse_sort(sort: str | None) -> list[SortSpec]:
    """
    Parse query param sort thành list[SortSpec]

    Example:
        "created_at,-email"
        -> [
            SortSpec(field="created_at", direction="asc"),
            SortSpec(field="email", direction="desc"),
        ]
    """
    if not sort:
        return []

    specs: list[SortSpec] = []

    for part in sort.split(","):
        part = part.strip()
        if not part:
            continue

        if part.startswith("-"):
            specs.append(
                SortSpec(
                    field=part[1:],
                    direction="desc",
                )
            )
        else:
            specs.append(
                SortSpec(
                    field=part,
                    direction="asc",
                )
            )

    return specs
