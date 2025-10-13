document.addEventListener("DOMContentLoaded", () => {
    fetch("/static/data/projet_chart_data.json")
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('monChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Valeurs',
                        data: data.valeurs,
                        fill: false,
                        borderColor: 'blue',
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Données mensuelles'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error("Erreur lors du chargement du fichier JSON :", error);
        });
});
