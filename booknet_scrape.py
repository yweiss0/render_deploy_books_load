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

# Selenium WebDriver options setup
def get_driver():
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"  # Specify the location of Chrome binary
    options.add_argument('--headless')  # Run headless to work better on servers/environments without GUI
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Lock to prevent threading issues with WebDriver
lock = threading.Lock()

# Test array of books to search for
books = [
    {"name": "תחנת דמשק", "author": "", "image": "", "description": ""},
    {"name": "הרוזנת מטוסקנה", "author": "", "image": "", "description": ""},
    {"name": "תישאר קרוב", "author": "", "image": "", "description": ""},
    {"name": "כראמל 4", "author": "", "image": "", "description": ""},
]

def fetch_book_data(book_name):
    book = {"name": book_name, "author": "", "image": "", "description": "", "link": ""}
    search_url = f"https://www.booknet.co.il/%D7%97%D7%99%D7%A4%D7%95%D7%A9?q={quote(book_name)}"
    driver = get_driver()

    try:
        with lock:
            # Use Selenium to request the page
            driver.get(search_url)

            # Wait for the desired content to load (e.g., a book-item container)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".book-item"))
            )

            # Extract page source once the content is loaded
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # Locate the book container where all relevant information is available
            book_container = soup.select_one(".book-item")
            if book_container:
                # Extract author
                author_element = book_container.select_one(".book-below-title.product-author")
                book["author"] = author_element.text.strip() if author_element else "Author not available"

                # Extract link to the book
                link_element = book_container.select_one("a")
                if link_element:
                    book_link = link_element.get("href")
                    full_link = f"https://www.booknet.co.il{book_link}"
                    book["link"] = full_link

                    # Visit the book page to extract the description and image
                    driver.get(full_link)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "itemSummary"))
                    )
                    book_page_html = driver.page_source
                    book_soup = BeautifulSoup(book_page_html, "html.parser")

                    # Extract description from itemSummary div
                    description_element = book_soup.select_one("#itemSummary")
                    book["description"] = description_element.text.strip() if description_element else "Description not available"

                    # Extract image from big-thumb class
                    big_thumb_element = book_soup.select_one(".big-thumb")
                    if big_thumb_element:
                        image_element = big_thumb_element.select_one("img")
                        if image_element:
                            image_url = image_element.get("src")
                            book["image"] = f"https://www.booknet.co.il{image_url}"
                        else:
                            book["image"] = "Image not available"
                    else:
                        book["image"] = "Image not available"
                else:
                    book["link"] = "Link not available"

    except Exception as e:
        book["error"] = f"Could not fetch details: {str(e)}"
    finally:
        driver.quit()  # Ensure the driver is properly closed

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

@app.route('/api/books', methods=['GET'])
def get_books():
    results = []
    for book in books:
        book_data = fetch_book_data(book["name"])
        results.append(book_data)
    return jsonify(results)

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
