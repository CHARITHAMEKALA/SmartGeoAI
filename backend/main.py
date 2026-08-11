from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pydantic import BaseModel

import os
import re
import math
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="SmartGeoAI",
    description="AI-Powered Indian Address Resolution",
    version="1.0.0"
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
# REQUEST MODEL
# ============================================================

class AddressRequest(BaseModel):
    address: str


# ============================================================
# DATABASE
# ============================================================

database = pd.DataFrame()


def load_database():

    global database

    print()
    print("=" * 60)
    print("SMARTGEOAI DATABASE")
    print("=" * 60)

    print(
        "Data folder:",
        DATA_DIR
    )

    if not os.path.exists(DATA_DIR):

        print(
            "WARNING: data folder does not exist."
        )

        print("=" * 60)

        return


    excel_files = [

        file

        for file in os.listdir(DATA_DIR)

        if file.lower().endswith(
            (".xlsx", ".xls")
        )

    ]


    if not excel_files:

        print(
            "WARNING: No Excel file found."
        )

        print("=" * 60)

        return


    excel_path = os.path.join(
        DATA_DIR,
        excel_files[0]
    )


    try:

        database = pd.read_excel(
            excel_path
        )


        database.columns = [

            str(column).strip()

            for column
            in database.columns

        ]


        print(
            "Excel file:",
            excel_files[0]
        )

        print(
            "Rows:",
            len(database)
        )

        print(
            "Columns:",
            list(database.columns)
        )

        print(
            "Database loaded successfully."
        )


    except Exception as error:

        print(
            "ERROR loading Excel:"
        )

        print(error)

        database = pd.DataFrame()


    print("=" * 60)
    print()


load_database()


# ============================================================
# JSON SAFE VALUE
# ============================================================

def safe_value(value):

    """
    Convert Excel / pandas / numpy values
    into values that FastAPI can safely return as JSON.
    """

    if value is None:
        return None


    # pandas NaN / NaT
    try:

        if pd.isna(value):

            return None

    except Exception:

        pass


    # Python float infinity / NaN
    if isinstance(value, float):

        if not math.isfinite(value):

            return None

        return value


    # numpy integer / float
    if hasattr(value, "item"):

        try:

            converted = value.item()

            if isinstance(
                converted,
                float
            ):

                if not math.isfinite(
                    converted
                ):

                    return None

            return converted

        except Exception:

            pass


    # pandas timestamp
    if hasattr(
        value,
        "isoformat"
    ):

        try:

            return value.isoformat()

        except Exception:

            pass


    # Everything else
    return value


# ============================================================
# SAFE STRING
# ============================================================

def safe_string(value, default="N/A"):

    value = safe_value(value)


    if value is None:

        return default


    text = str(value).strip()


    if not text:

        return default


    return text


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(possible_names):

    if database.empty:

        return None


    for column in database.columns:

        column_name = (

            str(column)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")

        )


        for name in possible_names:

            search_name = (

                str(name)
                .strip()
                .lower()
                .replace(" ", "")
                .replace("_", "")
                .replace("-", "")

            )


            if column_name == search_name:

                return column


    return None


# ============================================================
# GET VALUE FROM ROW
# ============================================================

def get_row_value(
    row,
    possible_names
):

    if row is None:

        return None


    column = find_column(
        possible_names
    )


    if column is None:

        return None


    try:

        return safe_value(
            row[column]
        )

    except Exception:

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

        r"\bnear\s+(.+?)(?:,|\s+\d{6}|$)",

        r"\bopposite\s+(.+?)(?:,|\s+\d{6}|$)",

        r"\bbeside\s+(.+?)(?:,|\s+\d{6}|$)",

        r"\bbehind\s+(.+?)(?:,|\s+\d{6}|$)",

        r"\bnext\s+to\s+(.+?)(?:,|\s+\d{6}|$)"

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

                return landmark


    return "Not identified"


# ============================================================
# EXTRACT CITY
# ============================================================

def extract_city(address):

    parts = [

        part.strip()

        for part
        in address.split(",")

        if part.strip()

    ]


    # Remove pincode from consideration
    clean_parts = []

    for part in parts:

        if re.fullmatch(
            r"[1-9][0-9]{5}",
            part
        ):

            continue

        clean_parts.append(part)


    if len(clean_parts) >= 2:

        # Usually city is near the end
        return clean_parts[-2]


    if len(clean_parts) == 1:

        return clean_parts[0]


    return "Not identified"


