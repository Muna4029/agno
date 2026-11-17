from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agno.utils.common import dataclass_to_dict


@dataclass
class File:
    name: str | None = None
    description: str | None = None
    columns: list[str] | None = None
    path: str | None = None
    type: str = "FILE"

    def get_metadata(self) -> dict[str, Any]:
        return dataclass_to_dict(self, exclude_none=True)
