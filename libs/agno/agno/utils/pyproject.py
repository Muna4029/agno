from __future__ import annotations

from pathlib import Path

from agno.utils.log import log_debug, logger


def read_pyproject_agno(pyproject_file: Path) -> dict | None:
    log_debug(f"Reading {pyproject_file}")
    try:
        import tomli

        pyproject_dict = tomli.loads(pyproject_file.read_text())
        agno_conf = pyproject_dict.get("tool", {}).get("agno", None)
        if agno_conf is not None and isinstance(agno_conf, dict):
            return agno_conf
    except Exception as e:
        logger.error(f"Could not read {pyproject_file}: {e}")
    return None
