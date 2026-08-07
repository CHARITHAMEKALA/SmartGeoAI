"""
SmartGeoAI
AI Address Parser Agent

Extracts structured information
from messy Indian addresses.
"""


import re



# Common Indian state names

STATES = [

    "Andhra Pradesh",
    "Telangana",
    "Tamil Nadu",
    "Karnataka",
    "Kerala",
    "Maharashtra",
    "Delhi",
    "Gujarat",
    "Rajasthan"

]



# City corrections

CITY_CORRECTIONS = {

    "hyd": "Hyderabad",

    "hydrabad": "Hyderabad",

    "hyderbad": "Hyderabad",

    "hyd city": "Hyderabad",

    "blr": "Bangalore",

    "banglore": "Bangalore",

    "chennai": "Chennai"

}




def clean_text(text):


    text = text.lower()


    text = text.replace(
        "opp.",
        "opposite"
    )


    text = text.replace(
        "opp",
        "opposite"
    )


    text = text.replace(
        "nr",
        "near"
    )


    return text.strip()




def extract_pincode(text):


    match = re.search(

        r"\b[1-9][0-9]{5}\b",

        text

    )


    if match:

        return match.group()



    return None





def extract_landmark(text):


    landmark = None



    patterns = [

        r"opposite\s+(.*?)\s+(near|beside|behind|road|$)",

        r"near\s+(.*?)\s+(road|area|$)",

        r"beside\s+(.*?)\s+(road|$)"

    ]



    for pattern in patterns:


        result = re.search(

            pattern,

            text

        )


        if result:


            landmark = result.group(1).strip()

            break



    return landmark




def extract_city(text):


    for wrong, correct in CITY_CORRECTIONS.items():


        if wrong in text:

            return correct



    for state in STATES:


        if state.lower() in text:

            words = text.split()


            index = words.index(

                state.lower()

            )


            if index > 0:

                return words[index-1].title()



    return None





def parse_address(address):


    original = address



    text = clean_text(address)



    result = {


        "raw_address":

            original,


        "cleaned_address":

            text,


        "landmark":

            extract_landmark(text),


        "city":

            extract_city(text),


        "state":

            None,


        "pincode":

            extract_pincode(text)

    }



    for state in STATES:


        if state.lower() in text:


            result["state"] = state



    return result