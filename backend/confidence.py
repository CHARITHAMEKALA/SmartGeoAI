def calculate_confidence(
    parsed_address,
    pincode_validation,
    location,
    landmark_evidence
):

    score = 0
    evidence = []


    # Pincode check
    if pincode_validation.get("valid"):

        score += 30

        evidence.append(
            "✓ Pincode matched with database"
        )

    else:

        evidence.append(
            "✗ Pincode verification failed"
        )


    # Location check
    if location.get("found"):

        score += 30

        evidence.append(
            "✓ Coordinates available"
        )

    else:

        evidence.append(
            "✗ Unable to find exact coordinates"
        )


    # Landmark check
    if landmark_evidence.get("found"):

        score += 20

        evidence.append(
            "✓ Landmark verified"
        )

    else:

        evidence.append(
            "✗ Landmark evidence unavailable"
        )


    # Address completeness
    if (
        parsed_address.get("city")
        and
        parsed_address.get("pincode")
    ):

        score += 20

        evidence.append(
            "✓ Address information complete"
        )

    else:

        evidence.append(
            "✗ Address information incomplete"
        )


    if score >= 80:

        level = "HIGH"

        decision = "Auto-confirm"

    elif score >= 50:

        level = "MEDIUM"

        decision = "Needs verification"

    else:

        level = "LOW"

        decision = "Do not auto-confirm"



    return {

        "score": score,

        "level": level,

        "decision": decision,

        "evidence": evidence

    }