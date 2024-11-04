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
import logging
import os

# Set up Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)

# Lock to prevent threading issues with WebDriver
lock = threading.Lock()

def fetch_book_data(book_name):
    book = {"name": book_name, "author": "", "image": "", "description": ""}
    search_url = f"https://www.e-vrit.co.il/Search/{quote(book_name)}"
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless to work better on servers/environments without GUI
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Explicitly set the path to the Chrome binary
    options.binary_location = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")

    driver = None  # Initialize driver to None to handle exceptions

    try:
        # Use ChromeDriverManager to install and manage the ChromeDriver version
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

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
        app.logger.error(f"Error fetching book details for {book_name}: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()  # Ensure the driver quits after processing
            except Exception as e:
                app.logger.error(f"Driver could not be closed properly: {str(e)}")
    
    return book

# API endpoint to fetch book data
@app.route('/api/book', methods=['GET'])
def get_book_data():
    # Get the book name from the request arguments
    book_name = request.args.get('book_name')
    
    if not book_name:
        return jsonify({"error": "book_name parameter is required"}), 400
    
    # Fetch the book data
    book_data = fetch_book_data(book_name)
    
    return jsonify(book_data)

# Simple test endpoint to confirm server is working
@app.route('/api/test', methods=['GET'])
def test_endpoint():
    name = request.args.get('name', 'World')
    return jsonify({"message": f"Hello, {name}!"})

if __name__ == '__main__':
    app.run(debug=True)
