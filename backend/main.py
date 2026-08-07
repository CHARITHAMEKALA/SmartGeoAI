"""
SmartGeoAI
AI Build 2026 - Pata Track

Main FastAPI Backend

Pipeline:

User Address
      |
      ↓
Address Parser
      |
      ↓
Normalizer
      |
      ↓
Pincode Validation
      |
      ↓
OpenStreetMap Geocoder
      |
      ↓
Landmark Verification
      |
      ↓
Confidence Engine
      |
      ↓
Final Result
"""


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import time


# Import AI Modules

from parser import parse_address

from normalizer import normalize_address

from pincode import validate_pincode

from geocoder import geocode_address

from landmark import verify_landmarks

from confidence import calculate_confidence



# ---------------------------------------
# FastAPI Application
# ---------------------------------------

app = FastAPI(

    title="SmartGeoAI",

    description=
    "AI Address Parsing and Location Intelligence System",

    version="1.0"

)



# ---------------------------------------
# CORS
# ---------------------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)



# ---------------------------------------
# Request Model
# ---------------------------------------

class AddressRequest(BaseModel):

    address: str




# ---------------------------------------
# Home API
# ---------------------------------------

@app.get("/")
def home():

    return {

        "project": "SmartGeoAI",

        "status": "Running",

        "message":
        "AI Address Resolution API"

    }




# ---------------------------------------
# Main Resolve API
# ---------------------------------------

@app.post("/resolve_address")
def resolve_address(request: AddressRequest):


    start_time = time.time()


    try:


        # Original address

        original_address = request.address



        # -----------------------------
        # 1. Address Parser
        # -----------------------------

        parsed_address = parse_address(

            original_address

        )



        # -----------------------------
        # 2. Address Normalizer
        # -----------------------------

        normalized_address = normalize_address(

            parsed_address

        )



        # -----------------------------
        # 3. Pincode Validation
        # -----------------------------

        pincode_result = validate_pincode(

            normalized_address

        )



        # -----------------------------
        # 4. Geocoding
        # -----------------------------

        location_result = geocode_address(

            normalized_address

        )



        # -----------------------------
        # 5. Landmark Verification
        # -----------------------------

        landmark_result = verify_landmarks(

            normalized_address

        )



        # -----------------------------
        # 6. Confidence Score
        # -----------------------------

        confidence_result = calculate_confidence(

            pincode_result,

            landmark_result,

            normalized_address,

            location_result

        )



        processing_time = round(

            (time.time() - start_time) * 1000,

            2

        )



        # Final JSON Response

        return {


            "original_address":

                original_address,



            "parsed_address":

                parsed_address,



            "normalized_address":

                normalized_address,



            "pincode_validation":

                pincode_result,



            "location":

                location_result,



            "landmark_evidence":

                landmark_result,



            "confidence":

                confidence_result,



            "performance":

                {

                    "processing_time_ms":

                    processing_time

                }

        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )