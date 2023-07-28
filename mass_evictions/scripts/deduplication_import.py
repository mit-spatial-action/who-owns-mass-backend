import os
from tqdm import tqdm
import geopandas as gpd
from config.settings import DEDUPLICATIONS_DIR
from mass_evictions.models import Parcel


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


def import_owners(filename):
    owners_file = os.path.join(DEDUPLICATIONS_DIR, filename)
    pass
