const icons = ['🦊', '♥️', '⚽️', '🚕', '😎', '🍎', '🌞', '🌻', '📺', '🔭', '🤖', '😂'];
let cards = [];
let flippedCards = [];
let matchedCards = [];
let attempts = 0;
let gameStarted = false;
let countdownInterval;

function initGame() {
    cards = [];
    flippedCards = [];
    matchedCards = [];
    attempts = 0;
    gameStarted = true;

    const shuffledIcons = [...icons, ...icons].sort(() => Math.random() - 0.5);
    shuffledIcons.forEach((icon, index) => {
        cards.push({ id: index, icon: icon, flipped: false, matched: false });
    });

    renderCards();
    startTimer(60);
}

function renderCards() {
    const cardContainer = document.querySelector('#game-board');
    cardContainer.innerHTML = "";

    cards.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'card';
        if (card.flipped || card.matched) cardElement.classList.add('flipped');

        cardElement.dataset.id = card.id;
        cardElement.innerHTML = card.flipped || card.matched ? card.icon : '';
        cardElement.addEventListener('click', () => flipCard(card.id));
        cardContainer.appendChild(cardElement);
    });
}

function flipCard(id) {
    if (!gameStarted) return;
    const card = cards.find(c => c.id == id);
    if (!card || card.flipped || card.matched || flippedCards.length === 2) return;

    card.flipped = true;
    flippedCards.push(card);
    renderCards();

    if (flippedCards.length === 2) {
        setTimeout(checkMatch, 500);
    }
}

function checkMatch() {
    if (flippedCards.length !== 2) return;

    attempts++;
    const [firstCard, secondCard] = flippedCards;

    if (firstCard.icon === secondCard.icon) {
        firstCard.matched = true;
        secondCard.matched = true;
        matchedCards.push(firstCard, secondCard);
    } else {
        firstCard.flipped = false;
        secondCard.flipped = false;
    }

    flippedCards = [];
    renderCards();

    if (matchedCards.length === cards.length) {
        clearInterval(countdownInterval);
        alert(`🎉 Bravo ! You found all pairs in ${attempts} attempts.`);
        gameStarted = false;
    }
}

function startTimer(duration = 60) {
    clearInterval(countdownInterval);
    let seconds = duration;
    const timerElement = document.querySelector('#timer');
    timerElement.textContent = `Time left : ${seconds} secondes`;

    countdownInterval = setInterval(() => {
        if (!gameStarted) return;

        seconds--;
        timerElement.textContent = `Time left : ${seconds} secondes`;

        if (seconds <= 0) {
            clearInterval(countdownInterval);
            timerElement.textContent = "Game Over !";
            alert("⏰ Game Over ! You lost.");
            gameStarted = false;
            cards.forEach(card => card.flipped = false); // Optionnel : masquer toutes les cartes
            renderCards();
        }
    }, 1000);
}

// Bouton démarrer
document.querySelector('#start-button').addEventListener('click', () => {
    if (!gameStarted) initGame();
});

// Bouton réinitialiser
document.querySelector('#reset-button').addEventListener('click', () => {
    clearInterval(countdownInterval);
    gameStarted = false;
    initGame();
});
