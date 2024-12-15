'use strict';

// Global State and Variables
let GameState = {
    player_points: 0,
    ingredients_collected: [],
    affected_municipalities: [],
    virus_created: false,
    agents: []
};

const redIcon = L.divIcon({ className: 'red-icon' });
const purpleIcon = L.divIcon({ className: 'purple-icon' });
let selectedMunicipality = null; // Tracks the currently selected municipality
let currentActiveMarker = null; // To track the active marker

// Map Setup using Leaflet
const map = L.map('map', { tap: false });
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    minZoom: 4,
    maxZoom: 10,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
}).addTo(map);
map.setView([60, 24], 7);

const bounds = [
    [60.0, 19.0],
    [70.0, 32.0]
];

// Prevent dragging out of bounds
map.setMaxBounds(bounds);
map.on('drag', function () {
    map.panInsideBounds(bounds, { animate: true });
});

// Main Functions
async function getData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch data from server');
        return await response.json();
    } catch (error) {
        console.error("Error in getData:", error);
        throw error;
    }
}

function updateState(newValues) {
    Object.assign(GameState, newValues);
    updateUI(GameState);
}

// Game Setup and Initialization
async function gameSetup() {
    try {
        const gameData = await getData('http://127.0.0.1:5000/newgame');
        console.log("Game Setup Data:", gameData);

        const markerMap = {}; // Track markers for all municipalities

        // Add markers to map
        gameData.location.forEach(location => {
            const marker = L.marker([location.latitude, location.longitude]).addTo(map);
            const popUpContent = createPopupContent(location);
            marker.bindPopup(popUpContent);

            // Set initial icon based on active status
            if (location.name === "Helsinki-Vantaa Airport") {
                marker.setIcon(redIcon); // Set Helsinki as active by default
                currentActiveMarker = marker; // Track as the currently active marker
                selectedMunicipality = location.name; // Set as the initially selected municipality
            } else {
                marker.setIcon(purpleIcon);
            }

            // Add the marker to the marker map
            markerMap[location.name] = marker;

            // Add click event to update the selected municipality
            marker.on('click', () => {
                selectedMunicipality = location.name; // Update the selected municipality
                console.log(`Selected Municipality: ${selectedMunicipality}`);
                document.getElementById('affect-municipalities').disabled = false; // Enable the button

                // Set all markers to purple and reset the current active marker
                Object.values(markerMap).forEach(m => m.setIcon(purpleIcon));

                // Set the clicked marker to red (active)
                marker.setIcon(redIcon);
                currentActiveMarker = marker; // Update the current active marker
            });
        });

        // Initialize game state, explicitly set agents to an empty array
        updateState({
            player_points: gameData.player_points,
            ingredients_collected: gameData.ingredients_collected,
            affected_municipalities: gameData.affected_municipalities,
            agents: [] // Ensure agents start as an empty array
        });

        // Display alert message on page load
        alert("Please collect the ingredients first.");
    } catch (error) {
        console.error("Error during game setup:", error);
    }
}

function createPopupContent(location) {
    const popUpContent = document.createElement('div');
    const airportName = document.createElement('span');
    airportName.innerHTML = location.name;
    popUpContent.append(airportName);

    const p = document.createElement('p');
    p.innerHTML = `Distance ${location.distance}km`;
    popUpContent.append(p);

    return popUpContent;
}

// Actions and Event Handlers
async function gatherIngredient() {
    try {
        if (!Array.isArray(GameState.ingredients_collected)) {
            GameState.ingredients_collected = [];
        }

        const allIngredients = ["Ingredient1", "Ingredient2", "Ingredient3", "Ingredient4", "Ingredient5", "Ingredient6", "Ingredient7", "Ingredient8", "Ingredient9", "Ingredient10"];

        const availableIngredients = allIngredients.filter(ingredient =>
            !GameState.ingredients_collected.includes(ingredient)
        );

        if (availableIngredients.length > 0) {
            const ingredient = availableIngredients[0]; // Take the first available ingredient
            GameState.ingredients_collected.push(ingredient); // Add to collected ingredients
            GameState.player_points += 5; // Add points for gathering an ingredient

            updateState({
                ingredients_collected: GameState.ingredients_collected,
                player_points: GameState.player_points
            });

            console.log("Gathered Ingredient:", ingredient);
        } else {
            alert("No more ingredients to collect.");
        }
    } catch (error) {
        console.error("Error gathering ingredient:", error);
    }
}

