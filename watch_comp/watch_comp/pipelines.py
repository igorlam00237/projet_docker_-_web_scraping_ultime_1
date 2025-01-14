# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import re

# Export JSON
import json

# Export SQL DB
import pymysql
from scrapy.exceptions import DropItem


class WatchCompPipeline:
    def process_item(self, item, spider):

        if 'price' in item:
            price_str = str(item['price'])
            cleaned_price = re.sub(r'[^\d,\.]', '', price_str)
            cleaned_price = cleaned_price.replace(',', '.')

            try:
                item['price'] = float(cleaned_price)

            except:
                item['price'] = None

        # Nettoyage de la référence
        
        if 'ref' in item:
            cleaned_ref = item['ref'].strip()  # Retirer les espaces autour
            cleaned_ref = re.sub(r'\s+', '', cleaned_ref)  # Retirer les espaces internes
            item['ref'] = cleaned_ref

        return item

# Export JSON
class JsonExportPipeline:

    def open_spider(self, spider):
        self.file = open(f"{spider.name}_output.json", 'w')
        self.file.write('[')
        self.first_item = True

    def close_spider(self, spider):
        self.file.write(']')  # Fin du tableau JSON
        self.file.close()

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(',')  # Ajouter une virgule entre les objets JSON
        self.first_item = False
        line = json.dumps(dict(item), ensure_ascii=False)
        self.file.write(line)
        return item

# Export MySQL
class MySQLPipeline:
    def open_spider(self, spider):
        # Connexion à la base de données
        self.connection = pymysql.connect(
            host='127.0.0.1',  # Adresse de l'hôte MySQL
            port=3307,         # Port exposé dans docker-compose.yml
            # host='db',  # Nom du conteneur Docker pour la base de données
            user='root',
            password='password',
            database='scrapy_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        # Fermer la connexion
        self.connection.close()

    def process_item(self, item, spider):
        # Insérer les données dans la base de données
        try:
            self.cursor.execute("""
                INSERT INTO products (name, price, url, reference) VALUES (%s, %s, %s, %s)
            """, (item['name'], item['price'], item['url'], item['ref']))
            self.connection.commit()
        except Exception as e:
            spider.logger.error(f"Erreur lors de l'insertion : {e}")
            raise DropItem(f"Erreur avec l'item {item}")
        return item