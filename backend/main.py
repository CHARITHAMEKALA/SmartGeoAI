from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import pandas as pd
import os
import re


# ============================================================
# SMARTGEOAI APPLICATION
# ============================================================

app = FastAPI(
    title="SmartGeoAI",
    description="Intelligent Address Resolution and Geospatial Validation",
    version="2.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# PROJECT PATHS
# ============================================================

BACKEND_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    BACKEND_DIR
)

DATA_DIR = os.path.join(
    PROJECT_DIR,
    "data"
)

INDEX_FILE = os.path.join(
    PROJECT_DIR,
    "index.html"
)


# ============================================================
# DATABASE
# ============================================================

pincode_df = None


def load_database():

    global pincode_df

    print()
    print("=" * 70)
    print("SMARTGEOAI DATABASE")
    print("=" * 70)

    if not os.path.exists(DATA_DIR):

        print("ERROR: data folder not found")
        print("Expected:", DATA_DIR)

        return

    excel_files = []

    for filename in os.listdir(DATA_DIR):

        if filename.lower().endswith(
            (".xlsx", ".xls")
        ):

            excel_files.append(
                os.path.join(
                    DATA_DIR,
                    filename
                )
            )

    if not excel_files:

        print("ERROR: No Excel file found")
        print("Put your Excel file inside:")
        print(DATA_DIR)

        return

    excel_file = excel_files[0]

    print(
        "Loading:",
        os.path.basename(excel_file)
    )

    try:

        pincode_df = pd.read_excel(
            excel_file
        )

        pincode_df.columns = [
            str(column).strip()
            for column in pincode_df.columns
        ]

        print(
            "Rows:",
            len(pincode_df)
        )

        print(
            "Columns:",
            list(pincode_df.columns)
        )

        print(
            "Database loaded successfully."
        )

    except Exception as error:

        print(
            "ERROR loading Excel:",
            error
        )

        pincode_df = None

    print("=" * 70)
    print()


# Load database when server starts
load_database()


# ============================================================
# REQUEST MODEL
# ============================================================

class AddressRequest(BaseModel):

    address: str


# ============================================================
# COLUMN NORMALIZATION
# ============================================================

def clean_column_name(
    value
):

    return (
        str(value)
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .replace(".", "")
        .strip()
    )


def find_column(
    possible_names
):

    if pincode_df is None:

        return None

    wanted = [
        clean_column_name(name)
        for name in possible_names
    ]

    for column in pincode_df.columns:

        current = clean_column_name(
            column
        )

        if current in wanted:

            return column

    return None


# ============================================================
# GET VALUE FROM DATABASE
# ============================================================

def get_value(
    row,
    possible_names
):

    column = find_column(
        possible_names
    )

    if column is None:

        return None

    try:

        value = row[column]

        if pd.isna(value):

            return None

        return str(value).strip()

    except Exception:

        return None


# ============================================================
# GET NUMERIC VALUE
# ============================================================

def get_number(
    row,
    possible_names
):

    column = find_column(
        possible_names
    )

    if column is None:

        return None

    try:

        value = row[column]

        if pd.isna(value):

            return None

        return float(value)

    except Exception:

        return None


# ============================================================
# PINCODE NORMALIZATION
# ============================================================

def normalize_pincode(
    value
):

    if value is None:

        return None

    match = re.search(
        r"\b\d{6}\b",
        str(value)
    )

    if match:

        return match.group()

    return None


# ============================================================
# FIND PINCODE IN DATABASE
# ============================================================

def search_pincode(
    pincode
):

    if pincode_df is None:

        return None

    column = find_column(
        [
            "pincode",
            "pin",
            "pin_code",
            "postalcode",
            "postal_code",
            "postcode"
        ]
    )

    if column is None:

        return None

    target = normalize_pincode(
        pincode
    )

    if target is None:

        return None

    for _, row in pincode_df.iterrows():

        current = normalize_pincode(
            row[column]
        )

        if current == target:

            return row

    return None


