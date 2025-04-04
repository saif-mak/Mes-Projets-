from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import mysql.connector
from database import insert_into_mysql


def close_cookie_banner(driver):
    """
    Attend que la bannière de cookies s'affiche et clique sur le bouton "Continuer sans accepter".
    """
    try:
        bouton_cookie = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Continuer sans accepter')]"))
        )
        bouton_cookie.click()
        print("✅ Bannière cookies fermée.")
    except Exception as e:
        print("⚠ Impossible de fermer la bannière de cookies :", e)


def scrape_products(driver):
    """
    Extrait les informations de chaque produit affiché sur la page.
    """
    try:
        product_containers = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "dpb-holder"))
        )
    except Exception as e:
        print("⚠ Impossible de trouver les produits :", e)
        return []

    data = []
    for container in product_containers:
        try:
            product_link = container.find_element(By.CSS_SELECTOR, "a.dpb-product-model-link").get_attribute("href")
        except:
            product_link = ""

        try:
            product_title_element = container.find_element(By.CSS_SELECTOR, "a.product-title")
            brand = product_title_element.find_element(By.TAG_NAME, "strong").text.strip()
            product_name = product_title_element.find_element(By.TAG_NAME, "h2").text.strip()
        except:
            brand, product_name = "", ""

        try:
            price = container.find_element(By.CSS_SELECTOR, ".price-presentation .vtmn-price").text.strip()
        except:
            price = ""

        try:
            rating = container.find_element(By.CSS_SELECTOR, ".vtmn-rating").get_attribute("title")
        except:
            rating = "0"

        try:
            shipping = container.find_element(By.CSS_SELECTOR, ".dpb-leadtime").text.strip()
        except:
            shipping = "non spécifié"

        data.append({
            "Marque": brand,
            "Nom du produit": product_name,
            "Lien": product_link,
            "Prix": price,
            "Rating (nombre d'avis)": rating,
            "Infos de livraison": shipping
        })
    
    return data


def scrape_all_pages(driver, num_pages=12, page_size=40):
    """
    Fonction pour scraper toutes les pages en fonction du nombre total de pages et du nombre d'articles par page.
    """
    all_data = []
    for page_num in range(num_pages):
        try:
            # Calculer le paramètre 'from' pour naviguer dans les pages
            from_param = page_num * page_size
            url = f"https://www.decathlon.fr/nouveautes/nouveautes-homme?from={from_param}&size={page_size}"
            driver.get(url)
            time.sleep(3)  # Attendre que la page charge

            # Fermer la bannière cookies si présente
            close_cookie_banner(driver)
            time.sleep(2)

            # Scraper les produits de cette page
            products_data = scrape_products(driver)
            if products_data:
                all_data.extend(products_data)  # Ajouter les résultats de chaque page
            print(f"✅ Page {page_num + 1} scrappée ({len(products_data)} produits).")
        except Exception as e:
            print(f"❌ Erreur lors du scraping de la page {page_num + 1}: {e}")

    return all_data


def save_to_csv(data, filename="products.csv"):
    """
    Sauvegarde les données scrappées dans un fichier CSV avec un bon encodage.
    """
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding="utf-8-sig", sep=";") 
        print(f"📂 Données sauvegardées dans {filename}")
    except Exception as e:
        print("❌ Erreur lors de la sauvegarde dans le CSV :", e)


def main():
    # Instanciation du WebDriver Edge
    options = webdriver.EdgeOptions()
    options.add_argument("start-maximized")
    driver = webdriver.Edge(options=options)

    # Scraper tous les produits de toutes les pages
    print("🔄 Démarrage du scraping multi-pages...")
    products_data = scrape_all_pages(driver, num_pages=12, page_size=40)  # On récupère toutes les pages

    if products_data:
        df = pd.DataFrame(products_data)
        print(df)

        # Sauvegarder en CSV
        save_to_csv(products_data)

        # 🔥 Insérer les données dans MySQL
        insert_into_mysql(products_data)

    else:
        print("❌ Aucun produit trouvé.")

    # Fermer le navigateur
    time.sleep(5)
    driver.quit()


if __name__ == "__main__":
    main()
