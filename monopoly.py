"""
TP Monopoly - Squelette de code
Durée: 16h sur 4 séances de 4h
"""

import mysql.connector
import random
from typing import List, Optional

# =============================================================================
# SÉANCE 1 : FONDATIONS (3h)
# =============================================================================

class Case:
    """Classe de base pour toutes les cases du plateau"""
    def __init__(self, nom: str, position: int):
        self.nom = nom
        self.position = position
    
    def action(self, joueur: 'Joueur', jeu: 'Monopoly'):
        """Action exécutée quand un joueur arrive sur la case"""
        pass

class Propriete(Case):
    """Case représentant une propriété achetable"""
    def __init__(self, nom: str, position: int, prix: int, loyer: int, couleur: str):
        super().__init__(nom, position)
        self.prix = prix
        self.loyer_base = loyer
        self.couleur = couleur
        self.proprietaire: Optional['Joueur'] = None
        self.nb_maisons = 0
        self.a_hotel = False
    
    def calculer_loyer(self) -> int:
        """Calcule le loyer en fonction des maisons/hôtels"""
        # TODO SÉANCE 2: Implémenter le calcul avec maisons et hôtels
        return self.loyer_base
    
    def action(self, joueur: 'Joueur', jeu: 'Monopoly'):
        """Gère l'arrivée d'un joueur sur la propriété"""
        # TODO SÉANCE 1: Implémenter la logique d'achat ou de paiement du loyer
        if self.proprietaire is None:
            # Propriété non possédée, proposer l'achat aux IA
            decision = StrategieIA().decider_achat(joueur, self)
            if decision:
                joueur.acheter_propriete(self)
        elif self.proprietaire == joueur:
            # Propriété possédée par le joueur, rien à faire
            pass
        else:
            # Propriété possédée par un autre joueur, payer le loyer
            loyer = self.calculer_loyer()
            joueur.payer(loyer, self.proprietaire)
        pass

class Gare(Propriete):
    """Case représentant une gare"""
    def __init__(self, nom: str, position: int):
        super().__init__(nom, position, prix=200, loyer=25, couleur="gare")
    
    def calculer_loyer(self) -> int:
        """Calcule le loyer en fonction du nombre de gares possédées"""
        if not self.proprietaire:
            return 0
        nb_gares = sum(1 for prop in self.proprietaire.proprietes if isinstance(prop, Gare))
        return 25 * (2 ** (nb_gares - 1))
    
class Compagnie(Propriete):
    """Case représentant une compagnie de services publics"""
    def __init__(self, nom: str, position: int):
        super().__init__(nom, position, prix=150, loyer=0, couleur="Compagnie")
    
    def calculer_loyer(self) -> int:
        """Calcule le loyer en fonction du nombre de compagnies possédées"""
        pass

class CaseSpeciale(Case):
    """Cases comme Départ, Prison, Taxe, etc."""
    def __init__(self, nom: str, position: int, type_case: str):
        super().__init__(nom, position)
        self.type_case = type_case
    
    def action(self, joueur: 'Joueur', jeu: 'Monopoly'):
        """Action selon le type de case spéciale"""
        # TODO SÉANCE 2: Implémenter les actions des cases spéciales
        pass

