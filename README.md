# Projet VCub — Partie 2

**Licence 1 — UE Base de données**

- **Auteur** : Lefrançois Mathias
- **Date** : Mai 2026

---

## 1. Prérequis

- PostgreSQL 14 ou supérieur (testé sous PostgreSQL 16, installation Homebrew sur macOS)
- Python 3.10 ou supérieur
- Bibliothèque Python : `psycopg2-binary`

Installation de `psycopg2-binary` :

```bash
pip3 install psycopg2-binary
```

## 2. Mise en place de la base de données

À exécuter une seule fois, depuis le dossier `SQL/` du projet :

```bash
# 1. Créer la base de données
createdb vcub

# 2. Créer les tables
psql -d vcub -f script_creation.sql

# 3. Insérer les données de test
psql -d vcub -f script_insertion.sql

# 4. Créer la vue V_NbAbonnesParAbonnement
psql -d vcub -f script_view.sql
```

Vérification : la commande suivante doit lister 6 tables (`abonne`, `abonnement`, `emprunt`, `plot`, `station`, `velo`) :

```bash
psql -d vcub -c "\dt"
```

## 3. Lancement de l'application

Depuis la racine du projet :

```bash
python3 python/menu.py
```

Le menu interactif s'affiche. Naviguer avec les chiffres, `0` pour revenir en arrière / quitter.

## 4. Structure du livrable

```
projet_vcub/
├── SQL/
│   ├── MR                    # modèle relationnel
│   ├── script_creation.sql   # création des 6 tables
│   ├── script_insertion.sql  # données : 67 stations, 1100 vélos,
│   │                         #          1267 plots, 4 abonnements,
│   │                         #          30 abonnés, 15 emprunts
│   └── script_view.sql       # vue V_NbAbonnesParAbonnement
├── python/
│   └── menu.py               # application back-office, besoins 1 et 2
├── README.md                 # ce fichier
└── rapport.pdf               # état des fonctionnalités
```

## 5. Choix de réalisation

- **Besoin obligatoire réalisé** : besoin 2 (abonnements).
- **Besoin au choix réalisé** : besoin 1 (stations).
- Le besoin 3 (emprunts) **n'apparaît pas** dans le menu Python, conformément aux instructions du sujet. Les tables `Emprunt` sont néanmoins présentes en BDD.

## 6. Génération des données d'insertion

Le fichier `script_insertion.sql` a été généré par un script Python qui lit le fichier Excel fourni (67 stations) et complète avec des données cohérentes (vélos, plots, abonnés, emprunts) générées aléatoirement avec une seed fixe (42) pour la reproductibilité.

Le sujet n'imposant qu'un fichier `.sql` en livrable, seul `script_insertion.sql` est rendu (non le script Python générateur).
