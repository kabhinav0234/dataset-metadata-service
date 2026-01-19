from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app import schemas, models, crud

app = FastAPI(title="Metadata Service")


def dataset_to_out(ds: models.Dataset):
    return schemas.DatasetOut(
        fqn=ds.fqn,
        source_type=ds.source_type.value if hasattr(ds.source_type, "value") else str(ds.source_type),
        columns=[schemas.ColumnIn(name=c.name, dtype=c.dtype) for c in ds.columns],
        upstream=[e.upstream.fqn for e in ds.upstream_edges],
        downstream=[e.downstream.fqn for e in ds.downstream_edges],
    )


@app.post("/datasets", response_model=schemas.DatasetOut)
def add_dataset(payload: schemas.DatasetCreate, db: Session = Depends(get_db)):
    ds = crud.create_dataset(db, payload)
    return dataset_to_out(ds)


@app.post("/lineage")
def create_lineage(payload: schemas.LineageCreate, db: Session = Depends(get_db)):
    try:
        crud.add_lineage(db, payload.upstream_fqn, payload.downstream_fqn)
        return {"message": "Lineage created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/datasets/{fqn}", response_model=schemas.DatasetOut)
def get_dataset(fqn: str, db: Session = Depends(get_db)):
    ds = crud.get_dataset_with_lineage(db, fqn)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset_to_out(ds)


@app.get("/search", response_model=list[schemas.SearchResponse])
def search(q: str, db: Session = Depends(get_db)):
    q = q.lower().strip()

    results = []

    # Priority 1: Table name (last part of FQN)
    datasets = db.query(models.Dataset).all()

    for ds in datasets:
        parts = ds.fqn.lower().split(".")
        if len(parts) < 4:
            continue

        conn, dbname, schema, table = parts[0], parts[1], parts[2], parts[3]

        # 1) Table
        if q in table:
            results.append((1, ds))
            continue

        # 2) Column
        if any(q in c.name.lower() for c in ds.columns):
            results.append((2, ds))
            continue

        # 3) Schema
        if q in schema:
            results.append((3, ds))
            continue

        # 4) Database
        if q in dbname:
            results.append((4, ds))
            continue

    # sort by priority
    results.sort(key=lambda x: x[0])

    return [{"priority": p, "dataset": dataset_to_out(ds)} for p, ds in results]
