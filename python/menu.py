"""
menu.py - Application de back-office VCub (besoins 1 et 2)
Mode console : un menu principal pilote tout depuis le terminal.
Connexion PostgreSQL via psycopg2, requetes parametrees (anti-injection).
"""

import psycopg2

# --- Configuration de connexion ---
# Pas de mot de passe en local (auth "trust" par defaut de Postgres.app/brew).
# Si besoin : ajouter 'user': 'xxx', 'password': 'xxx'.
DB_CONFIG = {
    'dbname': 'vcub',
    'host': 'localhost',
}


def get_connection():
    """Ouvre une connexion a la BDD vcub."""
    return psycopg2.connect(**DB_CONFIG)


# Menu principal
def menu_principal(conn):
    while True:
        print("\n========== VCub Back-Office ==========")
        print("1. Gestion des stations")
        print("2. Gestion des abonnements")
        print("3. Requetes")
        print("4. Vue")
        print("0. Quitter")
        choix = input("Votre choix : ").strip()

        if choix == '0':
            print("Au revoir.")
            break
        elif choix == '1':
            menu_stations(conn)
        elif choix == '2':
            menu_abonnements(conn)
        elif choix == '3':
            menu_requetes(conn)
        elif choix == '4':
            menu_vue(conn)
        else:
            print("Choix invalide.")


# 1. Gestion des stations (besoin 1)
def liste_stations(conn):
    """1a. Liste des stations filtree par etat (F / M / T=toutes)."""
    print("Filtrer par etat ? F=fonctionnement, M=maintenance, T=toutes")
    f = input("Choix : ").strip().upper()
    with conn.cursor() as cur:
        if f == 'T':
            cur.execute(
                "SELECT numStation, nomStation, capaciteStation, etatMaintenanceStation "
                "FROM Station ORDER BY numStation;"
            )
        elif f in ('F', 'M'):
            cur.execute(
                "SELECT numStation, nomStation, capaciteStation, etatMaintenanceStation "
                "FROM Station WHERE etatMaintenanceStation = %s ORDER BY numStation;",
                (f,)
            )
        else:
            print("Etat invalide.")
            return
        rows = cur.fetchall()
        print(f"\n{len(rows)} station(s) trouvee(s) :")
        for num, nom, cap, etat in rows:
            print(f"  [{num:>3}] {nom:<30} capacite={cap:>2} etat={etat}")


def detail_station(conn):
    """1b. Detail d'une station + liste de ses plots."""
    try:
        num = int(input("Numero de station : ").strip())
    except ValueError:
        print("Numero invalide.")
        return
    with conn.cursor() as cur:
        cur.execute(
            "SELECT numStation, nomStation, capaciteStation, etatMaintenanceStation, numBorne "
            "FROM Station WHERE numStation = %s;",
            (num,)
        )
        s = cur.fetchone()
        if not s:
            print(f"Aucune station numero {num}.")
            return
        print(f"\nStation [{s[0]}] {s[1]}")
        print(f"  capacite = {s[2]}, etat = {s[3]}, borne = {s[4]}")
        cur.execute(
            "SELECT numPlot, etatMaintenancePlot, etatUtilisationPlot, numVelo "
            "FROM Plot WHERE numStation = %s ORDER BY numPlot;",
            (num,)
        )
        plots = cur.fetchall()
        print(f"  Plots ({len(plots)}) :")
        for numP, eM, eU, v in plots:
            velo = f"velo #{v}" if v else "vide"
            print(f"    Plot {numP:>4} : maintenance={eM} utilisation={eU} {velo}")


def ajout_station(conn):
    """1c. Saisie d'une nouvelle station."""
    try:
        num = int(input("numStation : ").strip())
        nom = input("nomStation : ").strip()
        cap = int(input("capaciteStation : ").strip())
        etat = input("etatMaintenanceStation (F/M) : ").strip().upper()
        if etat not in ('F', 'M'):
            print("Etat invalide (F ou M).")
            return
        borne = int(input("numBorne : ").strip())
    except ValueError:
        print("Entree invalide (un nombre etait attendu).")
        return
    with conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO Station VALUES (%s, %s, %s, %s, %s);",
                (num, nom, cap, etat, borne)
            )
            conn.commit()
            print(f"Station [{num}] ajoutee.")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Erreur : {e}")


