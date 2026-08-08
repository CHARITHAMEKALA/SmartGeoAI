from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import re

app = FastAPI(title="SmartGeoAI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

pincode_df = None


def load_database():
    global pincode_df

    if not os.path.exists(DATA_DIR):
        print("Data folder not found")
        return

    files = os.listdir(DATA_DIR)

    excel_file = None

    for file in files:
        if file.lower().endswith((".xlsx", ".xls")):
            excel_file = os.path.join(DATA_DIR, file)
            break

    if excel_file is None:
        print("No Excel file found in data folder")
        return

    try:
        pincode_df = pd.read_excel(excel_file)

        pincode_df.columns = [
            str(c).strip()
            for c in pincode_df.columns
        ]

        print("Database loaded successfully")
        print("File:", excel_file)
        print("Rows:", len(pincode_df))
        print("Columns:", list(pincode_df.columns))

    except Exception as e:
        print("Database error:", e)
        pincode_df = None


load_database()


class AddressRequest(BaseModel):
    address: str


def normalize_pin(value):
    if value is None:
        return None

    text = str(value).strip()

    match = re.search(r"\d{6}", text)

    if match:
        return match.group()

    return None


def find_column(possible_names):
    if pincode_df is None:
        return None

    for column in pincode_df.columns:

        cleaned = (
            str(column)
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

        for name in possible_names:

            target = (
                name.lower()
                .replace(" ", "")
                .replace("_", "")
                .replace("-", "")
            )

            if cleaned == target:
                return column

    return None


def get_value(row, names):

    column = find_column(names)

    if column is None:
        return None

    value = row[column]

    if pd.isna(value):
        return None

    return str(value).strip()


def get_number(row, names):

    column = find_column(names)

    if column is None:
        return None

    try:
        value = row[column]

        if pd.isna(value):
            return None

        return float(value)

    except:
        return None


def search_pincode(pincode):

    if pincode_df is None:
        return None

    pin_column = find_column([
        "pincode",
        "pin",
        "postalcode",
        "postcode"
    ])

    if pin_column is None:
        return None

    target = normalize_pin(pincode)

    if target is None:
        return None

    for _, row in pincode_df.iterrows():

        current = normalize_pin(
            row[pin_column]
        )

        if current == target:
            return row

    return None


def detect_city(address):

    cities = {
        "vijayawada": "Vijayawada",
        "guntur": "Guntur",
        "hyderabad": "Hyderabad",
        "visakhapatnam": "Visakhapatnam",
        "vizag": "Visakhapatnam",
        "tenali": "Tenali",
        "tirupati": "Tirupati",
        "nellore": "Nellore",
        "kakinada": "Kakinada",
        "rajahmundry": "Rajahmundry",
        "kurnool": "Kurnool",
        "kadapa": "Kadapa",
        "ongole": "Ongole",
        "eluru": "Eluru",
        "warangal": "Warangal",
        "amaravati": "Amaravati"
    }

    text = address.lower()

    for key, city in cities.items():

        if re.search(
            r"\b" + re.escape(key) + r"\b",
            text
        ):
            return city

    return None


def detect_landmark(address):

    patterns = [
        r"\bnear\s+(.+?)(?=\s*,|\s+\d{6}\b|$)",
        r"\bopposite\s+(.+?)(?=\s*,|\s+\d{6}\b|$)",
        r"\bopp\.?\s+(.+?)(?=\s*,|\s+\d{6}\b|$)",
        r"\bbehind\s+(.+?)(?=\s*,|\s+\d{6}\b|$)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            address,
            re.IGNORECASE
        )

        if match:

            value = match.group(1).strip()

            if value:
                return value

    return None


def parse_address(address):

    pin_match = re.search(
        r"\b\d{6}\b",
        address
    )

    pincode = (
        pin_match.group()
        if pin_match
        else None
    )

    return {
        "original": address,
        "landmark": detect_landmark(address),
        "city": detect_city(address),
        "pincode": pincode
    }


def validate_address(parsed):

    row = search_pincode(
        parsed["pincode"]
    )

    if row is None:

        return {
            "valid": False,
            "pincode": parsed["pincode"],
            "district": None,
            "state": None,
            "latitude": None,
            "longitude": None
        }

    district = get_value(
        row,
        [
            "district",
            "districtname"
        ]
    )

    state = get_value(
        row,
        [
            "state",
            "statename"
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
            "longitude",
            "lng"
        ]
    )

    return {
        "valid": True,
        "pincode": normalize_pin(
            parsed["pincode"]
        ),
        "district": district,
        "state": state,
        "latitude": latitude,
        "longitude": longitude
    }


def calculate_confidence(
    parsed,
    validation
):

    score = 0
    evidence = []

    if validation["valid"]:

        score += 50

        evidence.append(
            "✓ Pincode matched with database"
        )

    else:

        evidence.append(
            "✗ Pincode verification failed"
        )

    if (
        validation["latitude"] is not None
        and
        validation["longitude"] is not None
    ):

        score += 25

        evidence.append(
            "✓ Coordinates available"
        )

    else:

        evidence.append(
            "✗ Coordinates unavailable"
        )

    if parsed["landmark"]:

        score += 10

        evidence.append(
            "✓ Landmark identified"
        )

    else:

        evidence.append(
            "⚠ Landmark not identified"
        )

    if parsed["city"]:

        score += 15

        evidence.append(
            "✓ City identified"
        )

    else:

        evidence.append(
            "⚠ City not identified"
        )

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
        "score": score,
        "level": level,
        "decision": decision,
        "evidence": evidence
    }


@app.get("/")
def root():

    return {
        "project": "SmartGeoAI",
        "status": "Backend running successfully"
    }


@app.get("/health")
def health():

    return {
        "status": "online",
        "database_loaded": pincode_df is not None,
        "rows": (
            len(pincode_df)
            if pincode_df is not None
            else 0
        )
    }


@app.post("/resolve_address")
def resolve_address(
    request: AddressRequest
):

    address = request.address.strip()

    if not address:

        return {
            "success": False,
            "message": "Address cannot be empty"
        }

    parsed = parse_address(address)

    validation = validate_address(parsed)

    if validation["state"]:
        state = validation["state"]
    else:
        state = "Not detected"

    normalized_parts = []

    if parsed["landmark"]:
        normalized_parts.append(
            "Near " +
            parsed["landmark"]
        )

    if parsed["city"]:
        normalized_parts.append(
            parsed["city"]
        )

    if state != "Not detected":
        normalized_parts.append(
            state
        )

    if validation["pincode"]:
        normalized_parts.append(
            validation["pincode"]
        )

    normalized_address = ", ".join(
        normalized_parts
    )

    confidence = calculate_confidence(
        parsed,
        validation
    )

    return {

        "success": True,

        "original_address": address,

        "address_results": {

            "landmark":
                parsed["landmark"]
                or "Not detected",

            "city":
                parsed["city"]
                or "Not detected",

            "state":
                state,

            "pincode":
                validation["pincode"]
                or "Not available",

            "district":
                validation["district"]
                or "Not available",

            "latitude":
                validation["latitude"],

            "longitude":
                validation["longitude"]
        },

        "normalized_address":
            normalized_address,

        "confidence":
            confidence
    }


@app.get("/run")
def run():

    return {
        "message":
            "SmartGeoAI backend is running",
        "endpoint":
            "/resolve_address"
    }