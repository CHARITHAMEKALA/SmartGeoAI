"""
SmartGeoAI
Geocoding Agent

Uses OpenStreetMap Nominatim
to convert Indian addresses
into coordinates.
"""

import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"



def geocode_address(normalized_address):


    result = {

        "found": False,

        "latitude": None,

        "longitude": None,

        "display_name": None,

        "accuracy": "LOW",

        "source": "OpenStreetMap"

    }


    try:


        city = normalized_address.get(
            "city",
            ""
        )


        state = normalized_address.get(
            "state",
            ""
        )


        pincode = normalized_address.get(
            "pincode",
            ""
        )


        landmark = normalized_address.get(
            "landmark",
            ""
        )



        query = (
            f"{landmark}, "
            f"{city}, "
            f"{state}, "
            f"{pincode}, India"
        )



        headers = {

            "User-Agent":
            "SmartGeoAI-Hackathon"

        }



        params = {

            "q": query,

            "format": "json",

            "limit": 1,

            "addressdetails": 1

        }



        response = requests.get(

            NOMINATIM_URL,

            params=params,

            headers=headers,

            timeout=10

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


            result["accuracy"] = "HIGH"



        else:


            # fallback search using only city+pincode


            fallback = (

                f"{city}, "
                f"{state}, "
                f"{pincode}, India"

            )


            params["q"] = fallback



            response = requests.get(

                NOMINATIM_URL,

                params=params,

                headers=headers,

                timeout=10

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


                result["accuracy"] = "MEDIUM"



    except Exception as e:


        result["error"] = str(e)



    return result