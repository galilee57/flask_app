// projet_musculation.js

const API_EXERCICES_URL = window.API_EXERCICES_URL;
const API_PROGRAMMES_BASE = window.API_PROGRAMMES_BASE;
const GIF_BASE_URL = window.GIF_BASE_URL;

// Catalogues et état courant
let exercicesCatalog = [];      // vient de exercices.json
let currentProgram = [];        // [{ exercice_id, reps, weight }, ...]
let currentProgramId = null;    // null = nouveau programme, sinon id existant

// Références DOM
const exerciseSelect = document.getElementById("exerciseSelect");
const repsInput = document.getElementById("nb_rep");
const weightInput = document.getElementById("weight");  // id généré par WTForms
const addExerciseBtn = document.getElementById("add_exercice_form");

const exerciseDetailsEl = document.getElementById("exerciseDetails");
const programNameInput = document.querySelector("#programForm input[name='plan_name']");
const saveProgramBtn = document.getElementById("save_program");
const loadProgramBtn = document.getElementById("load_program");
const programSelect = document.getElementById("programSelect");
const programDetailsEl = document.getElementById("programDetails");
const newProgramBtn = document.getElementById("new_program");
const resetProgramBtn = document.getElementById("reset_program");

const analyseProgramBtn = document.getElementById("analyze_program");
const programAnalysisEl = document.getElementById("programAnalysis");


// ---------- 1. Charger les exercices et remplir le select ----------
async function loadExercices() {
  try {
    const res = await fetch(API_EXERCICES_URL);
    if (!res.ok) {
      console.error("Erreur chargement exercices", res.status);
      return;
    }
    exercicesCatalog = await res.json();

    // remplir la liste déroulante des exercices
    exercicesCatalog.forEach((ex, index) => {
      const option = document.createElement("option");
      option.value = index;           // index = notre exercice_id
      option.textContent = ex.exercise;
      exerciseSelect.appendChild(option);
    });
  } catch (err) {
    console.error("Erreur réseau lors du chargement des exercices :", err);
  }
}

// afficher les détails de l'exercice sélectionné
function renderExerciseDetails(exerciceIndex) {
  const ex = exercicesCatalog[exerciceIndex];
  if (!ex) {
    exerciseDetailsEl.innerHTML = "";
    return;
  }

  exerciseDetailsEl.innerHTML = `
    <div class="exercise-card">
      <div class="exercise-layout">
        <div class="exercise-text">
          <h2>${ex.exercise} (${ex.exercise_en})</h2>
          <p><strong>Région :</strong> ${ex.region}</p>
          <p><strong>Matériel :</strong> ${ex.equipment.join(", ")}</p>
          <p><strong>Articulations :</strong> ${ex.joints.join(", ")}</p>
          <p><strong>Muscles principaux :</strong> ${ex.primary_muscles.join(", ")}</p>
          <p><strong>Muscles secondaires :</strong> ${ex.secondary_muscles.join(", ")}</p>
        </div>
        <img src="${GIF_BASE_URL}${ex.gif}" alt="GIF ${ex.exercise}" style="max-width: 320px; border-radius: 8px;">
      </div>
    </div>
  `;
}


// ---------- 2. Gestion du programme courant en mémoire ----------
function resetProgram() {
  currentProgramId = null;
  currentProgram = [];
  programNameInput.value = "";
  programSelect.value = "";
  programDetailsEl.innerHTML = "<p>Aucun exercice dans ce programme pour l'instant.</p>";
}

