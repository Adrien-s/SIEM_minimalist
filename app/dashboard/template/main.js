document.addEventListener("DOMContentLoaded", function() {
    console.log("main.js chargé et DOMContentLoaded");
  
    const tableBody = document.querySelector("#dataTable tbody");
    let rowData = []; // Données récupérées
    let currentDrawerRow = null;   // Ligne contenant le tiroir actuellement ouvert
    let currentSelectedRow = null; // Ligne actuellement sélectionnée
  
    function createRow(log) {
      const tr = document.createElement("tr");
      // On suppose que log est un tableau. On définit un mapping entre index et label pour plus de clarté
      const fieldsIndex = {
        time: 1,
        computer: 2,
        event_id: 3,
        channel: 4,
        process_id: 5,
        thread_id: 6,
        level: 7
      };
      
      Object.keys(fieldsIndex).forEach(field => {
        const td = document.createElement("td");
        let value = log[ fieldsIndex[field] ] || "";
        if (field === "time" && value) {
          // Si la valeur est au format ISO, on garde la date seule
          value = value.split("T")[0];
        }
        td.textContent = value;
        tr.appendChild(td);
      });
    
      // Ajout de l'écouteur sur la ligne
      tr.addEventListener("click", function() {
        handleRowClick(tr, log);
      });
      return tr;
    }
    
  
    // Affiche ou masque le tiroir sous la ligne cliquée
    function handleRowClick(rowElement, log) {
      // Si on clique sur la ligne déjà sélectionnée, on ferme le tiroir
      if (currentSelectedRow === rowElement) {
        closeDrawer();
        return;
      }
      // Ferme le tiroir ouvert, le cas échéant
      closeDrawer();
  
      // Marque la ligne sélectionnée
      rowElement.classList.add("selected");
      currentSelectedRow = rowElement;
  
      // Crée une nouvelle ligne pour le tiroir
      const drawerRow = document.createElement("tr");
      const drawerCell = document.createElement("td");
      drawerCell.colSpan = rowElement.children.length;
      drawerCell.innerHTML = `
        <div class="details-drawer">
          <h3>Evenement créer le ${log.time}</h3>
          <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
          <strong>Event Id:</strong> ${log.event_id}</p>
        </div>
      `;
      drawerRow.appendChild(drawerCell);
      // Insère le tiroir juste après la ligne cliquée
      rowElement.parentNode.insertBefore(drawerRow, rowElement.nextSibling);
      currentDrawerRow = drawerRow;
    }
  
    // Ferme le tiroir et désélectionne la ligne
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
  
    // Affiche le tableau à partir de rowData
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
  
    // Récupération des données via /data
    fetch("/data")
      .then(response => response.json())
      .then(jsonData => {
        console.log("Données reçues :", jsonData);
        rowData = jsonData.events;
        renderTable();
      })
      .catch(error => console.error("Erreur lors de la récupération des données:", error));
  });
  