'use strict';

// Global State and Variables
let GameState = {
    player_points: 5, // Initial points set to 5
    ingredients_collected: [], // Empty at start
    affected_municipalities: [], // No municipalities affected initially
    virus_created: false, // Virus not created initially
    agents: [] // No agents deployed initially
};

const redIcon = L.divIcon({ className: 'red-icon' });
const purpleIcon = L.divIcon({ className: 'purple-icon' });
let selectedMunicipality = null; // Tracks the currently selected municipality
let currentActiveMarker = null; // To track the active marker

// Helsinki-Vantaa Airport Coordinates
const helsinkiVantaa = L.latLng(60.3172, 24.9634);  // Helsinki-Vantaa coordinates

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

    // Check game-ending conditions
    if (GameState.player_points <= 0) {
        alert("You ran out of points. Game over!");
        resetGame();
    }

    if (GameState.affected_municipalities.length >= 10) {
        alert("Congratulations! You've affected 10 municipalities and won the game!");
        resetGame();
    }
}

// Game Reset
function resetGame() {
    GameState = {
        player_points: 5, // Reset to 5 points
        ingredients_collected: [],
        affected_municipalities: [],
        virus_created: false,
        agents: []
    };
    updateUI(GameState);
    location.reload();
}

// Game Setup and Initialization
async function gameSetup() {
    try {
        const gameData = await getData('flyto.json');
        console.log("Game Setup Data:", gameData);

        const markerMap = {}; // Track markers for all municipalities

        // Add markers to map
        gameData.location.forEach(location => {
            const marker = L.marker([location.latitude, location.longitude]).addTo(map);
            const popUpContent = createPopupContent(location);
            marker.bindPopup(popUpContent);

            if (location.name === "Helsinki Vantaa Airport") {
                marker.setIcon(redIcon); // Set Helsinki as active by default
                 currentActiveMarker = marker; // Track as the currently active marker
                 selectedMunicipality = location.name; // Set as the initially selected municipality
            } else {
                marker.setIcon(purpleIcon);
            }

            markerMap[location.name] = marker;


            // Add click event to update the selected municipality
            marker.on('click', () => {
                selectedMunicipality = location.name;
                document.getElementById('affect-municipalities').disabled = false; // Enable the button

                // Reset all markers to purple and set the clicked marker to red (active)
                Object.values(markerMap).forEach(m => m.setIcon(purpleIcon));
                marker.setIcon(redIcon);
                currentActiveMarker = marker; // Update the current active marker
            });
        });

        // Initialize game state
        updateState({
            player_points: 5, // Ensure points start from 5
            ingredients_collected: [],
            affected_municipalities: [],
            agents: [] // Empty array for agents
        });

        // Display alert message on page load
        alert("Hey, you terrorist! Your goal is to spread the virus to 10 destinations. Good luck!");
    } catch (error) {
        console.error("Error during game setup:", error);
    }
}

function createPopupContent(location) {
    const popUpContent = document.createElement('div');
    const airportName = document.createElement('span');
    airportName.innerHTML = location.name;
    popUpContent.append(airportName);

    // Calculate distance from Helsinki-Vantaa Airport using Leaflet's distanceTo method
    let distanceText = 'Distance: undefined'; // Default value if no distance is calculated
    if (location.name !== "Helsinki Vantaa Airport") {
        const distance = helsinkiVantaa.distanceTo(L.latLng(location.latitude, location.longitude)) / 1000;
        distanceText = `Distance: ${distance.toFixed(1)} km`;
    } else {
        distanceText = 'Distance: 0 km'; // Helsinki airport itself
    }

    const p = document.createElement('p');
    p.innerHTML = distanceText;
    popUpContent.append(p);

    return popUpContent;
}

// Actions and Event Handlers
async function gatherIngredient() {
    try {
        const allIngredients = ["Ingredient1", "Ingredient2", "Ingredient3", "Ingredient4", "Ingredient5"];

        // Filter ingredients that are not yet collected
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
        if (GameState.ingredients_collected.length >= 5) {
            GameState.ingredients_collected.splice(0, 5); // Remove 5 ingredients
            GameState.virus_created = true;
            updateState({ virus_created: true, ingredients_collected: GameState.ingredients_collected });
            alert("Virus created successfully!");
        } else {
            alert("Not enough ingredients to create the virus.");
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
            GameState.player_points -= 5;
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
                if (!GameState.affected_municipalities.includes(municipality)) {
                    const randomDiscount = Math.floor(Math.random() * 11) + 10; // Random integer between 10 and 20
                    if (GameState.player_points >= randomDiscount) {
                        GameState.affected_municipalities.push(municipality);
                        GameState.agents.pop(); // Reduce the agent count by 1
                        GameState.virus_created = false; // Reset virus status
                        GameState.player_points -= randomDiscount; // Deduct random points
                        updateState({
                            affected_municipalities: GameState.affected_municipalities,
                            agents: GameState.agents,
                            virus_created: false,
                            player_points: GameState.player_points
                        });

                        alert(`${municipality} has been infected! ${randomDiscount} points deducted.`);
                    } else {
                        alert("Not enough points to infect the municipality.");
                    }
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
    const points = status.player_points || 0;
    const ingredientsCollected = status.ingredients_collected.length || 0;
    const affectedMunicipalities = `${status.affected_municipalities.length}/10`;
    const virusCreated = status.virus_created ? "Yes" : "No";
    const agents = status.agents.length || 0;

    document.getElementById('cPoint').innerHTML = `${points}`;
    document.getElementById('igCollected').innerHTML = `${ingredientsCollected}`;
    document.getElementById('mAffected').innerHTML = `${affectedMunicipalities}`;
    document.getElementById('virus').innerHTML = virusCreated;
    document.getElementById('agents').innerHTML = `${agents}`;
}

// Attach Event Listeners
document.getElementById('gather-ingredients').addEventListener('click', gatherIngredient);
document.getElementById('create-virus').addEventListener('click', createVirus);
document.getElementById('deploy-agent').addEventListener('click', deployAgent);
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('affect-municipalities').addEventListener('click', () => {
        if (!selectedMunicipality) {
            alert("Select a municipality first.");
            return;
        }
        administerVirus(selectedMunicipality);
    });
});

// Initialize Game
document.getElementById('gather-ingredients').disabled = false;
gameSetup();
