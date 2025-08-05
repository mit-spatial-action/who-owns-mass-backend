# logic for api routes - receive request, talk to database, return data


from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload, joinedload
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape
from typing import List, Optional

from who_owns_mass_fastapi.database import SessionLocal
from who_owns_mass_fastapi.models import MetaCorp, Owner, Site, Address, Municipality, Tract, BlockGroup, ZipCode, ParcelPoint
from who_owns_mass_fastapi.schemas import MetaCorpDetail, SiteDetail, OwnerDetail, SimpleOwner, SimpleSite, MetaCorpBase


router = APIRouter()


# gives a session to query the database in each route
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# HELPERS
def to_simple_owner(owner: Owner) -> SimpleOwner:
    return SimpleOwner.model_validate(owner, from_attributes=True)

def to_simple_site(site: Site) -> SimpleSite:
    return SimpleSite.model_validate(site, from_attributes=True)

def serialize_site(site: Site) -> dict:
    return SiteDetail.model_validate(site, from_attributes=True).model_dump(mode="json")

def get_site_geo(site: Site):
    try:
        shape = to_shape(site.address.parcel.geometry)
        return mapping(shape) if not shape.is_empty else None
    except Exception:
        return None

def to_geojson_feat(item: dict, geo: dict):
    return {"type": "Feature", "geometry": geo, "properties": {k: v for k, v in item.items() if k != "geometry"}}

def to_feat_collect(features: List[dict], metadata: Optional[dict] = None):
    return {"type": "FeatureCollection", "features": features, **({"metadata": metadata} if metadata else {})}

def get_metacorp_base_from_site(site: Site) -> Optional[MetaCorpBase]:
    if site.owners and site.owners[0].metacorp:
        return MetaCorpBase.model_validate(site.owners[0].metacorp, from_attributes=True)
    return None


# REST ENDPOINTS
@router.get("/metacorps", response_model=List[MetaCorpDetail])
def list_metacorps(limit: int = Query(5, ge=1, le=100), offset: int = 0, db: Session = Depends(get_db)):
    metacorps = db.query(MetaCorp).options(
        selectinload(MetaCorp.owners).selectinload(Owner.sites).selectinload(Site.address).selectinload(Address.parcel),
        selectinload(MetaCorp.owners).selectinload(Owner.address)
    ).offset(offset).limit(limit).all()

    return [MetaCorpDetail(
            **MetaCorpDetail.model_validate(corp, from_attributes=True).dict(exclude={"owners", "sites", "aliases"}),
            owners=[to_simple_owner(o) for o in corp.owners],
            sites=[to_simple_site(s) for o in corp.owners for s in o.sites],
            aliases=list({o.name for o in corp.owners if o.name})) for corp in metacorps]

@router.get("/metacorps/{metacorp_id}", response_model=MetaCorpDetail)
def get_metacorp(metacorp_id: str, db: Session = Depends(get_db)):
    corp = db.query(MetaCorp).options(
        selectinload(MetaCorp.owners).selectinload(Owner.sites).selectinload(Site.address).selectinload(Address.parcel),
        selectinload(MetaCorp.owners).selectinload(Owner.address)
    ).filter(MetaCorp.id == metacorp_id).first()

    if not corp:
        raise HTTPException(status_code=404, detail="MetaCorp not found")

    return MetaCorpDetail(
        **MetaCorpDetail.model_validate(corp, from_attributes=True).dict(exclude={"owners", "sites", "aliases"}),
        owners=[to_simple_owner(o) for o in corp.owners],
        sites=[to_simple_site(s) for o in corp.owners for s in o.sites],
        aliases=list({o.name for o in corp.owners if o.name}))


@router.get("/owners", response_model=List[OwnerDetail])
def list_owners(name: Optional[str] = None, limit: int = 5, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Owner).options(
        selectinload(Owner.sites).selectinload(Site.address).selectinload(Address.parcel),
        selectinload(Owner.address))
    if name:
        query = query.filter(Owner.name.ilike(f"%{name}%"))

    return [OwnerDetail(
            **OwnerDetail.model_validate(o, from_attributes=True).dict(exclude={"sites"}),
            sites=[to_simple_site(s) for s in o.sites] )
            for o in query.offset(offset).limit(limit).all()]


# querying by owner name
# @router.get("/owners/{name}", response_model=List[OwnerDetail])
# def list_owners(name: Optional[str] = None, limit: int = 5, offset: int = 0, db: Session = Depends(get_db)):
#     query = db.query(Owner).options(
#         selectinload(Owner.sites).selectinload(Site.address).selectinload(Address.parcel),
#         selectinload(Owner.address))
#     if name:
#         query = query.filter(Owner.name.ilike(f"%{name}%"))

