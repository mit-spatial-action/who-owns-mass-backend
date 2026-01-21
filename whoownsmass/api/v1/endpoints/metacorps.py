from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from whoownsmass.models import Owner, Site, Address, MetaCorp
from whoownsmass.schemas import MetaCorpDetail
from whoownsmass.api.dependencies import (
    get_db,
    get_site_geo,
    to_feat_collect,
    to_simple_site,
    to_simple_owner,
    serialize_site,
    to_geojson_feat,
)

router = APIRouter()


@router.get("/", response_model=List[MetaCorpDetail])
def list_metacorps(
    limit: int = Query(5, ge=1, le=100), offset: int = 0, db: Session = Depends(get_db)
):
    metacorps = (
        db.query(MetaCorp)
        .options(
            selectinload(MetaCorp.owners)
            .selectinload(Owner.sites)
            .selectinload(Site.address)
            .selectinload(Address.parcel),
            selectinload(MetaCorp.owners).selectinload(Owner.address),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        MetaCorpDetail(
            **MetaCorpDetail.model_validate(corp, from_attributes=True).dict(
                exclude={"owners", "sites", "aliases"}
            ),
            owners=[to_simple_owner(o) for o in corp.owners],
            sites=[to_simple_site(s) for o in corp.owners for s in o.sites],
            aliases=list({o.name for o in corp.owners if o.name})
        )
        for corp in metacorps
    ]


@router.get("/{metacorp_id}", response_model=MetaCorpDetail)
def get_metacorp(metacorp_id: str, db: Session = Depends(get_db)):
    corp = (
        db.query(MetaCorp)
        .options(
            selectinload(MetaCorp.owners)
            .selectinload(Owner.sites)
            .selectinload(Site.address)
            .selectinload(Address.parcel),
            selectinload(MetaCorp.owners).selectinload(Owner.address),
        )
        .filter(MetaCorp.id == metacorp_id)
        .first()
    )

    if not corp:
        raise HTTPException(status_code=404, detail="MetaCorp not found")

    return MetaCorpDetail(
        **MetaCorpDetail.model_validate(corp, from_attributes=True).dict(
            exclude={"owners", "sites", "aliases"}
        ),
        owners=[to_simple_owner(o) for o in corp.owners],
        sites=[to_simple_site(s) for o in corp.owners for s in o.sites],
        aliases=list({o.name for o in corp.owners if o.name})
    )


# GEOJSON ENDPOINTS
@router.get("/metacorps.geojson")
def geojson_metacorps(limit: int = 5, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(MetaCorp).options(
        selectinload(MetaCorp.owners)
        .selectinload(Owner.sites)
        .selectinload(Site.address)
        .selectinload(Address.parcel)
    )

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

    return to_feat_collect(
        features, metadata={"limit": limit, "offset": offset, "total": query.count()}
    )
