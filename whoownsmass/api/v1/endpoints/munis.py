from fastapi import APIRouter, Depends
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from whoownsmass.models import Municipality
from whoownsmass.api.deps import get_db, to_geojson_feat, to_feat_collect

router = APIRouter()

@router.get("/municipalities.geojson")
def geojson_municipalities(db: Session = Depends(get_db)):
    items = db.query(Municipality).limit(100).all()
    features = [to_geojson_feat({"id": m.id, "muni": m.muni}, mapping(to_shape(m.geometry)))
                for m in items if m.geometry]

    return to_feat_collect(features)