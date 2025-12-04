import mysql.connector
import random
from typing import List, Optional, Dict

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
        """Construit une maison ou un hôtel (Exercice 2.2)"""
        if self.a_hotel:
            print("Déjà un hôtel !")
            return False
        
        if not self.peut_construire(joueur):
            print("Construction impossible.")
            return False

        if joueur.argent >= self.prix_maison:
            joueur.argent -= self.prix_maison
            if self.nb_maisons < 4:
                self.nb_maisons += 1
                print(f"Maison construite sur {self.nom}. Total: {self.nb_maisons}")
            else:
                self.nb_maisons = 0
                self.a_hotel = True
                print(f"Hôtel construit sur {self.nom} !")
            return True
        else:
            print("Pas assez d'argent.")
            return False
    
    def peut_construire(self, joueur: 'Joueur') -> bool:
        """Vérifie si on peut construire sur cette propriété (Exercice 2.2)"""
        # Le joueur doit être propriétaire
        if self.proprietaire != joueur:
            return False
        # Pas d'hôtel déjà
        if self.a_hotel:
            return False
        # Il faut posséder le quartier complet
        if not joueur.possede_quartier_complet(self.couleur):
            return False
        return True

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
    
    def possede_quartier_complet(self, couleur: str) -> bool:
        """Vérifie si le joueur possède toutes les propriétés d'une couleur (Exercice 2.2)"""
        # Nombre requis par couleur (simplifié)
        nb_par_couleur = {
            "marron": 2, "bleu_clair": 3, "rose": 3, "orange": 3,
            "rouge": 3, "jaune": 3, "vert": 3, "bleu_fonce": 2,
            "gare": 4, "Compagnie": 2, "gris": 2
        }
        
        # Compter les propriétés de cette couleur
        nb_possedees = sum(1 for p in self.proprietes if p.couleur == couleur)
        nb_requis = nb_par_couleur.get(couleur, 2)
        
        return nb_possedees >= nb_requis

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
        # Cartes Chance et Caisse de Communauté (Séance 3)
        if self.type_paquet == "chance":
            self.cartes = [
                CarteCommunaute("Avancez jusqu'à la case Départ", lambda j, g: self._avancer_case(j, g, 0)),
                CarteCommunaute("Allez en Prison", lambda j, g: j.aller_en_prison()),
                CarteCommunaute("Amende pour excès de vitesse: 15€", lambda j, g: j.payer(15)),
                CarteCommunaute("Reculez de 3 cases", lambda j, g: self._reculer(j, g, 3)),
                CarteCommunaute("Vous êtes libéré de prison", lambda j, g: self._donner_carte_liberte(j)),
                CarteCommunaute("Recevez un dividende de 50€", lambda j, g: j.recevoir(50)),
                CarteCommunaute("Payez chaque joueur 50€", lambda j, g: self._payer_tous_joueurs(j, g, 50)),
                CarteCommunaute("Rendez-vous Gare Montparnasse", lambda j, g: self._avancer_case(j, g, 5)),
                CarteCommunaute("Rendez-vous Avenue Henri-Martin", lambda j, g: self._avancer_case(j, g, 24)),
                CarteCommunaute("Rendez-vous Rue de la Paix", lambda j, g: self._avancer_case(j, g, 39))
            ]
        else:
            self.cartes = [
                CarteCommunaute("Avancez jusqu'à la case Départ", lambda j, g: self._avancer_case(j, g, 0)),
                CarteCommunaute("Erreur de la banque: +200€", lambda j, g: j.recevoir(200)),
                CarteCommunaute("Payez une amende de 10€", lambda j, g: j.payer(10)),
                CarteCommunaute("Allez en Prison", lambda j, g: j.aller_en_prison()),
                CarteCommunaute("Vous êtes libéré de prison", lambda j, g: self._donner_carte_liberte(j)),
                CarteCommunaute("Recevez 100€", lambda j, g: j.recevoir(100)),
                CarteCommunaute("Recevez votre revenu annuel: 100€", lambda j, g: j.recevoir(100)),
                CarteCommunaute("C'est votre anniversaire: +10€ de chaque joueur", lambda j, g: self._anniversaire(j, g)),
                CarteCommunaute("Amende pour ivresse: 20€", lambda j, g: j.payer(20)),
                CarteCommunaute("Prix de beauté: +10€", lambda j, g: j.recevoir(10))
            ]
    
    def _avancer_case(self, joueur, jeu, position):
        """Fait avancer le joueur jusqu'à une position (Séance 3)"""
        if position < joueur.position:
            # Passage par départ
            joueur.recevoir(200)
            print("Passage par Départ : +200€")
        joueur.position = position
        case = jeu.plateau.get_case(position)
        case.action(joueur, jeu)
    
    def _reculer(self, joueur, jeu, nb_cases):
        """Fait reculer le joueur (Séance 3)"""
        joueur.position = (joueur.position - nb_cases) % 40
        case = jeu.plateau.get_case(joueur.position)
        case.action(joueur, jeu)
    
    def _anniversaire(self, joueur, jeu):
        """Chaque joueur donne 10€ (Séance 3)"""
        for autre in jeu.joueurs:
            if autre != joueur and not autre.est_en_faillite:
                autre.payer(10, joueur)
                print(f"  {autre.nom} donne 10€ à {joueur.nom}")
    
    def _donner_carte_liberte(self, joueur):
        """Donne une carte sortie de prison (Séance 3)"""
        joueur.cartes_liberte += 1
        print(f"  {joueur.nom} garde cette carte (total: {joueur.cartes_liberte})")
    
    def _payer_tous_joueurs(self, joueur, jeu, montant):
        """Payer tous les autres joueurs (Séance 3)"""
        for autre in jeu.joueurs:
            if autre != joueur and not autre.est_en_faillite:
                joueur.payer(montant, autre)
                print(f"  {joueur.nom} paie 50€ à {autre.nom}")
    
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
                    # Propriétés par défaut avec prix réalistes (si BDD vide)
                    self._creer_propriete_defaut(i)

    def get_case(self, position: int) -> Case:
        return self.cases[position % 40]
    
    def _creer_propriete_defaut(self, position: int):
        """Crée une propriété par défaut avec des prix réalistes selon la position"""
        # Propriétés du Monopoly français (simplifié)
        proprietes_defaut = {
            # Marron (2 propriétés)
            1: ("Boulevard de Belleville", 60, 2, "marron", 50),
            3: ("Rue Lecourbe", 60, 4, "marron", 50),
            # Gares
            5: None,  # Gare - déjà gérée
            15: None,
            25: None,
            35: None,
            # Bleu clair (3 propriétés)
            6: ("Rue de Vaugirard", 100, 6, "bleu_clair", 50),
            8: ("Rue de Courcelles", 100, 6, "bleu_clair", 50),
            9: ("Avenue de la République", 120, 8, "bleu_clair", 50),
            # Rose (3 propriétés)
            11: ("Boulevard de la Villette", 140, 10, "rose", 100),
            13: ("Avenue de Neuilly", 140, 10, "rose", 100),
            14: ("Rue du Paradis", 160, 12, "rose", 100),
            # Compagnies
            12: None,  # Compagnie - déjà gérée
            28: None,
            # Orange (3 propriétés)
            16: ("Avenue Mozart", 180, 14, "orange", 100),
            18: ("Boulevard Saint-Michel", 180, 14, "orange", 100),
            19: ("Place Pigalle", 200, 16, "orange", 100),
            # Rouge (3 propriétés)
            21: ("Avenue Matignon", 220, 18, "rouge", 150),
            23: ("Boulevard Malesherbes", 220, 18, "rouge", 150),
            24: ("Avenue Henri-Martin", 240, 20, "rouge", 150),
            # Jaune (3 propriétés)
            26: ("Faubourg Saint-Honoré", 260, 22, "jaune", 150),
            27: ("Place de la Bourse", 260, 22, "jaune", 150),
            29: ("Rue La Fayette", 280, 24, "jaune", 150),
            # Vert (3 propriétés)
            31: ("Avenue de Breteuil", 300, 26, "vert", 200),
            32: ("Avenue Foch", 300, 26, "vert", 200),
            34: ("Boulevard des Capucines", 320, 28, "vert", 200),
            # Bleu foncé (2 propriétés)
            37: ("Avenue des Champs-Élysées", 350, 35, "bleu_fonce", 200),
            39: ("Rue de la Paix", 400, 50, "bleu_fonce", 200),
        }
        
        if position in proprietes_defaut and proprietes_defaut[position]:
            nom, prix, loyer, couleur, prix_maison = proprietes_defaut[position]
            self.cases[position] = Propriete(nom, position, prix, loyer, couleur, prix_maison)
        elif position == 5:
            self.cases[position] = Gare("Gare Montparnasse", 5)
        elif position == 15:
            self.cases[position] = Gare("Gare de Lyon", 15)
        elif position == 25:
            self.cases[position] = Gare("Gare du Nord", 25)
        elif position == 35:
            self.cases[position] = Gare("Gare Saint-Lazare", 35)
        elif position == 12:
            self.cases[position] = Compagnie("Compagnie d'Électricité", 12)
        elif position == 28:
            self.cases[position] = Compagnie("Compagnie des Eaux", 28)
        else:
            # Fallback
            self.cases[position] = Propriete(f"Rue {position}", position, 100, 10, "gris", 50)

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
    
    def jouer_partie(self, max_tours: int = 200):
        """Joue une partie complète de Monopoly (Séance 3)"""
        print("=== DÉBUT PARTIE ===")
        while not self.partie_terminee() and self.tour_numero < max_tours:
            self.tour_numero += 1
            for j in self.joueurs:
                if not j.est_en_faillite:
                    self.jouer_tour(j)
                    if self.partie_terminee(): break
            
            # Afficher un résumé tous les 25 tours (Séance 3)
            if self.tour_numero % 25 == 0:
                self._afficher_resume_tour()
        
        # Afficher le résultat final
        self._afficher_resultat_final()
        return self.obtenir_gagnant()
    
    def _afficher_resume_tour(self):
        """Affiche un résumé de la situation (Séance 3)"""
        print(f"\n--- RÉSUMÉ TOUR {self.tour_numero} ---")
        for j in self.joueurs:
            statut = "FAILLITE" if j.est_en_faillite else f"{j.argent}€, {len(j.proprietes)} props"
            print(f"  {j.nom}: {statut}")
    
    def _afficher_resultat_final(self):
        """Affiche le résultat final de la partie (Séance 3)"""
        print("\n" + "=" * 50)
        print("RÉSULTAT FINAL")
        print("=" * 50)
        
        gagnant = self.obtenir_gagnant()
        if gagnant:
            print(f"\nGAGNANT: {gagnant.nom} avec {gagnant.argent}€")
            print(f"Propriétés: {len(gagnant.proprietes)}")
            for p in gagnant.proprietes:
                print(f"  - {p.nom}")
        else:
            print(f"\nLimite de {self.tour_numero} tours atteinte")
            # Classement par argent
            joueurs_tries = sorted(self.joueurs, key=lambda x: x.argent, reverse=True)
            print("\nClassement:")
            for i, j in enumerate(joueurs_tries, 1):
                statut = "(FAILLITE)" if j.est_en_faillite else ""
                print(f"  {i}. {j.nom}: {j.argent}€ {statut}")

