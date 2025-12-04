CREATE TABLE types_proprietes (
    id INTEGER PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL
);

INSERT INTO types_proprietes (id, code, libelle) VALUES
(1, 'propriete', 'Propriété'),
(2, 'gare', 'Gare'),
(3, 'compagnie', 'Compagnie');

-- ============================================
-- Table des cases du plateau
-- ============================================
CREATE TABLE proprietes (
    position INTEGER PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    type_propriete_id INTEGER NOT NULL,
    -- Propriétés (NULL pour les cases spéciales)
    prix_achat INTEGER,
    loyer_base INTEGER,
    couleur VARCHAR(50),
    prix_maison INTEGER,
    
    FOREIGN KEY (type_propriete_id) REFERENCES types_proprietes(id)
);

-- ============================================
-- Insertion des 40 cases du plateau français
-- ============================================

-- Positions 1-9
INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(1, 'Boulevard de Belleville', 1, 60, 2, 'marron', 50);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(3, 'Rue Lecourbe', 1, 60, 4, 'marron', 50);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(5, 'Gare Montparnasse', 2, 200, 25, 'gare', 0);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(6, 'Rue de Vaugirard', 1, 100, 6, 'bleu_clair', 50);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(8, 'Rue de Courcelles', 1, 100, 6, 'bleu_clair', 50),
(9, 'Avenue de la République', 1, 120, 8, 'bleu_clair', 50);

-- Positions 11-19
INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(11, 'Boulevard de la Villette', 1, 140, 10, 'rose', 100);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(12, 'Compagnie d''Électricité', 3, 150, 0, 'compagnie', 0);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(13, 'Avenue de Neuilly', 1, 140, 10, 'rose', 100),
(14, 'Rue de Paradis', 1, 160, 12, 'rose', 100);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(15, 'Gare de Lyon', 2, 200, 25, 'gare', 0);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(16, 'Avenue Mozart', 1, 180, 14, 'orange', 100);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(18, 'Boulevard Saint-Michel', 1, 180, 14, 'orange', 100),
(19, 'Place Pigalle', 1, 200, 16, 'orange', 100);

-- Positions 21-29
INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(21, 'Avenue Matignon', 1, 220, 18, 'rouge', 150);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(23, 'Boulevard Malesherbes', 1, 220, 18, 'rouge', 150),
(24, 'Avenue Henri-Martin', 1, 240, 20, 'rouge', 150);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(25, 'Gare du Nord', 2, 200, 25, 'gare', 0);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(26, 'Faubourg Saint-Honoré', 1, 260, 22, 'jaune', 150),
(27, 'Place de la Bourse', 1, 260, 22, 'jaune', 150);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(28, 'Compagnie des Eaux', 3, 150, 0, 'compagnie', 0);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(29, 'Rue La Fayette', 1, 280, 24, 'jaune', 150);

-- Positions 31-39
INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(31, 'Avenue de Breteuil', 1, 300, 26, 'vert', 200),
(32, 'Avenue Foch', 1, 300, 26, 'vert', 200);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(34, 'Boulevard des Capucines', 1, 320, 28, 'vert', 200);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(35, 'Gare Saint-Lazare', 2, 200, 25, 'gare', 0);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(37, 'Avenue des Champs-Élysées', 1, 350, 35, 'bleu_fonce', 200);

INSERT INTO proprietes (position, nom, type_propriete_id, prix_achat, loyer_base, couleur, prix_maison) VALUES
(39, 'Rue de la Paix', 1, 400, 50, 'bleu_fonce', 200);

