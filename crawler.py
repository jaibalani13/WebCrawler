import sys
import requests
from bs4 import BeautifulSoup
import json
import validators
import re


def clear_file_if_exists():
    with open("results.json", 'w') as file:
        json.dump({"results": []}, file)

def getdata(url):
    r = requests.get(url, timeout=5)
    return r.text

def write_data_to_file(image_data):
    with open("results.json") as file:
        try:
            data = json.load(file)
        except Exception as e:
            data = {"results": []}
        data["results"].extend(image_data)
    with open("results.json", 'w') as file:
        json.dump(data, file)


def scrape_images(start_url, current_depth, final_depth):
    if current_depth > final_depth:
        return
    try:
        htmldata = getdata(start_url)
    except Exception as e:
        return
    soup = BeautifulSoup(htmldata, 'html.parser')
    image_data = []
    for item in soup.find_all('img'):
        image_data.append({
            "imageUrl": item['src'],
            "sourceUrl": start_url,
            "depth": current_depth
        })
    write_data_to_file(image_data)

    links_in_page = []
    for item in soup.find_all('a'):
        # to allow only correct full urls + relative urls
        if item.get("href"):
            if validators.url(item["href"]):
                if item["href"] != start_url:
                    links_in_page.append(item['href'])
            elif re.search(r"/.*", item["href"]):
                new_url = start_url + item['href'].strip("/")
                if new_url != start_url:
                    links_in_page.append(new_url)


    for link in links_in_page:
        scrape_images(link, current_depth+1, final_depth)

if __name__ == '__main__':
    clear_file_if_exists()
    if len(sys.argv) != 3:
        raise Exception("Incorrect number of args passed.")

    start_url = sys.argv[1]
    final_depth = int(sys.argv[2])
    scrape_images(start_url, 0, final_depth)


