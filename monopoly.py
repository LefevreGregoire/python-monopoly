import mysql.connector
import random
from typing import List, Optional

# =============================================================================
# CLASSES DE BASE (SÉANCE 1 & 2)
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
    def __init__(self, nom: str, position: int, prix: int, loyer: int, couleur: str, prix_maison: int = 50):
        super().__init__(nom, position)
        self.prix = prix
        self.loyer_base = loyer
        self.couleur = couleur
        self.prix_maison = prix_maison 
        self.proprietaire: Optional['Joueur'] = None
        self.nb_maisons = 0
        self.a_hotel = False
    
    def possede_quartier_complet(self, joueur: 'Joueur', jeu: 'Monopoly') -> bool:
        """Vérifie si le joueur possède toutes les propriétés d'une couleur (Exercice 2.2)"""
        # Compter combien de terrains de cette couleur existent sur le plateau
        total_quartier = 0
        for case in jeu.plateau.cases:
            if isinstance(case, Propriete) and case.couleur == self.couleur:
                total_quartier += 1
        
        # Compter combien le joueur en possède
        possedes = 0
        for prop in joueur.proprietes:
            if prop.couleur == self.couleur:
                possedes += 1
                
        return possedes == total_quartier and total_quartier > 0

    def calculer_loyer(self) -> int:
        """Calcule le loyer en fonction des maisons/hôtels (Exercice 2.2)"""
        if self.proprietaire is None:
            return 0

        # Si hôtel : loyer x 5 (simplifié)
        if self.a_hotel:
            return self.loyer_base * 5
            
        # Si maisons : loyer * 2^(nb_maisons)
        if self.nb_maisons > 0:
            return self.loyer_base * (2 ** self.nb_maisons)
            
        # Si terrain nu : loyer de base
        # (Note: La règle du x2 si quartier complet sans maison est gérée dans l'action pour simplifier l'accès au jeu)
        return self.loyer_base
    
    def construire_maison(self, joueur: 'Joueur'):
        """Construit une maison ou un hôtel"""
        if self.a_hotel:
            print("Déjà un hôtel !")
            return

        if joueur.argent >= self.prix_maison:
            joueur.argent -= self.prix_maison
            if self.nb_maisons < 4:
                self.nb_maisons += 1
                print(f"Maison construite sur {self.nom}. Total: {self.nb_maisons}")
            else:
                self.nb_maisons = 0
                self.a_hotel = True
                print(f"Hôtel construit sur {self.nom} !")
        else:
            print("Pas assez d'argent.")

    def action(self, joueur: 'Joueur', jeu: 'Monopoly'):
        """Gère l'arrivée d'un joueur sur la propriété"""
        print(f"-> {self.nom} (Prix: {self.prix}€, Loyer actuel: {self.calculer_loyer()}€)")
        
        if self.proprietaire is None:
            # Achat automatique si possible (pour simplifier)
            if joueur.argent >= self.prix:
                joueur.acheter_propriete(self)
                print(f"{joueur.nom} achète {self.nom} pour {self.prix}€")
        
        elif self.proprietaire == joueur:
            # Le joueur est chez lui, il essaie de construire si possible
            if self.possede_quartier_complet(joueur, jeu) and joueur.argent > 500:
                 self.construire_maison(joueur)
            else:
                print("Vous êtes chez vous.")

        else:
            # Payer le loyer
            loyer = self.calculer_loyer()
            
            # Règle : Loyer doublé si terrain nu + quartier complet
            if self.nb_maisons == 0 and not self.a_hotel:
                if self.proprietaire.possede_quartier(self.couleur, jeu.plateau.cases):
                    loyer = loyer * 2
                    print("(Loyer doublé : quartier complet !)")

            joueur.payer(loyer, self.proprietaire)
            print(f"Loyer de {loyer}€ payé à {self.proprietaire.nom}")

class Gare(Propriete):
    """Case représentant une gare (Exercice 2.3)"""
    def __init__(self, nom: str, position: int):
        super().__init__(nom, position, prix=200, loyer=25, couleur="gare", prix_maison=0)
    
    def calculer_loyer(self) -> int:
        if not self.proprietaire:
            return 0
        # Compter les gares du proprio
        nb_gares = sum(1 for p in self.proprietaire.proprietes if isinstance(p, Gare))
        # 25, 50, 100, 200
        return 25 * (2 ** (nb_gares - 1)) if nb_gares > 0 else 0
    
