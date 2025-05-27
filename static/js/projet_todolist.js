const form = document.querySelector('#my_form');
const purgeButton = document.querySelector('#clear_list');
const ul = document.querySelector('#tasks_ul');

const todoList = [];

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const task = formData.get('task');

    todoList.push(task);
    displayList();
});

// Fonction d'affichage
const displayList = () => {
    ul.innerHTML = "";

    todoList.forEach((item, index) => {
        const li = document.createElement('li');
        li.className = "list-group-item d-flex justify-content-between align-items-center";

        const span = document.createElement('span');
        span.textContent = item;

        const deleteBtn = document.createElement('button');
        deleteBtn.className = "btn btn-close";
        deleteBtn.onclick = () => {
            todoList.splice(index, 1);
            displayList();
        }

        li.appendChild(span);
        li.appendChild(deleteBtn);
        ul.appendChild(li);
    });
}

// Fonction pour gérer la purge avec le bouton
purgeButton.addEventListener('click', () => {
    todoList.length = 0;
    displayList();
});

// Fonction pour modifier le fond d'écran
const changeBackground = (image) => {
    document.body.style.backgroundImage = `url('${image}')`;
};