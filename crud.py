from sqlalchemy.orm import Session
from app import models, schemas
from app.lineage import validate_no_cycle


def create_dataset(db: Session, payload: schemas.DatasetCreate):
    existing = db.query(models.Dataset).filter(models.Dataset.fqn == payload.fqn).first()
    if existing:
        return existing

    ds = models.Dataset(fqn=payload.fqn, source_type=payload.source_type)
    db.add(ds)
    db.flush()

    for col in payload.columns:
        db.add(models.DatasetColumn(dataset_id=ds.id, name=col.name, dtype=col.dtype))

    db.commit()
    db.refresh(ds)
    return ds


def add_lineage(db: Session, upstream_fqn: str, downstream_fqn: str):
    up = db.query(models.Dataset).filter(models.Dataset.fqn == upstream_fqn).first()
    down = db.query(models.Dataset).filter(models.Dataset.fqn == downstream_fqn).first()

    if not up or not down:
        raise ValueError("Both upstream and downstream datasets must exist before creating lineage.")

    if up.id == down.id:
        raise ValueError("Invalid lineage: upstream and downstream cannot be same dataset.")

    validate_no_cycle(db, up.id, down.id)

    edge = models.LineageEdge(upstream_id=up.id, downstream_id=down.id)
    db.add(edge)
    db.commit()
    return edge


def get_dataset_with_lineage(db: Session, fqn: str):
    ds = db.query(models.Dataset).filter(models.Dataset.fqn == fqn).first()
    return ds
