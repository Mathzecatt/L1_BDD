-- script_creation.sql
-- Projet VCub - creation des tables (besoins 1, 2, 3)
-- A executer dans la base vcub (creee prealablement via : createdb vcub)

-- DROP dans l'ordre INVERSE des dependances (idempotence)
DROP TABLE IF EXISTS Emprunt CASCADE;
DROP TABLE IF EXISTS Abonne CASCADE;
DROP TABLE IF EXISTS Abonnement CASCADE;
DROP TABLE IF EXISTS Plot CASCADE;
DROP TABLE IF EXISTS Velo CASCADE;
DROP TABLE IF EXISTS Station CASCADE;

-- numStation : INT explicite (on conserve les numeros officiels du fichier Excel).
CREATE TABLE Station (
    numStation INT PRIMARY KEY,
    nomStation VARCHAR(100) NOT NULL,
    capaciteStation INT NOT NULL CHECK (capaciteStation > 0),
    etatMaintenanceStation CHAR(1) NOT NULL CHECK (etatMaintenanceStation IN ('F','M')),
    numBorne INT NOT NULL UNIQUE
);

-- etatMaintenanceVelo : F=Fonctionnement, M=Maintenance, P=Perdu
-- etatUtilisationVelo : D=Disponible, O=Occupe
CREATE TABLE Velo (
    numVelo SERIAL PRIMARY KEY,
    etatMaintenanceVelo CHAR(1) NOT NULL CHECK (etatMaintenanceVelo IN ('F','M','P')),
    etatUtilisationVelo CHAR(1) NOT NULL CHECK (etatUtilisationVelo IN ('D','O')),
    dateMiseEnCirculation DATE NOT NULL
);

-- numVelo : nullable + UNIQUE  => traduction de "accrocher" 0,1 -- 0,1
CREATE TABLE Plot (
    numPlot SERIAL PRIMARY KEY,
    etatMaintenancePlot CHAR(1) NOT NULL CHECK (etatMaintenancePlot IN ('F','M')),
    etatUtilisationPlot CHAR(1) NOT NULL CHECK (etatUtilisationPlot IN ('D','O')),
    numStation INT NOT NULL REFERENCES Station(numStation),
    numVelo INT UNIQUE REFERENCES Velo(numVelo)
);

-- codeAbonnement : J=24h, S=7j, M=Mensuel, A=Annuel
-- Montants en NUMERIC(6,2) pour eviter les erreurs de flottants.
CREATE TABLE Abonnement (
    codeAbonnement CHAR(1) PRIMARY KEY CHECK (codeAbonnement IN ('J','S','M','A')),
    libelleAbonnement VARCHAR(20) NOT NULL,
    dureeAbonnement INT NOT NULL CHECK (dureeAbonnement > 0),
    montantAbonnement NUMERIC(6,2) NOT NULL CHECK (montantAbonnement >= 0),
    creditTempsBase INT NOT NULL CHECK (creditTempsBase >= 0),
    tarifHoraire NUMERIC(6,2) NOT NULL CHECK (tarifHoraire >= 0),
    caution NUMERIC(6,2) NOT NULL CHECK (caution >= 0)
);

CREATE TABLE Abonne (
    numAbonne SERIAL PRIMARY KEY,
    codeSecret VARCHAR(10) NOT NULL,
    nomAbonne VARCHAR(50) NOT NULL,
    prenomAbonne VARCHAR(50) NOT NULL,
    creditTemps INT NOT NULL DEFAULT 0,
    dateDebutAbonnement DATE NOT NULL,
    dateFinAbonnement DATE NOT NULL,
    codeAbonnement CHAR(1) NOT NULL REFERENCES Abonnement(codeAbonnement),
    CHECK (dateFinAbonnement >= dateDebutAbonnement)
);

-- dateHeureFinEmprunt nullable : un emprunt en cours n'a pas encore de fin.
CREATE TABLE Emprunt (
    numEmprunt SERIAL PRIMARY KEY,
    dateHeureDebutEmprunt TIMESTAMP NOT NULL,
    dateHeureFinEmprunt TIMESTAMP,
    numAbonne INT NOT NULL REFERENCES Abonne(numAbonne),
    numVelo INT NOT NULL REFERENCES Velo(numVelo),
    CHECK (dateHeureFinEmprunt IS NULL OR dateHeureFinEmprunt >= dateHeureDebutEmprunt)
);
