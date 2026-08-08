from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import re

app = FastAPI(
    title="SmartGeoAI",
    description="Intelligent Address Resolution & Geospatial Intelligence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

database = pd.DataFrame()


# ============================================================
# LOAD EXCEL DATABASE
# ============================================================

def load_database():

    global database

    if not os.path.exists(DATA_DIR):
        print("WARNING: data folder not found.")
        return

    excel_files = [
        file
        for file in os.listdir(DATA_DIR)
        if file.lower().endswith((".xlsx", ".xls"))
    ]

    if not excel_files:
        print("WARNING: No Excel file found in data folder.")
        return

    excel_file = os.path.join(
        DATA_DIR,
        excel_files[0]
    )

    try:

        database = pd.read_excel(
            excel_file
        )

        database.columns = [
            str(column).strip()
            for column in database.columns
        ]

        print("=" * 60)
        print("SmartGeoAI Database Loaded")
        print("=" * 60)
        print("File:", excel_file)
        print("Rows:", len(database))
        print("Columns:", list(database.columns))
        print("=" * 60)

    except Exception as error:

        print("ERROR loading Excel:")
        print(error)

        database = pd.DataFrame()


load_database()


# ============================================================
# REQUEST MODEL
# ============================================================

class AddressRequest(BaseModel):

    address: str


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(names):

    if database.empty:
        return None

    for column in database.columns:

        column_name = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
        )

        for name in names:

            search_name = (
                str(name)
                .strip()
                .lower()
                .replace(" ", "")
                .replace("_", "")
            )

            if column_name == search_name:
                return column

    return None


# ============================================================
# EXTRACT PINCODE
# ============================================================

def extract_pincode(address):

    match = re.search(
        r"\b[1-9][0-9]{5}\b",
        address
    )

    if match:
        return match.group(0)

    return None


# ============================================================
# EXTRACT LANDMARK
# ============================================================

def extract_landmark(address):

    patterns = [
        r"near\s+(.+?)(?:,|\s+\d{6}|$)",
        r"opposite\s+(.+?)(?:,|\s+\d{6}|$)",
        r"beside\s+(.+?)(?:,|\s+\d{6}|$)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            address,
            re.IGNORECASE
        )

        if match:

            return (
                match.group(1)
                .strip()
                .title()
            )

    return "Not identified"


# ============================================================
# EXTRACT CITY
# ============================================================

def extract_city(address):

    parts = [
        part.strip()
        for part in address.split(",")
        if part.strip()
    ]

    ignored_states = [
        "andhra pradesh",
        "telangana",
        "karnataka",
        "tamil nadu",
        "kerala"
    ]

    for part in parts:

        if re.search(
            r"\b[1-9][0-9]{5}\b",
            part
        ):
            continue

        lower = part.lower()

        if lower in ignored_states:
            continue

        if lower.startswith("near "):
            continue

        if lower.startswith("opposite "):
            continue

        if lower.startswith("beside "):
            continue

        return part.title()

    return "Not identified"


# ============================================================
# FIND PINCODE ROW
# ============================================================

def find_pincode_row(pincode):

    if database.empty:
        return None

    pincode_column = find_column([
        "pincode",
        "pin code"
    ])

    if pincode_column is None:
        return None

    try:

        values = (
            database[pincode_column]
            .astype(str)
            .str.extract(r"(\d{6})")[0]
        )

        matches = database[
            values == str(pincode)
        ]

        if len(matches) > 0:
            return matches.iloc[0]

    except Exception as error:

        print(
            "Pincode search error:",
            error
        )

    return None


# ============================================================
# SAFE VALUE
# ============================================================

def safe_value(value):

    try:

        if pd.isna(value):
            return None

    except Exception:
        pass

    return value


# ============================================================
# GET COORDINATES
# ============================================================

def get_coordinates(row):

    if row is None:
        return None, None

    latitude_column = find_column([
        "latitude",
        "lat"
    ])

    longitude_column = find_column([
        "longitude",
        "lon",
        "lng",
        "long"
    ])

    latitude = None
    longitude = None

    try:

        if latitude_column:

            value = safe_value(
                row[latitude_column]
            )

            if value is not None:
                latitude = float(value)

    except Exception:

        latitude = None

    try:

        if longitude_column:

            value = safe_value(
                row[longitude_column]
            )

            if value is not None:
                longitude = float(value)

    except Exception:

        longitude = None

    return latitude, longitude