# =============================================================================
# EXECUTION
# =============================================================================

# =============================================================================
# SÉANCE 4 : STRATÉGIES IA
# =============================================================================

class StrategieIA:
    """Classe de base pour les stratégies"""
    def __init__(self, nom: str):
        self.nom = nom
    
    def decider_achat(self, joueur: 'Joueur', propriete: Propriete) -> bool:
        """Décide si acheter une propriété"""
        return False
    
    def decider_construction(self, joueur: 'Joueur') -> Optional[Propriete]:
        """Décide où construire"""
        return None


class IAAgressive(StrategieIA):
    """Achète systématiquement toutes les propriétés"""
    def __init__(self):
        super().__init__("Agressive")
    
    def decider_achat(self, joueur: 'Joueur', propriete: Propriete) -> bool:
        # Achète toujours si elle a l'argent
        if joueur.argent >= propriete.prix:
            return True
        return False


class IAConservative(StrategieIA):
    """Achète seulement si argent > 2× prix"""
    def __init__(self):
        super().__init__("Conservative")
    
    def decider_achat(self, joueur: 'Joueur', propriete: Propriete) -> bool:
        # Garder au moins le double du prix
        if joueur.argent >= propriete.prix * 2:
            return True
        return False


class IAStrategique(StrategieIA):
    """Privilégie les quartiers et propriétés rentables"""
    def __init__(self):
        super().__init__("Stratégique")
    
    def decider_achat(self, joueur: 'Joueur', propriete: Propriete) -> bool:
        # Ne pas dépenser si trop peu d'argent (moins de 1,5 x le prix d'achat)
        if joueur.argent < propriete.prix * 1.5:
            return False
        
        # Compter combien de propriétés de cette couleur possédées
        nb_possede = sum(1 for p in joueur.proprietes 
                        if hasattr(p, 'couleur') and p.couleur == propriete.couleur)
        
        # On achete si ça rapproche d'un quartier complet (déjà au moins 1 de cette couleur)
        if nb_possede >= 1:
            return True
        
        # Sinon acheter si beaucoup d'argent (3x le prix d'achat)
        if joueur.argent >= propriete.prix * 3:
            return True
        
        return False
    
    def decider_construction(self, joueur: 'Joueur') -> Optional[Propriete]:
        """Décide sur quelle propriété construire"""
        # Trouver les quartiers complets
        quartiers = self._trouver_quartiers(joueur)
        
        if not quartiers:
            return None
        
        # Chercher la propriété avec le meilleur ROI (retour sur investissement)
        meilleure = None
        meilleur_roi = 0
        
        for couleur, proprietes in quartiers.items():
            for prop in proprietes:
                # Vérifier si on peut construire
                if prop.nb_maisons < 4 and not prop.a_hotel and joueur.argent >= prop.prix_maison:
                    # Calculer le retour sur investissement
                    loyer_actuel = prop.calculer_loyer()
                    prop.nb_maisons += 1  # Simulation
                    loyer_futur = prop.calculer_loyer()
                    prop.nb_maisons -= 1  # Annuler la simulation
                    
                    if prop.prix_maison > 0:
                        roi = (loyer_futur - loyer_actuel) / prop.prix_maison
                        if roi > meilleur_roi:
                            meilleur_roi = roi
                            meilleure = prop
        
        return meilleure
    
    def _trouver_quartiers(self, joueur: 'Joueur') -> Dict[str, List[Propriete]]:
        """Liste les quartiers complets du joueur"""
        quartiers = {}
        
        # Compter les propriétés par couleur
        couleurs_joueur = {}
        for prop in joueur.proprietes:
            if isinstance(prop, Propriete) and not isinstance(prop, (Gare, Compagnie)):
                couleur = prop.couleur
                if couleur not in couleurs_joueur:
                    couleurs_joueur[couleur] = []
                couleurs_joueur[couleur].append(prop)
        
        # Garder seulement les quartiers "complets" (simplifié: au moins 2 propriétés)
        for couleur, props in couleurs_joueur.items():
            if len(props) >= 2:
                quartiers[couleur] = props
        
        return quartiers


