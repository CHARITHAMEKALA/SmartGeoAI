
const BACKEND_URL = "http://127.0.0.1:8000";

const addressInput = document.getElementById("addressInput");
const searchButton = document.getElementById("searchButton");
const status = document.getElementById("status");
const results = document.getElementById("results");

function useExample(address) {
    addressInput.value = address;
    addressInput.focus();
}

searchButton.addEventListener("click", resolveAddress);

addressInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        resolveAddress();
    }
});

async function resolveAddress() {

    const address = addressInput.value.trim();

    if (!address) {
        status.innerHTML =
            '<span style="color:red;">⚠ Please enter an address.</span>';
        return;
    }

    searchButton.disabled = true;
    searchButton.textContent = "⏳ Resolving...";
    status.textContent = "Connecting to SmartGeoAI...";

    try {

        const response = await fetch(
            BACKEND_URL + "/resolve_address",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    address: address
                })
            }
        );

        if (!response.ok) {
            throw new Error(
                "Backend error: HTTP " + response.status
            );
        }

        const data = await response.json();

        console.log("SmartGeoAI response:", data);

        if (!data.success) {
            throw new Error(
                data.message || "Address resolution failed"
            );
        }

        displayResults(data);

        results.style.display = "block";

        status.innerHTML =
            '<span style="color:green;">✓ Address resolved successfully.</span>';

    } catch (error) {

        console.error(error);

        status.innerHTML =
            '<span style="color:red;">✗ ' +
            error.message +
            "</span>";

    } finally {

        searchButton.disabled = false;
        searchButton.textContent = "🔍 Search Address";
    }
}

function displayResults(data) {

    const result = data.address_results;

    const resultGrid =
        document.getElementById("resultGrid");

    resultGrid.innerHTML = "";

    addResult("Original Address", result.original);
    addResult("Landmark", result.landmark);
    addResult("City", result.city);
    addResult("State", result.state);
    addResult("Pincode", result.pincode);
    addResult("District", result.district);
    addResult("Latitude", result.latitude);
    addResult("Longitude", result.longitude);

    document.getElementById("normalizedAddress").textContent =
        data.normalized_address || "Not available";

    displayConfidence(data.confidence);
    displayPincode(data.pincode_validation);
    displayMap(result.latitude, result.longitude);
}

function addResult(label, value) {

    const box = document.createElement("div");
    box.className = "result-box";

    box.innerHTML = `
        <div class="result-label">${label}</div>
        <div class="result-value">
            ${value ?? "Not available"}
        </div>
    `;

    document
        .getElementById("resultGrid")
        .appendChild(box);
}

function displayConfidence(confidence) {

    if (!confidence) return;

    document.getElementById("confidenceScore").textContent =
        confidence.score + "%";

    document.getElementById("confidenceLevel").textContent =
        confidence.level || "-";

    document.getElementById("confidenceDecision").textContent =
        confidence.decision || "-";

    const evidenceList =
        document.getElementById("evidenceList");

    evidenceList.innerHTML = "";

    if (Array.isArray(confidence.evidence)) {

        confidence.evidence.forEach(function (item) {

            const li = document.createElement("li");

            li.textContent = item;

            evidenceList.appendChild(li);

        });
    }
}

function displayPincode(validation) {

    const element =
        document.getElementById("pincodeStatus");

    if (!validation) {
        element.innerHTML = "";
        return;
    }

    if (validation.valid) {

        element.innerHTML = `
            <div class="pincode-valid">
                ✓ Pincode verified successfully
                <br>
                <small>
                    ${validation.pincode || ""}
                    • ${validation.district || ""}
                    • ${validation.state || ""}
                </small>
            </div>
        `;

    } else {

        element.innerHTML = `
            <div class="pincode-invalid">
                ✗ Pincode could not be verified.
            </div>
        `;
    }
}

function displayMap(latitude, longitude) {

    const mapFrame =
        document.getElementById("mapFrame");

    const coordinates =
        document.getElementById("coordinates");

    const mapLink =
        document.getElementById("mapLink");

    if (
        latitude === null ||
        latitude === undefined ||
        longitude === null ||
        longitude === undefined
    ) {

        coordinates.textContent =
            "Coordinates unavailable";

        mapFrame.src = "about:blank";

        return;
    }

    const lat = Number(latitude);
    const lon = Number(longitude);

    coordinates.textContent =
        lat + ", " + lon;

    const delta = 0.015;

    const embedUrl =
        "https://www.openstreetmap.org/export/embed.html" +
        "?bbox=" +
        (lon - delta) +
        "%2C" +
        (lat - delta) +
        "%2C" +
        (lon + delta) +
        "%2C" +
        (lat + delta) +
        "&layer=mapnik" +
        "&marker=" +
        lat +
        "%2C" +
        lon;

    mapFrame.src = embedUrl;

    mapLink.href =
        "https://www.openstreetmap.org/" +
        "?mlat=" +
        lat +
        "&mlon=" +
        lon +
        "#map=15/" +
        lat +
        "/" +
        lon;
}