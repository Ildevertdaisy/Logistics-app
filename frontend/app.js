// Configuration de l'API GraphQL
const API_URL = 'http://localhost:8001/graphql';

// Variable globale pour stocker les produits temporaires d'une commande
let produitsCommande = [];

// Fonction utilitaire pour effectuer des requêtes GraphQL
async function graphqlQuery(query, variables = {}) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query,
                variables
            })
        });

        const result = await response.json();

        if (result.errors) {
            console.error('GraphQL Errors:', result.errors);
            throw new Error(result.errors[0].message);
        }

        return result.data;
    } catch (error) {
        console.error('Erreur GraphQL:', error);
        showToast('Erreur: ' + error.message, 'error');
        throw error;
    }
}

// Fonction pour afficher les notifications toast
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    toastMessage.textContent = message;
    toast.classList.remove('hidden');

    if (type === 'success') {
        toast.classList.remove('bg-red-600', 'bg-gray-800');
        toast.classList.add('bg-green-600');
    } else {
        toast.classList.remove('bg-green-600', 'bg-gray-800');
        toast.classList.add('bg-red-600');
    }

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Fonction pour changer d'onglet
function switchTab(tabName) {
    // Masquer toutes les sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });

    // Retirer la classe active de tous les onglets
    document.querySelectorAll('nav button').forEach(tab => {
        tab.classList.remove('tab-active', 'border-b-2', 'border-blue-500', 'text-blue-600', 'bg-blue-50');
        tab.classList.add('text-gray-600');
    });

    // Afficher la section sélectionnée
    const section = document.getElementById(`section-${tabName}`);
    if (section) {
        section.classList.remove('hidden');
        section.classList.add('fade-in');
    }

    // Activer l'onglet sélectionné
    const activeTab = document.getElementById(`tab-${tabName}`);
    if (activeTab) {
        activeTab.classList.add('tab-active', 'border-b-2', 'border-blue-500', 'text-blue-600', 'bg-blue-50');
        activeTab.classList.remove('text-gray-600');
    }

    // Charger les données de la section
    if (tabName === 'dashboard') {
        chargerDashboard();
    } else if (tabName === 'hydravions') {
        chargerHydravions();
    } else if (tabName === 'commandes') {
        chargerCommandes();
    } else if (tabName === 'clients') {
        chargerClients();
    } else if (tabName === 'produits') {
        chargerProduits();
    } else if (tabName === 'iles') {
        chargerIles();
    }
}

// ========== DASHBOARD ==========

async function chargerDashboard() {
    try {
        const query = `
            query {
                hydravions { id }
                commandes { id statut }
                clients { id }
                produits { id }
                livraisons {
                    id
                    statut
                    itineraire
                    date_depart
                    hydravion { nom }
                    commande { port_destination }
                }
            }
        `;

        const data = await graphqlQuery(query);

        // Mettre à jour les statistiques
        document.getElementById('stat-hydravions').textContent = data.hydravions.length;
        document.getElementById('stat-commandes').textContent =
            data.commandes.filter(c => c.statut !== 'livree' && c.statut !== 'annulee').length;
        document.getElementById('stat-clients').textContent = data.clients.length;
        document.getElementById('stat-produits').textContent = data.produits.length;

        // Afficher les livraisons en cours
        const livraisonsEnCours = data.livraisons.filter(l =>
            l.statut === 'en_cours' || l.statut === 'en_vol'
        );

        const livraisonsDiv = document.getElementById('livraisons-en-cours');
        if (livraisonsEnCours.length === 0) {
            livraisonsDiv.innerHTML = '<p class="text-gray-500 text-center py-4">Aucune livraison en cours</p>';
        } else {
            livraisonsDiv.innerHTML = livraisonsEnCours.map(livraison => `
                <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition duration-200 bg-yellow-50">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <h4 class="font-semibold text-gray-800">Hydravion: ${livraison.hydravion.nom}</h4>
                            <p class="text-sm text-gray-600">Destination: ${livraison.commande.port_destination}</p>
                            <p class="text-sm text-gray-600">Itinéraire: ${livraison.itineraire.join(' → ')}</p>
                            <p class="text-xs text-gray-500 mt-1">Départ: ${new Date(livraison.date_depart).toLocaleString('fr-FR')}</p>
                        </div>
                        <span class="text-xs px-2 py-1 rounded bg-yellow-200 text-yellow-800">
                            ${livraison.statut}
                        </span>
                    </div>
                </div>
            `).join('');
        }

    } catch (error) {
        console.error('Erreur lors du chargement du dashboard:', error);
    }
}

