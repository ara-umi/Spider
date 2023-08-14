import requests
from bs4 import BeautifulSoup

def get_html(url):
    response = requests.get(url)
    html = response.content.decode("utf-8")

    return html

def extract_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.select_one(".Mid2L_con").text
    next_page = soup.select("#pe100_page_contentpage .page_css a")[-1]
    next_page_link = None
    if next_page.text == "下一页":
        next_page_link = next_page.attrs['href']
        print(next_page_link)
    return content, next_page_link


if __name__ == '__main__':
    url = 'https://www.gamersky.com/handbook/202205/1482021.shtml'
    content = ""
    while url:
        html = get_html(url)
        page_content, next_page_link = extract_html(html)
        url = next_page_link
        content += page_content
    print(content)