def menu_stations(conn):
    while True:
        print("\n--- Gestion des stations ---")
        print("1. Liste des stations (par etat)")
        print("2. Detail d'une station (+ plots)")
        print("3. Ajouter une station")
        print("0. Retour")
        choix = input("Votre choix : ").strip()
        if choix == '0':
            return
        elif choix == '1':
            liste_stations(conn)
        elif choix == '2':
            detail_station(conn)
        elif choix == '3':
            ajout_station(conn)
        else:
            print("Choix invalide.")


# 2. Gestion des abonnements (besoin 2)
def liste_abonnements(conn):
    """2a. Liste de tous les abonnements."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT codeAbonnement, libelleAbonnement, dureeAbonnement, "
            "montantAbonnement, creditTempsBase, tarifHoraire, caution "
            "FROM Abonnement ORDER BY dureeAbonnement;"
        )
        print("\nAbonnements :")
        print(f"  {'Code':<4} {'Libelle':<10} {'Duree':>5} {'Montant':>8} {'CredBase':>8} {'TarifH':>7} {'Caution':>8}")
        for code, lib, duree, mt, ctb, tar, cau in cur.fetchall():
            print(f"  {code:<4} {lib:<10} {duree:>5} {mt:>8} {ctb:>8} {tar:>7} {cau:>8}")


def detail_abonnement(conn):
    """2b. Detail d'un abonnement + liste des abonnes."""
    code = input("Code abonnement (J/S/M/A) : ").strip().upper()
    if code not in ('J', 'S', 'M', 'A'):
        print("Code invalide.")
        return
    with conn.cursor() as cur:
        cur.execute(
            "SELECT codeAbonnement, libelleAbonnement, dureeAbonnement, "
            "montantAbonnement, creditTempsBase, tarifHoraire, caution "
            "FROM Abonnement WHERE codeAbonnement = %s;",
            (code,)
        )
        a = cur.fetchone()
        if not a:
            print("Abonnement introuvable.")
            return
        print(f"\nAbonnement [{a[0]}] {a[1]}")
        print(f"  duree={a[2]}j  montant={a[3]} EUR  creditBase={a[4]}min  tarif={a[5]} EUR/h  caution={a[6]} EUR")
        cur.execute(
            "SELECT numAbonne, nomAbonne, prenomAbonne, dateDebutAbonnement, dateFinAbonnement "
            "FROM Abonne WHERE codeAbonnement = %s ORDER BY numAbonne;",
            (code,)
        )
        abonnes = cur.fetchall()
        print(f"  Abonnes ({len(abonnes)}) :")
        for num, nom, prenom, dd, df in abonnes:
            print(f"    #{num:>3} {prenom} {nom}  ({dd} -> {df})")


def update_abonnement(conn):
    """2c. Mise a jour montant / creditTempsBase / tarifHoraire / caution."""
    code = input("Code abonnement a modifier (J/S/M/A) : ").strip().upper()
    if code not in ('J', 'S', 'M', 'A'):
        print("Code invalide.")
        return
    with conn.cursor() as cur:
        cur.execute(
            "SELECT montantAbonnement, creditTempsBase, tarifHoraire, caution "
            "FROM Abonnement WHERE codeAbonnement = %s;",
            (code,)
        )
        row = cur.fetchone()
        if not row:
            print("Abonnement introuvable.")
            return
        mt, ctb, tar, cau = row
        print(f"Actuels : montant={mt}  creditBase={ctb}  tarifH={tar}  caution={cau}")
        print("(Entrer vide pour garder l'ancienne valeur)")
        try:
            new_mt  = input(f"  nouveau montant [{mt}] : ").strip()
            new_ctb = input(f"  nouveau creditTempsBase [{ctb}] : ").strip()
            new_tar = input(f"  nouveau tarifHoraire [{tar}] : ").strip()
            new_cau = input(f"  nouvelle caution [{cau}] : ").strip()
            new_mt  = float(new_mt)  if new_mt  else mt
            new_ctb = int(new_ctb)   if new_ctb else ctb
            new_tar = float(new_tar) if new_tar else tar
            new_cau = float(new_cau) if new_cau else cau
        except ValueError:
            print("Entree invalide.")
            return
        try:
            cur.execute(
                "UPDATE Abonnement SET montantAbonnement = %s, creditTempsBase = %s, "
                "tarifHoraire = %s, caution = %s WHERE codeAbonnement = %s;",
                (new_mt, new_ctb, new_tar, new_cau, code)
            )
            conn.commit()
            print(f"Abonnement [{code}] mis a jour.")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Erreur : {e}")


