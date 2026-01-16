from django.contrib import admin
from .models import (
    MetaCorp,
    Municipality,
    ZipCode,
    BlockGroup,
    Tract,
    ParcelPoint,
    Address,
    Site,
    Company,
    Owner,
    SiteToOwner,
    Role,
    Officer,
    OfficerToRole,
)

admin.site.register(MetaCorp)
admin.site.register(Municipality)
admin.site.register(ZipCode)
admin.site.register(BlockGroup)
admin.site.register(Tract)
admin.site.register(ParcelPoint)
admin.site.register(Address)
admin.site.register(Site)
admin.site.register(Company)
admin.site.register(Owner)
admin.site.register(SiteToOwner)
admin.site.register(Role)
admin.site.register(Officer)
admin.site.register(OfficerToRole)