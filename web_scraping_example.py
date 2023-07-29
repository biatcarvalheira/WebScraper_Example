import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Constants
MAIN_URL = 'http://books.toscrape.com/index.html'
BASE_URL = 'http://books.toscrape.com/catalogue'


def in_stock(title: str, topic: str) -> bool:
    try:
        response = requests.get(MAIN_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the category URL based on the provided topic
        side_bar = soup.find('div', {'class': 'side_categories'})
        side_bar_item = side_bar.find_all('li')
        topic_lower = topic.lower()
        category_url = None
        for s in side_bar_item:
            category = s.text.strip()
            if topic_lower == category.lower():
                target_link = s.find('a')['href']
                category_url = urljoin(BASE_URL, target_link)
                break

        if not category_url:
            print(f"Error: Invalid topic '{topic}'.")
            return False

        # Process the category page to find the book
        page_number = 1
        while category_url:
            category_page = requests.get(category_url)
            category_page.raise_for_status()
            category_soup = BeautifulSoup(category_page.text, 'html.parser')

            # Use CSS selector to fetch all book titles on the page at once
            book_titles = [
                title_tag['title']
                for title_tag in category_soup.select('h3 a[title]')
            ]

            if title.lower() in [t.lower() for t in book_titles]:
                return True

            # Check if there are more pages in the category
            next_page_tag = category_soup.find('li', {'class': 'next'})
            if next_page_tag:
                page_number += 1
                category_url = urljoin(category_url, f"page-{page_number}.html")
            else:
                break

    except requests.exceptions.RequestException as e:
        print(f"An error has occurred while fetching data: {e}")
    except Exception as e:
        print(f"An error has occurred: {e}")

    return False


print(in_stock('Online Marketing for Busy Authors: A Step-By-Step guide', 'Self help'))
