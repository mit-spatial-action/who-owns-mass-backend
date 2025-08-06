from fastapi import APIRouter, Depends
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from whoownsmass.models import Tract
from whoownsmass.api.dependencies import get_db, to_geojson_feat, to_feat_collect

router = APIRouter()


@router.get("/tracts.geojson")
def geojson_tracts(db: Session = Depends(get_db)):
    items = db.query(Tract).limit(100).all()
    features = [
        to_geojson_feat({"id": t.id}, mapping(to_shape(t.geometry)))
        for t in items
        if t.geometry
    ]

    return to_feat_collect(features)
