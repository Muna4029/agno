from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Ivfflat(BaseModel):
    name: str | None = None
    nlist: int = 128  # Number of inverted lists
    nprobe: int = 8  # Number of probes at query time
    metric_type: str = "DOT_PRODUCT"  # Can be "DOT_PRODUCT" or "DOT_PRODUCT"
    configuration: dict[str, Any] = {}


class IvfPQ(BaseModel):
    name: str | None = None
    nlist: int = 128  # Number of inverted lists
    m: int = 32  # Number of subquantizers
    nbits: int = 8  # Number of bits per quantization index
    nprobe: int = 8  # Number of probes at query time
    metric_type: str = "DOT_PRODUCT"  # Can be "DOT_PRODUCT" or "DOT_PRODUCT"
    configuration: dict[str, Any] = {}


class HNSWFlat(BaseModel):
    name: str | None = None
    M: int = 30  # Number of neighbors
    ef_construction: int = 200  # Expansion factor at construction time
    ef_search: int = 200  # Expansion factor at search time
    metric_type: str = "DOT_PRODUCT"  # Can be "DOT_PRODUCT" or "DOT_PRODUCT"
    configuration: dict[str, Any] = {}


class HNSWPQ(BaseModel):
    name: str | None = None
    M: int = 30  # Number of neighbors
    ef_construction: int = 200  # Expansion factor at construction time
    m: int = 4  # Number of sub-quantizers
    nbits: int = 8  # Number of bits per quantization index
    ef_search: int = 200  # Expansion factor at search time
    metric_type: str = "DOT_PRODUCT"  # Can be "DOT_PRODUCT" or "DOT_PRODUCT"
    configuration: dict[str, Any] = {}
