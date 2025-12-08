"""NewAdvent.org tools for Church Fathers, Catholic Encyclopedia, and Summa Theologica."""

import re
import httpx
from bs4 import BeautifulSoup
from diskcache import Cache
from urllib.parse import urljoin, quote

# Initialize cache
_cache = Cache("/tmp/theological_cache/newadvent")
CACHE_EXPIRY = 86400 * 7  # 7 days


async def search_church_fathers(
    query: str,
    father: str | None = None,
    work: str | None = None,
) -> dict:
    """
    Search NewAdvent.org for Church Fathers writings.

    Args:
        query: Search term or topic
        father: Specific Church Father (e.g., "Augustine", "Chrysostom", "Aquinas")
        work: Specific work to search within

    Returns:
        Dictionary with search results and relevant passages
    """
    cache_key = f"fathers:{query}:{father}:{work}"
    cached = _cache.get(cache_key)
    if cached:
        return {"source": "cache", "data": cached}

    base_url = "https://www.newadvent.org/fathers/"

    # Map of Church Fathers to their works on NewAdvent
    father_works = {
        "augustine": ["1", "2"],  # Multiple volumes
        "chrysostom": ["chrysostom"],
        "ambrose": ["ambrose"],
        "jerome": ["jerome"],
        "athanasius": ["athanasius"],
        "basil": ["basil"],
        "gregory": ["gregory"],
        "cyril": ["cyril"],
        "origen": ["origen"],
        "tertullian": ["tertullian"],
        "irenaeus": ["irenaeus"],
        "clement": ["clement"],
        "ignatius": ["ignatius"],
        "justin": ["justin"],
        "polycarp": ["polycarp"],
    }

    results = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            # If specific father requested, search their works
            if father:
                father_key = father.lower().split()[0]  # Get first name
                if father_key in father_works:
                    # Fetch the father's index page
                    index_url = f"{base_url}index.htm"
                    response = await client.get(index_url)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")

                        # Find links related to this father
                        for link in soup.find_all("a"):
                            link_text = link.get_text(strip=True).lower()
                            href = link.get("href", "")

                            if father.lower() in link_text:
                                results.append({
                                    "father": father,
                                    "work": link.get_text(strip=True),
                                    "url": urljoin(base_url, href),
                                })

            # Search the fathers index for the query
            index_url = f"{base_url}index.htm"
            response = await client.get(index_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                for link in soup.find_all("a"):
                    link_text = link.get_text(strip=True)
                    if query.lower() in link_text.lower():
                        href = link.get("href", "")
                        results.append({
                            "title": link_text,
                            "url": urljoin(base_url, href),
                        })

            result = {
                "source": "newadvent.org/fathers",
                "query": query,
                "father": father,
                "results": results[:20],
            }

            _cache.set(cache_key, result, expire=CACHE_EXPIRY)
            return result

        except httpx.RequestError as e:
            return {"status": "error", "error": str(e)}


async def search_encyclopedia(query: str) -> dict:
    """
    Search the Catholic Encyclopedia on NewAdvent.org.

    Args:
        query: Topic to search for

    Returns:
        Dictionary with encyclopedia entries
    """
    cache_key = f"encyclopedia:{query}"
    cached = _cache.get(cache_key)
    if cached:
        return {"source": "cache", "data": cached}

    base_url = "https://www.newadvent.org/cathen/"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            # NewAdvent encyclopedia has an alphabetical index
            # First letter of query determines which index page
            first_letter = query[0].lower()
            index_url = f"{base_url}{first_letter}.htm"

            response = await client.get(index_url)

            results = []
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                for link in soup.find_all("a"):
                    link_text = link.get_text(strip=True)
                    if query.lower() in link_text.lower():
                        href = link.get("href", "")
                        if href and not href.startswith("http"):
                            href = urljoin(base_url, href)
                        results.append({
                            "title": link_text,
                            "url": href,
                        })

            result = {
                "source": "newadvent.org/cathen",
                "query": query,
                "results": results[:20],
            }

            _cache.set(cache_key, result, expire=CACHE_EXPIRY)
            return result

        except httpx.RequestError as e:
            return {"status": "error", "error": str(e)}


async def search_summa(
    query: str,
    part: str | None = None,
    question: int | None = None,
    article: int | None = None,
) -> dict:
    """
    Search St. Thomas Aquinas's Summa Theologica on NewAdvent.org.

    Args:
        query: Topic to search for
        part: Part of Summa (FP=First Part, FS=First of Second, SS=Second of Second, TP=Third Part)
        question: Question number
        article: Article number

    Returns:
        Dictionary with Summa content
    """
    base_url = "https://www.newadvent.org/summa/"

    # Direct lookup if part, question, and article specified
    if part and question:
        # Build direct URL - e.g., /summa/1001.htm for FP Q1
        part_codes = {
            "fp": "1",  # First Part
            "fs": "2",  # First of Second Part
            "ss": "3",  # Second of Second Part
            "tp": "4",  # Third Part
            "xp": "5",  # Supplement
        }

        part_code = part_codes.get(part.lower(), "1")
        url = f"{base_url}{part_code}{question:03d}.htm"

        if article:
            url = f"{url}#article{article}"

        cache_key = f"summa:{part}:{question}:{article}"
        cached = _cache.get(cache_key)
        if cached:
            return {"source": "cache", "data": cached}

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")

                    # Extract the relevant content
                    content = soup.get_text(separator="\n", strip=True)

                    result = {
                        "source": "newadvent.org/summa",
                        "part": part,
                        "question": question,
                        "article": article,
                        "url": url,
                        "content": content[:10000],
                    }

                    _cache.set(cache_key, result, expire=CACHE_EXPIRY)
                    return result

            except httpx.RequestError as e:
                return {"status": "error", "error": str(e)}

    # General search through Summa index
    cache_key = f"summa:search:{query}"
    cached = _cache.get(cache_key)
    if cached:
        return {"source": "cache", "data": cached}

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            # Search the Summa index
            index_url = f"{base_url}index.html"
            response = await client.get(index_url)

            results = []
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                for link in soup.find_all("a"):
                    link_text = link.get_text(strip=True)
                    if query.lower() in link_text.lower():
                        href = link.get("href", "")
                        if href:
                            results.append({
                                "title": link_text,
                                "url": urljoin(base_url, href),
                            })

            result = {
                "source": "newadvent.org/summa",
                "query": query,
                "results": results[:20],
            }

            _cache.set(cache_key, result, expire=CACHE_EXPIRY)
            return result

        except httpx.RequestError as e:
            return {"status": "error", "error": str(e)}


async def fetch_newadvent_content(url: str) -> dict:
    """
    Fetch full content from a NewAdvent.org URL.

    Args:
        url: Full URL to NewAdvent page

    Returns:
        Dictionary with page content
    """
    if "newadvent.org" not in url:
        return {"status": "error", "error": "URL must be from newadvent.org"}

    cache_key = f"newadvent:content:{url}"
    cached = _cache.get(cache_key)
    if cached:
        return {"source": "cache", "data": cached}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                return {"status": "error", "error": f"HTTP {response.status_code}"}

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove navigation elements
            for element in soup(["script", "style", "nav"]):
                element.decompose()

            # Try to find main content
            content_area = soup.find("div", class_="content") or soup.body

            if content_area:
                content = content_area.get_text(separator="\n", strip=True)
            else:
                content = soup.get_text(separator="\n", strip=True)

            result = {
                "source": "newadvent.org",
                "url": url,
                "content": content[:15000],
            }

            _cache.set(cache_key, result, expire=CACHE_EXPIRY)
            return result

        except httpx.RequestError as e:
            return {"status": "error", "error": str(e)}
