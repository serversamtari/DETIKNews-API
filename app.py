import httpx
import asyncio
import uvicorn
import json
from fastapi import FastAPI

from selectolax.parser import HTMLParser

app = FastAPI()


async def parse_item(result):
    # Extract the title and URL of each search result item
    title = result.css_first('h2').text()
    url = result.css_first('a').attrs['href']
    category = result.css_first('span.category').text()
    date = result.css_first('span.date').text().lstrip(category)
    desc = result.css_first('span.box_text > p').text()
    content = await parse_content(url)
    return {
        'title': title,
        'url': url,
        'category': category,
        'date': date,
        'desc': desc,
        'content': content
    }

async def parse_content(url):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
        except httpx.TimeoutException:
            return {"error": f"Sorry, unable to connect to {url}. \nPlease try again."}

    parser = HTMLParser(response.text)
    contents = parser.css('div.detail__body-text > p')
    contents = [content.text() for content in contents]
    return "\n".join(contents)

async def parse(url, params, headers):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
        except httpx.TimeoutException:
            return {"error": f"Sorry, unable to connect to {url}. \nPlease try again."}

    parser = HTMLParser(response.text)

    # Extract the search result items from the HTML
    search_results = parser.css('article')

    # Extract the items in parallel using map and asyncio.gather
    items = await asyncio.gather(*[parse_item(result) for result in search_results])
    return items


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


@app.get("/scrape/")
async def scrape_data(keyword: str, pages: int):
    url = "https://www.detik.com/search/searchall?"

    params = {
        "query": keyword,
        "page": pages,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/244.178.44.111 Safari/537.36",
    }

    # Scrape the first `pages` pages of search results asynchronously using map and asyncio.gather
    items = await asyncio.gather(*[parse(url, {**params, 'page': page}, headers) for page in range(1, pages + 1)])

    # Flatten the nested list of items
    items = [item for page_items in items for item in page_items]

    return json.dumps(items)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