// ========== GESTION DES HYDRAVIONS ==========

async function chargerHydravions() {
    const query = `
        query {
            hydravions {
                id
                nom
                modele
                capacite_caisses
                consommation_carburant
                statut
                port_actuel
                carburant_actuel
            }
        }
    `;

    try {
        const data = await graphqlQuery(query);
        afficherHydravions(data.hydravions);
    } catch (error) {
        console.error('Erreur lors du chargement des hydravions:', error);
    }
}

function afficherHydravions(hydravions) {
    const liste = document.getElementById('liste-hydravions');

    if (!hydravions || hydravions.length === 0) {
        liste.innerHTML = '<p class="text-gray-500 text-center py-4">Aucun hydravion trouvé</p>';
        return;
    }

    const statutColors = {
        'entrepot': 'bg-gray-100 text-gray-800',
        'port': 'bg-blue-100 text-blue-800',
        'en_vol': 'bg-green-100 text-green-800',
        'maintenance': 'bg-red-100 text-red-800'
    };

    const modeleLabels = {
        'petit': '🛩️ Petit',
        'moyen': '✈️ Moyen',
        'grand': '🛫 Grand'
    };

    liste.innerHTML = hydravions.map(h => `
        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition duration-200">
            <div class="flex justify-between items-start mb-2">
                <h3 class="text-lg font-semibold text-gray-800">${h.nom}</h3>
                <span class="text-xs px-2 py-1 rounded ${statutColors[h.statut] || 'bg-gray-100 text-gray-800'}">
                    ${h.statut}
                </span>
            </div>
            <div class="text-sm text-gray-600 space-y-1">
                <p>${modeleLabels[h.modele]} - ${h.capacite_caisses} caisses</p>
                <p>⛽ Consommation: ${h.consommation_carburant}L/100km</p>
                <p>🔋 Carburant: ${h.carburant_actuel || 100}%</p>
                ${h.port_actuel ? `<p>📍 Port actuel: ${h.port_actuel}</p>` : ''}
                <p class="text-xs text-gray-400 mt-2">ID: ${h.id}</p>
            </div>
        </div>
    `).join('');
}

document.getElementById('form-hydravion').addEventListener('submit', async (e) => {
    e.preventDefault();

    const modele = document.getElementById('hydravion-modele').value;
    const capacites = {
        'petit': { capacite: 50, consommation: 15 },
        'moyen': { capacite: 100, consommation: 20 },
        'grand': { capacite: 150, consommation: 25 }
    };

    const mutation = `
        mutation CreerHydravion($input: HydravionInput!) {
            creerHydravion(input: $input) {
                id
                nom
            }
        }
    `;

    const variables = {
        input: {
            nom: document.getElementById('hydravion-nom').value,
            modele: modele,
            capacite_caisses: capacites[modele].capacite,
            consommation_carburant: capacites[modele].consommation,
            statut: document.getElementById('hydravion-statut').value,
            port_actuel: document.getElementById('hydravion-port').value || null
        }
    };

    try {
        await graphqlQuery(mutation, variables);
        showToast('Hydravion créé avec succès!');
        document.getElementById('form-hydravion').reset();
        chargerHydravions();
    } catch (error) {
        showToast('Erreur lors de la création de l\'hydravion', 'error');
    }
});

// ========== GESTION DES COMMANDES ==========

async function chargerCommandes() {
    const query = `
        query {
            commandes {
                id
                client { nom prenom }
                port_destination
                nombre_caisses_requises
                date_commande
                date_livraison_souhaitee
                statut
                priorite
                produits {
                    produit_id
                    quantite
                    produit {
                        nom
                    }
                }
            }
        }
    `;

    try {
        const data = await graphqlQuery(query);
        afficherCommandes(data.commandes);
    } catch (error) {
        console.error('Erreur lors du chargement des commandes:', error);
    }
}

