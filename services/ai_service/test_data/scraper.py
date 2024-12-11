import json
from typing import Any
import requests
from bs4 import BeautifulSoup

URL = "https://www.timeout.com/copenhagen/restaurants/best-restaurants-in-copenhagen"

# mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def fetch_restaurant_data(url: str) -> list[dict[str, Any]]:
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        restaurants: list[dict[str, Any]] = []
        for item in soup.find_all("div", class_="articleContent"):
            name = item.find("h3", class_="_h3_70r6w_1")
            description = item.find("p")
            if name and description:  # ensure both fields are found
                restaurants.append(
                    {
                        "name": name.get_text(strip=True).lstrip("0123456789. "),
                        "description": description.get_text(strip=True).lstrip(
                            "0123456789. "
                        ),
                    }
                )

        return restaurants

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


def save_to_json(
    data: list[dict[str, Any]], filename: str = "test_data/restaurants.json"
):
    with open(filename, mode="w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Data saved to {filename}")


if __name__ == "__main__":
    print("Fetching restaurant data...")
    restaurants = fetch_restaurant_data(URL)
    if restaurants:
        print(f"Found {len(restaurants)} restaurants.")
        save_to_json(restaurants)
    else:
        print("No data found.")
