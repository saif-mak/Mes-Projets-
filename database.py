import mysql.connector

def insert_into_mysql(data):
    """
    Insère les données scrappées dans la base de données MySQL.
    """
    try:
        # Connexion à la base de données
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="mamadou", 
            database="scraping_db"
        )
        cursor = conn.cursor()

        # Requête SQL d'insertion
        sql = """
        INSERT INTO produits (marque, nom_produit, lien, prix, rating, infos_livraison) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        # Insérer les données
        cursor.executemany(sql, [(p["Marque"], p["Nom du produit"], p["Lien"], p["Prix"], p["Rating (nombre d'avis)"], p["Infos de livraison"]) for p in data])

        # Commit et fermeture
        conn.commit()
        print("✅ Données insérées avec succès dans MySQL.")

    except mysql.connector.Error as e:
        print(f"❌ Erreur MySQL : {e}")

    finally:
        cursor.close()
        conn.close()
