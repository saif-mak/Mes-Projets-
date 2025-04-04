import mysql.connector
import pandas as pd

# 📌 Connexion à MySQL et chargement des données brutes
def load_data_from_mysql():
    """
    Je récupère les données brutes depuis MySQL et les charge dans un DataFrame Pandas.
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mamadou",  # Mon mot de passe MySQL
            database="scraping_db"
        )

        # J'exécute une requête pour récupérer tous les produits
        query = "SELECT * FROM produits"
        df = pd.read_sql(query, conn)

        conn.close()
        print("✅ Données chargées depuis MySQL.")
        return df

    except mysql.connector.Error as e:
        print(f"❌ Erreur MySQL : {e}")
        return None


# 📌 Nettoyage des données pour les rendre exploitables
def clean_data(df):
    """
    Ici, je nettoie les données du DataFrame pour éviter les erreurs et les incohérences :
    - Suppression des doublons
    - Suppression des espaces inutiles
    - Conversion en minuscules pour standardiser
    - Nettoyage des prix en convertissant en float
    - Remplacement des valeurs nulles et vides dans rating et infos_livraison
    """
    print("🔄 Nettoyage des données en cours...")

    # Suppression des doublons (je me base sur le nom du produit)
    df.drop_duplicates(subset=["nom_produit"], inplace=True)

    # Je supprime les espaces inutiles et mets tout en minuscules pour normaliser
    df["marque"] = df["marque"].str.strip().str.lower()
    df["nom_produit"] = df["nom_produit"].str.strip().str.lower()

    # ⚠️ Correction : Remplacement des valeurs NULL ou vides avant de normaliser
    df["infos_livraison"] = df["infos_livraison"].fillna("").astype(str)  # Conversion en string obligatoire
    df["infos_livraison"] = df["infos_livraison"].replace("", "non spécifié")  # Je remplace les champs vides
    df["infos_livraison"] = df["infos_livraison"].str.strip()  # Nettoyage des espaces

    # Nettoyage des prix : suppression des symboles, conversion en float
    df["prix"] = df["prix"].str.replace("€", "").str.replace(",", ".").astype(float)

    # Je remplace les valeurs NULL ou vides dans `rating` par "0"
    df["rating"] = df["rating"].replace("", "0")  # Gestion des chaînes vides
    df["rating"] = df["rating"].fillna("0")  # Gestion des valeurs NULL

    print("✅ Nettoyage terminé.")
    return df


# 📌 Sauvegarde des données nettoyées (CSV + MySQL)
def save_cleaned_data(df, to_mysql=True):
    """
    J'enregistre les données propres dans un fichier CSV et, si nécessaire, dans MySQL.
    """
    df.to_csv("cleaned_products.csv", index=False, encoding="utf-8-sig", sep=";")
    print("📂 Données nettoyées sauvegardées en CSV.")

    if to_mysql:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mamadou",
                database="scraping_db"
            )
            cursor = conn.cursor()

            # Pour éviter d'accumuler de la donnée en double, je recrée une table propre
            cursor.execute("DROP TABLE IF EXISTS produits_clean;")
            cursor.execute("""
                CREATE TABLE produits_clean (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    marque VARCHAR(255),
                    nom_produit VARCHAR(255),
                    lien TEXT,
                    prix FLOAT,
                    rating VARCHAR(50) DEFAULT '0',
                    infos_livraison VARCHAR(255) DEFAULT 'non spécifié'
                )
            """)

            # Vérification : s'assurer que toutes les colonnes sont bien présentes
            cleaned_data = df[["marque", "nom_produit", "lien", "prix", "rating", "infos_livraison"]].values.tolist()

            # Insertion des données dans MySQL
            sql = """
            INSERT INTO produits_clean (marque, nom_produit, lien, prix, rating, infos_livraison)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(sql, cleaned_data)
            conn.commit()

            print("✅ Données nettoyées insérées dans MySQL (table `produits_clean`).")

        except mysql.connector.Error as e:
            print(f"❌ Erreur MySQL : {e}")

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()


# 📌 Exécution complète : Chargement → Nettoyage → Sauvegarde
def main():
    # Je récupère les données brutes depuis MySQL
    df = load_data_from_mysql()
    
    if df is not None:
        # Nettoyage en profondeur des données
        df_cleaned = clean_data(df)

        # Vérification rapide après nettoyage
        print(df_cleaned[df_cleaned["infos_livraison"] == "non spécifié"])  # Vérifier que les valeurs NULL sont bien remplacées
        print(df_cleaned[df_cleaned["rating"] == "0"])  # Vérifier que le rating est bien remplacé

        # Sauvegarde des données nettoyées
        save_cleaned_data(df_cleaned)


if __name__ == "__main__":
    main()
