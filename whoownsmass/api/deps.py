from whoownsmass.database import session
from typing import Optional, List

# gives a session to query the database in each route
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def to_geojson_feat(item: dict, geo: dict):
    return {"type": "Feature", "geometry": geo, "properties": {k: v for k, v in item.items() if k != "geometry"}}

def to_feat_collect(features: List[dict], metadata: Optional[dict] = None):
    return {"type": "FeatureCollection", "features": features, **({"metadata": metadata} if metadata else {})}
    