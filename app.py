from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import quote
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

# Set up Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Selenium WebDriver setup
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run headless to work better on servers/environments without GUI
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Lock to prevent threading issues with WebDriver
lock = threading.Lock()

def fetch_book_data(book_name):
    book = {"name": book_name, "author": "", "image": "", "description": ""}
    search_url = f"https://www.e-vrit.co.il/Search/{quote(book_name)}"
    
    try:
        with lock:
            # Use Selenium to request the page
            driver.get(search_url)
            
            # Wait for the desired content to load (e.g., a product-item container)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-list .product-item"))
            )
            
            # Extract page source once the content is loaded
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # Locate the product container where all relevant information is available
            product_container = soup.select_one(".product-list .product-item")
            if product_container:
                # Extract image URL
                image_element = product_container.select_one(".product-image img")
                if image_element:
                    image_url = image_element["src"]
                    book["image"] = image_url
                else:
                    book["image"] = "Image not available"

                # Extract author
                author_element = product_container.select_one(".product-inner-data.link-list a")
                book["author"] = author_element.text.strip() if author_element else "Author not available"
                
                # Extract description
                description_element = soup.select_one(".product-desc.tab-content__single-tab.tab-content__about-book.highlight__done")
                book["description"] = description_element.text.strip() if description_element else "Description not available"

    except Exception as e:
        book["error"] = f"Could not fetch details: {str(e)}"
    
    return book

@app.route('/api/book', methods=['GET'])
def get_book():
    book_name = request.args.get('name')
    if not book_name:
        return jsonify({"error": "No book name provided"}), 400
    
    # Fetch the book data
    book_data = fetch_book_data(book_name)
    # Return the book data as JSON
    return jsonify(book_data)

@app.route('/health')
def health_check():
    return "Server is up and running!", 200

# Simple test endpoint to confirm server is working
@app.route('/api/test', methods=['GET'])
def test_endpoint():
    name = request.args.get('name', 'World')
    return jsonify({"message": f"Hello, {name}!"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

driver.quit()  # Close the browser when done