def menu_abonnements(conn):
    while True:
        print("\n--- Gestion des abonnements ---")
        print("1. Liste des abonnements")
        print("2. Detail d'un abonnement (+ abonnes)")
        print("3. Mettre a jour un abonnement")
        print("0. Retour")
        choix = input("Votre choix : ").strip()
        if choix == '0':
            return
        elif choix == '1':
            liste_abonnements(conn)
        elif choix == '2':
            detail_abonnement(conn)
        elif choix == '3':
            update_abonnement(conn)
        else:
            print("Choix invalide.")


# 3. Requetes
def afficher_resultat(cur, titre):
    """Helper : affiche les en-tetes + lignes du curseur."""
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print(f"\n{titre} ({len(rows)} ligne(s))")
    print("  " + " | ".join(cols))
    for row in rows:
        print("  " + " | ".join(str(v) if v is not None else 'NULL' for v in row))


def req_a(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT numStation, capaciteStation, nomStation FROM Station "
            "ORDER BY capaciteStation DESC, nomStation ASC;"
        )
        afficher_resultat(cur, "Stations triees par capacite DESC, nom ASC")


def req_b(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT a.libelleAbonnement, COUNT(ab.numAbonne) AS NbAbonnes "
            "FROM Abonnement a LEFT JOIN Abonne ab ON ab.codeAbonnement = a.codeAbonnement "
            "GROUP BY a.libelleAbonnement;"
        )
        afficher_resultat(cur, "Nombre d'abonnes par abonnement")


def req_c(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT s.numStation, s.nomStation, s.capaciteStation, "
            "COUNT(p.numPlot) AS nbPlotsDisponibles "
            "FROM Station s JOIN Plot p ON p.numStation = s.numStation "
            "WHERE p.etatUtilisationPlot = 'D' "
            "GROUP BY s.numStation, s.nomStation, s.capaciteStation "
            "HAVING COUNT(p.numPlot) > 5 ORDER BY nbPlotsDisponibles DESC;"
        )
        afficher_resultat(cur, "Stations avec > 5 plots disponibles")


def req_d(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT s.numStation, s.nomStation, s.capaciteStation "
            "FROM Station s JOIN Plot p ON p.numStation = s.numStation "
            "GROUP BY s.numStation, s.nomStation, s.capaciteStation "
            "HAVING COUNT(DISTINCT p.etatMaintenancePlot) = 2;"
        )
        afficher_resultat(cur, "Stations avec plots M ET F")


def req_e(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT s.numStation, s.nomStation, s.capaciteStation FROM Station s "
            "WHERE NOT EXISTS ("
            "  SELECT 1 FROM Plot p JOIN Velo v ON p.numVelo = v.numVelo "
            "  WHERE p.numStation = s.numStation AND v.etatMaintenanceVelo = 'M'"
            ");"
        )
        afficher_resultat(cur, "Stations sans velo en maintenance")


def menu_requetes(conn):
    while True:
        print("\n--- Requetes ---")
        print("a. Stations triees par capacite")
        print("b. Nb abonnes par abonnement")
        print("c. Stations avec > 5 plots disponibles")
        print("d. Stations avec plots M et F")
        print("e. Stations sans velo en maintenance")
        print("0. Retour")
        choix = input("Votre choix : ").strip().lower()
        if choix == '0':
            return
        elif choix == 'a': req_a(conn)
        elif choix == 'b': req_b(conn)
        elif choix == 'c': req_c(conn)
        elif choix == 'd': req_d(conn)
        elif choix == 'e': req_e(conn)
        else:
            print("Choix invalide.")


# 4. Vue
def vue_complete(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM V_NbAbonnesParAbonnement;")
        afficher_resultat(cur, "V_NbAbonnesParAbonnement")


def vue_filtre_1000(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM V_NbAbonnesParAbonnement WHERE NbAbonnes > 1000;")
        afficher_resultat(cur, "Abonnements > 1000 abonnes")


def menu_vue(conn):
    while True:
        print("\n--- Vue V_NbAbonnesParAbonnement ---")
        print("1. Afficher la vue")
        print("2. Abonnements avec > 1000 abonnes")
        print("0. Retour")
        choix = input("Votre choix : ").strip()
        if choix == '0':
            return
        elif choix == '1':
            vue_complete(conn)
        elif choix == '2':
            vue_filtre_1000(conn)
        else:
            print("Choix invalide.")


# Point d'entree
if __name__ == '__main__':
    try:
        conn = get_connection()
        print(f"Connexion OK a la base '{DB_CONFIG['dbname']}'.")
        menu_principal(conn)
    except psycopg2.OperationalError as e:
        print(f"Erreur de connexion : {e}")
    finally:
        if 'conn' in dir() and conn:
            conn.close()
