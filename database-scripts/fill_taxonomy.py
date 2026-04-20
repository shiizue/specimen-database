import sqlite3
import urllib.request
import json
import time

# ===========================================================================
# CONFIGURATION
# ===========================================================================

db_path = "database-scripts/cunha_invertebrate_specimens.db"

# Create a dictionary to map the columns to the keys that GBIF will return

TAXONOMY_MAP = {
    "phylum": "phylum",
    "class_name": "class",  # use "class_name" because "class" is used in Python
    "subclass": "subclass",  # GBIF won't always return subclass
    "family": "family",
    "taxon_order": "order",  # use "taxon_order" because "order" is used in Python
}
CONFIDENCE_THRESHOLD = 90  # start with a confidence score of 90 for matches

REQUEST_DELAY = 0.3  # add a delay between API calls as to not overload server

# ===========================================================================
# STEP 1: ADD MISSING COLUMNS TO THE DATABASE
# ===========================================================================
# We need to add new columns for different levels
# Some of which were removed during cleaning (e.g. family)


def add_missing_cols(cursor):
    """Add any taxonomy columns that don't already exist in SpecimenData."""
    print("\n--- Checking for missing taxonomy columns... ---")
    for db_col in TAXONOMY_MAP.keys():
        try:
            cursor.execute(f"ALTER TABLE SpecimenData ADD COLUMN {db_col} TEXT;")
            print(f"  Added new column to SpecimenData: {db_col}")
        except sqlite3.OperationalError:
            # Column already exists — this is expected for phylum, class_name, subclass
            print(f"  Column already exists in Specimen Data. Skipping: {db_col}")


# ===========================================================================
# STEP 2: FETCH TAXONOMY FROM GBIF
# ===========================================================================

# GBIF takes a name as the query and returns the most confident taxonomy matches
# we can query with the full species name, or fall back to genus


def fetch_gbif_taxonomy(genus, species):
    """
    Query the GBIF species match API and return a dict of taxonomy fields,
    or None if no confident match was found.
    """

    # If species name is unknown or incomplete, fall back to using the Genus as the search term
    species_is_unknown = not species or str(species).strip().lower() in (
        "sp.",
        "sp",
        "nan",
        "none",
        "",
    )

    if species_is_unknown:
        search_name = str(genus).strip()
    else:
        # Combine genus + species into a full name
        search_name = f"{str(genus).strip()} {str(species).strip()}"

    # GBIF doesn't require an API key, you can just build a URL for the query
    base_url = "https://api.gbif.org/v1/species/match"
    query = urllib.parse.urlencode({"name": search_name, "verbose": "false"})
    url = f"{base_url}?{query}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"    [API ERROR] Could not reach GBIF for search '{search_name}': {e}")
        return None
