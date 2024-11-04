
# Working booknet צומת ספרים
# import requests
# from bs4 import BeautifulSoup
# import os
# from urllib.parse import quote
# import urllib.request

# # Sample book names
# books = [
#     {"name": "תחנת דמשק", "author": "", "image": "", "description": ""},
#     {"name": "הרוזנת מטוסקנה", "author": "", "image": "", "description": ""},
#     {"name": "תישאר קרוב", "author": "", "image": "", "description": ""},
# ]

# # Directory to save images
# image_directory = "book_images"
# os.makedirs(image_directory, exist_ok=True)

# def fetch_books_data():
#     for book in books:
#         book_name = book["name"]
#         search_url = f"https://www.booknet.co.il/%D7%97%D7%99%D7%A4%D7%95%D7%A9?q={quote(book_name)}"

#         try:
#             # Request the search page
#             response = requests.get(search_url)
#             response.raise_for_status()
#             html = response.text

#             # Parse the HTML
#             soup = BeautifulSoup(html, "html.parser")

#             # Locate the product container where all relevant information is available
#             product_container = soup.select_one(".products.product-cube")
#             if product_container:
#                 # Extract image URL
#                 image_element = product_container.select_one(".productImage img")
#                 if image_element:
#                     image_url = "https://www.booknet.co.il" + image_element["data-original"]
#                     book["image"] = image_url
#                     # Save the image
#                     image_path = os.path.join(image_directory, f"{book_name}.jpg")
#                     urllib.request.urlretrieve(image_url, image_path)
#                     print(f"Image saved for {book_name} at {image_path}")
#                 else:
#                     book["image"] = "Image not available"

#                 # Extract author
#                 author_element = product_container.select_one(".book-below-title.product-author")
#                 book["author"] = author_element.text if author_element else "Author not available"

#                 # Print details
#                 print(f"Book Name: {book_name}")
#                 print(f"Author: {book['author']}")
#                 print(f"Image URL: {book['image']}")
#                 print("--------------------------------------------")

#         except requests.RequestException as e:
#             print(f"Could not fetch details for book: {book_name}", e)

# if __name__ == "__main__":
#     fetch_books_data()



# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# import os
# import urllib.request
# from urllib.parse import quote

# # Sample book names
# books = [
#     {"name": "תחנת דמשק", "author": "", "image": "", "description": ""},
#     {"name": "הרוזנת מטוסקנה", "author": "", "image": "", "description": ""},
#     {"name": "תישאר קרוב", "author": "", "image": "", "description": ""},
#     {"name": "כראמל 4", "author": "", "image": "", "description": ""},
# ]

# # Directory to save images
# image_directory = "book_images"
# os.makedirs(image_directory, exist_ok=True)

# # Set up Selenium WebDriver with webdriver-manager
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# def fetch_books_data():
#     for book in books:
#         book_name = book["name"]
#         search_url = f"https://www.e-vrit.co.il/Search/{quote(book_name)}"
        
#         try:
#             # Use Selenium to request the page
#             driver.get(search_url)
            
#             # Wait for the desired content to load (e.g., a product-item container)
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, ".product-list .product-item"))
#             )
            
#             # Extract page source once the content is loaded
#             html = driver.page_source
#             soup = BeautifulSoup(html, "html.parser")

#             # Locate the product container where all relevant information is available
#             product_container = soup.select_one(".product-list .product-item")
#             if product_container:
#                 # Extract image URL
#                 image_element = product_container.select_one(".product-image img")
#                 if image_element:
#                     image_url = image_element["src"]
#                     book["image"] = image_url
#                     # Save the image
#                     image_path = os.path.join(image_directory, f"{book_name}.jpg")
#                     urllib.request.urlretrieve(image_url, image_path)
#                     print(f"Image saved for {book_name} at {image_path}")
#                 else:
#                     book["image"] = "Image not available"

#                 # Extract author
#                 author_element = product_container.select_one(".product-author")
#                 book["author"] = author_element.text.strip() if author_element else "Author not available"
                
#                 # Extract description
#                 description_element = soup.select_one(".product-desc.tab-content__single-tab.tab-content__about-book.highlight__done")
#                 book["description"] = description_element.text.strip() if description_element else "Description not available"

#                 # Print details
#                 print(f"Book Name: {book_name}")
#                 print(f"Author: {book['author']}")
#                 print(f"Image URL: {book['image']}")
#                 print(f"Description: {book['description']}")
#                 print("--------------------------------------------")

#         except Exception as e:
#             print(f"Could not fetch details for book: {book_name}", e)

# if __name__ == "__main__":
#     fetch_books_data()
#     driver.quit()  # Close the browser when done


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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

driver.quit()  # Close the browser when done

