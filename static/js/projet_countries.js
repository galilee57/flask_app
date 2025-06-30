document.addEventListener("DOMContentLoaded", () => {
      const bouton = document.getElementById("charger");
      const liste = document.getElementById("liste-pays");

      bouton.addEventListener("click", () => {
        axios.get("https://restcountries.com/v3.1/all?fields=name,capital,population,flags")
          .then(response => {
            const data = response.data;
            liste.innerHTML = "";

            shuffle(data).slice(0, 5).forEach(country => {
              const name = country.name.common;
              const capitale = country.capital ? country.capital[0] : "N/A";
              const population = country.population.toLocaleString();
              const flagUrl = country.flags.png;

              const img = document.createElement("img");
              img.src = flagUrl;
              img.alt = `Drapeau de ${name}`;
              img.style.width = "50px";

              const li = document.createElement("li");
              li.textContent = `${name} — Capitale : ${capitale}, Population : ${population}`;
              li.prepend(img);
              liste.appendChild(li);
            });
          })
          .catch(error => {
            liste.innerHTML = "<li>Erreur lors du chargement des données</li>";
            console.error(error);
          });
      });
    });

// Function to shuffle an array
function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}
