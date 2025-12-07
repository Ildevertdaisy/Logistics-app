const queryInput = document.getElementById("query");
const variablesInput = document.getElementById("variables");
const endpointInput = document.getElementById("endpoint");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const copyBtn = document.getElementById("copy-result");

const templates = {
  hydravions: `query {
  hydravions {
    id
    nom
    modele
    capacite_caisses
    statut
    port_actuel
  }
}`,
  clients: `query {
  clients {
    id
    nom
    prenom
    ile_principale
    organisation
  }
}`,
  ports: `query {
  ports {
    nom
    ile
    nombre_lockers
    capacite_hydravions
  }
}`,
  routes: `query($depart: String!, $arrivee: String!) {
  routeOptimale(port_depart: $depart, port_arrivee: $arrivee) {
    ports
    distance_totale
    consommation_estimee
    segments {
      depart
      arrivee
      distance
    }
  }
}`,
};

function setTemplate(name) {
  if (templates[name]) {
    queryInput.value = templates[name];
    if (name === "routes") {
      variablesInput.value = JSON.stringify({ depart: "San Cristobal", arrivee: "Santa Cruz" }, null, 2);
    }
  }
}

async function executeQuery() {
  const endpoint = endpointInput.value.trim();
  const query = queryInput.value.trim();
  const variables = variablesInput.value.trim();

  if (!endpoint || !query) {
    statusEl.textContent = "Veuillez fournir un endpoint et une requête.";
    statusEl.className = "text-sm text-amber-600";
    return;
  }

  let parsedVariables = undefined;
  if (variables) {
    try {
      parsedVariables = JSON.parse(variables);
    } catch (error) {
      statusEl.textContent = "Variables JSON invalides";
      statusEl.className = "text-sm text-rose-600";
      return;
    }
  }

  statusEl.textContent = "Envoi de la requête...";
  statusEl.className = "text-sm text-slate-500";

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, variables: parsedVariables }),
    });

    const payload = await response.json();
    const formatted = JSON.stringify(payload, null, 2);
    resultEl.textContent = formatted;

    statusEl.textContent = response.ok ? "Requête exécutée" : `Erreur ${response.status}`;
    statusEl.className = response.ok ? "text-sm text-emerald-600" : "text-sm text-rose-600";
  } catch (error) {
    console.error(error);
    statusEl.textContent = "Impossible de joindre l'API";
    statusEl.className = "text-sm text-rose-600";
    resultEl.textContent = error.toString();
  }
}

function copyResult() {
  const text = resultEl.textContent;
  navigator.clipboard.writeText(text).then(() => {
    copyBtn.textContent = "Copié !";
    setTimeout(() => (copyBtn.textContent = "Copier"), 1200);
  });
}

// Listeners
document.querySelectorAll(".template-btn").forEach((btn) => {
  btn.addEventListener("click", () => setTemplate(btn.dataset.template));
});

document.getElementById("execute").addEventListener("click", executeQuery);
copyBtn.addEventListener("click", copyResult);

// Pré-remplir une requête par défaut
setTemplate("hydravions");