# ============================================================
# CITY DETECTION
# ============================================================

CITY_MAP = {

    "vijayawada":
        "Vijayawada",

    "guntur":
        "Guntur",

    "hyderabad":
        "Hyderabad",

    "visakhapatnam":
        "Visakhapatnam",

    "vizag":
        "Visakhapatnam",

    "tenali":
        "Tenali",

    "tirupati":
        "Tirupati",

    "nellore":
        "Nellore",

    "kakinada":
        "Kakinada",

    "rajahmundry":
        "Rajahmundry",

    "kurnool":
        "Kurnool",

    "kadapa":
        "Kadapa",

    "ongole":
        "Ongole",

    "eluru":
        "Eluru",

    "warangal":
        "Warangal",

    "amaravati":
        "Amaravati",

    "machilipatnam":
        "Machilipatnam",

    "anantapur":
        "Anantapur",

    "chittoor":
        "Chittoor",

    "srikakulam":
        "Srikakulam"
}


def detect_city(
    address
):

    text = address.lower()

    for key, city in CITY_MAP.items():

        pattern = (
            r"\b"
            + re.escape(key)
            + r"\b"
        )

        if re.search(
            pattern,
            text
        ):

            return city

    return None


# ============================================================
# LANDMARK DETECTION
# ============================================================

def detect_landmark(
    address
):

    patterns = [

        r"\bnear\s+(.+?)(?=\s*,|\s+\d{6}\b|$)",

        r"\bopposite\s+(.+?)(?=\s*,|\s+\d{6}\b|$)",

        r"\bopp\.?\s+(.+?)(?=\s*,|\s+\d{6}\b|$)",

        r"\bbehind\s+(.+?)(?=\s*,|\s+\d{6}\b|$)",

        r"\bnearby\s+(.+?)(?=\s*,|\s+\d{6}\b|$)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            address,
            re.IGNORECASE
        )

        if match:

            landmark = (
                match.group(1)
                .strip()
                .strip(",")
            )

            if landmark:

                return landmark.title()

    return None


# ============================================================
# PARSE ADDRESS
# ============================================================

def parse_address(
    address
):

    pincode_match = re.search(
        r"\b\d{6}\b",
        address
    )

    pincode = None

    if pincode_match:

        pincode = (
            pincode_match.group()
        )

    return {

        "original":
            address,

        "landmark":
            detect_landmark(
                address
            ),

        "city":
            detect_city(
                address
            ),

        "pincode":
            pincode
    }


# ============================================================
# PINCODE VALIDATION
# ============================================================

def validate_pincode(
    pincode
):

    row = search_pincode(
        pincode
    )

    if row is None:

        return {

            "valid":
                False,

            "pincode":
                normalize_pincode(
                    pincode
                ),

            "district":
                None,

            "state":
                None,

            "latitude":
                None,

            "longitude":
                None
        }

    district = get_value(
        row,
        [
            "district",
            "districtname",
            "district_name"
        ]
    )

    state = get_value(
        row,
        [
            "state",
            "statename",
            "state_name"
        ]
    )

    latitude = get_number(
        row,
        [
            "latitude",
            "lat"
        ]
    )

    longitude = get_number(
        row,
        [
            "longitude",
            "long",
            "lng"
        ]
    )

    return {

        "valid":
            True,

        "pincode":
            normalize_pincode(
                pincode
            ),

        "district":
            district,

        "state":
            state,

        "latitude":
            latitude,

        "longitude":
            longitude
    }


# ============================================================
# CONFIDENCE SCORE
# ============================================================