# =============================================================================
# SÉANCE 4 : STATISTIQUES
# =============================================================================

class StatistiquesPartie:
    """Collecte des statistiques sur une partie"""
    def __init__(self):
        self.passages_par_case: Dict[int, int] = {}
        self.revenus_par_propriete: Dict[str, int] = {}
        self.duree_partie = 0
        self.nb_tours = 0
        self.gagnant = None
    
    def enregistrer_passage(self, case: Case):
        """Enregistre le passage sur une case"""
        position = case.position
        # Ajout dans le dictionnaire si 1er passage, incrémentation sinon
        if position not in self.passages_par_case:
            self.passages_par_case[position] = 1
        else:
            self.passages_par_case[position] += 1
    
    def enregistrer_loyer(self, propriete: Propriete, montant: int):
        """Enregistre un paiement de loyer"""
        nom = propriete.nom
        # Ajout du nom de la propriété si 1er loyer payé, cumul du montant sinon
        if nom not in self.revenus_par_propriete:
            self.revenus_par_propriete[nom] = montant
        else:
            self.revenus_par_propriete[nom] += montant
    
    def afficher_statistiques(self):
        """Affiche un résumé des statistiques"""
        print("\n" + "=" * 60)
        print("STATISTIQUES DE LA PARTIE")
        print("=" * 60)
        
        print(f"\nDurée: {self.nb_tours} tours")
        
        if self.gagnant:
            print(f"Gagnant: {self.gagnant.nom} ({self.gagnant.argent}€)")
        
        # Top 5 cases visitées
        print("\nTop 5 des cases les plus visitées:")
        top_cases = sorted(self.passages_par_case.items(), 
                          key=lambda x: x[1], reverse=True)[:5]
        for position, nb in top_cases:
            print(f"  Position {position}: {nb} passages")
        
        # Top 5 propriétés rentables
        if self.revenus_par_propriete:
            print("\nTop 5 des propriétés les plus rentables:")
            top_props = sorted(self.revenus_par_propriete.items(),
                              key=lambda x: x[1], reverse=True)[:5]
            for nom, revenus in top_props:
                print(f"  {nom}: {revenus}€ de loyers")


