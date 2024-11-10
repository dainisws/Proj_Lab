import threading
import time
from bs4 import BeautifulSoup
from models import Food
import random
from urllib.request import urlopen
from selenium import webdriver
import yaml # pip install pyyaml
import re
import traceback

with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

def write(store, link, name, mainCategory, lastCategory, info, amount, pricePerKg, calories, protein, fat, carbs):
    with app.app_context():
        food = Food(store, link, name, mainCategory, lastCategory, info, amount, pricePerKg, calories, protein, fat, carbs)
        db.session.add(food)
        db.session.commit()

def updatePrice(link, pricePerKg):
    with app.app_context():
        db.session.query(Food).filter(Food.link == link).update({Food.pricePerKg: pricePerKg})
        db.session.commit()
    

def scrapeBarbora():
    print("Scraping Barbora...")

def scrapeRimi():
    print("Scraping Rimi...")
    browser = webdriver.Firefox(executable_path=config["scraper"]["geckodriver_path"]) # This might not work in a production environment

    URLS = [
        "https://www.rimi.lv/e-veikals/lv/produkti/gatavots-rimi/c/SH-17",
        "https://www.rimi.lv/e-veikals/lv/produkti/augli-un-darzeni/c/SH-2",
        "https://www.rimi.lv/e-veikals/lv/produkti/gala-zivis-un-gatava-kulinarija/svaiga-gala/c/SH-6-15",
        "https://www.rimi.lv/e-veikals/lv/produkti/veganiem-un-vegetariesiem/c/SH-16",
        "https://www.rimi.lv/e-veikals/lv/produkti/piena-produkti-un-olas/c/SH-11",
        "https://www.rimi.lv/e-veikals/lv/produkti/maize-un-konditoreja/c/SH-7",
        "https://www.rimi.lv/e-veikals/lv/produkti/saldetie-edieni/c/SH-12",
        "https://www.rimi.lv/e-veikals/lv/produkti/iepakota-partika/c/SH-4",
        "https://www.rimi.lv/e-veikals/lv/produkti/saldumi-un-uzkodas/c/SH-13",
        "https://www.rimi.lv/e-veikals/lv/produkti/dzerieni/c/SH-5"
    ]

    mainUrl = "https://www.rimi.lv"

    for url in URLS:
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, "html.parser")
        while len(soup.findAll('li', class_='pagination__item -chevron', attrs={"aria-disabled": True, "aria-label": "Next &amp;raquo;"})) == 0:
            
            # find all products within a page that aren't in the database and update price of those that are
            productUrls = []
            for productCard in soup.findAll('li', class_='product-grid__item'):
                if len(productCard.findAll('button', class_='-secondary')) == 0:
                    fullUrl = mainUrl + productCard.find('a', class_='js-gtm-eec-product-click')['href']
                    with app.app_context():
                        if (db.session.query(db.exists().where(Food.link == fullUrl)).scalar()):
                            val = re.search(r'\d+\,\d+|\d+', productCard.find("p", class_="card__price-per").get_text())
                            price = float(val.group().replace(",", "."))
                            updatePrice(fullUrl, price)
                        else:
                            productUrls.append(fullUrl)

            # loop all found products
            for productUrl in productUrls:
                time.sleep(random.uniform(4, 7))
                browser.get(productUrl)
                time.sleep(1)
                soup2 = BeautifulSoup(browser.page_source, "html.parser")

                # get price
                try:
                    val = re.search(r'\d+\,\d+|\d+', soup2.find('p', class_='price-per').get_text())
                    price = float(val.group().replace(",", "."))
                except:
                    #traceback.print_exc()
                    continue

                # get categories     section-header__container     get all 'a' and then first and last 

                try:
                    categories = soup2.find("div", "section-header__container").findAll("a")
                    main_category = categories[0].get_text()
                    last_category = categories[-1].get_text()
                except:
                    pass

                # get name          product__main-info         get div and then get 'h1' class "name"

                try:
                    name = soup2.find("div", "product__main-info").find("h1", "name").get_text()
                except:
                    pass

                # get info    product__list-wrapper    product__list-wrapper -simple

                try:
                    info = " ".join(p.get_text() for div in soup2.findAll("div", "product__list-wrapper") for p in div.find_all("p"))
                except:
                    pass


                # get nutritional information
                try:
                    tds = soup2.find('div', class_='product__table').findAll('td')
                    if (tds[2].get_text().replace(" ", "").replace("\n", "") != "tauki" or tds[6].get_text().replace(" ", "").replace("\n", "") != "ogļhidrāti" or tds[10].get_text().replace(" ", "").replace("\n", "") != "olbaltumvielas"):
                        #print("Invalid nutritional information: " + tds.get_text()) # write here
                        write("Rimi", productUrl, name, main_category, last_category, info, 1, price, None, None, None, None)
                        continue
                    fat = float(tds[3].get_text().replace(" ", "").replace("g", ""))
                    carbs = float(tds[7].get_text().replace(" ", "").replace("g", ""))
                    protein = float(tds[11].get_text().replace(" ", "").replace("g", ""))
                    calories = fat*9.3+carbs*4.1+protein*4.1
                    write("Rimi", productUrl, name, main_category, last_category, info, 1, price, calories, protein, fat, carbs)
                except:
                    write("Rimi", productUrl, name, main_category, last_category, info, 1, price, None, None, None, None)

            time.sleep(random.uniform(4, 7))
            try:
                url = soup.find('a', attrs={"aria-label": "Next &raquo;"})['href'] # get url to the next page
            except:
                break
            browser.get(mainUrl + url)
            time.sleep(1)
            soup = BeautifulSoup(browser.page_source, "html.parser")
        time.sleep(random.uniform(4, 7))
    browser.quit()


def task():
    timestamp_ms = int(time.time() * 1000)
    if (timestamp_ms > config["scraper"]["last_scrape"] + 86400):
        print("Scraping foods...")
        #scrapeBarbora()
        scrapeRimi()

        # update last scrape time

        config["scraper"]["last_scrape"] = timestamp_ms
        with open("config.yml", "w") as file:
            yaml.dump(config, file)

class FoodScraper():

    def __init__(self, database, application):
        global db, app
        db = database
        app = application

    def schedule_task():
        while True:
            task_thread = threading.Thread(target=task)
            task_thread.start()
            time.sleep(86400)

    if (config["scraper"]["use"]):
        scheduler_thread = threading.Thread(target=schedule_task)
        scheduler_thread.daemon = True
        scheduler_thread.start()