class Joueur:
    """Représente un joueur de Monopoly"""
    def __init__(self, nom: str, argent_initial: int = 1500):
        self.nom = nom
        self.argent = argent_initial
        self.position = 0
        self.proprietes: List[Propriete] = []
        self.en_prison = False
        self.tours_en_prison = 0
        self.est_en_faillite = False
    
    def deplacer(self, nombre_cases: int, plateau_taille: int = 40):
        """Déplace le joueur sur le plateau"""
        # TODO SÉANCE 1: Implémenter le déplacement avec gestion du passage par Départ
        if self.position + nombre_cases >= plateau_taille:
            self.position = (self.position + nombre_cases) % plateau_taille
            self.recevoir(200) 
            return True
        else:
            self.position += nombre_cases
            return False
    
    def payer(self, montant: int, beneficiaire: Optional['Joueur'] = None):
        """Le joueur paye un montant (à un autre joueur ou à la banque)"""
        # TODO SÉANCE 1: Implémenter le paiement avec gestion de la faillite
        if self.argent >= montant:
            self.argent -= montant
            if beneficiaire:
                beneficiaire.recevoir(montant)
        else:
            self.declarer_faillite(beneficiaire)
    
    def declarer_faillite(self, beneficiaire: Optional['Joueur'] = None):
        """Déclare la faillite du joueur"""
        self.est_en_faillite = True
        self.proprietes.clear()
        self.argent = 0
        if beneficiaire:
            # Transférer les propriétés au bénéficiaire
            for propriete in self.proprietes:
                propriete.proprietaire = beneficiaire
                beneficiaire.proprietes.append(propriete)

    def recevoir(self, montant: int):
        """Le joueur reçoit de l'argent"""
        self.argent += montant
    
    def acheter_propriete(self, propriete: Propriete) -> bool:
        """Achète une propriété si le joueur a assez d'argent"""
        # TODO SÉANCE 1: Implémenter l'achat de propriété
        # Verifier si la propriété est déjà possédée
        if propriete.proprietaire is not None:
            return False
        # Verifier si le joueur a assez d'argent
        if self.argent >= propriete.prix:
            self.argent -= propriete.prix
            propriete.proprietaire = self
            self.proprietes.append(propriete)
            return True
        return False
    
    def possede_quartier(self, couleur: str, toutes_proprietes: List[Propriete]) -> bool:
        """Vérifie si le joueur possède toutes les propriétés d'une couleur"""
        # TODO SÉANCE 2: Implémenter la vérification de quartier
        kartier_a_moi = [p for p in self.proprietes if p.couleur == couleur]
        kartier = [p for p in toutes_proprietes if p.couleur == couleur]
        return len(kartier_a_moi) == len(kartier)


class DB:
    @classmethod
    def connexionBase(cls):
        mydb = mysql.connector.connect(
            host="localhost",
            port=1433,
            user="SA",
            password="Azerty*!*",
            database="Toto"
        )
        return mydb

    # TABLE PROPRIETES -------------------------------------------------------

    # Liste des proprietes. donnée de classe
    __Proprietes = []

    @classmethod
    def get_proprietes(cls):
        if cls.__Proprietes == []:
            maConnexion = cls.connexionBase()
            monCurseur = maConnexion.cursor(dictionary=True)

            monCurseur.execute("""
                SELECT position,
                       nom,
                       type_propriete_code,
                       prix_achat,
                       loyer_base,
                       couleur,
                       prix_maison
                FROM   v_proprietes;
            """)
            mesResultats = monCurseur.fetchall()

            for r in mesResultats:
                p = None

                if r["type_propriete_code"] == "propriete":
                    # Création d'une propriété "classique"
                    # Ajuste l'ordre / le nombre d'arguments selon ton __init__ de Propriete
                    p = Propriete(
                        r["position"],
                        r["nom"],
                        r["prix_achat"],
                        r["loyer_base"],
                        r["couleur"],
                        r["prix_maison"]
                    )

                elif r["type_propriete_code"] == "gare":
                    # Création d'une gare
                    # Ajuste si ta classe Gare a un autre __init__
                    p = Gare(
                        r["position"],
                        r["nom"],
                        r["prix_achat"],
                        r["loyer_base"]
                    )

                elif r["type_propriete_code"] == "compagnie":
                    # Création d'une compagnie
                    # Ajuste si ta classe Compagnie a un autre __init__
                    p = Compagnie(
                        r["position"],
                        r["nom"],
                        r["prix_achat"],
                        r["loyer_base"]
                    )

                if p is not None:
                    cls.__Proprietes.append(p)

            # On ferme proprement
            monCurseur.close()
            maConnexion.close()

        return cls.__Proprietes



