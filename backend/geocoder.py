"""
SmartGeoAI
Geocoding Agent

Uses OpenStreetMap Nominatim API
to convert address into coordinates.
"""


import requests
from urllib.parse import quote



NOMINATIM_URL = (
    "https://nominatim.openstreetmap.org/search"
)



def geocode_address(address_data):


    result = {

        "found": False,

        "latitude": None,

        "longitude": None,

        "display_name": None

    }



    address = address_data.get(
        "formatted_address",
        ""
    )


    if not address:

        return result



    try:


        params = {

            "q": address,

            "format": "json",

            "limit": 1

        }



        headers = {

            "User-Agent":
            "SmartGeoAI-Hackathon"

        }



        response = requests.get(

            NOMINATIM_URL,

            params=params,

            headers=headers,

            timeout=5

        )



        data = response.json()



        if data:


            location = data[0]


            result["found"] = True


            result["latitude"] = float(

                location["lat"]

            )


            result["longitude"] = float(

                location["lon"]

            )


            result["display_name"] = (

                location["display_name"]

            )



    except Exception as e:


        result["error"] = str(e)



    return result