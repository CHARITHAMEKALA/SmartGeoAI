let map = null;
let marker = null;


/* =========================
   PAGE ELEMENTS
========================= */

const addressInput =
    document.getElementById("address");

const resultSection =
    document.getElementById("resultSection");

const result =
    document.getElementById("result");

const mapSection =
    document.getElementById("mapSection");

const resolveButton =
    document.getElementById("resolveButton");

const buttonText =
    document.getElementById("buttonText");

const loader =
    document.getElementById("loader");

const characterCount =
    document.getElementById("characterCount");


/* =========================
   CHARACTER COUNT
========================= */

addressInput.addEventListener(
    "input",
    function () {

        const count =
            addressInput.value.length;

        characterCount.textContent =
            count + " characters";
    }
);


/* =========================
   ENTER KEY
========================= */

addressInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            event.ctrlKey
        ) {

            resolveAddress();

        }

    }
);


/* =========================
   RESOLVE ADDRESS
========================= */

async function resolveAddress() {

    const address =
        addressInput.value.trim();


    if (!address) {

        showError(
            "Please enter an Indian address.",
            "Add locality, landmark, city, district or pincode information."
        );

        return;
    }


    setLoading(true);


    resultSection.classList.remove("hidden");

    mapSection.classList.add("hidden");


    result.innerHTML = `

        <div class="result-box">

            <div class="result-header">

                <div class="result-title">

                    <span class="section-label">
                        SMARTGEOAI ENGINE
                    </span>

                    <h2>
                        Resolving Address
                    </h2>

                    <p>
                        Parsing, normalizing and verifying
                        the submitted address.
                    </p>

                </div>

            </div>

            <div class="info-card">

                <span>
                    Processing
                </span>

                <strong>
                    Please wait while SmartGeoAI
                    analyzes the address...
                </strong>

            </div>

        </div>

    `;


    try {

        const response =
            await fetch(
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


        let data = null;


        try {

            data =
                await response.json();

        } catch (jsonError) {

            throw new Error(
                "Backend returned an invalid response."
            );

        }


        if (!response.ok) {

            const message =
                data?.error ||
                data?.message ||
                "Server returned HTTP " +
                response.status;

            throw new Error(message);
        }


        displayResult(
            data,
            address
        );

    }


    catch (error) {

        console.error(
            "SmartGeoAI:",
            error
        );


        showError(
            "Unable to resolve this address.",
            error.message
        );

    }


    finally {

        setLoading(false);

    }

}


/* =========================
   DISPLAY RESULT
========================= */

function displayResult(
    data,
    originalAddress
) {

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
        Number(confidence.score) || 0;


    const level =
        String(
            confidence.level || "LOW"
        ).toUpperCase();


    let confidenceClass =
        "low";


    if (score >= 80) {

        confidenceClass = "high";

    }

    else if (score >= 50) {

        confidenceClass = "medium";

    }


    const formattedAddress =
        normalized.formatted_address ||
        originalAddress;


    const district =
        validation.district ||
        parsed.district ||
        "Not available";


    const state =
        validation.state ||
        parsed.state ||
        "Not available";


    const pincode =
        validation.pincode ||
        parsed.pincode ||
        "Not available";


    const latitude =
        location.latitude ??
        "Not available";


    const longitude =
        location.longitude ??
        "Not available";


    const decision =
        confidence.decision ||
        "Do not auto-confirm";


    const evidence =
        Array.isArray(
            confidence.evidence
        )
            ? confidence.evidence
            : [];


    let evidenceHTML = "";


    if (evidence.length > 0) {

        evidenceHTML = evidence
            .map(
                item => `

                    <div class="evidence-item">
                        ${escapeHTML(item)}
                    </div>

                `
            )
            .join("");

    }

    else {

        evidenceHTML = `

            <div class="evidence-item">
                Verification information returned
                by the SmartGeoAI engine.
            </div>

        `;

    }


    resultSection.classList.remove(
        "hidden"
    );


    result.innerHTML = `

        <div class="result-box">

            <div class="result-header">

                <div class="result-title">

                    <span class="section-label">
                        RESOLUTION COMPLETE
                    </span>

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
                        ${escapeHTML(level)}
                        CONFIDENCE
                    </small>

                </div>

            </div>


            <div class="info-grid">

                <div class="info-card">

                    <span>
                        Normalized Address
                    </span>

                    <strong>
                        ${escapeHTML(
                            formattedAddress
                        )}
                    </strong>

                </div>


                <div class="info-card">

                    <span>
                        District
                    </span>

                    <strong>
                        ${escapeHTML(
                            district
                        )}
                    </strong>

                </div>


                <div class="info-card">

                    <span>
                        State
                    </span>

                    <strong>
                        ${escapeHTML(
                            state
                        )}
                    </strong>

                </div>


                <div class="info-card">

                    <span>
                        Pincode
                    </span>

                    <strong>
                        ${escapeHTML(
                            pincode
                        )}
                    </strong>

                </div>


                <div class="info-card">

                    <span>
                        Latitude
                    </span>

                    <strong>
                        ${escapeHTML(
                            latitude
                        )}
                    </strong>

                </div>


                <div class="info-card">

                    <span>
                        Longitude
                    </span>

                    <strong>
                        ${escapeHTML(
                            longitude
                        )}
                    </strong>

                </div>

            </div>


            <div class="decision-card">

                <div class="decision-top">

                    <h3>
                        Verification Decision
                    </h3>

                </div>

                <p>
                    ${escapeHTML(
                        decision
                    )}
                </p>

            </div>


            <div class="verification">

                <h3>
                    Verification Details
                </h3>

                <div class="evidence-list">

                    ${evidenceHTML}

                </div>

            </div>

        </div>

    `;


    /* =========================
       SHOW MAP
    ========================= */

    const validLatitude =
        typeof location.latitude === "number" ||
        !isNaN(
            Number(location.latitude)
        );


    const validLongitude =
        typeof location.longitude === "number" ||
        !isNaN(
            Number(location.longitude)
        );


    if (
        location.found === true &&
        validLatitude &&
        validLongitude
    ) {

        showMap(
            Number(location.latitude),
            Number(location.longitude),
            formattedAddress
        );

    }

    else {

        clearMap();

    }


    window.scrollTo({
        top:
            resultSection.offsetTop - 90,
        behavior: "smooth"
    });

}


/* =========================
   MAP
========================= */

function showMap(
    latitude,
    longitude,
    address
) {

    clearMap();


    mapSection.classList.remove(
        "hidden"
    );


    map =
        L.map("map")
            .setView(
                [
                    latitude,
                    longitude
                ],
                15
            );


    L.tileLayer(
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,

            attribution:
                "&copy; OpenStreetMap contributors"
        }
    ).addTo(map);


    marker =
        L.marker(
            [
                latitude,
                longitude
            ]
        )
        .addTo(map);


    marker.bindPopup(
        `
        <strong>
            Resolved Delivery Location
        </strong>
        <br><br>
        ${escapeHTML(address)}
        `
    );


    marker.openPopup();


    setTimeout(
        function () {

            map.invalidateSize();

        },
        300
    );


    mapSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


/* =========================
   CLEAR MAP
========================= */

function clearMap() {

    if (map) {

        map.remove();

        map = null;

        marker = null;
    }


    mapSection.classList.add(
        "hidden"
    );


    const mapElement =
        document.getElementById("map");


    if (mapElement) {

        mapElement.innerHTML = "";

    }

}


/* =========================
   ERROR
========================= */

function showError(
    title,
    message
) {

    resultSection.classList.remove(
        "hidden"
    );


    mapSection.classList.add(
        "hidden"
    );


    result.innerHTML = `

        <div class="result-box">

            <div class="error">

                <strong>
                    ${escapeHTML(title)}
                </strong>

                <span>
                    ${escapeHTML(message)}
                </span>

            </div>

        </div>

    `;


    window.scrollTo({
        top:
            resultSection.offsetTop - 90,

        behavior: "smooth"
    });

}


/* =========================
   LOADING
========================= */

function setLoading(
    loading
) {

    resolveButton.disabled =
        loading;


    if (loading) {

        buttonText.textContent =
            "Resolving...";

        loader.classList.remove(
            "hidden"
        );

    }

    else {

        buttonText.textContent =
            "Resolve Address";

        loader.classList.add(
            "hidden"
        );

    }

}


/* =========================
   SECURITY
========================= */

function escapeHTML(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(value);


    return div.innerHTML;

}