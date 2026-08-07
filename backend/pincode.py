"""
SmartGeoAI
Pincode Validation Agent

Validates Indian pincode using pincode.xlsx dataset.
"""

import pandas as pd
import os


# Dataset path
DATA_PATH = "../data/pincode.xlsx"


pincode_df = None



def load_dataset():

    global pincode_df


    if pincode_df is not None:
        return pincode_df



    if os.path.exists(DATA_PATH):

        pincode_df = pd.read_excel(
            DATA_PATH
        )

    else:

        pincode_df = pd.DataFrame()



    return pincode_df




def validate_pincode(address_data):


    df = load_dataset()


    pincode = address_data.get(
        "pincode"
    )


    result = {

        "pincode": pincode,

        "valid": False,

        "district": None,

        "state": None,

        "latitude": None,

        "longitude": None,

        "message": ""

    }



    if not pincode:

        result["message"] = "Pincode not detected"

        return result



    if df.empty:

        result["message"] = "Pincode dataset not loaded"

        return result




    # Find pincode

    match = df[

        df["pincode"].astype(str)

        ==

        str(pincode)

    ]




    if not match.empty:


        row = match.iloc[0]


        result["valid"] = True


        # District

        if "district" in df.columns:

            result["district"] = row["district"]



        # State

        if "statename" in df.columns:

            result["state"] = row["statename"]



        # Coordinates

        if "latitude" in df.columns:

            result["latitude"] = row["latitude"]


        if "longitude" in df.columns:

            result["longitude"] = row["longitude"]



        result["message"] = "Pincode verified successfully"



    else:


        result["message"] = "Pincode not found"



    return result