async function createVirus() {
    try {
        // Check if there are enough ingredients, points, and at least one agent
        if (GameState.ingredients_collected.length >= 3 && GameState.player_points >= 10 && GameState.agents.length > 0) {
            GameState.virus_created = true;
            updateState({ virus_created: true });
            alert("Virus created successfully!");
        } else {
            alert("Not enough ingredients, points, or agents to create the virus.");
        }
    } catch (error) {
        console.error("Error creating virus:", error);
    }
}

async function deployAgent() {
    try {
        if (GameState.player_points >= 5) {
            const agent = { id: GameState.agents.length + 1, name: `Agent ${GameState.agents.length + 1}` };
            GameState.agents.push(agent);
            GameState.player_points -= 5; // Deduct points for deploying an agent
            updateState({ agents: GameState.agents, player_points: GameState.player_points });
            alert(`The agent has been deployed!`);
        } else {
            alert("Not enough points to deploy an agent.");
        }
    } catch (error) {
        console.error("Error deploying agent:", error);
    }
}

async function administerVirus(municipality) {
    try {
        if (GameState.virus_created) {
            if (GameState.agents.length > 0) {
                // Check if the municipality is already affected
                if (!GameState.affected_municipalities.includes(municipality)) {
                    GameState.affected_municipalities.push(municipality);
                    GameState.agents.pop(); // Reduce the agent count by 1
                    updateState({
                        affected_municipalities: GameState.affected_municipalities,
                        agents: GameState.agents
                    });

                    // Update map markers to reflect the infection
                    const markers = map._layers;
                    Object.values(markers).forEach(layer => {
                        if (layer instanceof L.Marker) {
                            const popupContent = layer.getPopup().getContent();
                            let contentText = typeof popupContent === "string" ? popupContent : popupContent.innerText;
                            if (contentText.includes(municipality)) {
                                layer.setIcon(redIcon); // Change to red icon
                            }
                        }
                    });

                    alert(`${municipality} has been infected!`);
                } else {
                    alert(`${municipality} is already infected.`);
                }
            } else {
                alert("No agents available to infect municipalities.");
            }
        } else {
            alert("Virus must be created first.");
        }
    } catch (error) {
        console.error("Error administering virus:", error);
    }
}

// Update the UI function
function updateUI(status) {
    document.getElementById('cPoint').innerHTML = `${status.player_points}`;
    document.getElementById('igCollected').innerHTML = `${status.ingredients_collected.length}`;
    document.getElementById('mAffected').innerHTML = `${status.affected_municipalities.length}`;
    document.getElementById('virus').innerHTML = `${status.virus_created ? "Yes" : "No"}`;
    document.getElementById('agents').innerHTML = `${status.agents.length}`;
}

// Attach Event Listeners
document.getElementById('gather-ingredients').addEventListener('click', gatherIngredient);
document.getElementById('create-virus').addEventListener('click', createVirus);
document.getElementById('deploy-agent').addEventListener('click', deployAgent);
document.getElementById('affect-municipalities').addEventListener('click', () => {
    if (!selectedMunicipality) { // Check if no municipality is selected
        alert("Please select the municipality you'd like to affect.");
        return; // Exit the function early if no municipality is selected
    }

    console.log(`Infecting Municipality: ${selectedMunicipality}`);
    administerVirus(selectedMunicipality);
});

// Initialize Game
document.getElementById('affect-municipalities').disabled = true; // Disable button initially
gameSetup();