class Plateau:
    """Représente le plateau de jeu Monopoly"""
    def __init__(self):
        self.cases: List[Case] = []
        self._creer_plateau()
    
    def _creer_plateau(self):
        """Crée les 40 cases du plateau Monopoly"""
        # TODO SÉANCE 1: Créer les cases du plateau
        self.cases.append(CaseSpeciale("Départ", 0, "depart"))
        self.cases.append(Propriete("Boulevard de Belleville", 1, 60, 2, "marron"))
        self.cases.append(CaseSpeciale("Caisse de Communauté", 2, "caisse"))
        self.cases.append(Propriete("Rue Lecourbe", 3, 60, 4, "marron"))
        self.cases.append(CaseSpeciale("Impôts sur le revenu", 4, "taxe"))
        self.cases.append(Gare("Gare Montparnasse", 5))
        self.cases.append(Propriete("Rue de Vaugirard", 6, 100, 6, "bleu clair"))
        self.cases.append(CaseSpeciale("Chance", 7, "chance"))
        self.cases.append(Propriete("Rue de Courcelles", 8, 100, 6, "bleu clair"))
        self.cases.append(Propriete("Avenue de la République", 9, 120, 8, "bleu clair"))
        self.cases.append(CaseSpeciale("Prison", 10, "prison"))
        self.cases.append(Propriete("Boulevard de la Villette", 11, 140, 10, "rose"))
        self.cases.append(Compagnie("Compagnie d'électricité", 12))
        self.cases.append(Propriete("Avenue de Neuilly", 13, 140, 10, "rose"))
        self.cases.append(Propriete("Rue de Paradis", 14, 160, 12, "rose"))
        self.cases.append(Gare("Gare de Lyon", 15))
        self.cases.append(Propriete("Avenue Mozart", 16, 180, 14, "orange"))
        self.cases.append(CaseSpeciale("Caisse de Communauté", 17, "caisse"))
        self.cases.append(Propriete("Boulevard Saint-Michel", 18, 180, 14, "orange"))
        self.cases.append(Propriete("Place Pigalle", 19, 200, 16, "orange"))
        self.cases.append(CaseSpeciale("Parc Gratuit", 20, "parc"))
        self.cases.append(Propriete("Avenue Matignon", 21, 220, 18, "rouge"))
        self.cases.append(CaseSpeciale("Chance", 22, "chance"))
        self.cases.append(Propriete("Boulevard Malesherbes", 23, 220, 18, "rouge"))
        self.cases.append(Propriete("Avenue Henri-Martin", 24, 240, 20, "rouge"))
        self.cases.append(Gare("Gare Montparnasse", 25))
        self.cases.append(Propriete("Faubourg Saint-Honoré", 26, 260, 22, "jaune"))
        self.cases.append(Propriete("Place de la Bourse", 27, 260, 22, "jaune"))
        self.cases.append(Compagnie("Compagnie de distribution des eaux", 28))
        self.cases.append(Propriete("Rue La Fayette", 29, 280, 24, "jaune"))
        self.cases.append(CaseSpeciale("Allez en Prison", 30, "allez_prison"))
        self.cases.append(Propriete("Avenue de Breteuil", 31, 300, 26, "vert"))
        self.cases.append(Propriete("Avenue Foch", 32, 300, 26, "vert"))
        self.cases.append(CaseSpeciale("Caisse de Communauté", 33, "caisse"))
        self.cases.append(Propriete("Boulevard des Capucines", 34, 320, 28, "vert"))
        self.cases.append(Gare("Gare Saint-Lazare", 35))
        self.cases.append(CaseSpeciale("Chance", 36, "chance"))
        self.cases.append(Propriete("Avenue des Champs-Élysées", 37, 350, 35, "bleu foncé"))
        self.cases.append(CaseSpeciale("Taxe de luxe", 38, "taxe"))
        self.cases.append(Propriete("Rue de la Paix", 39, 400, 50, "bleu foncé"))
    
    def get_case(self, position: int) -> Case:
        """Retourne la case à une position donnée"""
        return self.cases[position % len(self.cases)]

# =============================================================================
# SÉANCE 3 : JOUABILITÉ (3h)
# =============================================================================

class CarteCommunaute:
    """Représente une carte Caisse de Communauté ou Chance"""
    def __init__(self, description: str, action):
        self.description = description
        self.action = action  # Fonction à exécuter