# ============================================================
# SEARCH DATABASE BY PINCODE
# ============================================================

def search_database(pincode):

    if database.empty:

        return None


    pincode_column = find_column([

        "pincode",

        "pin code",

        "pin",

        "postal code",

        "postalcode"

    ])


    if pincode_column is None:

        print(
            "WARNING: No pincode column found."
        )

        return None


    try:

        # Convert the whole column safely
        values = (

            database[pincode_column]
            .astype(str)
            .str.extract(
                r"(\d{6})"
            )[0]

        )


        matches = database[
            values == str(pincode)
        ]


        if not matches.empty:

            return matches.iloc[0]


    except Exception as error:

        print(
            "Database search error:"
        )

        print(error)


    return None


# ============================================================
# GET COORDINATES
# ============================================================

def get_coordinates(row):

    if row is None:

        return None, None


    latitude = get_row_value(
        row,
        [
            "latitude",
            "lat"
        ]
    )


    longitude = get_row_value(
        row,
        [
            "longitude",
            "lon",
            "lng"
        ]
    )


    # Convert latitude
    if latitude is not None:

        try:

            latitude = float(
                latitude
            )

            if not math.isfinite(
                latitude
            ):

                latitude = None

        except Exception:

            latitude = None


    # Convert longitude
    if longitude is not None:

        try:

            longitude = float(
                longitude
            )

            if not math.isfinite(
                longitude
            ):

                longitude = None

        except Exception:

            longitude = None


    return latitude, longitude


# ============================================================
# MAIN ADDRESS LOGIC
# ============================================================

def resolve_address_logic(address):

    print()
    print("-" * 60)

    print(
        "Resolving address:"
    )

    print(address)


    # --------------------------------------------------------
    # EXTRACT
    # --------------------------------------------------------

    pincode = extract_pincode(
        address
    )


    landmark = extract_landmark(
        address
    )


    city = extract_city(
        address
    )


    print(
        "Pincode:",
        pincode
    )

    print(
        "Landmark:",
        landmark
    )

    print(
        "City:",
        city
    )


    # --------------------------------------------------------
    # DATABASE SEARCH
    # --------------------------------------------------------

    row = None


    if pincode:

        row = search_database(
            pincode
        )


    # --------------------------------------------------------
    # DEFAULT VALUES
    # --------------------------------------------------------

    district = "N/A"

    state = "N/A"

    latitude = None

    longitude = None


    # --------------------------------------------------------
    # DATABASE DATA
    # --------------------------------------------------------

    if row is not None:

        district_value = get_row_value(
            row,
            [
                "district",
                "district name",
                "districtname"
            ]
        )


        if district_value is not None:

            district = safe_string(
                district_value
            )


        state_value = get_row_value(
            row,
            [
                "state",
                "state name",
                "statename"
            ]
        )


        if state_value is not None:

            state = safe_string(
                state_value
            )


        latitude, longitude = (
            get_coordinates(row)
        )


    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    score = 0

    evidence = []


    if pincode:

        score += 25

        evidence.append(
            "6-digit pincode detected"
        )


    if row is not None:

        score += 35

        evidence.append(
            "Pincode matched with database"
        )


    if city != "Not identified":

        score += 15

        evidence.append(
            "City/location identified"
        )


    if landmark != "Not identified":

        score += 10

        evidence.append(
            "Landmark detected"
        )


    if (
        latitude is not None
        and
        longitude is not None
    ):

        score += 15

        evidence.append(
            "GPS coordinates available"
        )


    score = min(
        score,
        100
    )


    # --------------------------------------------------------
    # LEVEL
    # --------------------------------------------------------

    if score >= 80:

        level = "HIGH"

        decision = "Auto-confirm"


    elif score >= 50:

        level = "MEDIUM"

        decision = "Review recommended"


    else:

        level = "LOW"

        decision = "Manual verification required"


    # --------------------------------------------------------
    # NORMALIZED ADDRESS
    # --------------------------------------------------------

    normalized_parts = []


    if landmark != "Not identified":

        normalized_parts.append(
            "Near " + landmark
        )


    if city != "Not identified":

        normalized_parts.append(
            city
        )


    if district != "N/A":

        normalized_parts.append(
            district
        )


    if state != "N/A":

        normalized_parts.append(
            state
        )


    if pincode:

        normalized_parts.append(
            pincode
        )


    if normalized_parts:

        normalized_address = (
            ", ".join(
                normalized_parts
            )
        )

    else:

        normalized_address = address


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    result = {

        "success": True,

        "project": "SmartGeoAI",

        "original_address":
            address,


        # Used by your current frontend
        "parsed_address": {

            "original":
                address,

            "landmark":
                landmark,

            "city":
                city,

            "district":
                district,

            "state":
                state,

            "pincode":
                pincode

        },


        # Used by older frontend versions
        "address_results": {

            "original":
                address,

            "landmark":
                landmark,

            "city":
                city,

            "state":
                state,

            "pincode":
                pincode,

            "district":
                district,

            "latitude":
                latitude,

            "longitude":
                longitude

        },


        "normalized_address": {

            "formatted_address":
                normalized_address

        },


        # Also provide simple string
        # for older frontend versions
        "normalized_address_text":
            normalized_address,


        "pincode_validation": {

            "valid":
                row is not None,

            "pincode":
                pincode,

            "district":
                district,

            "state":
                state,

            "latitude":
                latitude,

            "longitude":
                longitude

        },


        "location": {

            "found":
                (
                    latitude is not None
                    and
                    longitude is not None
                ),

            "latitude":
                latitude,

            "longitude":
                longitude

        },


        "confidence": {

            "score":
                score,

            "level":
                level,

            "decision":
                decision,

            "evidence":
                evidence

        }

    }


    print(
        "Database match:",
        row is not None
    )

    print(
        "Coordinates:",
        latitude,
        longitude
    )

    print(
        "Confidence:",
        score,
        level
    )

    print(
        "Decision:",
        decision
    )

    print(
        "Resolution successful"
    )

    print("-" * 60)
    print()


    return result


