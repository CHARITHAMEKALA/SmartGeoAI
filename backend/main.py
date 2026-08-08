import os
import re
import requests
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI(
    title="SmartGeoAI",
    description="AI Address Resolution System"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
DATA_DIR = os.path.join(PROJECT_DIR, "data")


pincode_df = None
PINCODE_FILE = None


if os.path.exists(DATA_DIR):

    for filename in os.listdir(DATA_DIR):

        if filename.lower().endswith((".xlsx", ".xls")):

            PINCODE_FILE = os.path.join(
                DATA_DIR,
                filename
            )

            break


if PINCODE_FILE:

    try:

        pincode_df = pd.read_excel(
            PINCODE_FILE
        )

        pincode_df.columns = [
            str(column).strip()
            for column in pincode_df.columns
        ]

        print("Pincode database loaded:")
        print(PINCODE_FILE)
        print("Rows:", len(pincode_df))
        print("Columns:", list(pincode_df.columns))

    except Exception as error:

        print("Excel loading error:", error)

else:

    print("WARNING: Pincode Excel file not found.")


class AddressRequest(BaseModel):
    address: str


def find_column(names):

    if pincode_df is None:
        return None

    for column in pincode_df.columns:

        clean_column = (
            str(column)
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
            .replace("*", "")
        )

        for name in names:

            clean_name = (
                str(name)
                .lower()
                .replace(" ", "")
                .replace("_", "")
                .replace("-", "")
                .replace("*", "")
            )

            if clean_column == clean_name:
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

    value = row[column]

    if pd.isna(value):
        return None

    try:
        return float(value)

    except Exception:
        return None


def find_pincode(pincode):

    if pincode_df is None:
        return None

    column = find_column(
        [
            "pincode",
            "pin",
            "pincodenumber",
            "pincode number"
        ]
    )

    if column is None:
        return None

    target = str(pincode).strip()

    for _, row in pincode_df.iterrows():

        value = row[column]

        if pd.isna(value):
            continue

        try:

            current = str(
                int(float(value))
            )

        except Exception:

            current = str(value).strip()

        if current == target:
            return row

    return None


def parse_address(address):

    cleaned = address.strip().lower()

    cleaned = re.sub(
        r"\bopp\b",
        "opposite",
        cleaned
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    ).strip()


    match = re.search(
        r"\b\d{6}\b",
        cleaned
    )

    if match:
        pincode = match.group()

    else:
        pincode = None


    cities = {
        "hyderabad": "Hyderabad",
        "hyd": "Hyderabad",
        "secunderabad": "Secunderabad",
        "vijayawada": "Vijayawada",
        "guntur": "Guntur",
        "tenali": "Tenali",
        "warangal": "Warangal",
        "visakhapatnam": "Visakhapatnam",
        "vizag": "Visakhapatnam"
    }


    city = None

    for key, value in cities.items():

        if re.search(
            r"\b" + re.escape(key) + r"\b",
            cleaned
        ):

            city = value
            break


    landmark = None

    landmark_match = re.search(
        r"(?:near|opposite)\s+(.+?)(?:\s+(?:hyderabad|hyd|secunderabad|vijayawada|guntur|tenali|warangal|vizag|visakhapatnam)|\s+\d{6}|$)",
        cleaned,
        re.IGNORECASE
    )

    if landmark_match:

        landmark = (
            landmark_match
            .group(1)
            .strip(" ,")
        )


    return {
        "raw_address": address,
        "cleaned_address": cleaned,
        "landmark": landmark,
        "city": city,
        "state": None,
        "pincode": pincode
    }


def validate_pincode(pincode):

    if not pincode:

        return {
            "valid": False,
            "pincode": None,
            "district": None,
            "state": None,
            "latitude": None,
            "longitude": None,
            "evidence": [
                "Pincode not provided"
            ]
        }


    row = find_pincode(pincode)

    if row is None:

        return {
            "valid": False,
            "pincode": pincode,
            "district": None,
            "state": None,
            "latitude": None,
            "longitude": None,
            "evidence": [
                "Pincode not found in database"
            ]
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
            "lon",
            "lng"
        ]
    )


    evidence = [
        "Pincode exists in India directory"
    ]


    if (
        latitude is not None
        and longitude is not None
    ):

        evidence.append(
            "Location details verified"
        )

    else:

        evidence.append(
            "Coordinates unavailable"
        )


    return {
        "valid": True,
        "pincode": pincode,
        "district": district,
        "state": state,
        "latitude": latitude,
        "longitude": longitude,
        "evidence": evidence
    }


def normalize_address(parsed):

    parts = []


    if parsed["landmark"]:

        parts.append(
            "Near "
            + parsed["landmark"]
            .strip(" ,")
            .title()
        )


    if parsed["city"]:
        parts.append(parsed["city"])


    if parsed["state"]:
        parts.append(parsed["state"])


    if parsed["pincode"]:
        parts.append(parsed["pincode"])


    formatted = ", ".join(parts)


    return {
        **parsed,
        "formatted_address": formatted
    }


