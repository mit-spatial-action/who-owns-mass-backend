from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape

from whoownsmass.models import BlockGroup
from whoownsmass.api.dependencies import get_db, to_geojson_feat, to_feat_collect

router = APIRouter()


@router.get("/bgs.geojson")
def geojson_bgs(db: Session = Depends(get_db)):
    items = db.query(BlockGroup).limit(100).all()
    features = [
        to_geojson_feat({"id": b.id}, mapping(to_shape(b.geometry)))
        for b in items
        if b.geometry
    ]

    return to_feat_collect(features)
