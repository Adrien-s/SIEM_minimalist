# SIEM Minimaliste – Projet Master

Ce dépôt contient un **SIEM simplifié** développé pour un Projet Master. Il permet de collecter des logs d’événements Windows, de les stocker en SQLite, d’appliquer un moteur de règles, et de les visualiser via un dashboard web.

---

## Structure du dépôt

```
SIEM_minimalist/
├── app/                      # Code principal
|   |
│   ├── data/                 # Services et logique métier
│   │   ├── database.py       # Initialisation et accès SQLite (logs, rules, alerts)
│   │   ├── event_service.py  # Définitions et glossaire d’Event IDs
│   │   ├── rules_engine.py   # Moteur de détection des règles
|   |   ├── backlog_agent.py  # Lecture du backlog d’un canal
│   │   └── tail_agent.py
│   ├── dashboard/            # Dashboard web (template HTML/CSS/JS et serveur)
│   └── main.py               # Point d’entrée (initialisation et lancement)
├── tests/                    # Tests unitaires avec pytest
├── docs/                     # Livrables PDF (L1, L2, rapport final)
├── requirements.txt          # Dépendances Python
└── README.md                 # Ce fichier

## Prérequis

* Python 3.9 ou supérieur
* pip pour installer les dépendances
* Accès administrateur sous Windows pour lire les journaux d’événements

---

## Installation

1. Cloner le dépôt :

   ```bash
   git clone https://github.com/Adrien-s/SIEM_minimalist.git
   cd SIEM_minimalist
   ```
2 Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

---

## Lancement

Depuis la racine du projet :

``` Lancer un terminal en mode administrateur ```

```bash 
cd SIEM_minimalist/app 

python /main.py
```

Le dashboard est alors accessible sur : `http://localhost:8000`

---

## Fonctionnalités

* Collecte : agents BacklogAgent et TailAgent pour les canaux Security et Application
* Stockage : base SQLite avec tables `logs`, `rules`, `alerts`, `event_definitions`
* Moteur de règles : seuils temporels configurables et génération d’alertes
* Dashboard :

  * Logs paginés, recherche multi-champs, détails déroulants
  * Analyses statistiques et graphiques via Chart.js
  * Gestion des règles (CRUD)
  * Glossaire des Event IDs avec liens vers la documentation Microsoft

---

## Tests unitaires

Lancer les tests avec pytest :

```bash
cd SIEM_minimalist/

pytest --maxfail=1 --disable-warnings -q
```

Les tests couvrent :

* Agents de collecte (`tests/test_backlog_agent.py`, `tests/test_tail_agent.py`)
* Accès à la base (`tests/test_database.py`, `tests/test_query_logs.py`)
* Service d’Event IDs (`tests/test_event_service.py`)
* Moteur de règles (`tests/test_rules_engine.py`)

---

## Évolutions futures

* Intégration de nouvelles sources de logs (Syslog, fichiers texte)
* Alerting en temps réel (email, Slack)
* Authentification et gestion des utilisateurs du dashboard
* Support de bases de données externes (MySQL, PostgreSQL)

---

*Dernière mise à jour : 2025-05-17*
