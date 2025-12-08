"""Vatican.va document search and Catechism lookup tools."""

import re
import httpx
from bs4 import BeautifulSoup
from diskcache import Cache

# Initialize cache
_cache = Cache("/tmp/theological_cache/vatican")
CACHE_EXPIRY = 86400 * 7  # 7 days for Vatican documents (they don't change)


async def search_catechism(
    query: str | None = None,
    paragraph: int | None = None,
    section: str | None = None,
) -> dict:
    """
    Search the Catechism of the Catholic Church on Vatican.va.

    Args:
        query: Text to search for in the Catechism
        paragraph: Specific CCC paragraph number (e.g., 1374 for Real Presence)
        section: Section name (e.g., "sacraments", "creed", "commandments")

    Returns:
        Dictionary with Catechism content and references
    """
    base_url = "https://www.vatican.va/archive/ENG0015"

    # Direct paragraph lookup
    if paragraph:
        cache_key = f"ccc:para:{paragraph}"
        cached = _cache.get(cache_key)
        if cached:
            return {"source": "cache", "data": cached}

        # CCC paragraphs are organized in sections
        # We need to find the right file for the paragraph
        url = await _find_ccc_paragraph_url(paragraph)
        if url:
            content = await _fetch_and_parse(url, paragraph)
            if content:
                _cache.set(cache_key, content, expire=CACHE_EXPIRY)
                return {
                    "source": "vatican.va",
                    "type": "catechism",
                    "paragraph": paragraph,
                    "data": content,
                }

        return {
            "source": "vatican.va",
            "status": "not_found",
            "error": f"Could not find CCC paragraph {paragraph}",
        }

    # Section-based lookup
    if section:
        section_urls = {
            "creed": f"{base_url}/_P1.HTM",  # Part 1: Profession of Faith
            "sacraments": f"{base_url}/_P2.HTM",  # Part 2: Sacraments
            "commandments": f"{base_url}/_P3.HTM",  # Part 3: Life in Christ
            "prayer": f"{base_url}/_P4.HTM",  # Part 4: Prayer
        }
        url = section_urls.get(section.lower())
        if url:
            content = await _fetch_and_parse(url)
            return {
                "source": "vatican.va",
                "type": "catechism_section",
                "section": section,
                "data": content,
            }

    # General search - use index
    if query:
        return await _search_ccc_index(query)

    return {"status": "error", "error": "Must provide query, paragraph, or section"}


async def _find_ccc_paragraph_url(paragraph: int) -> str | None:
    """Find the URL containing a specific CCC paragraph."""
    base_url = "https://www.vatican.va/archive/ENG0015"

    # The Vatican CCC uses __P (double underscore) page format
    # Known paragraph ranges based on actual site structure:
    # These are approximate starting paragraphs for each page
    page_ranges = [
        (1, "1"),      # Prologue
        (26, "B"),     # Part 1 Section 1
        (142, "16"),   # Creed articles
        (198, "1B"),
        (232, "1F"),
        (268, "1J"),
        (325, "1P"),
        (422, "1Y"),
        (456, "22"),
        (512, "26"),
        (571, "2B"),
        (638, "2G"),
        (683, "2K"),
        (748, "2Q"),
        (811, "2V"),
        (871, "30"),
        (946, "35"),
        (988, "39"),
        (1066, "3D"),
        (1113, "3H"),
        (1210, "3N"),
        (1285, "3T"),
        (1333, "3Z"),  # Eucharist
        (1356, "41"),  # CCC 1374 is here (Real Presence)
        (1382, "42"),
        (1402, "43"),
        (1420, "44"),
        (1499, "4A"),
        (1533, "4D"),
        (1601, "4I"),
        (1691, "4O"),
        (1762, "4T"),
        (1830, "4Y"),
        (1877, "52"),
        (1928, "55"),
        (1987, "59"),
        (2030, "5D"),
        (2083, "5H"),
        (2142, "5L"),
        (2196, "5P"),
        (2258, "5U"),
        (2331, "5Z"),
        (2392, "64"),
        (2443, "68"),
        (2500, "6D"),
        (2558, "6H"),
        (2626, "6M"),
        (2683, "6Q"),
        (2746, "6V"),
        (2803, "70"),
        (2857, "74"),
    ]

    # Find the page that should contain this paragraph
    target_page = None
    for i, (start_para, page_code) in enumerate(page_ranges):
        if paragraph >= start_para:
            target_page = page_code
        else:
            break

    if not target_page:
        target_page = "1"

    # Try the target page and nearby pages
    pages_to_try = [target_page]

    # Add some nearby pages in case mapping is slightly off
    try:
        page_idx = [p[1] for p in page_ranges].index(target_page)
        if page_idx > 0:
            pages_to_try.append(page_ranges[page_idx - 1][1])
        if page_idx < len(page_ranges) - 1:
            pages_to_try.append(page_ranges[page_idx + 1][1])
    except (ValueError, IndexError):
        pass

    async with httpx.AsyncClient(timeout=10.0) as client:
        for page_code in pages_to_try:
            url = f"{base_url}/__P{page_code}.HTM"
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    # Check if the paragraph number appears in the content
                    if re.search(rf'\b{paragraph}\b', response.text):
                        return url
            except httpx.RequestError:
                continue

    return None


