from tqdm import tqdm
from who_owns.models import (
    Attorney,
    Address,
    CompanyType,
    Institution,
    LandlordType,
    LegacyCorps,
    LegacyInds,
    LegacyEdges,
    LegacyOwners,
    MetaCorp,
    Parcel,
    Person,
    Role,
)


### move people, corps, out of LegacyOwners, LegacyCorps, LegacyInds into other tables
def create_metacorps():
    """Taking the existing clusters and using them as IDs for MetaCorps"""
    legacycorps = (
        LegacyCorps.objects.all().values_list("group_network", flat=True).distinct()
    )
    for lc_group in legacycorps:
        MetaCorp.objects.get_or_create(id=lc_group)


def create_landlord_institutions():
    legacycorps = LegacyCorps.objects.all()
    ll_role, _ = Role.objects.get_or_create(name="landlord")
    owner_role, _ = Role.objects.get_or_create(name="owner")
    ll_company, _ = CompanyType.objects.get_or_create(name="landlord")
    for lc in tqdm(legacycorps):
        metacorp, _ = MetaCorp.objects.get_or_create(id=lc.group_network)
        inst, _ = Institution.objects.get_or_create(id=lc.id)
        inst.name = lc.entityname
        inst.company_type = ll_company
        inst.metacorp = metacorp
        inst.save()
        # owners are connected to corps through edges
        edges = LegacyEdges.objects.filter(id_corp=inst.id)
        for edge in edges:
            owners = LegacyOwners.objects.filter(group=edge.id_link)
            corps = LegacyCorps.objects.filter(id=edge.id_corp)
            for owner in owners:
                address, _ = Address.objects.get_or_create(
                    street=owner.own_addr,
                    city=owner.own_city,
                    state=owner.own_state,
                    zip=owner.own_zip,
                )
                prsn, _ = Person.objects.get_or_create(
                    name_address=owner.name_address, name=owner.owner1, address=address
                )
                prsn.roles.add(ll_role)
                prsn.roles.add(owner_role)
                prsn.save()

                for corp in corps:
                    inst2, _ = Institution.objects.get_or_create(id=corp.id)
                    inst2.company_type = ll_company
                    inst2.metacorp = metacorp
                    inst2.name = lc.entityname
                    inst2.people.add(prsn)
                    inst2.save()
                inst.people.add(prsn)
                inst.save()

            inds = LegacyInds.objects.filter(group_network=edge.id_link)
            for ind in inds:
                address, _ = Address.objects.get_or_create(
                    street=ind.address_simp, state=None, city=None, zip=None
                )
                prsn, _ = Person.objects.get_or_create(
                    name=ind.fullname_simp,
                    name_address=owner.owner1,
                    legacy_inds_id=ind.id,
                    address=address,
                )
                prsn.roles.add(ll_role)
                prsn.save()

                edges = LegacyEdges.objects.filter(id_link=inds.id)
                for edge in edges:
                    corps = LegacyCorps.objects.filter(id=edge.id_corp)
                    for corp in corps:
                        inst2, _ = Institution.objects.get_or_create(id=corp.id)
                        inst2.people.add(prsn)
                        inst2.name = lc.entityname
                        inst2.company_type = ll_company
                        inst2.metacorp = metacorp
                        inst2.save()


# owners are connected to corps through edges
# inds are found in edges using inds.id edges.id_link
