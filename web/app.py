from flask import Flask, render_template
import pymysql

app = Flask(__name__)

# Configuration de la base de données
DB_CONFIG = {
    'host': 'db',  # Nom du service MySQL dans docker-compose.yml
    'user': 'root',
    'password': 'password',
    'database': 'scrapy_db',
    'charset': 'utf8mb4'
}

@app.route('/')
def home():
    # Connexion à la base de données
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Récupérer tous les produits
    cursor.execute("""
        SELECT reference, name, price, url
        FROM products
        ORDER BY reference, price ASC
    """)
    products = cursor.fetchall()

    # Organiser les données par référence
    products_grouped = {}
    for product in products:
        ref = product['reference']
        if ref not in products_grouped:
            products_grouped[ref] = []
        products_grouped[ref].append(product)

    connection.close()

    return render_template('index.html', products_grouped=products_grouped)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
