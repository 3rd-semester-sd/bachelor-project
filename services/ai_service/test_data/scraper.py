import json
import requests
from bs4 import BeautifulSoup
import csv

# Target URL
URL = "https://www.timeout.com/copenhagen/restaurants/best-restaurants-in-copenhagen"

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def fetch_restaurant_data(url):
    try:
        # Send HTTP request
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse the page content
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract restaurant names and descriptions
        restaurants = []
        for item in soup.find_all(
            "div", class_="articleContent"
        ):  # Update the class based on actual site
            name = item.find("h3", class_="_h3_70r6w_1")
            description = item.find("p")
            if name and description:  # Ensure both fields are found
                restaurants.append(
                    {
                        "name": name.get_text(strip=True).lstrip("0123456789. "),
                        "description": description.get_text(strip=True).lstrip("0123456789. "),
                    }
                )

        return restaurants

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


def save_to_csv(data, filename="restaurants.csv"):
    # Save data to a CSV file
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "description"])
        writer.writeheader()
        writer.writerows(data)

    print(f"Data saved to {filename}")


def save_to_json(data, filename="test_data/restaurants.json"):
    # Save data to a JSON file
    with open(filename, mode="w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Data saved to {filename}")


# Main logic
if __name__ == "__main__":
    print("Fetching restaurant data...")
    restaurants = fetch_restaurant_data(URL)
    if restaurants:
        print(f"Found {len(restaurants)} restaurants.")
        save_to_json(restaurants)
    else:
        print("No data found.")