def verify_landmark(
    landmark,
    latitude,
    longitude
):

    if not landmark:

        return {
            "found": False,
            "landmarks": [],
            "evidence": [],
            "count": 0,
            "message": "No landmark provided"
        }


    if (
        latitude is None
        or longitude is None
    ):

        return {
            "found": False,
            "landmarks": [],
            "evidence": [],
            "count": 0,
            "message": "Landmark verification requires coordinates"
        }


    try:

        url = (
            "https://nominatim.openstreetmap.org/search"
        )


        search_query = (
            landmark
            + ", "
            + str(latitude)
            + ", "
            + str(longitude)
        )


        params = {
            "q": search_query,
            "format": "json",
            "limit": 5,
            "addressdetails": 1
        }


        headers = {
            "User-Agent": "SmartGeoAI/1.0"
        }


        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=5
        )


        if response.status_code != 200:

            return {
                "found": False,
                "landmarks": [],
                "evidence": [
                    "OpenStreetMap search failed"
                ],
                "count": 0,
                "message": "OpenStreetMap unavailable"
            }


        results = response.json()


        if not results:

            return {
                "found": False,
                "landmarks": [],
                "evidence": [
                    "Landmark not found on OpenStreetMap"
                ],
                "count": 0,
                "message": "Landmark not found"
            }


        landmarks = []


        for item in results:

            landmarks.append(
                {
                    "name": item.get(
                        "display_name",
                        landmark
                    ),
                    "latitude": item.get(
                        "lat"
                    ),
                    "longitude": item.get(
                        "lon"
                    ),
                    "type": item.get(
                        "type"
                    )
                }
            )


        return {
            "found": True,
            "landmarks": landmarks,
            "evidence": [
                "Landmark found on OpenStreetMap"
            ],
            "count": len(landmarks),
            "message": "Landmark verified"
        }


    except Exception as error:

        return {
            "found": False,
            "landmarks": [],
            "evidence": [
                "Landmark search unavailable"
            ],
            "count": 0,
            "message": str(error)
        }


def calculate_confidence(
    parsed,
    validation,
    location,
    landmark_result
):

    score = 0

    evidence = []


    if validation["valid"]:

        score += 40

        evidence.append(
            "Pincode matched with database"
        )

    else:

        evidence.append(
            "Pincode verification failed"
        )


    if location["found"]:

        score += 30

        evidence.append(
            "Coordinates available"
        )

    else:

        evidence.append(
            "Coordinates unavailable"
        )


    if landmark_result["found"]:

        score += 20

        evidence.append(
            "Landmark verified"
        )

    elif parsed["landmark"]:

        score += 5

        evidence.append(
            "Landmark identified but not verified"
        )

    else:

        evidence.append(
            "Landmark evidence unavailable"
        )


    if (
        parsed["city"]
        and parsed["pincode"]
        and validation["valid"]
    ):

        score += 10

        evidence.append(
            "Address information complete"
        )

    else:

        evidence.append(
            "Address information incomplete or pincode invalid"
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
def home():

    index_file = os.path.join(
        FRONTEND_DIR,
        "index.html"
    )

    return FileResponse(
        os.path.abspath(index_file)
    )


@app.post("/resolve_address")
def resolve_address(
    request: AddressRequest
):

    address = request.address


    parsed = parse_address(
        address
    )


    validation = validate_pincode(
        parsed["pincode"]
    )


    if validation["state"]:

        parsed["state"] = (
            validation["state"]
        )


    normalized = normalize_address(
        parsed
    )


    if (
        validation["valid"]
        and validation["latitude"] is not None
        and validation["longitude"] is not None
    ):

        location = {

            "found": True,

            "latitude":
                validation["latitude"],

            "longitude":
                validation["longitude"],

            "display_name":
                normalized[
                    "formatted_address"
                ],

            "accuracy":
                "PINCODE LEVEL",

            "source":
                "Pincode Database"
        }

    else:

        location = {

            "found": False,

            "latitude": None,

            "longitude": None,

            "display_name": None,

            "accuracy": "LOW",

            "source":
                "Pincode Database"
        }


    landmark_result = verify_landmark(
        parsed["landmark"],
        location["latitude"],
        location["longitude"]
    )


    confidence = calculate_confidence(
        parsed,
        validation,
        location,
        landmark_result
    )


    return {

        "project":
            "SmartGeoAI",

        "original_address":
            address,

        "parsed_address":
            parsed,

        "normalized_address":
            normalized,

        "pincode_validation":
            validation,

        "location":
            location,

        "landmark_evidence":
            landmark_result,

        "confidence":
            confidence
    }


if os.path.exists(FRONTEND_DIR):

    app.mount(
        "/static",
        StaticFiles(
            directory=FRONTEND_DIR
        ),
        name="static"
    )