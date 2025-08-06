"""Dependency functions used across the application"""

from typing import Optional, List
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape

from whoownsmass.database import session
from whoownsmass.schemas import SimpleOwner, SimpleSite, MetaCorpBase, SiteDetail
from whoownsmass.models import Owner, Site


def get_db():
    """Returns a database session."""
    db = session()
    try:
        yield db
    finally:
        db.close()


def to_geojson_feat(item: dict, geo: dict):
    """Returns a GeoJSON Feature for a given item."""
    return {
        "type": "Feature",
        "geometry": geo,
        "properties": {k: v for k, v in item.items() if k != "geometry"},
    }


def to_feat_collect(features: List[dict], metadata: Optional[dict] = None):
    """Returns a GeoJSON FeatureCollection for a given list of items."""
    return {
        "type": "FeatureCollection",
        "features": features,
        **({"metadata": metadata} if metadata else {}),
    }


def to_simple_owner(owner: Owner) -> SimpleOwner:
    """Converts an Owner instance to a SimpleOwner."""
    return SimpleOwner.model_validate(owner, from_attributes=True)


def to_simple_site(site: Site) -> SimpleSite:
    """Converts an Site instance to a SimpleSite."""
    return SimpleSite.model_validate(site, from_attributes=True)


def get_metacorp_base_from_site(site: Site) -> Optional[MetaCorpBase]:
    """Given a site, returns an associated MetaCorp."""
    if site.owners and site.owners[0].metacorp:
        return MetaCorpBase.model_validate(
            site.owners[0].metacorp, from_attributes=True
        )
    return None


def serialize_site(site: Site) -> dict:
    """Given a site, returns a JSON-serialized object."""
    return SiteDetail.model_validate(site, from_attributes=True).model_dump(mode="json")


def get_site_geo(site: Site):
    """Given a site, returns a geometry."""
    try:
        shape = to_shape(site.address.parcel.geometry)
        return mapping(shape) if not shape.is_empty else None
    except TypeError:
        return None