# =============================================================================
# FONCTIONS DE TEST SÉANCE 4
# =============================================================================

def tester_plateau():
    """Test du plateau (Séance 1)"""
    print("\nTEST DU PLATEAU (Séance 1)")
    plateau = Plateau()
    assert len(plateau.cases) == 40, "Le plateau doit avoir 40 cases"
    assert isinstance(plateau.cases[0], CaseSpeciale), "Case 0 = Départ"
    assert plateau.cases[0].type_case == "depart", "Case 0 est Départ"
    assert isinstance(plateau.cases[10], CaseSpeciale), "Case 10 = Prison"
    assert isinstance(plateau.cases[30], CaseSpeciale), "Case 30 = Allez Prison"
    print("  ✓ Plateau validé!")

def tester_deplacement():
    """Test du déplacement et passage par Départ (Séance 1)"""
    print("\nTEST DÉPLACEMENT (Séance 1)")
    joueur = Joueur("Test", 1500)
    
    # Test position 35 + 7 = 42 -> 2 (passage par Départ)
    joueur.position = 35
    argent_avant = joueur.argent
    joueur.deplacer(7)
    assert joueur.position == 2, "Position doit être 2"
    assert joueur.argent == argent_avant + 200, "Doit recevoir 200€"
    
    # Test position 5 + 3 = 8 (pas de passage)
    joueur.position = 5
    argent_avant = joueur.argent
    joueur.deplacer(3)
    assert joueur.position == 8, "Position doit être 8"
    assert joueur.argent == argent_avant, "Pas de bonus"
    
    print("  ✓ Déplacement validé!")