class PaquetCartes:
    """Gère un paquet de cartes (Chance ou Communauté)"""
    def __init__(self, type_paquet: str):
        self.type_paquet = type_paquet
        self.cartes: List[CarteCommunaute] = []
        self._creer_cartes()
    
    def _creer_cartes(self):
        """Crée les cartes du paquet"""
        # TODO SÉANCE 3: Créer les différentes cartes
        pass
    
    def piocher(self) -> CarteCommunaute:
        """Pioche une carte au hasard"""
        # TODO SÉANCE 3: Implémenter la pioche avec mélange
        pass

# =============================================================================
# CLASSE PRINCIPALE DU JEU
# =============================================================================

class Monopoly:
    """Classe principale qui gère une partie de Monopoly"""
    def __init__(self, noms_joueurs: List[str]):
        self.plateau = Plateau()
        self.joueurs = [Joueur(nom) for nom in noms_joueurs]
        self.joueur_actuel_index = 0
        self.cartes_chance = PaquetCartes("chance")
        self.cartes_communaute = PaquetCartes("communaute")
        self.tour_numero = 0
    
    def lancer_des(self) -> tuple:
        """Lance deux dés et retourne les valeurs"""
        # TODO SÉANCE 1: Implémenter le lancer de dés
        de1 = random.randint(1, 6)
        de2 = random.randint(1, 6)
        return de1, de2
    
    def jouer_tour(self, joueur: Joueur):
        """Joue un tour complet pour un joueur"""
        # TODO SÉANCE 2: Implémenter la logique complète d'un tour
        print(f"\n--- Tour de {joueur.nom} ---")
        print(f"Position: {joueur.position}, Argent: {joueur.argent}€")
        
        de1, de2 = self.lancer_des() 
        total = de1 + de2 
        if  de1 == de2:
            print(f"{joueur.nom} a fait un double avec les dés !")
            joueur.doubles_consecutifs += 1
            if joueur.doubles_consecutifs == 3:
                print(f"{joueur.nom} a fait 3 doubles consécutifs et va en prison !")
                joueur.position = 10  # Position de la prison
                joueur.en_prison = True
                joueur.doubles_consecutifs = 0
                return 
        else:
            joueur.doubles_consecutifs = 0
            
        print(f"Dés: {de1} + {de2} = {total}") 
        joueur.deplacer(total)
        case_actuelle = self.plateau.get_case(joueur.position)
        print(f"{joueur.nom} arrive sur {case_actuelle.nom} (Case {case_actuelle.position})")
        # 3. Exécuter l'action de la case
        case_actuelle.action(joueur, self)
        pass
    
    def partie_terminee(self) -> bool:
        """Vérifie si la partie est terminée"""
        # TODO SÉANCE 3: Une seule personne non en faillite = partie terminée
        joueurs_actifs = [j for j in self.joueurs if not j.est_en_faillite]
        return len(joueurs_actifs) <= 1
    
    def obtenir_gagnant(self) -> Optional[Joueur]:
        """Retourne le joueur gagnant"""
        joueurs_actifs = [j for j in self.joueurs if not j.est_en_faillite]
        return joueurs_actifs[0] if len(joueurs_actifs) == 1 else None
    
    def jouer_partie(self, max_tours: int = 200):
        """Joue une partie complète de Monopoly"""
        # TODO SÉANCE 3: Implémenter la boucle principale du jeu
        print("=== DÉBUT DE LA PARTIE ===\n")
        
        while not self.partie_terminee() and self.tour_numero < max_tours:
            joueur = self.joueurs[self.joueur_actuel_index]
            
            if not joueur.est_en_faillite:
                self.jouer_tour(joueur)
            
            # Passer au joueur suivant
            self.joueur_actuel_index = (self.joueur_actuel_index + 1) % len(self.joueurs)
            
            if self.joueur_actuel_index == 0:
                self.tour_numero += 1
        
        # Afficher le résultat
        gagnant = self.obtenir_gagnant()
        if gagnant:
            print(f"\n🎉 {gagnant.nom} a gagné avec {gagnant.argent}€ !")
        else:
            print(f"\nPartie terminée après {max_tours} tours (limite atteinte)")

# =============================================================================
# SÉANCE 4 : IA ET STATISTIQUES (3h)
# =============================================================================

