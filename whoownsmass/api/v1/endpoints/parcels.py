from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape

from whoownsmass.models import ParcelPoint
from whoownsmass.api.dependencies import get_db, to_geojson_feat, to_feat_collect

router = APIRouter()


@router.get("/parcelpoints.geojson")
def geojson_parcelpoints(db: Session = Depends(get_db)):
    items = db.query(ParcelPoint).limit(100).all()
    features = [
        to_geojson_feat({"id": p.id}, mapping(to_shape(p.geometry)))
        for p in items
        if p.geometry
    ]

    return to_feat_collect(features)