class Compagnie(Propriete):
    """Case représentant une compagnie (Exercice 2.3)"""
    def __init__(self, nom: str, position: int):
        super().__init__(nom, position, prix=150, loyer=0, couleur="Compagnie", prix_maison=0)
        self.dernier_lancer = 0
    
    def action(self, joueur: 'Joueur', jeu: 'Monopoly'):
        self.dernier_lancer = sum(jeu.derniers_des) # On retient les dés
        super().action(joueur, jeu)

    def calculer_loyer(self) -> int:
        if not self.proprietaire:
            return 0
        nb_comp = sum(1 for p in self.proprietaire.proprietes if isinstance(p, Compagnie))
        facteur = 10 if nb_comp == 2 else 4
        return self.dernier_lancer * facteur

class CaseSpeciale(Case):
    """Cases comme Départ, Prison, Taxe, etc. (Exercice 2.1)"""
    def __init__(self, nom: str, position: int, type_case: str):
        super().__init__(nom, position)
        self.type_case = type_case
    
    def action(self, joueur: 'Joueur', jeu: 'Monopoly'):
        if self.type_case == "depart":
            print("Case Départ.")
        elif self.type_case == "allez_prison":
            print("Allez en prison !")
            joueur.aller_en_prison()
        elif self.type_case == "taxe":
            print("Taxe : Payez 100€")
            joueur.payer(100)
        elif self.type_case == "parc":
            print("Parc gratuit : repos.")
        elif self.type_case == "chance":
            print("Carte Chance !")
            jeu.cartes_chance.piocher_et_executer(joueur, jeu)
        elif self.type_case == "caisse":
            print("Caisse de Communauté !")
            jeu.cartes_communaute.piocher_et_executer(joueur, jeu)

class Joueur:
    """Représente un joueur"""
    def __init__(self, nom: str, argent_initial: int = 1500):
        self.nom = nom
        self.argent = argent_initial
        self.position = 0
        self.proprietes: List[Propriete] = []
        self.en_prison = False
        self.tours_en_prison = 0
        self.est_en_faillite = False
        self.doubles_consecutifs = 0
        self.cartes_liberte = 0 
    
    def deplacer(self, nombre_cases: int, plateau_taille: int = 40):
        anc_pos = self.position
        self.position = (self.position + nombre_cases) % plateau_taille
        if self.position < anc_pos and nombre_cases > 0:
            print("Passage par Départ : +200€")
            self.recevoir(200)
    
    def payer(self, montant: int, beneficiaire: Optional['Joueur'] = None):
        if self.argent >= montant:
            self.argent -= montant
            if beneficiaire:
                beneficiaire.recevoir(montant)
        else:
            self.declarer_faillite(beneficiaire)
    
    def declarer_faillite(self, beneficiaire: Optional['Joueur'] = None):
        print(f"XXX {self.nom} est en FAILLITE ! XXX")
        self.est_en_faillite = True
        self.argent = 0
        if beneficiaire:
            for p in self.proprietes:
                p.proprietaire = beneficiaire
                beneficiaire.proprietes.append(p)
        else:
            for p in self.proprietes: # Retour à la banque
                p.proprietaire = None
                p.nb_maisons = 0
                p.a_hotel = False
        self.proprietes.clear()

    def recevoir(self, montant: int):
        self.argent += montant
    
    def acheter_propriete(self, propriete: Propriete) -> bool:
        if propriete.proprietaire is None and self.argent >= propriete.prix:
            self.argent -= propriete.prix
            propriete.proprietaire = self
            self.proprietes.append(propriete)
            return True
        return False
    
    def aller_en_prison(self):
        self.position = 10
        self.en_prison = True
        self.tours_en_prison = 0
        self.doubles_consecutifs = 0

    def sortir_de_prison(self):
        self.en_prison = False
        self.tours_en_prison = 0
        
    def possede_quartier(self, couleur: str, toutes_cases: List[Case]) -> bool:
        """Helper pour vérifier les quartiers"""
        mes_props = [p for p in self.proprietes if p.couleur == couleur]
        total_props = [c for c in toutes_cases if isinstance(c, Propriete) and c.couleur == couleur]
        return len(mes_props) == len(total_props) and len(total_props) > 0

# =============================================================================
# ACCES DONNÉES ET CARTES (SÉANCE 3)
# =============================================================================