# ============================================================
# ADDRESS RESOLUTION
# ============================================================

def resolve_address_logic(address):

    pincode = extract_pincode(address)

    landmark = extract_landmark(address)

    city = extract_city(address)

    row = None

    if pincode:

        row = find_pincode_row(
            pincode
        )

    district = "Not available"
    state = "Not available"

    latitude = None
    longitude = None

    if row is not None:

        district_column = find_column([
            "district",
            "district name",
            "districtname"
        ])

        state_column = find_column([
            "state",
            "state name",
            "statename"
        ])

        if district_column:

            value = safe_value(
                row[district_column]
            )

            if value is not None:
                district = str(value)

        if state_column:

            value = safe_value(
                row[state_column]
            )

            if value is not None:
                state = str(value)

        latitude, longitude = get_coordinates(
            row
        )

    # ========================================================
    # CONFIDENCE
    # ========================================================

    score = 0

    evidence = []

    if row is not None:

        score += 40

        evidence.append(
            "Pincode matched with database"
        )

    if (
        latitude is not None
        and
        longitude is not None
    ):

        score += 30

        evidence.append(
            "Coordinates available"
        )

    if landmark != "Not identified":

        score += 15

        evidence.append(
            "Landmark identified"
        )

    if city != "Not identified":

        score += 15

        evidence.append(
            "City identified"
        )

    if score >= 80:

        level = "HIGH"
        decision = "Auto-confirm"

    elif score >= 50:

        level = "MEDIUM"
        decision = "Review recommended"

    else:

        level = "LOW"
        decision = "Manual verification required"

    # ========================================================
    # NORMALIZED ADDRESS
    # ========================================================

    normalized_parts = []

    if landmark != "Not identified":

        normalized_parts.append(
            "Near " + landmark
        )

    if city != "Not identified":

        normalized_parts.append(
            city
        )

    if district != "Not available":

        normalized_parts.append(
            district
        )

    if state != "Not available":

        normalized_parts.append(
            state
        )

    if pincode:

        normalized_parts.append(
            pincode
        )

    normalized_address = ", ".join(
        normalized_parts
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "success": True,

        "project": "SmartGeoAI",

        "original_address": address,

        "address_results": {

            "original": address,

            "landmark": landmark,

            "city": city,

            "state": state,

            "pincode": pincode,

            "district": district,

            "latitude": latitude,

            "longitude": longitude

        },

        "normalized_address":
            normalized_address,

        "confidence": {

            "score": score,

            "level": level,

            "decision": decision,

            "evidence": evidence

        },

        "pincode_validation": {

            "valid": row is not None,

            "pincode": pincode,

            "district": district,

            "state": state,

            "latitude": latitude,

            "longitude": longitude

        }

    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "project": "SmartGeoAI",

        "status":
            "Backend running successfully",

        "message":
            "Use POST /resolve_address"

    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status": "online",

        "project": "SmartGeoAI",

        "database_loaded":
            not database.empty,

        "rows":
            len(database)

    }


# ============================================================
# RESOLVE ADDRESS API
# ============================================================

@app.post("/resolve_address")
def resolve_address(
    request: AddressRequest
):

    address = request.address.strip()

    if not address:

        return {

            "success": False,

            "message":
                "Address cannot be empty"

        }

    try:

        return resolve_address_logic(
            address
        )

    except Exception as error:

        print(
            "Address resolution error:",
            error
        )

        return {

            "success": False,

            "message":
                "Address resolution failed",

            "error":
                str(error)

        }


print()
print("=" * 60)
print("SMARTGEOAI BACKEND READY")
print("=" * 60)
print("API  : http://127.0.0.1:8000")
print("DOCS : http://127.0.0.1:8000/docs")
print("=" * 60)
print()
@app.get("/app")
def frontend():
    index_file = os.path.join(
        FRONTEND_DIR,
        "index.html"
    )

    if os.path.exists(index_file):
        return FileResponse(index_file)

    return {
        "error": "frontend/index.html not found",
        "path": index_file
    }