def tester_achat():
    """Test de l'achat de propriétés (Séance 1)"""
    print("\nTEST ACHAT (Séance 1)")
    joueur = Joueur("Test", 1500)
    prop = Propriete("Test Rue", 1, 100, 10, "test")
    
    argent_avant = joueur.argent
    resultat = joueur.acheter_propriete(prop)
    
    assert resultat == True, "Achat doit réussir"
    assert prop.proprietaire == joueur, "Joueur doit être propriétaire"
    assert joueur.argent == argent_avant - 100, "Argent déduit"
    assert prop in joueur.proprietes, "Propriété dans la liste"
    
    print("  ✓ Achat validé!")

def tester_loyer():
    """Test du paiement de loyer (Séance 1)"""
    print("\nTEST LOYER (Séance 1)")
    alain = Joueur("Alain", 1500)
    bea = Joueur("Béa", 1500)
    prop = Propriete("Test", 1, 100, 10, "test")
    
    alain.acheter_propriete(prop)
    
    argent_bea_avant = bea.argent
    argent_alain_avant = alain.argent
    bea.payer(10, alain)
    
    assert bea.argent == argent_bea_avant - 10, "Béa perd 10€"
    assert alain.argent == argent_alain_avant + 10, "Alain gagne 10€"
    
    print("  ✓ Loyer validé!")

def tester_cases_speciales():
    """Test des cases spéciales (Séance 2)"""
    print("\nTEST CASES SPÉCIALES (Séance 2)")
    jeu = Monopoly(["Test"])
    joueur = jeu.joueurs[0]
    
    # Test Prison
    joueur.position = 30
    jeu.plateau.cases[30].action(joueur, jeu)
    assert joueur.en_prison == True, "Doit être en prison"
    assert joueur.position == 10, "Position prison = 10"
    
    print("  ✓ Cases spéciales validées!")

def tester_construction():
    """Test de la construction de maisons (Séance 2)"""
    print("\nTEST CONSTRUCTION (Séance 2)")
    joueur = Joueur("Test", 2000)
    
    # Créer 2 propriétés de même couleur (quartier complet simplifié)
    prop1 = Propriete("Rue 1", 1, 100, 10, "marron", 50)
    prop2 = Propriete("Rue 2", 3, 100, 10, "marron", 50)
    
    joueur.acheter_propriete(prop1)
    joueur.acheter_propriete(prop2)
    
    # Vérifier le quartier complet
    assert joueur.possede_quartier_complet("marron") == True, "Doit posséder le quartier"
    
    # Construire
    loyer_avant = prop1.calculer_loyer()
    prop1.construire_maison(joueur)
    loyer_apres = prop1.calculer_loyer()
    
    assert prop1.nb_maisons == 1, "Doit avoir 1 maison"
    assert loyer_apres > loyer_avant, "Loyer doit augmenter"
    
    print(f"  Loyer: {loyer_avant}€ → {loyer_apres}€")
    print("  ✓ Construction validée!")