function addExerciseToCurrentProgram() {
  const index = parseInt(exerciseSelect.value, 10);
  const reps = parseInt(repsInput.value, 10);
  const weight = parseInt(weightInput.value, 10);

  if (Number.isNaN(index)) {
    alert("Choisis un exercice");
    return;
  }
  if (Number.isNaN(reps) || reps <= 0) {
    alert("Nombre de répétitions invalide");
    return;
  }
  if (Number.isNaN(weight) || weight <= 0) {
    alert("Poids invalide");
    return;
  }

  const ex = exercicesCatalog[index];
  if (!ex) {
    alert("Exercice introuvable");
    return;
  }

  const exercice_id = ex.exercise;  // 🔹 on prend le nom

  currentProgram.push({ exercice_id, reps, weight });
  console.log("CURRENT PROGRAM :", currentProgram);
  renderProgramDetails();
}

function renderProgramDetails() {
  if (currentProgram.length === 0) {
    programDetailsEl.innerHTML = "<p>Aucun exercice dans ce programme pour l'instant.</p>";
    return;
  }

  const rows = currentProgram.map((item, idx) => {
    const name = item.exercice_id;  // nom de l'exercice

    return `
      <tr>
        <td>${idx + 1}</td>
        <td>${name}</td>
        <td>${item.reps}</td>
        <td>${item.weight} kg</td>
        <td class="text-center">
          <button 
            class="btn btn-sm btn-outline-danger"
            title="Supprimer"
            onclick="removeExerciseFromProgram(${idx})">
            ✖
          </button>
        </td>
      </tr>
    `;
  }).join("");

  programDetailsEl.innerHTML = `
    <table class="table table-striped align-middle">
      <thead>
        <tr>
          <th>#</th>
          <th>Exercice</th>
          <th>Reps</th>
          <th>Poids</th>
          <th class="text-center">Suppr.</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `;
}

function removeExerciseFromProgram(index) {
  if (!confirm("Supprimer cet exercice du programme ?")) {
    return;
  }

  currentProgram.splice(index, 1); // supprime l’élément
  renderProgramDetails();          // rafraîchit l’affichage
}

// ---------- 3. Sauvegarde du programme (POST ou PUT) ----------
async function saveCurrentProgram() {
  const name = programNameInput.value.trim();
  if (!name) {
    alert("Donne un nom à ton programme");
    return;
  }
  if (currentProgram.length === 0) {
    alert("Ajoute au moins un exercice au programme");
    return;
  }

  const payload = {
    name,
    exercices: currentProgram.map(e => ({
      exercice_id: e.exercice_id,
      reps: e.reps,
      weight: e.weight,
    })),
  };

  const isUpdate = currentProgramId !== null;
  const url = isUpdate
    ? `${API_PROGRAMMES_BASE}/${currentProgramId}`
    : API_PROGRAMMES_BASE;
  const method = isUpdate ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      console.error("Erreur sauvegarde programme", res.status, err);
      alert("Erreur lors de la sauvegarde du programme");
      return;
    }

    const data = await res.json();
    if (!isUpdate && data.programme_id) {
      currentProgramId = data.programme_id;
    }

    await loadProgrammesList(); // met à jour la liste déroulante
    alert(isUpdate ? "Programme mis à jour" : "Programme sauvegardé");
  } catch (err) {
    console.error("Erreur réseau lors de la sauvegarde :", err);
    alert("Erreur réseau lors de la sauvegarde du programme");
  }
}


// ---------- 4. Charger la liste des programmes dans le select ----------
async function loadProgrammesList() {
  try {
    const res = await fetch(API_PROGRAMMES_BASE);
    if (!res.ok) {
      console.error("Erreur chargement programmes", res.status);
      return;
    }
    const programmes = await res.json();

    // vider puis remplir
    programSelect.innerHTML = `<option value="">-- Choisir --</option>`;

    programmes.forEach(p => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = `${p.name} (${p.exercices_count} exos)`;
      programSelect.appendChild(opt);
    });
  } catch (err) {
    console.error("Erreur réseau lors du chargement des programmes :", err);
  }
}


