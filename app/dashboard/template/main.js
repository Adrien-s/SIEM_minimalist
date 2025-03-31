document.addEventListener("DOMContentLoaded", function() {
    console.log("main.js chargé et DOMContentLoaded");
  
    const tableBody = document.querySelector("#dataTable tbody");
    const detailsPanel = document.getElementById("detailsPanel");
    let rowData = []; // Stocke les données reçues
    let selectedRow = null; // Pour garder la référence à la ligne sélectionnée
  
    // Fonction qui crée une ligne de tableau pour un log donné
    function createRow(log) {
      const tr = document.createElement("tr");
      const fields = ["time", "computer", "event_id", "channel", "process_id", "thread_id"];
      fields.forEach(field => {
        const td = document.createElement("td");
        if (field === "time" && log[field]) {
          td.textContent = log[field].split("T")[0];
        } else {
          td.textContent = log[field] || "";
        }
        tr.appendChild(td);
      });
      // Ajout de l'écouteur sur la ligne
      tr.addEventListener("click", function() {
        // Enlève la classe 'selected' de la ligne précédemment sélectionnée
        if (selectedRow) {
          selectedRow.classList.remove("selected");
        }
        tr.classList.add("selected");
        selectedRow = tr;
        handleRowClick(log);
      });
      return tr;
    }
  
    // Fonction qui affiche le panneau de détails en forme de bulle
    function handleRowClick(log) {
      detailsPanel.style.display = "block";
      // Exemple de contenu statique "lorem ipsum" avec une indication du log sélectionné
      detailsPanel.innerHTML = `
        <h2>Détails du Log</h2>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur euismod, nisi at ultrices cursus, justo erat scelerisque nulla, non efficitur dui libero vitae urna.</p>
        <p><strong>Event Id:</strong> ${log.event_id}</p>
      `;
    }
  
    // Fonction qui rend la table à partir des données stockées dans rowData
    function renderTable() {
      tableBody.innerHTML = "";
      rowData.forEach(log => {
        tableBody.appendChild(createRow(log));
      });
    }
  
    // Gestion du tri : écouteurs sur chaque en-tête
    const headers = document.querySelectorAll("#dataTable th");
    headers.forEach(header => {
      header.addEventListener("click", function() {
        const field = header.getAttribute("data-field");
        const currentSort = header.getAttribute("data-sort") || "asc";
        const newSort = currentSort === "asc" ? "desc" : "asc";
        header.setAttribute("data-sort", newSort);
  
        // Réinitialise l'affichage de tous les headers
        headers.forEach(h => {
          h.classList.remove("sorted");
          if (h.getAttribute("data-original-text")) {
            h.textContent = h.getAttribute("data-original-text");
          }
        });
        if (!header.getAttribute("data-original-text")) {
          header.setAttribute("data-original-text", header.textContent);
        }
        header.classList.add("sorted");
        header.textContent = header.getAttribute("data-original-text") + (newSort === "asc" ? " ▲" : " ▼");
  
        // Tri simple de rowData selon le champ choisi
        rowData.sort((a, b) => {
          let aVal = a[field] || "";
          let bVal = b[field] || "";
          if (field === "time") {
            aVal = aVal.split("T")[0];
            bVal = bVal.split("T")[0];
          }
          if (aVal < bVal) return newSort === "asc" ? -1 : 1;
          if (aVal > bVal) return newSort === "asc" ? 1 : -1;
          return 0;
        });
        renderTable();
        // Réinitialise le panneau de détails si un nouveau tri est effectué
        detailsPanel.style.display = "none";
        if (selectedRow) {
          selectedRow.classList.remove("selected");
          selectedRow = null;
        }
      });
    });
  
    // Récupération des données depuis l'endpoint /data
    fetch("/data")
      .then(response => response.json())
      .then(jsonData => {
        console.log("Données reçues :", jsonData);
        rowData = jsonData.events; // On attend un objet { events: [...] }
        renderTable();
      })
      .catch(error => console.error("Erreur lors de la récupération des données:", error));
  });
  