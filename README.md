# 🎲 Python Monopoly

Un jeu de Monopoly complet en Python, développé dans le cadre d'un TP pédagogique sur la programmation orientée objet.

## 📋 Description

Ce projet implémente une simulation du jeu Monopoly avec :
- Un plateau de 40 cases (version française)
- Gestion des propriétés, gares et compagnies
- Système de construction (maisons et hôtels)
- Cartes Chance et Caisse de Communauté
- Système de prison
- 3 stratégies d'Intelligence Artificielle
- Statistiques de partie

## 🚀 Lancement rapide

### Lancer une partie simple
```python
from monopoly import Monopoly

jeu = Monopoly(['Alice', 'Bob', 'Charlie'])
jeu.jouer_partie(max_tours=100)
```

### Lancer avec une IA et des statistiques
```python
from monopoly import MonopolyIA, IAStrategique

jeu = MonopolyIA(['Alice', 'Bob', 'Charlie'], strategie=IAStrategique())
gagnant = jeu.jouer_partie(max_tours=150)
jeu.stats.afficher_statistiques()
```

### Lancer tous les tests
```bash
python3 monopoly.py
```

## 🤖 Stratégies IA disponibles

| Stratégie | Description |
|-----------|-------------|
| `IAAgressive()` | Achète toutes les propriétés si elle a l'argent |
| `IAConservative()` | Achète seulement si argent ≥ 2× le prix |
| `IAStrategique()` | Privilégie les quartiers complets et optimise la construction |

## 🏗️ Structure du projet

```
python-monopoly/
├── monopoly.py          # Code principal du jeu
├── README.md            # Ce fichier
└── monopoly/            # Fichiers SQL (optionnel)
    ├── monopoly.sqlproj
    └── plato.sql
```

## 📚 Séances du TP

### Séance 1 : Fondations
- Création du plateau (40 cases)
- Déplacement des joueurs avec dés
- Passage par la case Départ (+200€)
- Achat de propriétés
- Paiement des loyers

### Séance 2 : Mécanique de jeu
- Cases spéciales (Départ, Prison, Taxes, etc.)
- Construction de maisons et hôtels
- Calcul des loyers avec bonus
- Gares (loyer progressif selon le nombre)
- Compagnies (loyer basé sur les dés)

### Séance 3 : Jouabilité complète
- Système de prison (3 façons d'entrer, 3 façons de sortir)
- Cartes Chance (10 cartes)
- Cartes Caisse de Communauté (10 cartes)
- Gestion des faillites
- Boucle de jeu complète

### Séance 4 : IA et Analyse
- 3 stratégies d'IA avec héritage
- Système de statistiques
- Analyse des cases les plus visitées
- Analyse des propriétés les plus rentables

## 🎮 Classes principales

| Classe | Description |
|--------|-------------|
| `Case` | Classe de base pour toutes les cases |
| `Propriete` | Case achetable avec loyer |
| `Gare` | Propriété spéciale (loyer selon nb de gares) |
| `Compagnie` | Propriété spéciale (loyer selon dés) |
| `CaseSpeciale` | Départ, Prison, Taxes, Chance, etc. |
| `Joueur` | Gère argent, position, propriétés |
| `Plateau` | Contient les 40 cases |
| `Monopoly` | Moteur de jeu principal |
| `MonopolyIA` | Version avec IA et statistiques |
| `StrategieIA` | Classe de base pour les IA |
| `StatistiquesPartie` | Collecte les stats de jeu |

## 📊 Exemple de statistiques

```
============================================================
STATISTIQUES DE LA PARTIE
============================================================

Durée: 100 tours
Gagnant: Bob (1332€)

Top 5 des cases les plus visitées:
  Position 15: 33 passages
  Position 20: 33 passages
  Position 8: 29 passages

Top 5 des propriétés les plus rentables:
  Gare Saint-Lazare: 1000€ de loyers
  Gare du Nord: 700€ de loyers
  Avenue des Champs-Élysées: 560€ de loyers
```

## ⚙️ Configuration base de données (optionnel)

Le jeu peut charger les propriétés depuis une base MySQL. Sans base de données, un plateau par défaut est créé automatiquement.

```python
# Configuration dans la classe DB
host="localhost"
port=1433
user="SA"
password="Azerty*!*"
database="Toto"
```

## 📝 Licence

Projet pédagogique - Usage éducatif

## 👤 Auteur

LefevreGregoire
