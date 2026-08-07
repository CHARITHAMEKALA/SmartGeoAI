"""
SmartGeoAI
Confidence Engine

Evaluates address resolution reliability.
"""


def calculate_confidence(

        pincode_result,

        landmark_result,

        address_data,

        location_result=None

):


    score = 0

    evidence = []



    # -----------------------------
    # Pincode Validation
    # -----------------------------

    if pincode_result.get("valid"):


        score += 30


        evidence.append(

            "✓ Pincode matched with database"

        )


    else:


        evidence.append(

            "✗ Pincode verification failed"

        )





    # -----------------------------
    # Geocoding Check
    # -----------------------------

    if location_result and location_result.get("found"):


        score += 30


        evidence.append(

            "✓ Address converted to coordinates"

        )


    else:


        evidence.append(

            "✗ Unable to find exact coordinates"

        )





    # -----------------------------
    # Landmark Evidence
    # -----------------------------

    if landmark_result.get("found"):


        score += 25


        evidence.append(

            "✓ Real landmark evidence found from OpenStreetMap"

        )


    else:


        evidence.append(

            "✗ Landmark evidence unavailable"

        )





    # -----------------------------
    # Address Completeness
    # -----------------------------

    fields = [

        "landmark",

        "city",

        "state",

        "pincode"

    ]



    completed = 0



    for field in fields:


        if address_data.get(field):

            completed += 1





    completeness = (

        completed / len(fields)

    ) * 100





    if completeness >= 75:


        score += 15


        evidence.append(

            "✓ Address information complete"

        )


    else:


        evidence.append(

            "✗ Address information incomplete"

        )





    # Limit score

    score = min(

        round(score),

        100

    )





    # Confidence category


    if score >= 85:


        level = "HIGH"


        decision = (

            "Safe to deliver"

        )



    elif score >= 60:


        level = "MEDIUM"


        decision = (

            "Needs verification"

        )



    else:


        level = "LOW"


        decision = (

            "Do not auto-confirm"

        )





    return {


        "score":

        score,


        "level":

        level,


        "decision":

        decision,


        "evidence":

        evidence

    }