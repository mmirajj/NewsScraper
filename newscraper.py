import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

REQUEST_TIMEOUT = 10
OUTPUT_FILE = "news_data.json"


# -------------------------
# Generic Helper Functions
# -------------------------

def get_html(url):
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"Request failed: {e}")
        return None


def get_article_content(url, selector):
    soup = get_html(url)
    if not soup:
        return ""

    content = soup.select_one(selector)
    return content.get_text(strip=True) if content else ""


# -------------------------
# Kathmandu Post Scraper
# -------------------------

def scrape_kathmandu_post():
    print("\nScraping Kathmandu Post...")
    base_url = "https://kathmandupost.com"
    url = "https://kathmandupost.com/politics"

    soup = get_html(url)
    articles = []

    if not soup:
        return articles

    politics_title = soup.find("h4", class_="title--line__red")
    if not politics_title:
        return articles

    article_blocks = politics_title.find_next_siblings("article", class_="article-image")

    for block in article_blocks:
        title_tag = block.select_one(":scope > a")

        if title_tag:
            title = title_tag.get_text(strip=True)
            link = base_url + title_tag["href"]

            print("Processing:", title)

            content = get_article_content(link, "section.story-section")

            articles.append({
                "title": title,
                "url": link,
                "content": content
            })

    return articles


# -------------------------
# OnlineKhabar Scraper
# -------------------------

def scrape_online_khabar():
    print("\nScraping OnlineKhabar...")
    url = "https://english.onlinekhabar.com/category/political"

    soup = get_html(url)
    articles = []

    if not soup:
        return articles

    container = soup.find("div", class_="listical-news-big")

    if not container:
        return articles

    posts = container.find_all("div", class_="ok-news-post")

    for post in posts:

        title_container = post.find("div", class_="ok-post-contents")
        title_tag = title_container.find("a")

        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]

            print("Processing:", title)

            content = get_article_content(link, "div.post-content-wrap")

            articles.append({
                "title": title,
                "url": link,
                "content": content
            })

    return articles


# -------------------------
# Setopati Scraper
# -------------------------

def scrape_setopati():
    print("\nScraping Setopati...")
    url = "https://en.setopati.com/political"

    soup = get_html(url)
    articles = []

    if not soup:
        return articles

    titles = soup.select("a span.main-title")

    for title_elem in titles:

        parent = title_elem.find_parent("a")

        if not parent:
            continue

        if not parent.find("figure"):
            continue

        title = title_elem.get_text(strip=True)
        link = parent["href"]

        print("Processing:", title)

        content = get_article_content(link, "div.editor-box")

        articles.append({
            "title": title,
            "url": link,
            "content": content
        })

    return articles


# -------------------------
# Save Data
# -------------------------

def save_to_json(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved data to {OUTPUT_FILE}")


# -------------------------
# Main Controller
# -------------------------

def main():

    all_articles = {
        "scrape_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sources": {}
    }

    kp = scrape_kathmandu_post()
    ok = scrape_online_khabar()
    sp = scrape_setopati()

    all_articles["sources"]["kathmandu_post"] = kp
    all_articles["sources"]["onlinekhabar"] = ok
    all_articles["sources"]["setopati"] = sp

    total = len(kp) + len(ok) + len(sp)

    all_articles["total_articles"] = total

    save_to_json(all_articles)

    print("\nTotal articles scraped:", total)


if __name__ == "__main__":
    main()