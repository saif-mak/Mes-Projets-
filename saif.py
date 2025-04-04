from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd


def close_cookie_banner(driver):
    """
    Attend que la bannière de cookies s'affiche et clique sur le bouton "Continuer sans accepter".
    """
    try:
        bouton_cookie = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Continuer sans accepter')]"))
        )
        bouton_cookie.click()
        print("Bannière cookies fermée.")
    except Exception as e:
        print("Impossible de fermer la bannière de cookies :", e)


def scrape_products(driver):
    """
    Extrait les informations de chaque produit affiché sur la page.
    Pour chaque produit, on récupère :
      - La marque,
      - Le nom du produit,
      - Le lien,
      - Le prix,
      - Le rating (nombre d'avis),
      - Les informations de livraison.
    """
    try:
        # On attend que tous les conteneurs produits soient chargés.
        product_containers = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "dpb-holder"))
        )
    except Exception as e:
        print("Impossible de trouver les produits :", e)
        return []

    data = []
    for container in product_containers:
        try:
            # Récupération du lien du produit
            product_link_element = container.find_element(By.CSS_SELECTOR, "a.dpb-product-model-link")
            product_link = product_link_element.get_attribute("href")
        except:
            product_link = ""

        try:
            # Extraction de la marque et du nom du produit
            product_title_element = container.find_element(By.CSS_SELECTOR, "a.product-title")
            brand = product_title_element.find_element(By.TAG_NAME, "strong").text.strip()
            product_name = product_title_element.find_element(By.TAG_NAME, "h2").text.strip()
        except:
            brand = ""
            product_name = ""

        try:
            # Extraction du prix
            price_element = container.find_element(By.CSS_SELECTOR, ".price-presentation .vtmn-price")
            price = price_element.text.strip()
        except:
            price = ""

        try:
            # Extraction du rating (exemple : contenu de l'attribut "title")
            rating_element = container.find_element(By.CSS_SELECTOR, ".vtmn-rating")
            rating = rating_element.get_attribute("title")
        except:
            rating = ""

        try:
            # Extraction des informations de livraison
            shipping_element = container.find_element(By.CSS_SELECTOR, ".dpb-leadtime")
            shipping = shipping_element.text.strip()
        except:
            shipping = ""

        data.append({
            "Marque": brand,
            "Nom du produit": product_name,
            "Lien": product_link,
            "Prix": price,
            "Rating (nombre d'avis)": rating,
            "Infos de livraison": shipping
        })
    return data


def save_to_csv(data, filename="products.csv"):
    """
    Sauvegarde la liste des produits dans un fichier CSV en utilisant pandas.
    """
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding="utf-8")
        print("Données sauvegardées dans", filename)
    except Exception as e:
        print("Erreur lors de la sauvegarde dans le CSV :", e)


def main():
    # Instanciation du WebDriver (assurez-vous que le driver Chrome est installé et accessible)
    driver = webdriver.Chrome()

    # Ouvrir la page des nouveautés pour homme sur Decathlon
    driver.get("https://www.decathlon.fr/nouveautes/nouveautes-homme")
    time.sleep(3)  # Attendre le chargement de la page

    # Fermer la bannière de cookies
    close_cookie_banner(driver)
    time.sleep(3)

    # Extraire les informations des produits
    products_data = scrape_products(driver)
    if products_data:
        # Afficher le DataFrame sous forme de tableau dans la console
        df = pd.DataFrame(products_data)
        print(df)
        # Sauvegarder dans un fichier CSV
        save_to_csv(products_data)
    else:
        print("Aucun produit trouvé.")

    # Attendre quelques secondes avant de fermer le navigateur
    time.sleep(5)
    driver.quit()


if __name__ == "__main__":
    main()
