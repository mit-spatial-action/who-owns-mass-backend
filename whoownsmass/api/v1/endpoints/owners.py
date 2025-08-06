from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from whoownsmass.api.dependencies import (
    get_db,
    to_geojson_feat,
    to_feat_collect,
    get_site_geo,
    serialize_site,
    to_simple_site,
)
from whoownsmass.models import Owner, Site, Address
from whoownsmass.schemas import OwnerDetail


router = APIRouter()


@router.get("/owners", response_model=List[OwnerDetail])
def list_owners(
    name: Optional[str] = None,
    limit: int = 5,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Owner).options(
        selectinload(Owner.sites)
        .selectinload(Site.address)
        .selectinload(Address.parcel),
        selectinload(Owner.address),
    )
    if name:
        query = query.filter(Owner.name.ilike(f"%{name}%"))

    return [
        OwnerDetail(
            **OwnerDetail.model_validate(o, from_attributes=True).dict(
                exclude={"sites"}
            ),
            sites=[to_simple_site(s) for s in o.sites],
        )
        for o in query.offset(offset).limit(limit).all()
    ]


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
    owner = (
        db.query(Owner)
        .options(
            selectinload(Owner.sites)
            .selectinload(Site.address)
            .selectinload(Address.parcel),
            selectinload(Owner.address),
        )
        .filter(Owner.id == owner_id)
        .first()
    )

    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    return OwnerDetail(
        **OwnerDetail.model_validate(owner, from_attributes=True).dict(
            exclude={"sites"}
        ),
        sites=[to_simple_site(s) for s in owner.sites],
    )


@router.get("/owners.geojson")
def geojson_owners(limit: int = 5, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Owner).options(
        selectinload(Owner.sites)
        .selectinload(Site.address)
        .selectinload(Address.parcel)
    )

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

    return to_feat_collect(
        features, metadata={"limit": limit, "offset": offset, "total": query.count()}
    )


@router.get("/owners/{owner_id}/sites.geojson")
def geojson_sites_by_owner(owner_id: int, db: Session = Depends(get_db)):
    owner = (
        db.query(Owner)
        .options(
            selectinload(Owner.sites)
            .selectinload(Site.address)
            .selectinload(Address.parcel)
        )
        .filter(Owner.id == owner_id)
        .first()
    )

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
