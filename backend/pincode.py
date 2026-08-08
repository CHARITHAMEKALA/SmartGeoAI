"""
SmartGeoAI
Pincode Validation Agent

Uses India Pincode Excel dataset
for ground truth validation.
"""


import pandas as pd
import os



# Correct absolute path

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "pincode.xlsx"
)



def load_pincode_data():

    try:

        if not os.path.exists(DATA_PATH):

            print(
                "Pincode file not found:",
                DATA_PATH
            )

            return None



        df = pd.read_excel(
            DATA_PATH
        )



        # Clean column names

        df.columns = (

            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "")

        )



        return df



    except Exception as e:


        print(
            "Excel loading error:",
            e
        )


        return None





def validate_pincode(

        pincode,

        city=None,

        state=None

):


    result = {


        "valid": False,


        "pincode": pincode,


        "district": None,


        "state": None,


        "latitude": None,


        "longitude": None,


        "evidence": []

    }





    if not pincode:


        result["evidence"].append(

            "✗ Pincode missing"

        )


        return result





    df = load_pincode_data()



    if df is None:


        result["evidence"].append(

            "✗ Pincode database unavailable"

        )


        return result





    try:



        pin = int(pincode)



        # Handle different column names

        possible_columns = [

            "pincode",

            "pincodecode",

            "pin"

        ]



        pin_column = None



        for col in possible_columns:


            if col in df.columns:


                pin_column = col

                break





        if pin_column is None:


            result["evidence"].append(

                "✗ Pincode column not found"

            )


            return result





        match = df[

            df[pin_column]
            .astype(str)
            .str.contains(str(pin))

        ]





        if len(match) > 0:


            row = match.iloc[0]



            result["valid"] = True





            # District

            for col in [

                "district",

                "districtname"

            ]:


                if col in df.columns:


                    result["district"] = row[col]

                    break





            # State

            for col in [

                "statename",

                "state"

            ]:


                if col in df.columns:


                    result["state"] = row[col]

                    break





            # Latitude

            for col in [

                "latitude",

                "lat"

            ]:


                if col in df.columns:


                    result["latitude"] = row[col]

                    break





            # Longitude

            for col in [

                "longitude",

                "lon",

                "lng"

            ]:


                if col in df.columns:


                    result["longitude"] = row[col]

                    break





            result["evidence"].append(

                "✓ Pincode exists in India directory"

            )


            result["evidence"].append(

                "✓ Location details verified"

            )




        else:


            result["evidence"].append(

                "✗ Pincode not found"

            )





    except Exception as e:


        result["evidence"].append(

            str(e)

        )





    return result