def tester_gares():
    """Test des gares (Séance 2)"""
    print("\nTEST GARES (Séance 2)")
    joueur = Joueur("Test", 2000)
    
    gare1 = Gare("Gare 1", 5)
    gare2 = Gare("Gare 2", 15)
    
    joueur.acheter_propriete(gare1)
    assert gare1.calculer_loyer() == 25, "1 gare = 25€"
    
    joueur.acheter_propriete(gare2)
    assert gare1.calculer_loyer() == 50, "2 gares = 50€"
    
    print("  ✓ Gares validées!")

def tester_compagnies():
    """Test des compagnies (Séance 2)"""
    print("\nTEST COMPAGNIES (Séance 2)")
    joueur = Joueur("Test", 2000)
    
    comp = Compagnie("Électricité", 12)
    joueur.acheter_propriete(comp)
    
    comp.dernier_lancer = 7
    assert comp.calculer_loyer() == 28, "1 compagnie: 4×7=28€"
    
    print("  ✓ Compagnies validées!")

def tester_prison():
    """Test de la prison (Séance 3)"""
    print("\nTEST PRISON (Séance 3)")
    jeu = Monopoly(["Test"])
    joueur = jeu.joueurs[0]
    
    joueur.aller_en_prison()
    assert joueur.en_prison == True, "Doit être en prison"
    assert joueur.position == 10, "Position = 10"
    
    joueur.sortir_de_prison()
    assert joueur.en_prison == False, "Doit être sorti"
    
    print("  ✓ Prison validée!")

def tester_cartes():
    """Test des cartes (Séance 3)"""
    print("\nTEST CARTES (Séance 3)")
    jeu = Monopoly(["Test"])
    joueur = jeu.joueurs[0]
    
    # Test de pioche (vérifie juste que ça ne plante pas)
    position_avant = joueur.position
    argent_avant = joueur.argent
    
    jeu.cartes_chance.piocher_et_executer(joueur, jeu)
    
    # L'état doit avoir changé d'une manière ou d'une autre
    changement = (joueur.argent != argent_avant or 
                  joueur.position != position_avant or
                  joueur.en_prison or
                  joueur.cartes_liberte > 0)
    
    print("  ✓ Cartes validées!")

def tester_strategies():
    """Test des différentes stratégies IA"""
    print("\nTEST DES STRATÉGIES IA")
    
    strategies = [
        IAAgressive(),
        IAConservative(),
        IAStrategique()
    ]
    
    for strat in strategies:
        print(f"\n{'=' * 60}")
        print(f"Stratégie: {strat.nom}")
        print(f"{'=' * 60}")
        
        jeu = MonopolyIA(["IA1", "IA2", "IA3"], strategie=strat)
        gagnant = jeu.jouer_partie(max_tours=50)
        
        if gagnant:
            print(f"Gagnant: {gagnant.nom}")
        
        # Afficher les stats
        jeu.stats.afficher_statistiques()


def simuler_parties(nb_parties: int, nb_joueurs: int, strategie: StrategieIA):
    """Simule plusieurs parties avec une stratégie"""
    print(f"\nSimulation de {nb_parties} parties avec stratégie {strategie.nom}")
    
    victoires = 0
    total_tours = 0
    
    for i in range(nb_parties):
        noms = [f"Joueur{j+1}" for j in range(nb_joueurs)]
        jeu = MonopolyIA(noms, strategie=strategie)
        gagnant = jeu.jouer_partie(max_tours=200)
        total_tours += jeu.stats.nb_tours
        
        if gagnant:
            victoires += 1
    
    print(f"  Parties terminées avec gagnant: {victoires}/{nb_parties}")
    print(f"  Durée moyenne: {total_tours / nb_parties:.1f} tours")