#     return [OwnerDetail(
#             **OwnerDetail.model_validate(o, from_attributes=True).dict(exclude={"sites"}),
#             sites=[to_simple_site(s) for s in o.sites] )
#             for o in query.offset(offset).limit(limit).all()]

# #################

@router.get("/owners/{owner_id}", response_model=OwnerDetail)
def get_owner(owner_id: int, db: Session = Depends(get_db)):
    owner = db.query(Owner).options(
        selectinload(Owner.sites).selectinload(Site.address).selectinload(Address.parcel),
        selectinload(Owner.address)
    ).filter(Owner.id == owner_id).first()

    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    return OwnerDetail(
        **OwnerDetail.model_validate(owner, from_attributes=True).dict(exclude={"sites"}),
        sites=[to_simple_site(s) for s in owner.sites])

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


# GEOJSON ENDPOINTS
@router.get("/metacorps.geojson")
def geojson_metacorps(limit: int = 5, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(MetaCorp).options(
        selectinload(MetaCorp.owners).selectinload(Owner.sites).selectinload(Site.address).selectinload(Address.parcel))

    metacorps = query.offset(offset).limit(limit).all()
    features = []
    for metacorp in metacorps:
        for owner in metacorp.owners:
            for site in owner.sites:
                geom = get_site_geo(site)
                if not geom:
                    continue
                props = serialize_site(site)
                props["owner_id"] = owner.id
                props["owner_name"] = owner.name
                props["metacorp_id"] = metacorp.id
                props["metacorp_name"] = metacorp.name
                features.append(to_geojson_feat(props, geom))

    return to_feat_collect(features, metadata={
        "limit": limit, "offset": offset, "total": query.count()})


@router.get("/owners.geojson")
def geojson_owners(limit: int = 5, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Owner).options(
        selectinload(Owner.sites).selectinload(Site.address).selectinload(Address.parcel))

    owners = query.offset(offset).limit(limit).all()
    features = []
    for owner in owners:
        for site in owner.sites:
            geom = get_site_geo(site)
            if not geom:
                continue
            props = serialize_site(site)
            props["owner_id"] = owner.id
            props["owner_name"] = owner.name
            features.append(to_geojson_feat(props, geom))

    return to_feat_collect(features, metadata={
        "limit": limit, "offset": offset, "total": query.count()})


@router.get("/owners/{owner_id}/sites.geojson")
def geojson_sites_by_owner(owner_id: int, db: Session = Depends(get_db)):
    owner = db.query(Owner).options(
        selectinload(Owner.sites).selectinload(Site.address).selectinload(Address.parcel)).filter(Owner.id == owner_id).first()

    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    features = []
    for site in owner.sites:
        geom = get_site_geo(site)
        if not geom:
            continue
        props = serialize_site(site)
        props["owner_id"] = owner.id
        props["owner_name"] = owner.name
        features.append(to_geojson_feat(props, geom))

    return to_feat_collect(features)


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


@router.get("/municipalities.geojson")
def geojson_municipalities(db: Session = Depends(get_db)):
    items = db.query(Municipality).limit(100).all()
    features = [to_geojson_feat({"id": m.id, "muni": m.muni}, mapping(to_shape(m.geometry)))
                for m in items if m.geometry]

    return to_feat_collect(features)


@router.get("/tracts.geojson")
def geojson_tracts(db: Session = Depends(get_db)):
    items = db.query(Tract).limit(100).all()
    features = [to_geojson_feat({"id": t.id}, mapping(to_shape(t.geometry)))
                for t in items if t.geometry]

    return to_feat_collect(features)


@router.get("/blockgroups.geojson")
def geojson_blockgroups(db: Session = Depends(get_db)):
    items = db.query(BlockGroup).limit(100).all()
    features = [to_geojson_feat({"id": b.id}, mapping(to_shape(b.geometry)))
                for b in items if b.geometry]

    return to_feat_collect(features)


@router.get("/zipcodes.geojson")
def geojson_zipcodes(db: Session = Depends(get_db)):
    items = db.query(ZipCode).limit(100).all()
    features = [to_geojson_feat({"zip": z.zip}, mapping(to_shape(z.geometry)))
                for z in items if z.geometry]

    return to_feat_collect(features)


@router.get("/parcelpoints.geojson")
def geojson_parcelpoints(db: Session = Depends(get_db)):
    items = db.query(ParcelPoint).limit(100).all()
    features = [to_geojson_feat({"id": p.id}, mapping(to_shape(p.geometry)))
                for p in items if p.geometry]

    return to_feat_collect(features)
