# like django rest framework serializers — used to control how data is validated and returned in api responses (using pydantic)


from pydantic import BaseModel
from typing import Optional, List
from datetime import date


# BASE SCHEMAS
class MetaCorpBase(BaseModel):
    id: str
    name: Optional[str]
    val: Optional[int]
    prop_count: Optional[int]
    unit_count: Optional[float]
    area: Optional[int]
    units_per_prop: Optional[float]
    val_per_prop: Optional[float]
    val_per_area: Optional[float]
    company_count: Optional[int]

    class Config:
        from_attributes = True


class AddressBase(BaseModel):
    id: int
    addr: Optional[str]
    start: Optional[float]
    end: Optional[float]
    body: Optional[str]
    even: Optional[bool]
    muni: Optional[str]
    postal: Optional[str]
    state: Optional[str]

    class Config:
        from_attributes = True


class OwnerBase(BaseModel):
    id: int
    name: Optional[str]
    inst: Optional[bool]
    trust: Optional[bool]
    trustees: Optional[bool]
    metacorp_id: Optional[str]

    class Config:
        from_attributes = True


class SiteBase(BaseModel):
    id: int
    fy: int
    ls_date: Optional[date]
    ls_price: Optional[int]
    bld_area: Optional[int]
    res_area: Optional[int]
    units: int
    bld_val: int
    lnd_val: int
    use_code: str
    luc: str
    ooc: bool
    condo: bool
    address_id: Optional[int]

    class Config:
        from_attributes = True


# SIMPLE (used in nested lists)
class SimpleOwner(OwnerBase):
    pass


class SimpleSite(SiteBase):
    pass


# DETAILED
class MetaCorpDetail(MetaCorpBase):
    owners: Optional[List[SimpleOwner]] = []
    sites: Optional[List[SimpleSite]] = []
    aliases: Optional[List[str]] = []

    class Config:
        from_attributes = True


class SiteDetail(SiteBase):
    owners: Optional[List[SimpleOwner]] = []
    metacorp: Optional[MetaCorpBase] = None
    address: Optional[AddressBase] = None

    class Config:
        from_attributes = True


class OwnerDetail(OwnerBase):
    sites: Optional[List[SimpleSite]] = []
    address: Optional[AddressBase] = None

    class Config:
        from_attributes = True
