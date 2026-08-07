"""
SmartGeoAI
Landmark Verification Agent

Uses OpenStreetMap Overpass API
to find real nearby landmarks.
"""


import requests



OVERPASS_URL = (

    "https://overpass-api.de/api/interpreter"

)




def verify_landmarks(address_data):


    result = {


        "found": False,


        "landmarks": [],


        "evidence": [],


        "count": 0,


        "message": ""

    }



    city = address_data.get(

        "city"

    )



    landmark_keyword = address_data.get(

        "landmark"

    )



    if not city:


        result["message"] = (

            "City unavailable"

        )

        return result





    # Search area

    search_area = city





    query = f"""

    [out:json][timeout:10];


    area["name"="{search_area}"]
    ->.searchArea;


    (

      node["amenity"="school"]
      (area.searchArea);


      node["amenity"="hospital"]
      (area.searchArea);


      node["amenity"="bank"]
      (area.searchArea);


      node["amenity"="atm"]
      (area.searchArea);


      node["amenity"="place_of_worship"]
      (area.searchArea);


      node["tourism"]
      (area.searchArea);


    );


    out tags center 20;

    """




    try:


        response = requests.post(

            OVERPASS_URL,

            data=query,

            timeout=15

        )



        data = response.json()



        elements = data.get(

            "elements",

            []

        )





        for item in elements:



            tags = item.get(

                "tags",

                {}

            )



            name = tags.get(

                "name"

            )



            if name:



                category = (

                    tags.get(

                        "amenity"

                    )

                    or

                    tags.get(

                        "tourism",

                        "place"

                    )

                )



                landmark = {


                    "name":

                    name,


                    "type":

                    category

                }



                result["landmarks"].append(

                    landmark

                )





        result["count"] = len(

            result["landmarks"]

        )





        # Evidence generation


        if result["count"] > 0:



            result["found"] = True



            for item in result["landmarks"][:5]:


                result["evidence"].append(

                    "✓ "

                    + item["name"]

                    + " ("

                    + item["type"]

                    + ")"

                )



            result["message"] = (

                "OSM landmarks verified"

            )



        else:


            result["message"] = (

                "No nearby landmarks found"

            )



    except Exception as error:


        result["message"] = str(error)



    return result