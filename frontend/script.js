let map = null;
let marker = null;


async function resolveAddress() {

    const input =
        document.getElementById("address");

    const result =
        document.getElementById("result");


    const address =
        input.value.trim();


    if (!address) {

        result.innerHTML = `
            <div class="error">
                Please enter an address.
            </div>
        `;

        return;
    }


    result.innerHTML = `
        <p>Resolving address...</p>
    `;


    try {

        const response = await fetch(
            "/resolve_address",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",

                    "Accept":
                        "application/json"
                },

                body: JSON.stringify({
                    address: address
                })
            }
        );


        if (!response.ok) {

            throw new Error(
                "Server returned " +
                response.status
            );
        }


        const data =
            await response.json();


        console.log(
            "SmartGeoAI:",
            data
        );


        const parsed =
            data.parsed_address || {};

        const normalized =
            data.normalized_address || {};

        const validation =
            data.pincode_validation || {};

        const location =
            data.location || {};

        const confidence =
            data.confidence || {};


        const score =
            confidence.score || 0;

        const level =
            confidence.level || "LOW";


        let confidenceClass =
            "low";


        if (score >= 80) {

            confidenceClass =
                "high";

        } else if (score >= 50) {

            confidenceClass =
                "medium";
        }


        let evidence = "";


        if (
            Array.isArray(
                confidence.evidence
            )
        ) {

            evidence =
                confidence.evidence
                    .map(
                        item =>
                            `<p>${item}</p>`
                    )
                    .join("");
        }


        result.innerHTML = `

            <div class="result-header">

                <div>

                    <h2>
                        Address Resolved
                    </h2>

                    <p>
                        SmartGeoAI verification result
                    </p>

                </div>


                <div class="
                    confidence
                    ${confidenceClass}
                ">

                    <span>
                        ${score}%
                    </span>

                    <small>
                        ${level}
                    </small>

                </div>

            </div>


            <div class="info-grid">


                <div class="info-card">

                    <span>
                        Address
                    </span>

                    <strong>
                        ${
                            normalized
                                .formatted_address
                            || address
                        }
                    </strong>

                </div>


                <div class="info-card">

                    <span>
                        District
                    </span>

                    <strong>
                        ${
                            validation.district
                            || "N/A"
                        }
                    </strong>

                </div>


                <div class="info-card">

                    <span>
                        State
                    </span>

                    <strong>
                        ${
                            validation.state
                            || "N/A"
                        }
                    </strong>

                </div>


                <div class="info-card">

                    <span>
                        Pincode
                    </span>

                    <strong>
                        ${
                            validation.pincode
                            || "N/A"
                        }
                    </strong>

                </div>


                <div class="info-card">

                    <span>
                        Latitude
                    </span>

                    <strong>
                        ${
                            location.latitude
                            ?? "N/A"
                        }
                    </strong>

                </div>


                <div class="info-card">

                    <span>
                        Longitude
                    </span>

                    <strong>
                        ${
                            location.longitude
                            ?? "N/A"
                        }
                    </strong>

                </div>

            </div>


            <div class="decision-card">

                <h3>
                    Verification Decision
                </h3>

                <p>
                    ${
                        confidence.decision
                        || "Do not auto-confirm"
                    }
                </p>

            </div>


            <div class="verification">

                <h3>
                    Verification Details
                </h3>

                ${evidence}

            </div>

        `;


        // =========================
        // MAP
        // =========================

        if (
            location.found === true &&
            location.latitude !== null &&
            location.longitude !== null
        ) {

            showMap(
                location.latitude,
                location.longitude,
                normalized.formatted_address
            );

        } else {

            clearMap();

        }

    }

    catch (error) {

        console.error(
            "SmartGeoAI error:",
            error
        );


        result.innerHTML = `

            <div class="error">

                Unable to connect to
                SmartGeoAI backend.

                <br><br>

                ${error.message}

            </div>

        `;
    }
}



function showMap(
    latitude,
    longitude,
    address
) {

    clearMap();


    map =
        L.map("map").setView(
            [
                latitude,
                longitude
            ],
            15
        );


    L.tileLayer(
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution:
                "© OpenStreetMap contributors"
        }
    ).addTo(map);


    marker =
        L.marker(
            [
                latitude,
                longitude
            ]
        )
        .addTo(map)
        .bindPopup(
            `<b>Resolved Location</b><br>
             ${address}`
        )
        .openPopup();
}



function clearMap() {

    if (map) {

        map.remove();

        map = null;

        marker = null;
    }


    const mapElement =
        document.getElementById("map");


    if (mapElement) {

        mapElement.innerHTML = "";
    }
}