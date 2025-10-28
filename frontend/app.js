// Configuration
// Utiliser l'URL relative pour que ça fonctionne aussi bien en local qu'en production
const API_BASE_URL = window.location.origin;
console.log('API Base URL configurée:', API_BASE_URL);

// Variables globales
let map;
let routeLayer;
let currentGPX = null;

// Initialisation de la carte
function initMap() {
    map = L.map('map').setView([48.8566, 2.3522], 12); // Paris par défaut

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    // Groupe de couches pour la route
    routeLayer = L.layerGroup().addTo(map);
}

// Afficher la route sur la carte
function displayRoute(geojson, startAddress) {
    // Nettoyer la route précédente
    routeLayer.clearLayers();

    // Ajouter la nouvelle route
    const routeStyle = {
        color: '#fc5200',
        weight: 4,
        opacity: 0.8
    };

    const geoJsonLayer = L.geoJSON(geojson, {
        style: routeStyle
    }).addTo(routeLayer);

    // Centrer la carte sur la route
    map.fitBounds(geoJsonLayer.getBounds(), {
        padding: [50, 50]
    });

    // Ajouter un marqueur au point de départ
    const startCoords = geojson.features[0].geometry.coordinates[0];
    L.marker([startCoords[1], startCoords[0]], {
        icon: L.divIcon({
            className: 'start-marker',
            iconSize: [20, 20]
        })
    })
    .bindPopup(`<strong>Départ</strong><br>${startAddress}`)
    .addTo(routeLayer);
}

// Mettre à jour les métriques
function updateMetrics(metrics, startAddress) {
    document.getElementById('metricDistance').textContent = metrics.distance_km;
    document.getElementById('metricElevGain').textContent = metrics.elevation_gain_m;
    document.getElementById('metricElevLoss').textContent = metrics.elevation_loss_m;
    document.getElementById('metricDuration').textContent = metrics.estimated_duration_min || '-';
    document.getElementById('startAddressInfo').textContent = `Départ: ${startAddress}`;

    document.getElementById('metrics').classList.remove('d-none');
    document.getElementById('exportBtn').classList.remove('d-none');
}

// Afficher une erreur
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorAlert').classList.remove('d-none');

    // Masquer l'erreur après 5 secondes
    setTimeout(() => {
        document.getElementById('errorAlert').classList.add('d-none');
    }, 5000);
}

// Masquer l'erreur
function hideError() {
    document.getElementById('errorAlert').classList.add('d-none');
}

// Gérer le bouton de chargement
function setLoading(isLoading) {
    const btn = document.getElementById('generateBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');

    if (isLoading) {
        btn.disabled = true;
        btnText.textContent = 'Génération en cours...';
        btnSpinner.classList.remove('d-none');
    } else {
        btn.disabled = false;
        btnText.textContent = 'Générer le parcours';
        btnSpinner.classList.add('d-none');
    }
}

// Générer le parcours
async function generateRoute(event) {
    event.preventDefault();
    hideError();
    setLoading(true);

    // Récupérer les données du formulaire
    const formData = {
        start_location: document.getElementById('startLocation').value,
        distance_km: parseFloat(document.getElementById('distance').value),
        training_type: document.getElementById('trainingType').value,
        elevation_preference: document.getElementById('elevation').value,
        avoid_busy_roads: document.getElementById('avoidBusyRoads').checked,
        prefer_parks: document.getElementById('preferParks').checked
    };

    try {
        // Debug: afficher l'URL utilisée
        const apiUrl = `${API_BASE_URL}/api/generate-route`;
        console.log('API URL:', apiUrl);
        console.log('Form Data:', formData);

        // Appeler l'API
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur lors de la génération du parcours');
        }

        const data = await response.json();

        // Sauvegarder le GPX
        currentGPX = data.gpx;

        // Afficher la route sur la carte
        displayRoute(data.geojson, data.start_address);

        // Mettre à jour les métriques
        updateMetrics(data.metrics, data.start_address);

    } catch (error) {
        console.error('Erreur:', error);
        showError(error.message || 'Une erreur est survenue lors de la génération du parcours');
    } finally {
        setLoading(false);
    }
}

// Exporter le GPX
function exportGPX() {
    if (!currentGPX) {
        showError('Aucun parcours à exporter');
        return;
    }

    // Créer un blob et télécharger
    const blob = new Blob([currentGPX], { type: 'application/gpx+xml' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `parcours_${new Date().getTime()}.gpx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    initMap();

    // Gestionnaires d'événements
    document.getElementById('routeForm').addEventListener('submit', generateRoute);
    document.getElementById('exportBtn').addEventListener('click', exportGPX);

    // Exemples pré-remplis selon la localisation (Paris par défaut)
    const examples = [
        'Place de la République, Paris',
        'Tour Eiffel, Paris',
        'Jardin du Luxembourg, Paris',
        'Parc des Buttes-Chaumont, Paris'
    ];

    // Suggestion d'adresse au focus
    const startLocationInput = document.getElementById('startLocation');
    startLocationInput.addEventListener('focus', () => {
        if (!startLocationInput.value) {
            startLocationInput.placeholder = examples[Math.floor(Math.random() * examples.length)];
        }
    });
});
