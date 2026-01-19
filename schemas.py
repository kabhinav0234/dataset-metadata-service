from pydantic import BaseModel
from typing import List, Optional


class ColumnIn(BaseModel):
    name: str
    dtype: str


class DatasetCreate(BaseModel):
    fqn: str
    source_type: str
    columns: List[ColumnIn]


class DatasetOut(BaseModel):
    fqn: str
    source_type: str
    columns: List[ColumnIn]
    upstream: List[str] = []
    downstream: List[str] = []


class LineageCreate(BaseModel):
    upstream_fqn: str
    downstream_fqn: str


class SearchResponse(BaseModel):
    priority: int
    dataset: DatasetOut