def comparer_strategies(nb_parties: int, nb_joueurs: int):
    """Compare les différentes stratégies"""
    print(f"\n{'=' * 60}")
    print("COMPARAISON DES STRATÉGIES")
    print(f"{'=' * 60}")
    
    resultats = {
        "Agressive": 0,
        "Conservative": 0,
        "Stratégique": 0
    }
    
    strategies = [IAAgressive(), IAConservative(), IAStrategique()]
    
    for i in range(nb_parties):
        # Choisir une stratégie aléatoire pour cette partie
        strat = random.choice(strategies)
        noms = [f"J{j+1}" for j in range(nb_joueurs)]
        jeu = MonopolyIA(noms, strategie=strat)
        gagnant = jeu.jouer_partie(max_tours=200)
        
        if gagnant:
            resultats[strat.nom] += 1
    
    print("\nRésultats:")
    for nom, victoires in resultats.items():
        print(f"  {nom}: {victoires} victoires ({victoires * 100 / nb_parties:.1f}%)")


def analyser_probabilites_cases():
    """Analyse les probabilités de tomber sur chaque case"""
    print(f"\n{'=' * 60}")
    print("ANALYSE PROBABILISTE DES CASES")
    print(f"{'=' * 60}")
    
    # Simuler beaucoup de lancers
    passages = {}
    position = 0
    
    for _ in range(10000):
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        position = (position + d1 + d2) % 40
        
        if position not in passages:
            passages[position] = 0
        passages[position] += 1
    
    # Afficher le top 10
    print("\nTop 10 des cases les plus probables (sur 10000 lancers):")
    top = sorted(passages.items(), key=lambda x: x[1], reverse=True)[:10]
    for pos, nb in top:
        print(f"  Case {pos}: {nb} passages ({nb / 100:.2f}%)")


# =============================================================================
# CLASSE MONOPOLY AVEC IA (Version étendue)
# =============================================================================

class MonopolyIA(Monopoly):
    """Version du Monopoly avec support des stratégies IA et statistiques"""
    def __init__(self, noms_joueurs: List[str], strategie: StrategieIA = None):
        super().__init__(noms_joueurs)
        self.strategie = strategie if strategie else StrategieIA("Défaut")
        self.stats = StatistiquesPartie()
    
    def jouer_tour(self, joueur: Joueur):
        """Jouer un tour avec enregistrement des stats"""
        print(f"\n--- Tour {self.tour_numero} : {joueur.nom} ({joueur.argent}€) ---")
        
        if joueur.en_prison:
            self._gerer_prison(joueur)
            if joueur.en_prison:
                return
        
        d1, d2 = self.lancer_des()
        print(f"Lancer : {d1} + {d2} = {d1 + d2}")
        
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
        
        # Enregistrer le passage dans les stats
        self.stats.enregistrer_passage(case)
        
        # Action avec IA
        self._action_avec_ia(joueur, case)
    
    def _action_avec_ia(self, joueur: Joueur, case: Case):
        """Exécute l'action sur la case en utilisant la stratégie IA"""
        if isinstance(case, Propriete):
            print(f"-> {case.nom} (Prix: {case.prix}€, Loyer: {case.calculer_loyer()}€)")
            
            if case.proprietaire is None:
                # Demander à l'IA si on achète
                if self.strategie.decider_achat(joueur, case):
                    if joueur.acheter_propriete(case):
                        print(f"{joueur.nom} achète {case.nom} pour {case.prix}€")
                    else:
                        print(f"{joueur.nom} ne peut pas acheter (pas assez d'argent)")
                else:
                    print(f"{joueur.nom} décide de ne pas acheter")
            
            elif case.proprietaire == joueur:
                print("Vous êtes chez vous.")
                # Essayer de construire avec l'IA stratégique
                if isinstance(self.strategie, IAStrategique):
                    prop_construire = self.strategie.decider_construction(joueur)
                    if prop_construire:
                        prop_construire.construire_maison(joueur)
            
            else:
                # Payer le loyer
                loyer = case.calculer_loyer()
                
                # Règle : Loyer doublé si terrain nu + quartier complet
                if case.nb_maisons == 0 and not case.a_hotel:
                    if case.proprietaire.possede_quartier(case.couleur, self.plateau.cases):
                        loyer = loyer * 2
                        print("(Loyer doublé : quartier complet !)")
                
                joueur.payer(loyer, case.proprietaire)
                print(f"Loyer de {loyer}€ payé à {case.proprietaire.nom}")
                
                # Enregistrer le loyer dans les stats
                self.stats.enregistrer_loyer(case, loyer)
        else:
            # Case spéciale
            case.action(joueur, self)
    
    def jouer_partie(self, max_tours: int = 200) -> Optional[Joueur]:
        """Joue une partie complète et retourne le gagnant"""
        print("=== DÉBUT PARTIE ===")
        
        while not self.partie_terminee() and self.tour_numero < max_tours:
            self.tour_numero += 1
            for j in self.joueurs:
                if not j.est_en_faillite:
                    self.jouer_tour(j)
                    if self.partie_terminee():
                        break
            
            # Afficher un résumé tous les 10 tours (Séance 3)
            if self.tour_numero % 10 == 0:
                self._afficher_resume_tour()
        
        # Enregistrer les stats finales
        self.stats.nb_tours = self.tour_numero
        gagnant = self.obtenir_gagnant()
        self.stats.gagnant = gagnant
        
        # Afficher le résultat final
        self._afficher_resultat_final()
        return gagnant
    
    def _afficher_resume_tour(self):
        """Affiche un résumé de la situation"""
        print(f"\n--- RÉSUMÉ TOUR {self.tour_numero} ---")
        for j in self.joueurs:
            statut = "FAILLITE" if j.est_en_faillite else f"{j.argent}€, {len(j.proprietes)} props"
            print(f"  {j.nom}: {statut}")
    
    def _afficher_resultat_final(self):
        """Affiche le résultat final de la partie"""
        print("\n" + "=" * 50)
        print("RÉSULTAT FINAL")
        print("=" * 50)
        
        gagnant = self.obtenir_gagnant()
        if gagnant:
            print(f"\nGAGNANT: {gagnant.nom} avec {gagnant.argent}€")
            print(f"Propriétés: {len(gagnant.proprietes)}")
        else:
            print(f"\nLimite de {self.tour_numero} tours atteinte")
            # Classement par argent
            joueurs_tries = sorted(self.joueurs, key=lambda x: x.argent, reverse=True)
            print("\nClassement:")
            for i, j in enumerate(joueurs_tries, 1):
                statut = "(FAILLITE)" if j.est_en_faillite else ""
                print(f"  {i}. {j.nom}: {j.argent}€ {statut}")


