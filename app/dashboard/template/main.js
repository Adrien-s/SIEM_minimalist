document.addEventListener("DOMContentLoaded", function() {
  console.log("main.js chargé et DOMContentLoaded");

  // Gestion des onglets
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");

  // Variables pour la gestion des logs
  const tableBody = document.querySelector("#dataTable tbody");
  const limitSelect = document.getElementById("limitSelect");
  const prevButton = document.getElementById("prevPage");
  const nextButton = document.getElementById("nextPage");
  const pageDisplay = document.getElementById("pageDisplay");

  let rowData = [];        // Données récupérées
  let currentPage = 0;
  let currentLimit = parseInt(limitSelect.value); // Par défaut 100

  tabButtons.forEach(button => {
    button.addEventListener("click", () => {
      // Changer l'onglet actif
      tabButtons.forEach(btn => btn.classList.remove("active"));
      button.classList.add("active");
      // Afficher/masquer le contenu
      tabContents.forEach(content => content.classList.remove("active"));
      const tabId = button.getAttribute("data-tab");
      document.getElementById(tabId).classList.add("active");
    });
  });

  function updatePageDisplay() {
    pageDisplay.textContent = "Page " + (currentPage + 1);
  }

  // Charge les données avec pagination
  function loadData() {
    const offset = currentPage * currentLimit;
    fetch(`/data?limit=${currentLimit}&offset=${offset}`)
      .then(response => response.json())
      .then(jsonData => {
        console.log("Données reçues :", jsonData);
        rowData = jsonData.events;
        renderTable();
        updatePageDisplay();
      })
      .catch(error => console.error("Erreur lors de la récupération des données:", error));
  }

  // Création d'une ligne pour un log
  function createRow(log) {
    const tr = document.createElement("tr");
    const fields = ["time", "computer", "event_id", "channel", "process_id", "thread_id", "level"];
    fields.forEach(field => {
      const td = document.createElement("td");
      if (field === "time" && log[field]) {
        td.textContent = log[field].split("T")[0];
      } else {
        td.textContent = log[field] || "";
      }
      tr.appendChild(td);
    });
    tr.addEventListener("click", function() {
      handleRowClick(tr, log);
    });
    return tr;
  }

  let currentDrawerRow = null;
  let currentSelectedRow = null;
  function handleRowClick(rowElement, log) {
    if (currentSelectedRow === rowElement) {
      closeDrawer();
      return;
    }
    closeDrawer();
    rowElement.classList.add("selected");
    currentSelectedRow = rowElement;
    const drawerRow = document.createElement("tr");
    const drawerCell = document.createElement("td");
    drawerCell.colSpan = rowElement.children.length;
    drawerCell.innerHTML = `
      <div class="details-drawer">
        <h3>Evenement créé le ${log.time}</h3>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        <strong>Event Id:</strong> ${log.event_id}</p>
      </div>
    `;
    drawerRow.appendChild(drawerCell);
    rowElement.parentNode.insertBefore(drawerRow, rowElement.nextSibling);
    currentDrawerRow = drawerRow;
  }

  function closeDrawer() {
    if (currentDrawerRow) {
      currentDrawerRow.parentNode.removeChild(currentDrawerRow);
      currentDrawerRow = null;
    }
    if (currentSelectedRow) {
      currentSelectedRow.classList.remove("selected");
      currentSelectedRow = null;
    }
  }

  function renderTable() {
    tableBody.innerHTML = "";
    rowData.forEach(log => {
      const row = createRow(log);
      tableBody.appendChild(row);
    });
  }

  // Gestion du tri par colonne
  const headers = document.querySelectorAll("#dataTable th");
  headers.forEach(header => {
    header.addEventListener("click", function() {
      const field = header.getAttribute("data-field");
      const currentSort = header.getAttribute("data-sort") || "asc";
      const newSort = currentSort === "asc" ? "desc" : "asc";
      header.setAttribute("data-sort", newSort);
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
      closeDrawer();
    });
  });

  // Écouteur pour le sélecteur du nombre de lignes
  limitSelect.addEventListener("change", function() {
    currentLimit = parseInt(this.value);
    currentPage = 0; // revenir à la première page
    loadData();
  });

  // Boutons de navigation
  prevButton.addEventListener("click", function() {
    if (currentPage > 0) {
      currentPage--;
      loadData();
    }
  });
  nextButton.addEventListener("click", function() {
    currentPage++;
    loadData();
  });

  loadData();
  
  // --- Intégration de Chart.js dans la section Analyses ---
  function initCharts() {
    const alertTrendCtx = document.getElementById("ALERT ?").getContext("2d");
    new Chart(alertTrendCtx, {
      type: 'bar',
      data: {
        labels: ["10:00", "11:00", "12:00", "13:00"],
        datasets: [{
          label: "Alert ?",
          data: [5, 12, 9, 3],
          backgroundColor: "rgba(49, 163, 163, 0.6)"
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
  
    // Graphique Stacked Bar pour Events
    const eventsCtx = document.getElementById("Alert0 ?").getContext("2d");
    new Chart(eventsCtx, {
      type: 'bar',
      data: {
        labels: ["10:00", "11:00", "12:00", "13:00"],
        datasets: [
          {
            label: "Alert1 ?",
            data: [200, 250, 270, 300],
            backgroundColor: "rgba(33, 150, 243, 0.6)"
          },
          {
            label: "Alert2 ?",
            data: [120, 100, 150, 110],
            backgroundColor: "rgba(251, 192, 45, 0.6)"
          },
          {
            label: "Alert3 ?",
            data: [80, 60, 90, 70],
            backgroundColor: "rgba(156, 39, 176, 0.6)"
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          x: { stacked: true },
          y: { stacked: true, beginAtZero: true }
        }
      }
    });
  }
  
  document.getElementById("hostEventsCount").textContent = "12345";
  document.getElementById("networkEventsCount").textContent = "12345";
  
  // Initialiser Chart.js
  initCharts();
});