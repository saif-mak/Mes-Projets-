import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Connexion à MySQL pour récupérer les données nettoyées
def load_data():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mamadou",
            database="scraping_db"
        )
        query = "SELECT * FROM produits_clean"  # Je récupère uniquement les données nettoyées
        df = pd.read_sql(query, conn)
        conn.close()
        print("✅ Données chargées depuis MySQL.")
        return df
    except mysql.connector.Error as e:
        print(f"❌ Erreur MySQL : {e}")
        return None


# 📌 1️⃣ Je fais une analyse rapide des données pour voir si tout est en ordre
def analyze_data(df):
    print("🔎 Aperçu des données :")
    print(df.head())  # Quelques lignes pour vérifier
    print("\n📌 Infos générales :")
    print(df.info())  # Vérifier les types de données
    print("\n🔢 Statistiques descriptives :")
    print(df.describe())  # Avoir des stats globales

    print("\n❗️ Valeurs manquantes :")
    print(df.isnull().sum())  # Je veux voir s’il y a des données vides

    print("\n🔄 Nombre de doublons :", df.duplicated().sum())  # Vérifier les doublons


# 📌 2️⃣ Distribution des prix des produits avec annotations pour les produits les plus chers
def plot_price_distribution(df):
    plt.figure(figsize=(10, 6))
    sns.histplot(df["prix"], bins=20, kde=True, color="blue")
    plt.title("📈 Distribution des prix des produits (Marques incluses)")
    plt.xlabel("Prix (€)")
    plt.ylabel("Nombre de produits")

    # J'affiche les 5 produits les plus chers pour voir les extrêmes
    top_expensive = df.nlargest(5, "prix")[["marque", "nom_produit", "prix"]]
    for i, row in enumerate(top_expensive.iterrows()):
        index, row = row
        plt.annotate(f"{row['marque']} ({row['prix']}€)", 
                     xy=(row["prix"], 5),  # Position de l'annotation
                     xytext=(row["prix"] - 10, 20 + i * 10),  # Décalage progressif pour éviter la superposition
                     arrowprops=dict(arrowstyle="->", color="black"), fontsize=10, color="black")

    plt.grid(True)
    plt.show()


# 📌 3️⃣ Voir quelles marques proposent le plus de produits (Top 10)
def plot_products_per_brand(df):
    plt.figure(figsize=(10, 6))
    brand_counts = df["marque"].value_counts().head(10)
    sns.barplot(x=brand_counts.index, y=brand_counts.values, palette="viridis")
    plt.xticks(rotation=45)
    plt.title("Nombre de produits par marque (Top 10)")
    plt.xlabel("Marque")
    plt.ylabel("Nombre de produits")
    plt.show()


# 📌 4️⃣ Voir comment les prix varient en fonction des marques (boxplot)
def plot_price_boxplot(df):
    plt.figure(figsize=(12, 6))
    top_brands = df["marque"].value_counts().index[:10]  
    df_top_brands = df[df["marque"].isin(top_brands)]
    sns.boxplot(x="marque", y="prix", data=df_top_brands, palette="coolwarm")
    plt.xticks(rotation=45)
    plt.title("Répartition des prix par marque (Top 10)")
    plt.xlabel("Marque")
    plt.ylabel("Prix (€)")
    plt.show()


# 📌 5️⃣ Voir la répartition du nombre d’avis sur les produits
def plot_rating_distribution(df):
    plt.figure(figsize=(8, 5))
    sns.histplot(df["rating"].astype(float), bins=15, kde=True, color="green")
    plt.title("📊 Distribution des avis (nombre d'évaluations)")
    plt.xlabel("Nombre d'avis")
    plt.ylabel("Nombre de produits")
    plt.grid(True)
    plt.show()


# 📌 6️⃣ Voir si le prix a un impact sur le nombre d’avis
def plot_price_vs_rating(df):
    plt.figure(figsize=(10, 6))
    df["rating"] = df["rating"].astype(float)
    
    sns.scatterplot(x=df["prix"], y=df["rating"], alpha=0.5, color="red")
    
    # J'affiche les 3 produits les plus évalués pour voir les tendances
    top_rated = df.nlargest(3, "rating")[["marque", "nom_produit", "prix", "rating"]]
    for i, row in top_rated.iterrows():
        plt.annotate(f"{row['marque']} ({int(row['rating'])} avis)", 
                     xy=(row["prix"], row["rating"]), 
                     xytext=(row["prix"]+5, row["rating"]+500),
                     arrowprops=dict(arrowstyle="->", color="black"))

    plt.title("📊 Corrélation entre le prix et le nombre d'avis")
    plt.xlabel("Prix (€)")
    plt.ylabel("Nombre d'avis")
    plt.grid(True)
    plt.show()


# 📌 7️⃣ Voir comment se répartissent les méthodes de livraison
def plot_shipping_distribution(df):
    plt.figure(figsize=(8, 8))
    shipping_counts = df["infos_livraison"].value_counts()
    colors = sns.color_palette("pastel")

    plt.pie(shipping_counts, labels=shipping_counts.index, autopct="%1.1f%%", 
            colors=colors, wedgeprops={"edgecolor": "black"})

    plt.title("🚚 Répartition des types de livraison (en %)")
    plt.legend(title="Méthode de livraison", loc="best", bbox_to_anchor=(1, 1))
    plt.show()


# ✅ Exécuter toutes les analyses et visualisations
def main():
    df = load_data()
    
    if df is not None:
        analyze_data(df)  

        # 📊 Générer les graphiques améliorés
        plot_price_distribution(df)  
        plot_products_per_brand(df)
        plot_price_boxplot(df)
        plot_rating_distribution(df)
        plot_price_vs_rating(df)  
        plot_shipping_distribution(df) 


if __name__ == "__main__":
    main()