function afficherCommandes(commandes) {
    const liste = document.getElementById('liste-commandes');

    if (!commandes || commandes.length === 0) {
        liste.innerHTML = '<p class="text-gray-500 text-center py-4">Aucune commande trouvée</p>';
        return;
    }

    const statutColors = {
        'en_attente': 'bg-yellow-100 text-yellow-800',
        'en_preparation': 'bg-blue-100 text-blue-800',
        'prete': 'bg-green-100 text-green-800',
        'en_livraison': 'bg-purple-100 text-purple-800',
        'livree': 'bg-gray-100 text-gray-800',
        'annulee': 'bg-red-100 text-red-800'
    };

    liste.innerHTML = commandes.map(c => `
        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition duration-200">
            <div class="flex justify-between items-start mb-2">
                <div>
                    <h3 class="text-lg font-semibold text-gray-800">
                        ${c.client ? `${c.client.prenom} ${c.client.nom}` : 'Client inconnu'}
                    </h3>
                    <p class="text-sm text-gray-600">→ ${c.port_destination}</p>
                </div>
                <div class="flex flex-col items-end gap-1">
                    <span class="text-xs px-2 py-1 rounded ${statutColors[c.statut] || 'bg-gray-100 text-gray-800'}">
                        ${c.statut}
                    </span>
                    ${c.priorite > 3 ? '<span class="text-xs px-2 py-1 rounded bg-red-100 text-red-800">Urgent</span>' : ''}
                </div>
            </div>
            <div class="text-sm text-gray-600 space-y-1">
                <p>📦 ${c.nombre_caisses_requises} caisse(s) - ${c.produits.length} produit(s)</p>
                <p>🏷️ Priorité: ${c.priorite}/5</p>
                <p class="text-xs text-gray-500">Commandé le ${new Date(c.date_commande).toLocaleDateString('fr-FR')}</p>
                <p class="text-xs text-gray-400">ID: ${c.id}</p>
            </div>
        </div>
    `).join('');
}

function ajouterProduitCommande() {
    const produitId = document.getElementById('produit-id-temp').value.trim();
    const quantite = parseInt(document.getElementById('produit-quantite-temp').value);

    if (!produitId || quantite < 1) {
        showToast('Veuillez remplir les champs produit', 'error');
        return;
    }

    produitsCommande.push({ produit_id: produitId, quantite: quantite });

    // Afficher la liste
    const listeDiv = document.getElementById('liste-produits-temp');
    listeDiv.innerHTML = produitsCommande.map((p, index) => `
        <div class="flex justify-between items-center bg-gray-100 p-2 rounded">
            <span class="text-sm">Produit ${p.produit_id} - Qté: ${p.quantite}</span>
            <button type="button" onclick="retirerProduitCommande(${index})"
                    class="text-red-600 hover:text-red-800 text-sm">❌</button>
        </div>
    `).join('');

    // Réinitialiser les champs
    document.getElementById('produit-id-temp').value = '';
    document.getElementById('produit-quantite-temp').value = '1';
}

function retirerProduitCommande(index) {
    produitsCommande.splice(index, 1);
    const listeDiv = document.getElementById('liste-produits-temp');
    listeDiv.innerHTML = produitsCommande.map((p, i) => `
        <div class="flex justify-between items-center bg-gray-100 p-2 rounded">
            <span class="text-sm">Produit ${p.produit_id} - Qté: ${p.quantite}</span>
            <button type="button" onclick="retirerProduitCommande(${i})"
                    class="text-red-600 hover:text-red-800 text-sm">❌</button>
        </div>
    `).join('');
}

document.getElementById('form-commande').addEventListener('submit', async (e) => {
    e.preventDefault();

    if (produitsCommande.length === 0) {
        showToast('Veuillez ajouter au moins un produit', 'error');
        return;
    }

    const mutation = `
        mutation CreerCommande($input: CommandeInput!) {
            creerCommande(input: $input) {
                id
            }
        }
    `;

    const dateLivraison = document.getElementById('commande-date').value;

    const variables = {
        input: {
            client_id: document.getElementById('commande-client-id').value,
            produits: produitsCommande,
            port_destination: document.getElementById('commande-port').value,
            priorite: parseInt(document.getElementById('commande-priorite').value),
            date_livraison_souhaitee: dateLivraison || null
        }
    };

    try {
        await graphqlQuery(mutation, variables);
        showToast('Commande créée avec succès!');
        document.getElementById('form-commande').reset();
        produitsCommande = [];
        document.getElementById('liste-produits-temp').innerHTML = '';
        chargerCommandes();
    } catch (error) {
        showToast('Erreur lors de la création de la commande', 'error');
    }
});

// ========== GESTION DES CLIENTS ==========

