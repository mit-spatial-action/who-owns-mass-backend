from fastapi import APIRouter
from whoownsmass.api.v1.endpoints import owners, sites, bgs, munis, parcels, tracts, zctas

router = APIRouter(prefix="/v1")
router.include_router(owners.router, prefix="/owners", tags=["owners"])
router.include_router(sites.router, prefix="/sites", tags=["sites"])
router.include_router(bgs.router, prefix="/bgs", tags=["bgs"])
router.include_router(zctas.router, prefix="/zctas", tags=["zctas"])
router.include_router(munis.router, prefix="/munis", tags=["munis"])
router.include_router(parcels.router, prefix="/parcels", tags=["parcels"])
router.include_router(tracts.router, prefix="/tracts", tags=["tracts"])