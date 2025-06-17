-- Création de la base
CREATE DATABASE IF NOT EXISTS covoiturage_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE covoiturage_app;

-- Table utilisateurs (comptes & profils)
CREATE TABLE utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    telephone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(255) NOT NULL,
    role ENUM('conducteur', 'passager') DEFAULT 'passager',
    photo_profil VARCHAR(255),
    point_depart_habituel VARCHAR(255),
    horaire_depart_habituel TIME,
    horaire_arrivee_habituel TIME,
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vehicule_marque VARCHAR(100),
    vehicule_modele VARCHAR(100),
    vehicule_places INT CHECK (vehicule_places >= 0)

    ALTER TABLE utilisateurs ADD COLUMN dernier_sos TIMESTAMP NULL;
CREATE TABLE sos_alertes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    latitude DOUBLE,
    longitude DOUBLE,
    date_alerte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);

);

-- Table trajets (offres et demandes)
CREATE TABLE trajets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    type_trajet ENUM('offre', 'demande') NOT NULL,
    point_depart VARCHAR(255) NOT NULL,
    point_arrivee VARCHAR(255) NOT NULL,
    horaire_depart DATETIME NOT NULL,
    places_disponibles INT DEFAULT 0 CHECK (places_disponibles >= 0),
    date_publication TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);
-- Table trajets_reccurents
CREATE TABLE trajets_recurrents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    jour_semaine ENUM('lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche'),
    point_depart VARCHAR(255),
    point_arrivee VARCHAR(255),
    horaire_depart TIME,
    places_disponibles INT,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);
-- Table recompenses
CREATE TABLE recompenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    points INT DEFAULT 0,
    niveau ENUM('Bronze', 'Argent', 'Or', 'Platine') DEFAULT 'Bronze',
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);

-- Table correspondances
CREATE TABLE correspondances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trajet_conducteur_id INT NOT NULL,
    trajet_passager_id INT NOT NULL,
    statut ENUM('propose', 'accepté', 'refusé') DEFAULT 'propose',
    date_matching TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trajet_conducteur_id) REFERENCES trajets(id) ON DELETE CASCADE,
    FOREIGN KEY (trajet_passager_id) REFERENCES trajets(id) ON DELETE CASCADE
);

-- Table conversations
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table association utilisateurs / conversations
CREATE TABLE conversation_utilisateurs (
    conversation_id INT NOT NULL,
    utilisateur_id INT NOT NULL,
    PRIMARY KEY (conversation_id, utilisateur_id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);

-- Table messages
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    expediteur_id INT NOT NULL,
    contenu TEXT NOT NULL,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (expediteur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);
-- Table evaluations
CREATE TABLE evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    auteur_id INT NOT NULL,
    cible_id INT NOT NULL,
    note TINYINT CHECK (note BETWEEN 1 AND 5),
    commentaire TEXT,
    date_evaluation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (auteur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (cible_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);
-- Table notifications
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    lue BOOLEAN DEFAULT FALSE,
    date_notification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
);

-- Insertion d'exemples dans utilisateurs
INSERT INTO utilisateurs (id, nom, prenom, telephone, email, mot_de_passe, role, photo_profil, point_depart_habituel, horaire_depart_habituel, horaire_arrivee_habituel, vehicule_marque, vehicule_modele, vehicule_places)
VALUES
(1, 'Dupont', 'Jean', '0600000001', 'jean.dupont@example.com', 'motdepasse123', 'conducteur', NULL, 'Kpota, ', '08:00:00', '09:00:00', 'Peugeot', '208', 3),
(2, 'Martin', 'Claire', '0600000002', 'claire.martin@example.com', 'motdepasse456', 'passager', NULL, 'Bidossessi, ', '08:15:00', '09:15:00', NULL, NULL, NULL);

-- Insertion d'exemples dans trajets
INSERT INTO trajets (id, utilisateur_id, type_trajet, point_depart, point_arrivee, horaire_depart, places_disponibles)
VALUES
(1, 1, 'offre', 'Kpota, Calavi', 'Campus, ', '2025-06-12 08:00:00', 3),
(2, 2, 'demande', 'Bidossessi, Calavi', 'Campus, ', '2025-06-12 08:15:00', 0);

-- Insertion d'une correspondance
INSERT INTO correspondances (id, trajet_conducteur_id, trajet_passager_id, statut)-
VALUES (1, 1, 2, 'propose');

-- Insertion d'une conversation
INSERT INTO conversations (id, date_creation)
VALUES (1, NOW());

-- Association des utilisateurs à la conversation
INSERT INTO conversation_utilisateurs (conversation_id, utilisateur_id)
VALUES (1, 1), (1, 2);

-- Insertion de messages
INSERT INTO messages (id, conversation_id, expediteur_id, contenu)
VALUES
(1, 1, 1, 'Bonjour, je propose un covoiturage demain matin à 8h.'),
(2, 1, 2, 'Bonjour, je suis intéressée, merci !');

-- Insertion de notifications
INSERT INTO notifications (id, utilisateur_id, message)
VALUES
(1, 2, 'Vous avez reçu un nouveau message dans la conversation #1'),
(2, 1, 'Votre offre a reçu une demande de correspondance.');