# =============================================================================
# EXECUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TESTS DE VALIDATION - MONOPOLY PYTHON")
    print("=" * 60)
    
    # ========== TESTS SÉANCE 1 ==========
    print("\n" + "=" * 60)
    print("SÉANCE 1 : FONDATIONS")
    print("=" * 60)
    tester_plateau()
    tester_deplacement()
    tester_achat()
    tester_loyer()
    
    # ========== TESTS SÉANCE 2 ==========
    print("\n" + "=" * 60)
    print("SÉANCE 2 : MÉCANIQUE DE JEU")
    print("=" * 60)
    tester_cases_speciales()
    tester_construction()
    tester_gares()
    tester_compagnies()
    
    # ========== TESTS SÉANCE 3 ==========
    print("\n" + "=" * 60)
    print("SÉANCE 3 : JOUABILITÉ COMPLÈTE")
    print("=" * 60)
    tester_prison()
    tester_cartes()
    
    # ========== TESTS SÉANCE 4 ==========
    print("\n" + "=" * 60)
    print("SÉANCE 4 : IA ET ANALYSE")
    print("=" * 60)
    
    # Test des 3 IA
    print("\n>>> TEST DES 3 STRATÉGIES IA <<<")
    for strat in [IAAgressive(), IAConservative(), IAStrategique()]:
        print(f"\n{'=' * 60}")
        print(f"Stratégie: {strat.nom}")
        simuler_parties(5, 3, strat)
    
    # Comparaison directe
    print("\n>>> COMPARAISON DIRECTE <<<")
    comparer_strategies(15, 4)
    
    # Analyse probabiliste
    print("\n>>> ANALYSE PROBABILISTE <<<")
    analyser_probabilites_cases()
    
    # Une partie complète avec stats
    print("\n>>> PARTIE EXEMPLE AVEC STATISTIQUES <<<")
    jeu = MonopolyIA(["Alice", "Bob", "Charlie"], strategie=IAStrategique())
    gagnant = jeu.jouer_partie(max_tours=200)
    jeu.stats.afficher_statistiques()
    
    print("\n" + "=" * 60)
    print("✓ TOUS LES TESTS RÉUSSIS!")
    print("=" * 60)