// ---------- 5. Charger un programme (GET /api/programmes/<id>) ----------
async function loadSelectedProgram() {
  const id = parseInt(programSelect.value, 10);
  if (Number.isNaN(id)) {
    alert("Choisis un programme à charger");
    return;
  }

  try {
    const res = await fetch(`${API_PROGRAMMES_BASE}/${id}`);
    if (!res.ok) {
      console.error("Erreur chargement programme", res.status);
      alert("Erreur lors du chargement du programme");
      return;
    }

    const prog = await res.json();
    currentProgramId = prog.id;
    programNameInput.value = prog.name;

    // reconstruire currentProgram depuis les données renvoyées
    currentProgram = prog.exercices.map(ex => ({
      exercice_id: ex.exercice_id,
      reps: ex.reps,
      weight: ex.weight,
    }));

    renderProgramDetails();
  } catch (err) {
    console.error("Erreur réseau lors du chargement du programme :", err);
    alert("Erreur réseau lors du chargement du programme");
  }
}

// ---------- 6. Suppression du programme courant (DELETE) ----------
async function deleteCurrentProgram() {
  if (currentProgramId === null) {
    alert("Aucun programme chargé à supprimer.");
    return;
  }

  if (!confirm("⚠️ Supprimer définitivement ce programme ?")) {
    return;
  }

  try {
    const res = await fetch(`${API_PROGRAMMES_BASE}/${currentProgramId}`, {
      method: "DELETE",
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      console.error("Erreur suppression programme", res.status, err);
      alert("Erreur lors de la suppression du programme");
      return;
    }

    // ✅ Reset de l'UI
    currentProgramId = null;
    currentProgram = [];
    programNameInput.value = "";
    programSelect.value = "";

    renderProgramDetails();
    await loadProgrammesList();

    alert("✅ Programme supprimé");
  } catch (err) {
    console.error("Erreur réseau suppression :", err);
    alert("Erreur réseau lors de la suppression");
  }
}

// ---------- 7. Analyse du programme (GET /api/programmes/<id>/analyse) ----------
async function analyseCurrentProgram() {
  if (currentProgramId === null) {
    alert("Sauvegarde d'abord le programme pour pouvoir l'analyser.");
    return;
  }

  try {
    const url = `${API_PROGRAMMES_BASE}/${currentProgramId}/analyse`;
    const res = await fetch(url);

    if (!res.ok) {
      console.error("Erreur analyse programme", res.status);
      alert("Erreur lors de l'analyse du programme");
      return;
    }

    const data = await res.json();
    const totals = data.totals || {};
    const perEx = data.per_exercice || [];

    const totalForce = totals.force || 0;
    const totalHyp = totals.hypertrophie || 0;
    const totalEnd = totals.endurance || 0;
    const sumAll = totalForce + totalHyp + totalEnd || 1; // éviter division par 0

    const pctForce = (totalForce / sumAll) * 100;
    const pctHyp = (totalHyp / sumAll) * 100;
    const pctEnd = (totalEnd / sumAll) * 100;

    // --- Tableau détaillé par exercice ---
    const rows = perEx.map((ex, idx) => `
      <tr>
        <td>${idx + 1}</td>
        <td>${ex.exercice_id}</td>
        <td>${ex.reps}</td>
        <td>${ex.weight} kg</td>
        <td>${ex.volume}</td>
        <td>${ex.scores.force.toFixed(1)}</td>
        <td>${ex.scores.hypertrophie.toFixed(1)}</td>
        <td>${ex.scores.endurance.toFixed(1)}</td>
      </tr>
    `).join("");

    programAnalysisEl.innerHTML = `
      <h3 class="mt-3 mb-3">Analyse du programme</h3>

      <div class="row g-3 mb-3">
        <div class="col-md-4">
          <div class="card border-primary h-100">
            <div class="card-body text-center">
              <h5 class="card-title text-primary">Force</h5>
              <p class="display-6 mb-1">${totalForce.toFixed(1)}</p>
              <p class="text-muted mb-0">${pctForce.toFixed(1)} % du volume</p>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card border-success h-100">
            <div class="card-body text-center">
              <h5 class="card-title text-success">Hypertrophie</h5>
              <p class="display-6 mb-1">${totalHyp.toFixed(1)}</p>
              <p class="text-muted mb-0">${pctHyp.toFixed(1)} % du volume</p>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card border-warning h-100">
            <div class="card-body text-center">
              <h5 class="card-title text-warning">Endurance</h5>
              <p class="display-6 mb-1">${totalEnd.toFixed(1)}</p>
              <p class="text-muted mb-0">${pctEnd.toFixed(1)} % du volume</p>
            </div>
          </div>
        </div>
      </div>

      <h5>Détail par exercice</h5>
      <div class="table-responsive">
        <table class="table table-sm table-striped align-middle">
          <thead>
            <tr>
              <th>#</th>
              <th>Exercice</th>
              <th>Reps</th>
              <th>Poids</th>
              <th>Volume</th>
              <th>Force</th>
              <th>Hypertrophie</th>
              <th>Endurance</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    console.error("Erreur réseau lors de l'analyse :", err);
    alert("Erreur réseau lors de l'analyse du programme");
  }
}

// ---------- 5. Gestion de l'affichage des sections ----------
function showProgramUI() {
  const program = document.getElementById("programContainer");
  const exercise = document.getElementById("exerciseContainer");
  const analysis = document.getElementById("analysisContainer");

  [program, exercise, analysis].forEach(el => {
    if (!el) return;

    el.classList.remove("hidden");
    el.classList.remove("d-none"); // sécurité si une classe Bootstrap traîne

    el.classList.remove("fade-in");
    void el.offsetWidth;
    el.classList.add("fade-in");
  });
}

function hideProgramUI() {
  document.getElementById("programContainer")?.classList.add("hidden");
  document.getElementById("exerciseContainer")?.classList.add("hidden");
  document.getElementById("analysisContainer")?.classList.add("hidden");

  // sécurité si Bootstrap traîne
  document.getElementById("programContainer")?.classList.remove("d-none");
  document.getElementById("exerciseContainer")?.classList.remove("d-none");
  document.getElementById("analysisContainer")?.classList.remove("d-none");
}

// ---------- 6. Wiring des événements ----------
document.addEventListener("DOMContentLoaded", () => {
  hideProgramUI();
  // charger exercices au démarrage
  loadExercices().then(() => {
    // quand on change d'exercice dans le select, afficher les détails
    exerciseSelect.addEventListener("change", () => {
      const idx = parseInt(exerciseSelect.value, 10);
      if (Number.isNaN(idx)) {
        exerciseDetailsEl.innerHTML = "";
        return;
      }
      renderExerciseDetails(idx);
    });
  });

  // charger la liste des programmes au démarrage
  loadProgrammesList();

  // bouton "New Program"
  if (newProgramBtn) {
    newProgramBtn.addEventListener("click", (evt) => {
      evt.preventDefault();
      resetProgram();
    });
  }

  // bouton "Add exercice"
  addExerciseBtn.addEventListener("click", (evt) => {
    evt.preventDefault(); // ne pas soumettre le formulaire WTForms
    addExerciseToCurrentProgram();
    showProgramUI();
  });

  // bouton "Save Program"
  saveProgramBtn.addEventListener("click", (evt) => {
    evt.preventDefault();
    saveCurrentProgram();
    showProgramUI();
  });

  // bouton "Load Program"
  loadProgramBtn.addEventListener("click", (evt) => {
    evt.preventDefault();
    loadSelectedProgram();
    showProgramUI();
  });

  resetProgramBtn.addEventListener("click", (evt) => {
    evt.preventDefault();
    deleteCurrentProgram();
    hideProgramUI();
  });

  // bouton "Analyse Program"
  analyseProgramBtn.addEventListener("click", (evt) => {
    evt.preventDefault();
    analyseCurrentProgram();
    showProgramUI();
  });

});