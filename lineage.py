from sqlalchemy.orm import Session
from app.models import Dataset, LineageEdge


def _build_graph(db: Session):
    graph = {}
    datasets = db.query(Dataset).all()
    for d in datasets:
        graph[d.id] = []

    edges = db.query(LineageEdge).all()
    for e in edges:
        graph[e.upstream_id].append(e.downstream_id)

    return graph


def _dfs_has_path(graph, start, target, visited):
    if start == target:
        return True
    visited.add(start)

    for nxt in graph.get(start, []):
        if nxt not in visited:
            if _dfs_has_path(graph, nxt, target, visited):
                return True
    return False


def validate_no_cycle(db: Session, upstream_id: int, downstream_id: int):
    """
    Reject if downstream can already reach upstream (cycle)
    because adding upstream -> downstream will close the loop.
    """
    graph = _build_graph(db)

    # if downstream already reaches upstream => cycle
    if _dfs_has_path(graph, downstream_id, upstream_id, set()):
        raise ValueError("Invalid lineage: cycle detected (downstream is already upstream of source).")
