CREATE DATABASE IF NOT EXISTS scraping_db;

USE scraping_db;

CREATE TABLE IF NOT EXISTS produits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    marque VARCHAR(255),
    nom_produit VARCHAR(255),
    lien TEXT,
    prix VARCHAR(50),
    rating VARCHAR(50),
    infos_livraison VARCHAR(255)
);

SELECT * FROM produits;
describe produits; 

SELECT * FROM produits_clean ;

describe produits_clean;

