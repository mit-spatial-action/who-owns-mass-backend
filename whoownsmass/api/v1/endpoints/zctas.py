from fastapi import APIRouter, Depends
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from whoownsmass.models import ZipCode
from whoownsmass.api.dependencies import get_db, to_geojson_feat, to_feat_collect

router = APIRouter()


@router.get("/zipcodes.geojson")
def geojson_zipcodes(db: Session = Depends(get_db)):
    items = db.query(ZipCode).limit(100).all()
    features = [
        to_geojson_feat({"zip": z.zip}, mapping(to_shape(z.geometry)))
        for z in items
        if z.geometry
    ]

    return to_feat_collect(features)
