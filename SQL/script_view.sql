-- Vue V_NbAbonnesParAbonnement utilisee par les requetes 5a et 5b du menu.

-- LEFT JOIN volontaire : si un abonnement n'a aucun abonne, on l'affiche 
-- quand meme avec NbAbonnes = 0. Un INNER JOIN l'aurait fait disparaitre.
CREATE OR REPLACE VIEW V_NbAbonnesParAbonnement AS
SELECT A.libelleAbonnement, COUNT(AB.numAbonne) AS NbAbonnes
FROM Abonnement A
LEFT JOIN Abonne AB ON AB.codeAbonnement = A.codeAbonnement
GROUP BY A.libelleAbonnement;