async function chargerClients() {
    const query = `
        query {
            clients {
                id
                nom
                prenom
                email
                telephone
                role
                organisation
                ile_principale
            }
        }
    `;

    try {
        const data = await graphqlQuery(query);
        afficherClients(data.clients);
    } catch (error) {
        console.error('Erreur lors du chargement des clients:', error);
    }
}

function afficherClients(clients) {
    const liste = document.getElementById('liste-clients');

    if (!clients || clients.length === 0) {
        liste.innerHTML = '<p class="text-gray-500 text-center py-4">Aucun client trouvé</p>';
        return;
    }

    const roleColors = {
        'volcanologue': 'bg-red-100 text-red-800',
        'biologiste_marin': 'bg-blue-100 text-blue-800',
        'zoologue': 'bg-green-100 text-green-800',
        'botaniste': 'bg-emerald-100 text-emerald-800',
        'geologue': 'bg-amber-100 text-amber-800'
    };

    const roleLabels = {
        'volcanologue': '🌋 Volcanologue',
        'biologiste_marin': '🐟 Biologiste marin',
        'zoologue': '🦎 Zoologue',
        'botaniste': '🌿 Botaniste',
        'geologue': '⛰️ Géologue'
    };

    liste.innerHTML = clients.map(c => `
        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition duration-200">
            <div class="flex justify-between items-start mb-2">
                <h3 class="text-lg font-semibold text-gray-800">${c.prenom} ${c.nom}</h3>
                <span class="text-xs px-2 py-1 rounded ${roleColors[c.role] || 'bg-gray-100 text-gray-800'}">
                    ${roleLabels[c.role] || c.role}
                </span>
            </div>
            <div class="text-sm text-gray-600 space-y-1">
                <p>🏢 ${c.organisation}</p>
                <p>🏝️ ${c.ile_principale}</p>
                <p>📧 ${c.email}</p>
                <p>📱 ${c.telephone}</p>
                <p class="text-xs text-gray-400 mt-2">ID: ${c.id}</p>
            </div>
        </div>
    `).join('');
}

document.getElementById('form-client').addEventListener('submit', async (e) => {
    e.preventDefault();

    const mutation = `
        mutation CreerClient($input: ClientInput!) {
            creerClient(input: $input) {
                id
                nom
            }
        }
    `;

    const variables = {
        input: {
            nom: document.getElementById('client-nom').value,
            prenom: document.getElementById('client-prenom').value,
            email: document.getElementById('client-email').value,
            telephone: document.getElementById('client-telephone').value,
            role: document.getElementById('client-role').value,
            organisation: document.getElementById('client-organisation').value,
            ile_principale: document.getElementById('client-ile').value
        }
    };

    try {
        await graphqlQuery(mutation, variables);
        showToast('Client créé avec succès!');
        document.getElementById('form-client').reset();
        chargerClients();
    } catch (error) {
        showToast('Erreur lors de la création du client', 'error');
    }
});

// ========== GESTION DES PRODUITS ==========

async function chargerProduits() {
    const query = `
        query {
            produits {
                id
                nom
                description
                categorie
                poids
                dimensions {
                    hauteur
                    largeur
                    profondeur
                }
                stock_disponible
            }
        }
    `;

    try {
        const data = await graphqlQuery(query);
        afficherProduits(data.produits);
    } catch (error) {
        console.error('Erreur lors du chargement des produits:', error);
    }
}

function afficherProduits(produits) {
    const liste = document.getElementById('liste-produits');

    if (!produits || produits.length === 0) {
        liste.innerHTML = '<p class="text-gray-500 text-center py-4">Aucun produit trouvé</p>';
        return;
    }

    const categorieLabels = {
        'equipement_plongee': '🤿 Équipement plongée',
        'materiel_laboratoire': '🔬 Matériel laboratoire',
        'equipement_observation': '🔭 Équipement observation',
        'materiel_camping': '⛺ Matériel camping',
        'echantillons': '🧪 Échantillons',
        'medicaments': '💊 Médicaments'
    };

    liste.innerHTML = produits.map(p => `
        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition duration-200">
            <div class="flex justify-between items-start mb-2">
                <h3 class="text-lg font-semibold text-gray-800">${p.nom}</h3>
                <span class="text-xs px-2 py-1 rounded ${p.stock_disponible > 10 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                    Stock: ${p.stock_disponible}
                </span>
            </div>
            <div class="text-sm text-gray-600 space-y-1">
                <p>${categorieLabels[p.categorie] || p.categorie}</p>
                <p class="text-xs">${p.description}</p>
                <p>⚖️ ${p.poids} kg</p>
                <p>📐 ${p.dimensions.hauteur} × ${p.dimensions.largeur} × ${p.dimensions.profondeur} cm</p>
                <p class="text-xs text-gray-400 mt-2">ID: ${p.id}</p>
            </div>
        </div>
    `).join('');
}

