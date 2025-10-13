const form = document.querySelector('#my_form');
const purgeButton = document.querySelector('#clear_list');
const ul = document.querySelector('#tasks_ul');

const API_URL = '/projects/todolist/api/todoList';

// État local (miroir du serveur)
let todoList = [];

// ---- Utilitaires API ----
async function apiGetTodos() {
  const res = await fetch(API_URL, { headers: { 'Accept': 'application/json' } });
  if (!res.ok) throw new Error(`GET ${API_URL} => ${res.status}`);
  return res.json(); // attendu: [{id, task}, ...]
}

async function apiCreateTodo(task) {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ task })
  });
  if (!res.ok) throw new Error(`POST ${API_URL} => ${res.status}`);
  return res.json(); // attendu: {id, task}
}

async function apiDeleteTodo(id) {
  const res = await fetch(`${API_URL}/${encodeURIComponent(id)}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`DELETE ${API_URL}/${id} => ${res.status}`);
}

async function apiPurgeAll() {
  // Si ton backend supporte DELETE sur la collection, on l'utilise.
  const res = await fetch(API_URL, { method: 'DELETE' });
  if (!res.ok) throw new Error(`DELETE ${API_URL} => ${res.status}`);
}

// ---- Rendu UI ----
const displayList = () => {
  ul.innerHTML = "";
  if (!todoList.length) {
    const li = document.createElement('li');
    li.className = "list-group-item text-muted";
    li.textContent = "Aucune tâche.";
    ul.appendChild(li);
    return;
  }

  todoList.forEach((item) => {
    const li = document.createElement('li');
    li.className = "list-group-item d-flex justify-content-between align-items-center";

    const span = document.createElement('span');
    span.textContent = item.task;

    const deleteBtn = document.createElement('button');
    deleteBtn.className = "btn btn-close";
    deleteBtn.setAttribute('aria-label', 'Supprimer');
    deleteBtn.onclick = async () => {
      // Optimiste: retire immédiatement de l'UI, puis synchronise serveur
      const snapshot = [...todoList];
      todoList = todoList.filter(t => t.id !== item.id);
      displayList();
      try {
        await apiDeleteTodo(item.id);
      } catch (e) {
        console.error(e);
        // rollback si échec serveur
        todoList = snapshot;
        displayList();
        alert("Impossible de supprimer la tâche (problème serveur).");
      }
    };

    li.appendChild(span);
    li.appendChild(deleteBtn);
    ul.appendChild(li);
  });
};

// ---- Handlers ----
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const task = (formData.get('task') || '').trim();
  if (!task) return;

  // Création optimiste
  const tempId = `tmp-${Date.now()}`;
  const tempItem = { id: tempId, task };
  todoList.push(tempItem);
  displayList();

  try {
    const created = await apiCreateTodo(task);
    // Remplace l’item temporaire par la vraie ressource retournée
    todoList = todoList.map(t => t.id === tempId ? created : t);
    displayList();
    form.reset();
  } catch (e) {
    console.error(e);
    // rollback
    todoList = todoList.filter(t => t.id !== tempId);
    displayList();
    alert("Impossible d'ajouter la tâche (problème serveur).");
  }
});

// Purge totale
purgeButton.addEventListener('click', async () => {
  const confirmPurge = confirm("Supprimer toutes les tâches ?");
  if (!confirmPurge) return;

  const snapshot = [...todoList];
  todoList = [];
  displayList();

  try {
    // Tente purge serveur si disponible
    await apiPurgeAll();
  } catch (e) {
    // Si ton API ne supporte pas DELETE collection,
    // on tente de supprimer une par une (peut être long)
    try {
      await Promise.all(snapshot.map(item => apiDeleteTodo(item.id)));
    } catch (e2) {
      console.error(e, e2);
      // rollback si échec
      todoList = snapshot;
      displayList();
      alert("Impossible de purger la liste (problème serveur).");
    }
  }
});

// Changer le fond (inchangé)
const changeBackground = (image) => {
  document.body.style.backgroundImage = `url('${image}')`;
};

// ---- Chargement initial ----
(async function init() {
  try {
    todoList = await apiGetTodos();
  } catch (e) {
    console.error(e);
    // Fallback si le serveur est indisponible
    todoList = [{ id: 0, task: "a dummy task" }];
  } finally {
    displayList();
  }
})();