# ============================================================
# API - RESOLVE ADDRESS
# ============================================================

@app.post("/resolve_address")
def resolve_address(
    request: AddressRequest
):

    try:

        address = (
            request.address
            .strip()
        )


        if not address:

            return {

                "success": False,

                "message":
                    "Please enter an address."

            }


        print()
        print(
            "POST /resolve_address"
        )


        result = resolve_address_logic(
            address
        )


        return result


    except Exception as error:

        print()
        print("=" * 60)

        print(
            "RESOLVE ADDRESS ERROR"
        )

        print("=" * 60)

        print(
            repr(error)
        )

        print("=" * 60)

        print()


        return {

            "success": False,

            "message":
                "Address resolution failed.",

            "error":
                str(error)

        }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "online",

        "application":
            "SmartGeoAI",

        "database_loaded":
            not database.empty,

        "database_rows":
            int(len(database))

    }


# ============================================================
# FRONTEND
# ============================================================

@app.get("/")
def home():

    index_file = os.path.join(
        FRONTEND_DIR,
        "index.html"
    )


    if not os.path.exists(
        index_file
    ):

        return {

            "error":
                "frontend/index.html not found",

            "expected_path":
                index_file

        }


    return FileResponse(
        index_file
    )


# ============================================================
# FRONTEND STATIC FILES
# ============================================================

if os.path.exists(
    FRONTEND_DIR
):

    app.mount(
        "/frontend",
        StaticFiles(
            directory=FRONTEND_DIR
        ),
        name="frontend"
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn


    print()
    print("=" * 60)

    print(
        "SMARTGEOAI SERVER"
    )

    print("=" * 60)

    print()

    print(
        "Frontend:",
        FRONTEND_DIR
    )

    print(
        "Data:",
        DATA_DIR
    )

    print()

    print(
        "Website:"
    )

    print(
        "http://127.0.0.1:8000/"
    )

    print()

    print(
        "Health:"
    )

    print(
        "http://127.0.0.1:8000/health"
    )

    print()

    print(
        "API Docs:"
    )

    print(
        "http://127.0.0.1:8000/docs"
    )

    print()

    print("=" * 60)
    print()


    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False
    )