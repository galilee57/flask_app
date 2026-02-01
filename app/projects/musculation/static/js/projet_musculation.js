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
      <tr class="hover:bg-gray-50">
        <td class="px-3 py-2 text-sm text-gray-500">${idx + 1}</td>

        <td class="px-3 py-2 text-sm font-medium text-gray-900">
          ${name}
        </td>

        <td class="px-3 py-2 text-sm text-gray-700">
          ${item.reps}
        </td>

        <td class="px-3 py-2 text-sm text-gray-700">
          ${item.weight} kg
        </td>

        <td class="px-3 py-2 text-center">
          <button
            type="button"
            title="Supprimer"
            onclick="removeExerciseFromProgram(${idx})"
            class="inline-flex h-8 w-8 items-center justify-center rounded-full
                  border border-red-300 text-red-600
                  hover:bg-red-50 hover:text-red-700
                  focus:outline-none focus:ring-2 focus:ring-red-300"
          >
            ✕
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
      <div class="mt-4 rounded-2xl bg-white p-4 shadow">
        <h3 class="mb-4 text-xl font-bold">Analyse du programme</h3>

        <!-- Cartes récap -->
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div class="rounded-2xl border border-primary-200 p-4 text-center shadow-sm">
            <h5 class="text-sm font-semibold text-primary-700">Force</h5>
            <p class="mt-2 text-4xl font-bold">${totalForce.toFixed(1)}</p>
            <p class="mt-1 text-sm text-gray-500">${pctForce.toFixed(1)} % du volume</p>
          </div>

          <div class="rounded-2xl border border-secondary-200 p-4 text-center shadow-sm">
            <h5 class="text-sm font-semibold text-secondary-700">Hypertrophie</h5>
            <p class="mt-2 text-4xl font-bold">${totalHyp.toFixed(1)}</p>
            <p class="mt-1 text-sm text-gray-500">${pctHyp.toFixed(1)} % du volume</p>
          </div>

          <div class="rounded-2xl border border-neutral-200 p-4 text-center shadow-sm">
            <h5 class="text-sm font-semibold text-neutral-700">Endurance</h5>
            <p class="mt-2 text-4xl font-bold">${totalEnd.toFixed(1)}</p>
            <p class="mt-1 text-sm text-gray-500">${pctEnd.toFixed(1)} % du volume</p>
          </div>
        </div>

        <!-- Tableau -->
        <h5 class="mt-6 mb-2 text-base font-semibold">Détail par exercice</h5>

        <div class="overflow-x-auto rounded-xl border">
          <p class="mt-2 text-xs text-gray-500 md:hidden">Faites glisser le tableau vers la droite →</p>
          <table class="min-w-[820px] w-full whitespace-nowrap divide-y divide-gray-200 text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">#</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Exercice</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Reps</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Poids</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Volume</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Force</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Hypertrophie</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Endurance</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-100 bg-white">
              ${perEx.map((ex, idx) => `
                <tr class="hover:bg-gray-50">
                  <td class="whitespace-nowrap px-3 py-2 text-gray-700">${idx + 1}</td>
                  <td class="whitespace-nowrap px-3 py-2 font-medium text-gray-900">${ex.exercice_id}</td>
                  <td class="whitespace-nowrap px-3 py-2 text-gray-700">${ex.reps}</td>
                  <td class="whitespace-nowrap px-3 py-2 text-gray-700">${ex.weight} kg</td>
                  <td class="whitespace-nowrap px-3 py-2 text-gray-700">${ex.volume}</td>
                  <td class="whitespace-nowrap px-3 py-2 text-gray-700">${ex.scores.force.toFixed(1)}</td>
                  <td class="whitespace-nowrap px-3 py-2 text-gray-700">${ex.scores.hypertrophie.toFixed(1)}</td>
                  <td class="whitespace-nowrap px-3 py-2 text-gray-700">${ex.scores.endurance.toFixed(1)}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
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