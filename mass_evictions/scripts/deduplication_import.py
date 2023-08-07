import os
from tqdm import tqdm
import geopandas as gpd
import pandas as pd
from django.db import IntegrityError

from config.settings import DEDUPLICATIONS_DIR
from mass_evictions.models import Parcel, OwnerGroup, Owner, Corp

default_chunksize = 10**6


def import_parcels(filename):
    parcels_file = os.path.join(DEDUPLICATIONS_DIR, filename)
    gdf = gpd.read_file(parcels_file)
    parcels = gdf.to_dict("records")
    [
        Parcel.objects.create(
            object_id=parcel_dict["OBJECTID"],
            loc_id=parcel_dict["LOC_ID"],
            town_id=parcel_dict["TOWN_ID"],
            geometry=str(parcel_dict["geometry"]),
        )
        for parcel_dict in tqdm(parcels)
    ]


def create_owner_objects(owner):
    group, _ = OwnerGroup.objects.get_or_create(id=owner["group"])
    Owner.objects.create(
        prop_id=owner["prop_id"],
        loc_id=owner["loc_id"],
        fy=owner["fy"],
        use_code=owner["use_code"],
        city=owner["city"],
        owner1=owner["owner1"],
        own_addr=owner["own_addr"],
        own_city=owner["own_city"],
        own_state=owner["own_state"],
        own_zip=owner["own_zip"],
        co=owner["co"],
        zip=owner["zip"],
        name_address=owner["name_address"],
        group=group,
        id_corp=owner["id_corp"],
        count=owner["count"],
    )


def import_owners(filename, chunksize=default_chunksize):
    owners_file = os.path.join(DEDUPLICATIONS_DIR, filename)
    with pd.read_csv(
        owners_file,
        sep="|",
        converters={
            "prop_id": str,
            "loc_id": str,
            "fy": int,
            "use_code": str,
            "city": str,
            "owner1": str,
            "own_addr": str,
            "own_state": str,
            "own_zip": str,
            "co": str,
            "zip": str,
            "name_address": str,
            "group": str,
            "id_corp": str,
            "count": int,
        },
        chunksize=chunksize,
    ) as reader:
        for df in reader:
            owners = df.to_dict("records")
            [create_owner_objects(owner) for owner in tqdm(owners)]


def create_corp_objects(corp):
    group, _ = OwnerGroup.objects.get_or_create(id=corp["group_network"])
    try:
        Corp.objects.create(id=corp["id"], name=corp["entityname"], group=group)
    except IntegrityError:
        existing_corp = Corp.objects.get(id=corp["id"])
        if (
            existing_corp.name != corp["entityname"]
            or existing_corp.group.id != group.id
        ):
            raise ValueError(
                "Corporation with ID %s already exists. Mismatched values expected: %s"
                % (corp["id"], corp)
            )
        else:
            pass


def import_corps(filename):
    corps_file = os.path.join(DEDUPLICATIONS_DIR, filename)
    df = pd.read_csv(
        corps_file,
        sep="|",
        converters={"id": str, "name": str, "group_network": str},
    )
    corps = df.to_dict("records")
    [create_corp_objects(corp) for corp in tqdm(corps)]
