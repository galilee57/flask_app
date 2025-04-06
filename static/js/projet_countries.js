document.addEventListener("DOMContentLoaded", () => {
      const bouton = document.getElementById("charger");
      const liste = document.getElementById("liste-pays");

      bouton.addEventListener("click", () => {
        axios.get("https://restcountries.com/v3.1/all")
          .then(response => {
            const data = response.data;
            liste.innerHTML = "";
            data.slice(0, 10).forEach(pays => {
              const nom = pays.name.common;
              const capitale = pays.capital ? pays.capital[0] : "N/A";
              const population = pays.population.toLocaleString();

              const li = document.createElement("li");
              li.textContent = `${nom} — Capitale : ${capitale}, Population : ${population}`;
              liste.appendChild(li);
            });
          })
          .catch(error => {
            liste.innerHTML = "<li>Erreur lors du chargement des données</li>";
            console.error(error);
          });
      });
    });