class DB:
    # Liste des proprietes (cache)
    __Proprietes = []

    @classmethod
    def connexionBase(cls):
        # Configuration spécifique demandée
        mydb = mysql.connector.connect(
            host="localhost",
            port=1433,
            user="SA",
            password="Azerty*!*",
            database="Toto"
        )
        return mydb

    @classmethod
    def get_proprietes(cls):
        # Si déjà chargé, on retourne la liste
        if cls.__Proprietes:
            return cls.__Proprietes

        try:
            print("Connexion à la BDD...")
            maConnexion = cls.connexionBase()
            monCurseur = maConnexion.cursor(dictionary=True)

            # Requete sur la vue v_proprietes
            monCurseur.execute("""
                SELECT position, nom, type_propriete_code, prix_achat, 
                       loyer_base, couleur, prix_maison
                FROM v_proprietes;
            """)
            mesResultats = monCurseur.fetchall()

            for r in mesResultats:
                p = None
                # Instanciation selon le code type
                if r["type_propriete_code"] == "propriete":
                    p = Propriete(r["nom"], r["position"], r["prix_achat"], 
                                  r["loyer_base"], r["couleur"], r["prix_maison"])
                elif r["type_propriete_code"] == "gare":
                    p = Gare(r["nom"], r["position"])
                elif r["type_propriete_code"] == "compagnie":
                    p = Compagnie(r["nom"], r["position"])

                if p:
                    cls.__Proprietes.append(p)

            monCurseur.close()
            maConnexion.close()
            print(f"{len(cls.__Proprietes)} propriétés chargées depuis la BDD.")
            
        except Exception as e:
            print(f"Erreur BDD: {e}. Utilisation du mode sans BDD.")
            return [] # Retourne vide pour déclencher la création manuelle

        return cls.__Proprietes

class CarteCommunaute:
    def __init__(self, description: str, action):
        self.description = description
        self.action = action 
    def executer(self, joueur, jeu):
        print(f"CARTE: {self.description}")
        self.action(joueur, jeu)

class PaquetCartes:
    def __init__(self, type_paquet: str):
        self.type_paquet = type_paquet
        self.cartes = []
        self._creer_cartes()
        self.pioche = []
        self.melanger()
    
    def _creer_cartes(self):
        # Exemples simples de cartes (lambda functions)
        if self.type_paquet == "chance":
            self.cartes = [
                CarteCommunaute("Avancez à Départ", lambda j, g: j.deplacer(40 - j.position)),
                CarteCommunaute("Allez en Prison", lambda j, g: j.aller_en_prison()),
                CarteCommunaute("Amende 20€", lambda j, g: j.payer(20))
            ]
        else:
            self.cartes = [
                CarteCommunaute("Erreur banque : +200€", lambda j, g: j.recevoir(200)),
                CarteCommunaute("Libéré de prison", lambda j, g: setattr(j, 'cartes_liberte', j.cartes_liberte + 1)),
                CarteCommunaute("Frais médecin : -50€", lambda j, g: j.payer(50))
            ]
    
    def melanger(self):
        self.pioche = self.cartes.copy()
        random.shuffle(self.pioche)

    def piocher_et_executer(self, joueur, jeu):
        if not self.pioche:
            self.melanger()
        carte = self.pioche.pop()
        carte.executer(joueur, jeu)

# =============================================================================
# MOTEUR DE JEU (PLATEAU & MONOPOLY)
# =============================================================================

class Plateau:
    def __init__(self):
        self.cases: List[Case] = []
        self._creer_plateau()
    
    def _creer_plateau(self):
        self.cases = [None] * 40
        
        # 1. Charger depuis la BDD
        props = DB.get_proprietes()
        for p in props:
            if 0 <= p.position < 40:
                self.cases[p.position] = p
        
        # 2. Remplir les cases spéciales (fixes)
        if not self.cases[0]: self.cases[0] = CaseSpeciale("Départ", 0, "depart")
        if not self.cases[4]: self.cases[4] = CaseSpeciale("Impôts", 4, "taxe")
        if not self.cases[10]: self.cases[10] = CaseSpeciale("Prison", 10, "prison")
        if not self.cases[20]: self.cases[20] = CaseSpeciale("Parc", 20, "parc")
        if not self.cases[30]: self.cases[30] = CaseSpeciale("Allez Prison", 30, "allez_prison")
        if not self.cases[38]: self.cases[38] = CaseSpeciale("Taxe Luxe", 38, "taxe")

        # 3. Remplir les trous restants (Chance, Caisse, ou secours si pas de BDD)
        for i in range(40):
            if self.cases[i] is None:
                if i in [2, 17, 33]:
                    self.cases[i] = CaseSpeciale("Caisse Com.", i, "caisse")
                elif i in [7, 22, 36]:
                    self.cases[i] = CaseSpeciale("Chance", i, "chance")
                else:
                    # Propriété par défaut si BDD vide
                    self.cases[i] = Propriete(f"Rue {i}", i, 100, 10, "gris")

    def get_case(self, position: int) -> Case:
        return self.cases[position % 40]

