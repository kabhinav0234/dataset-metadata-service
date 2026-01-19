from sqlalchemy import Column, Integer, String, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base
import enum


class SourceType(str, enum.Enum):
    mysql = "MySQL"
    mssql = "MSSQL"
    postgresql = "PostgreSQL"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    fqn = Column(String(255), unique=True, nullable=False, index=True)  # FQN as primary key in logic
    source_type = Column(Enum(SourceType), nullable=False)

    columns = relationship("DatasetColumn", back_populates="dataset", cascade="all, delete-orphan")
    upstream_edges = relationship("LineageEdge", foreign_keys="LineageEdge.downstream_id", back_populates="downstream")
    downstream_edges = relationship("LineageEdge", foreign_keys="LineageEdge.upstream_id", back_populates="upstream")


class DatasetColumn(Base):
    __tablename__ = "dataset_columns"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    name = Column(String(100), nullable=False)
    dtype = Column(String(50), nullable=False)

    dataset = relationship("Dataset", back_populates="columns")

    __table_args__ = (UniqueConstraint("dataset_id", "name", name="uq_dataset_column"),)


class LineageEdge(Base):
    __tablename__ = "lineage_edges"

    id = Column(Integer, primary_key=True, index=True)
    upstream_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    downstream_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)

    upstream = relationship("Dataset", foreign_keys=[upstream_id], back_populates="downstream_edges")
    downstream = relationship("Dataset", foreign_keys=[downstream_id], back_populates="upstream_edges")

    __table_args__ = (UniqueConstraint("upstream_id", "downstream_id", name="uq_lineage_edge"),)
