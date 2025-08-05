from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session, selectinload, joinedload
from whoownsmass.api.deps import to_geojson_feat, to_feat_collect

from whoownsmass.schemas import SiteDetail
from whoownsmass.models import Owner, Site, Address
from whoownsmass.api.deps import get_db

router = APIRouter()

@router.get("/sites", response_model=List[SiteDetail])
def list_sites(limit: int = 5, offset: int = 0, db: Session = Depends(get_db)):
    sites = db.query(Site).options(
        selectinload(Site.owners).selectinload(Owner.metacorp),
        selectinload(Site.address).selectinload(Address.parcel)
    ).offset(offset).limit(limit).all()

    return [SiteDetail(
            **SiteDetail.model_validate(s, from_attributes=True).dict(exclude={"owners", "metacorp"}),
            owners=[to_simple_owner(o) for o in s.owners],
            metacorp=get_metacorp_base_from_site(s)) for s in sites]


@router.get("/sites.geojson")
def geojson_sites(limit: int = 5, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Site).options(
        selectinload(Site.owners).selectinload(Owner.metacorp),
        selectinload(Site.address).selectinload(Address.parcel))

    sites = query.offset(offset).limit(limit).all()
    features = []
    for site in sites:
        geom = get_site_geo(site)
        if not geom:
            continue
        props = serialize_site(site)
        if site.owners:
            owner = site.owners[0]
            props["owner_id"] = owner.id
            props["owner_name"] = owner.name
            if owner.metacorp:
                props["metacorp_id"] = owner.metacorp.id
                props["metacorp_name"] = owner.metacorp.name
        features.append(to_geojson_feat(props, geom))

    return to_feat_collect(features, metadata={
        "limit": limit, "offset": offset, "total": query.count()})


@router.get("/sites/{site_id}.geojson")
def geojson_single_site(site_id: int, db: Session = Depends(get_db)):
    site = db.query(Site).options(
        selectinload(Site.address).selectinload(Address.parcel)).filter(Site.id == site_id).first()

    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    geom = get_site_geo(site)
    if not geom:
        raise HTTPException(status_code=404, detail="Geometry not found")

    return to_feat_collect([to_geojson_feat(serialize_site(site), geom)])