class Monopoly:
    def __init__(self, noms_joueurs: List[str]):
        self.plateau = Plateau()
        self.joueurs = [Joueur(nom) for nom in noms_joueurs]
        self.joueur_actuel_index = 0
        self.cartes_chance = PaquetCartes("chance")
        self.cartes_communaute = PaquetCartes("communaute")
        self.tour_numero = 0
        self.derniers_des = (0, 0)
    
    def lancer_des(self) -> tuple:
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        self.derniers_des = (d1, d2)
        return d1, d2
    
    def _gerer_prison(self, joueur: Joueur):
        """Logique de sortie de prison (3 options)"""
        print(f"--- Prison : {joueur.nom} (Tour {joueur.tours_en_prison+1}/3) ---")
        
        # 1. Carte
        if joueur.cartes_liberte > 0:
            print("Utilise une carte Sortie de Prison.")
            joueur.cartes_liberte -= 1
            joueur.sortir_de_prison()
            return

        # 2. Payer 50€ (si riche)
        if joueur.argent > 1000:
            print("Paie 50€ pour sortir.")
            joueur.payer(50)
            joueur.sortir_de_prison()
            return
            
        # 3. Essai dés
        d1, d2 = self.lancer_des()
        print(f"Dés prison: {d1}, {d2}")
        if d1 == d2:
            print("Double ! Sortie.")
            joueur.sortir_de_prison()
            joueur.deplacer(d1+d2)
            self.plateau.get_case(joueur.position).action(joueur, self)
            return
        
        joueur.tours_en_prison += 1
        if joueur.tours_en_prison >= 3:
            print("3 tours : Sortie forcée (-50€).")
            joueur.payer(50)
            joueur.sortir_de_prison()
            joueur.deplacer(d1+d2)
            self.plateau.get_case(joueur.position).action(joueur, self)

    def jouer_tour(self, joueur: Joueur):
        print(f"\n--- Tour {self.tour_numero} : {joueur.nom} ({joueur.argent}€) ---")
        
        if joueur.en_prison:
            self._gerer_prison(joueur)
            if joueur.en_prison: return # Encore en prison

        d1, d2 = self.lancer_des()
        print(f"Lancer : {d1} + {d2} = {d1+d2}")
        
        # Règle des 3 doubles
        if d1 == d2:
            joueur.doubles_consecutifs += 1
            if joueur.doubles_consecutifs == 3:
                print("3 Doubles -> Prison !")
                joueur.aller_en_prison()
                return
        else:
            joueur.doubles_consecutifs = 0
            
        joueur.deplacer(d1 + d2)
        case = self.plateau.get_case(joueur.position)
        case.action(joueur, self)
    
    def partie_terminee(self) -> bool:
        actifs = sum(1 for j in self.joueurs if not j.est_en_faillite)
        return actifs <= 1
    
    def obtenir_gagnant(self) -> Optional[Joueur]:
        for j in self.joueurs:
            if not j.est_en_faillite: return j
        return None
    
    def jouer_partie(self, max_tours: int = 100):
        print("=== DÉBUT PARTIE ===")
        while not self.partie_terminee() and self.tour_numero < max_tours:
            self.tour_numero += 1
            for j in self.joueurs:
                if not j.est_en_faillite:
                    self.jouer_tour(j)
                    if self.partie_terminee(): break
        
        gagnant = self.obtenir_gagnant()
        print(f"\nFIN. Gagnant : {gagnant.nom if gagnant else 'Personne'}")

# =============================================================================
# EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Test simple
    jeu = Monopoly(["Alain", "Béa", "Charles"])
    jeu.jouer_partie(max_tours=50)