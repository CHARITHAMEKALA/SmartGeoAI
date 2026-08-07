"""
SmartGeoAI
Address Normalization Agent

Converts parsed messy address into
clean delivery-ready format.
"""


from rapidfuzz import process



# Common Indian corrections

CORRECTIONS = {


    "hydrabad":
    "Hyderabad",


    "hyderbad":
    "Hyderabad",


    "hyd":
    "Hyderabad",


    "banglore":
    "Bangalore",


    "blr":
    "Bangalore",


    "vijaywada":
    "Vijayawada",


    "madras":
    "Chennai",


    "tn":
    "Tamil Nadu"

}




def correct_word(word):


    word_lower = word.lower()



    if word_lower in CORRECTIONS:

        return CORRECTIONS[word_lower]



    return word.title()





def normalize_address(parsed_data):


    normalized = {}



    # Original

    normalized["raw_address"] = (

        parsed_data.get(
            "raw_address"
        )

    )



    # Landmark

    normalized["landmark"] = (

        parsed_data.get(
            "landmark"
        )

    )



    # City correction

    city = parsed_data.get(
        "city"
    )


    if city:

        normalized["city"] = (

            correct_word(city)

        )

    else:

        normalized["city"] = None





    # State

    normalized["state"] = (

        parsed_data.get(
            "state"
        )

    )




    # Pincode

    normalized["pincode"] = (

        parsed_data.get(
            "pincode"
        )

    )




    # Build final address


    address_parts = []



    if normalized["landmark"]:

        address_parts.append(

            "Near " +

            normalized["landmark"].title()

        )



    if normalized["city"]:

        address_parts.append(

            normalized["city"]

        )



    if normalized["state"]:

        address_parts.append(

            normalized["state"]

        )



    if normalized["pincode"]:

        address_parts.append(

            normalized["pincode"]

        )




    normalized["formatted_address"] = (

        ", ".join(address_parts)

    )




    return normalized