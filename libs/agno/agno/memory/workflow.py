from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from agno.run.response import RunResponse
from agno.utils.log import log_debug


class WorkflowRun(BaseModel):
    input: dict[str, Any] | None = None
    response: RunResponse | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class WorkflowMemory(BaseModel):
    runs: list[WorkflowRun] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

    def add_run(self, workflow_run: WorkflowRun) -> None:
        """Adds a WorkflowRun to the runs list."""
        self.runs.append(workflow_run)
        log_debug("Added WorkflowRun to WorkflowMemory")

    def clear(self) -> None:
        """Clear the WorkflowMemory"""

        self.runs = []

    def deep_copy(self, *, update: dict[str, Any] | None = None) -> WorkflowMemory:
        new_memory = self.model_copy(deep=True, update=update)
        # clear the new memory to remove any references to the old memory
        new_memory.clear()
        return new_memory