def calculate_confidence(
    parsed,
    validation
):

    score = 0

    evidence = []


    # PINCODE
    if validation["valid"]:

        score += 50

        evidence.append(
            "✓ Pincode matched with database"
        )

    else:

        evidence.append(
            "✗ Pincode verification failed"
        )


    # COORDINATES
    if (
        validation["latitude"]
        is not None
        and
        validation["longitude"]
        is not None
    ):

        score += 25

        evidence.append(
            "✓ Coordinates available"
        )

    else:

        evidence.append(
            "✗ Coordinates unavailable"
        )


    # LANDMARK
    if parsed["landmark"]:

        score += 10

        evidence.append(
            "✓ Landmark identified"
        )

    else:

        evidence.append(
            "⚠ Landmark not identified"
        )


    # CITY
    if parsed["city"]:

        score += 15

        evidence.append(
            "✓ City identified"
        )

    else:

        evidence.append(
            "⚠ City not identified"
        )


    # LEVEL
    if score >= 80:

        level = "HIGH"

        decision = "Auto-confirm"

    elif score >= 50:

        level = "MEDIUM"

        decision = "Needs verification"

    else:

        level = "LOW"

        decision = "Do not auto-confirm"


    return {

        "score":
            score,

        "level":
            level,

        "decision":
            decision,

        "evidence":
            evidence
    }


# ============================================================
# NORMALIZED ADDRESS
# ============================================================

def create_normalized_address(
    parsed,
    validation
):

    parts = []


    if parsed["landmark"]:

        parts.append(
            "Near " +
            parsed["landmark"]
        )


    if parsed["city"]:

        parts.append(
            parsed["city"]
        )


    if validation["state"]:

        parts.append(
            validation["state"]
        )


    if validation["pincode"]:

        parts.append(
            validation["pincode"]
        )


    return ", ".join(parts)


# ============================================================
# ROOT - SERVE FRONTEND
# ============================================================

@app.get("/")
def home():

    if not os.path.exists(
        INDEX_FILE
    ):

        return {

            "project":
                "SmartGeoAI",

            "status":
                "Backend running successfully",

            "message":
                "index.html not found",

            "expected_file":
                INDEX_FILE
        }

    return FileResponse(
        INDEX_FILE
    )


# ============================================================
# RUN STATUS
# ============================================================

@app.get("/run")
def run():

    return {

        "message":
            "SmartGeoAI backend is running",

        "endpoint":
            "/resolve_address",

        "status":
            "online"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "online",

        "project":
            "SmartGeoAI",

        "database_loaded":
            pincode_df is not None,

        "rows":
            (
                len(pincode_df)
                if pincode_df is not None
                else 0
            )
    }


# ============================================================
# ADDRESS RESOLUTION API
# ============================================================

@app.post("/resolve_address")
def resolve_address(
    request: AddressRequest
):

    address = (
        request.address
        .strip()
    )


    # EMPTY ADDRESS
    if not address:

        return {

            "success":
                False,

            "message":
                "Address cannot be empty"
        }


    # PARSE
    parsed = parse_address(
        address
    )


    # DATABASE VALIDATION
    validation = validate_pincode(
        parsed["pincode"]
    )


    # CONFIDENCE
    confidence = calculate_confidence(
        parsed,
        validation
    )


    # NORMALIZED ADDRESS
    normalized = (
        create_normalized_address(
            parsed,
            validation
        )
    )


    # FINAL RESPONSE
    return {

        "success":
            True,

        "project":
            "SmartGeoAI",

        "original_address":
            address,

        "address_results": {

            "original":
                address,

            "landmark":
                (
                    parsed["landmark"]
                    or "Not detected"
                ),

            "city":
                (
                    parsed["city"]
                    or "Not detected"
                ),

            "state":
                (
                    validation["state"]
                    or "Not detected"
                ),

            "pincode":
                (
                    validation["pincode"]
                    or "Not available"
                ),

            "district":
                (
                    validation["district"]
                    or "Not available"
                ),

            "latitude":
                validation["latitude"],

            "longitude":
                validation["longitude"]
        },

        "normalized_address":
            normalized,

        "confidence":
            confidence,

        "pincode_validation":
            validation
    }