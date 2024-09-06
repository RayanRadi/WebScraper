from selenium import webdriver  # WebDriver to control a web browser
from selenium.webdriver.chrome.service import Service  # Connects Selenium to ChromeDriver
from selenium.webdriver.common.by import By  # Used to locate elements on a webpage
from selenium.webdriver.support.ui import WebDriverWait  # Wait for elements to be clickable or visible
from selenium.webdriver.support import expected_conditions as EC  # Specify conditions for WebDriverWait
import csv  # Handle CSV file operations
import time  
import os  # To check if a file exists
import pickle  # For saving/loading your collection

url = "https://www.tcgplayer.com/search/pokemon/crown-zenith?productLineName=pokemon&setName=crown-zenith&page=1&view=grid"

# Define file paths
csv_file_path = "scraped_values.csv"
collection_file_path = "card_collection.pkl"

# Function to load card prices from the CSV file
def load_card_prices():
    card_prices = {}
    if os.path.isfile(csv_file_path):
        with open(csv_file_path, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) == 2:
                    name, price = row
                    card_prices[name] = price
    else:
        print("CSV file not found. Make sure the scraping script has run successfully.")
    return card_prices

# Function to load your collection from the file
def load_collection():
    if os.path.isfile(collection_file_path):
        with open(collection_file_path, 'rb') as file:
            return pickle.load(file)
    return {}

# Function to save your collection to the file
def save_collection(collection):
    with open(collection_file_path, 'wb') as file:
        pickle.dump(collection, file)

# Function to display your collection with live prices
def display_collection(collection, card_prices):
    print("\nYour Card Collection with Current Prices:")
    for card, quantity in collection.items():
        price = card_prices.get(card, "N/A")
        print(f"{card}: Quantity: {quantity}, Price: {price}")

# Function to add a new card to your collection
def add_card_to_collection(collection, card_prices):
    card_name = input("Enter the name of the card to add: ").strip()
    if card_name not in card_prices:
        print("Card not found in the live prices. Please check the name and try again.")
        return
    quantity = int(input(f"How many of '{card_name}' do you own? "))
    if card_name in collection:
        collection[card_name] += quantity
    else:
        collection[card_name] = quantity
    print(f"Added {quantity} of '{card_name}' to your collection.")

# Web scraping and CSV handling
def scrape_card_data():
    # Set up WebDriver
    service = Service(r'C:\Users\radir\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.get(url)

    # Wait for the page to load
    time.sleep(20)
    wait = WebDriverWait(driver, 10)
    
    current_page = 1
    max_pages = 7  # Maximum number of pages to scrape

    # Check if the CSV file already exists
    file_exists = os.path.isfile(csv_file_path)
    existing_data = {}

    # Load existing data if the file exists
    if file_exists:
        with open(csv_file_path, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) == 2:
                    name, price = row
                    existing_data[name] = price

    new_data = {}
    price_changed = False

    with open(csv_file_path, "a", newline='') as file:  # Open the file in append mode ('a')
        writer = csv.writer(file)

        # Write the header only if the file doesn't exist
        if not file_exists:
            writer.writerow(["NAMES", "PRICES"])

        while current_page <= max_pages:
            # Find the product names and prices
            names = driver.find_elements(By.CSS_SELECTOR, "span.product-card__title.truncate")
            prices = driver.find_elements(By.CSS_SELECTOR, "span.product-card__market-price--value")

            if not names or not prices:  # If no names or prices (a bug) say this
                print("No products found on the page.")
                break

            for name, price in zip(names, prices):
                name_text = name.text.strip()
                price_text = price.text.strip()

                # Store new data
                new_data[name_text] = price_text

                # Check if the price has changed
                if name_text in existing_data and existing_data[name_text] != price_text:
                    price_changed = True
                    print(f"Price change detected for '{name_text}': {existing_data[name_text]} -> {price_text}")
                    writer.writerow([name_text, price_text])
                elif name_text not in existing_data:
                    price_changed = True
                    print(f"New card detected: '{name_text}' with price {price_text}")
                    writer.writerow([name_text, price_text])

            # Try to find and click the "Next" button
            try:
                next_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label='Next page']")))

                # Check if the "Next" button is disabled
                if next_button.get_attribute("aria-disabled") == "true":
                    print("Reached the last page.")
                    break

                # Scroll to the "Next" button using JavaScript
                driver.execute_script("arguments[0].scrollIntoView();", next_button)

                # Click the "Next" button using JavaScript to avoid interception
                driver.execute_script("arguments[0].click();", next_button)

                time.sleep(5)  # Wait for the next page to load
                current_page += 1  # Increment the page number
            except Exception as e:
                print(f"No 'Next' button found or reached the last page: {e}")
                break

    # Close the WebDriver
    driver.quit()

    # Check if any prices have changed
    if not price_changed:
        print("No prices have changed for now.")

# Main logic
def main():
    # Scrape data from the website and update CSV
    scrape_card_data()

    # Load the card prices from CSV and your collection
    card_prices = load_card_prices()
    collection = load_collection()

    while True:
        print("\nOptions:")
        print("1. Display your card collection")
        print("2. Add a new card to your collection")
        print("3. Exit")

        choice = input("Choose an option (1/2/3): ").strip()

        if choice == '1':
            display_collection(collection, card_prices)
        elif choice == '2':
            add_card_to_collection(collection, card_prices)
            save_collection(collection)  # Save the updated collection
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