async def _fetch_and_parse(url: str, target_paragraph: int | None = None) -> dict:
    """Fetch a Vatican.va page and extract relevant content."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}"}

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove navigation and footer elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            text = soup.get_text(separator="\n", strip=True)

            # If looking for specific paragraph, try to extract it
            if target_paragraph:
                # CCC paragraphs typically start with the number
                # Try to find the paragraph and capture until the next paragraph number
                # Pattern: paragraph number followed by content until next 4-digit number
                pattern = rf"\b({target_paragraph})\s+(.*?)(?=\n\s*\d{{3,4}}\s|\Z)"
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    para_num = match.group(1)
                    content = match.group(2).strip()
                    # Clean up the content - limit to reasonable length
                    content = content[:2000] if len(content) > 2000 else content
                    return {
                        "paragraph_number": target_paragraph,
                        "content": f"{para_num} {content}",
                        "url": url,
                    }

                # Fallback: simpler extraction
                lines = text.split("\n")
                capture = False
                captured_lines = []
                for line in lines:
                    if str(target_paragraph) in line and re.search(rf'\b{target_paragraph}\b', line):
                        capture = True
                    if capture:
                        captured_lines.append(line)
                        # Stop after capturing enough content or hitting next paragraph
                        if len(captured_lines) > 1 and re.match(r'^\d{3,4}\s', line.strip()):
                            captured_lines.pop()  # Remove the next paragraph start
                            break
                        if len(captured_lines) > 10:
                            break

                if captured_lines:
                    return {
                        "paragraph_number": target_paragraph,
                        "content": "\n".join(captured_lines),
                        "url": url,
                    }

            # Return full page content
            return {
                "content": text[:8000],  # Limit size
                "url": url,
            }

        except httpx.RequestError as e:
            return {"error": str(e)}


async def _search_ccc_index(query: str) -> dict:
    """Search the CCC index for a topic."""
    index_url = "https://www.vatican.va/archive/ENG0015/_INDEX.HTM"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(index_url)
            if response.status_code != 200:
                return {"status": "error", "error": "Could not fetch CCC index"}

            soup = BeautifulSoup(response.text, "html.parser")

            # Find links matching the query
            results = []
            for link in soup.find_all("a"):
                link_text = link.get_text(strip=True).lower()
                if query.lower() in link_text:
                    href = link.get("href", "")
                    results.append({
                        "topic": link.get_text(strip=True),
                        "url": f"https://www.vatican.va/archive/ENG0015/{href}" if href else None,
                    })

            return {
                "source": "vatican.va",
                "type": "ccc_search",
                "query": query,
                "results": results[:20],  # Limit results
            }

        except httpx.RequestError as e:
            return {"status": "error", "error": str(e)}


async def search_vatican_documents(
    query: str,
    document_type: str | None = None,
    pope: str | None = None,
) -> dict:
    """
    Search Vatican.va for official Church documents.

    Args:
        query: Search term
        document_type: Type of document (encyclical, council, apostolic_letter, etc.)
        pope: Filter by pope (e.g., "Francis", "Benedict XVI", "John Paul II")

    Returns:
        Dictionary with search results
    """
    cache_key = f"vatican:docs:{query}:{document_type}:{pope}"
    cached = _cache.get(cache_key)
    if cached:
        return {"source": "cache", "data": cached}

    base_url = "https://www.vatican.va/content"

    # Pope-specific URLs
    pope_paths = {
        "francis": "francesco/en",
        "benedict xvi": "benedict-xvi/en",
        "benedict": "benedict-xvi/en",
        "john paul ii": "john-paul-ii/en",
        "john paul": "john-paul-ii/en",
        "paul vi": "paul-vi/en",
        "pius xii": "pius-xii/en",
        "pius xi": "pius-xi/en",
        "leo xiii": "leo-xiii/en",
    }

    # Document type paths
    doc_type_paths = {
        "encyclical": "encyclicals",
        "apostolic_letter": "apost_letters",
        "apostolic_exhortation": "apost_exhortations",
        "homily": "homilies",
        "audience": "audiences",
        "message": "messages",
    }

    results = []

    # Build search URL
    if pope:
        pope_path = pope_paths.get(pope.lower())
        if pope_path:
            search_url = f"{base_url}/{pope_path}.html"
        else:
            return {"status": "error", "error": f"Unknown pope: {pope}"}
    else:
        # General Vatican content search
        search_url = f"{base_url}/vatican/en.html"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(search_url)
            if response.status_code != 200:
                return {"status": "error", "error": f"HTTP {response.status_code}"}

            soup = BeautifulSoup(response.text, "html.parser")

            # Find links matching query
            for link in soup.find_all("a"):
                link_text = link.get_text(strip=True)
                href = link.get("href", "")

                if query.lower() in link_text.lower():
                    # Filter by document type if specified
                    if document_type:
                        type_path = doc_type_paths.get(document_type.lower(), "")
                        if type_path and type_path not in href:
                            continue

                    results.append({
                        "title": link_text,
                        "url": href if href.startswith("http") else f"https://www.vatican.va{href}",
                        "type": document_type,
                    })

            result = {
                "source": "vatican.va",
                "query": query,
                "pope": pope,
                "document_type": document_type,
                "results": results[:20],
            }

            _cache.set(cache_key, result, expire=CACHE_EXPIRY)
            return result

        except httpx.RequestError as e:
            return {"status": "error", "error": str(e)}


async def fetch_vatican_document(url: str) -> dict:
    """
    Fetch the full content of a Vatican document.

    Args:
        url: Full URL to the Vatican.va document

    Returns:
        Dictionary with document content
    """
    if "vatican.va" not in url:
        return {"status": "error", "error": "URL must be from vatican.va"}

    cache_key = f"vatican:doc:{url}"
    cached = _cache.get(cache_key)
    if cached:
        return {"source": "cache", "data": cached}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                return {"status": "error", "error": f"HTTP {response.status_code}"}

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove non-content elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
                element.decompose()

            # Try to find the main content area
            content_div = soup.find("div", class_="content") or soup.find("article") or soup.body

            if content_div:
                content = content_div.get_text(separator="\n", strip=True)
            else:
                content = soup.get_text(separator="\n", strip=True)

            result = {
                "source": "vatican.va",
                "url": url,
                "content": content[:15000],  # Limit size
            }

            _cache.set(cache_key, result, expire=CACHE_EXPIRY)
            return result

        except httpx.RequestError as e:
            return {"status": "error", "error": str(e)}