document.getElementById('form-produit').addEventListener('submit', async (e) => {
    e.preventDefault();

    const mutation = `
        mutation CreerProduit($input: ProduitInput!) {
            creerProduit(input: $input) {
                id
                nom
            }
        }
    `;

    const variables = {
        input: {
            nom: document.getElementById('produit-nom').value,
            description: document.getElementById('produit-description').value,
            categorie: document.getElementById('produit-categorie').value,
            poids: parseFloat(document.getElementById('produit-poids').value),
            stock_disponible: parseInt(document.getElementById('produit-stock').value),
            dimensions: {
                hauteur: parseFloat(document.getElementById('produit-hauteur').value),
                largeur: parseFloat(document.getElementById('produit-largeur').value),
                profondeur: parseFloat(document.getElementById('produit-profondeur').value)
            }
        }
    };

    try {
        await graphqlQuery(mutation, variables);
        showToast('Produit créé avec succès!');
        document.getElementById('form-produit').reset();
        chargerProduits();
    } catch (error) {
        showToast('Erreur lors de la création du produit', 'error');
    }
});

// ========== GESTION DES ÎLES ==========

async function chargerIles() {
    const query = `
        query {
            iles {
                nom
                coordonnees {
                    latitude
                    longitude
                }
                superficie
                population
                description
                ports {
                    nom
                    nombre_lockers
                    capacite_hydravions
                }
            }
        }
    `;

    try {
        const data = await graphqlQuery(query);
        afficherIles(data.iles);
    } catch (error) {
        console.error('Erreur lors du chargement des îles:', error);
    }
}

function afficherIles(iles) {
    const liste = document.getElementById('liste-iles');

    if (!iles || iles.length === 0) {
        liste.innerHTML = '<p class="text-gray-500 text-center py-4">Aucune île trouvée</p>';
        return;
    }

    liste.innerHTML = iles.map(ile => `
        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition duration-200">
            <h3 class="text-lg font-semibold text-gray-800 mb-2">🏝️ ${ile.nom}</h3>
            <div class="text-sm text-gray-600 space-y-1">
                <p>${ile.description}</p>
                <p>📍 ${ile.coordonnees.latitude.toFixed(4)}, ${ile.coordonnees.longitude.toFixed(4)}</p>
                <p>📏 Superficie: ${ile.superficie} km²</p>
                ${ile.population ? `<p>👥 Population: ${ile.population}</p>` : ''}
                ${ile.ports && ile.ports.length > 0 ? `
                    <div class="mt-2 pt-2 border-t border-gray-200">
                        <p class="font-semibold text-xs text-gray-700">Ports (${ile.ports.length}):</p>
                        <ul class="list-disc list-inside text-xs mt-1">
                            ${ile.ports.map(p => `<li>${p.nom} - ${p.nombre_lockers} lockers, ${p.capacite_hydravions} places</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

document.getElementById('form-ile').addEventListener('submit', async (e) => {
    e.preventDefault();

    const mutation = `
        mutation CreerIle($input: IleInput!) {
            creerIle(input: $input) {
                nom
            }
        }
    `;

    const variables = {
        input: {
            nom: document.getElementById('ile-nom').value,
            coordonnees: {
                latitude: parseFloat(document.getElementById('ile-latitude').value),
                longitude: parseFloat(document.getElementById('ile-longitude').value)
            },
            superficie: parseFloat(document.getElementById('ile-superficie').value),
            population: parseInt(document.getElementById('ile-population').value) || 0,
            description: document.getElementById('ile-description').value
        }
    };

    try {
        await graphqlQuery(mutation, variables);
        showToast('Île créée avec succès!');
        document.getElementById('form-ile').reset();
        chargerIles();
    } catch (error) {
        showToast('Erreur lors de la création de l\'île', 'error');
    }
});

// Charger le dashboard au démarrage
document.addEventListener('DOMContentLoaded', () => {
    chargerDashboard();
});