class StrategieIA:
    """Classe de base pour les stratégies d'IA"""
    def decider_achat(self, joueur: Joueur, propriete: Propriete) -> bool:
        """Décide si l'IA doit acheter une propriété"""
        # TODO SÉANCE 4: Implémenter différentes stratégies

        # Strategie agressive : acheter si possible
        if joueur.argent >= propriete.prix: 
            return True
        

        return False
    
    def decider_construction(self, joueur: Joueur, proprietes_quartier: List[Propriete]) -> Optional[Propriete]:
        """Décide sur quelle propriété construire"""
        # TODO SÉANCE 4: Implémenter la logique de construction
        return None

class StatistiquesPartie:
    """Collecte des statistiques sur une partie"""
    def __init__(self):
        self.passages_par_case = {}
        self.revenus_par_propriete = {}
        self.duree_partie = 0
    
    def enregistrer_passage(self, case: Case):
        """Enregistre le passage d'un joueur sur une case"""
        # TODO SÉANCE 4: Implémenter le tracking des statistiques
        pass
    
    def afficher_statistiques(self):
        """Affiche les statistiques collectées"""
        # TODO SÉANCE 4: Afficher les stats intéressantes
        pass

def simuler_parties(nb_parties: int, nb_joueurs: int):
    """Simule plusieurs parties et collecte des statistiques"""
    # TODO SÉANCE 4: Implémenter la simulation de multiples parties
    print(f"Simulation de {nb_parties} parties avec {nb_joueurs} joueurs...")
    pass

# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

if __name__ == "__main__":
        
    for p in DB.get_proprietes():
        print(f"{p.position} : ({p.couleur}) {p.nom} - prix d'achat : {p.prix}€")


    # Test basique
    noms = ["Alain", "Béa"]
    jeu = Monopoly(noms)
    alain = jeu.joueurs[0]

    alain.position = 1
    prop = jeu.plateau.cases[1]

    argent_avant = alain.argent
    prop.action(alain, jeu)

    assert prop.proprietaire == alain, "Alain doit posséder la propriété"
    assert alain.argent == argent_avant - prop.prix, "Le montant doit être débité"
    print("Achat de propriété validé!")

    # TODO: Décommenter quand les méthodes sont implémentées
    # jeu.jouer_partie(max_tours=100)
    
    print("Squelette de code chargé. Prêt pour le développement !")

    # test deplacement 
    # Position 35 + 7 cases = 2 (passage par départ)
    joueur_test = Joueur("Test")
    joueur_test.position = 35
    a_passe_depart = joueur_test.deplacer(7)
    print(joueur_test.position)
    assert joueur_test.position == 2, "Le joueur doit être à la position 2"
    assert a_passe_depart == True, "Le joueur doit avoir passé par Départ"  
    print("Déplacement validé!")

    plateau = Plateau() 
    assert len(plateau.cases) == 40, "Le plateau doit avoir 40 cases" 
    assert isinstance(plateau.cases[0], CaseSpeciale), "Case 0 = Départ" 
    assert isinstance(plateau.cases[5], Gare), "Case 5 = Gare" 
    assert plateau.cases[39].nom == "Rue de la Paix", "Dernière case" 
    print("Plateau validé!") 

#test du paiement 

alain = Joueur("Alain", 1500) 
bea = Joueur("Béa", 1500) 
prop = Propriete("Test", 1, 100, 10, "test") 

# Alain achète 
alain.acheter_propriete(prop) 
 
# Béa tombe dessus 
argent_bea_avant = bea.argent 
argent_alain_avant = alain.argent 
bea.payer(10, alain) 

assert bea.argent == argent_bea_avant - 10 
assert alain.argent == argent_alain_avant + 10 
print("Paiement validé!") 

jeu = Monopoly(["Alain", "Béa"]) 
for i in range(10): 
    for joueur in jeu.joueurs: 
        if not joueur.est_en_faillite: 
            jeu.jouer_tour(joueur) 

print("\nÉtat final:") 
for joueur in jeu.joueurs: 
    print(f"{joueur.nom}: {joueur.argent}€, {len(joueur.proprietes)} propriétés") 
