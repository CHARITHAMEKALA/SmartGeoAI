/*
SmartGeoAI
Frontend Dashboard

Displays:
- Address resolution
- Confidence
- Evidence
- Map location
*/


const API_URL = "http://127.0.0.1:8000";



// Initialize Map

let map = L.map("map").setView(

    [20.5937,78.9629],

    5

);



L.tileLayer(

    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",

    {

        attribution:
        "© OpenStreetMap contributors"

    }

).addTo(map);



let marker = null;





async function resolveAddress(){


    let address =

    document.getElementById(

        "addressInput"

    ).value;



    if(!address){

        alert(
            "Enter address"
        );

        return;

    }



    document.getElementById(

        "output"

    ).innerHTML =

    "⏳ AI agents processing address...";





    try{


        const response = await fetch(

            API_URL + "/resolve_address",

            {

                method:"POST",


                headers:{

                    "Content-Type":
                    "application/json"

                },


                body:JSON.stringify({

                    address:address

                })

            }

        );





        const data = await response.json();




        displayResult(data);



    }

    catch(error){


        document.getElementById(

            "output"

        ).innerHTML =

        "❌ Backend not connected";

    }

}






function displayResult(data){



    let confidence =

        data.confidence;



    let evidenceHTML = "";



    confidence.evidence.forEach(

        item => {


            evidenceHTML +=

            `<p>${item}</p>`;


        }

    );





    document.getElementById(

        "output"

    ).innerHTML = `



    <div class="card">


    <h3>
    📌 Original Address
    </h3>

    <p>
    ${data.original_address}
    </p>



    <h3>
    ✅ Corrected Address
    </h3>


    <p>
    ${data.normalized_address.formatted_address}
    </p>



    <h3>
    🎯 Confidence
    </h3>


    <h2>

    ${confidence.score}%

    (${confidence.level})

    </h2>



    <h3>
    Decision
    </h3>

    <p>

    ${confidence.decision}

    </p>



    <h3>
    🔍 Evidence
    </h3>


    ${evidenceHTML}


    </div>


    `;




    // Show location

    if(

        data.location &&

        data.location.found

    ){


        showMap(

            data.location.latitude,

            data.location.longitude,

            data.normalized_address.formatted_address

        );


    }

}





function showMap(

    lat,

    lon,

    address

){



    if(marker){

        map.removeLayer(marker);

    }



    marker = L.marker(

        [

            lat,

            lon

        ]

    )

    .addTo(map);



    marker.bindPopup(

        address

    )

    .openPopup();



    map.setView(

        [

            lat,

            lon

        ],

        15

    );

}