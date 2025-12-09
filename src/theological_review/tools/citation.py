"""Citation verification tools."""

import re
import httpx
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

from theological_review.tools.vatican import search_catechism, fetch_vatican_document
from theological_review.tools.newadvent import fetch_newadvent_content


def similarity_ratio(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


async def verify_citation(
    quoted_text: str,
    claimed_source: str,
    reference: str | None = None,
) -> dict:
    """
    Verify that a citation matches its claimed source.

    Args:
        quoted_text: The text as quoted in the blog post
        claimed_source: The source being cited (e.g., "CCC", "Vatican II", "Augustine")
        reference: Specific reference (paragraph number, chapter, etc.)

    Returns:
        Dictionary with verification results
    """
    result = {
        "quoted_text": quoted_text,
        "claimed_source": claimed_source,
        "reference": reference,
        "verified": False,
        "confidence": 0.0,
        "actual_text": None,
        "notes": "",
    }

    # Normalize the quoted text for comparison
    normalized_quote = re.sub(r"\s+", " ", quoted_text.strip().lower())

    # Route to appropriate verification based on source type
    source_lower = claimed_source.lower()

    # Catechism citations
    if any(term in source_lower for term in ["ccc", "catechism", "catholic church"]):
        return await _verify_catechism_citation(quoted_text, reference, result)

    # Vatican document citations
    if any(term in source_lower for term in ["vatican", "council", "encyclical", "pope"]):
        return await _verify_vatican_citation(quoted_text, claimed_source, reference, result)

    # Church Father citations
    if any(term in source_lower for term in [
        "augustine", "aquinas", "chrysostom", "jerome", "ambrose",
        "athanasius", "basil", "gregory", "cyril", "origen",
        "tertullian", "irenaeus", "clement", "ignatius", "polycarp",
        "father", "patristic"
    ]):
        return await _verify_patristic_citation(quoted_text, claimed_source, reference, result)

    # Scripture citations
    if any(term in source_lower for term in ["bible", "scripture", "gospel", "epistle"]):
        return await _verify_scripture_citation(quoted_text, reference, result)

    # Unknown source type
    result["notes"] = f"Unable to verify source type: {claimed_source}"
    result["confidence"] = 0.0
    return result


async def _verify_catechism_citation(
    quoted_text: str,
    reference: str | None,
    result: dict,
) -> dict:
    """Verify a Catechism citation."""

    # Extract paragraph number from reference
    paragraph = None
    if reference:
        match = re.search(r"(\d+)", reference)
        if match:
            paragraph = int(match.group(1))

    if not paragraph:
        result["notes"] = "No CCC paragraph number provided for verification"
        return result

    # Fetch the CCC paragraph
    ccc_result = await search_catechism(paragraph=paragraph)

    if ccc_result.get("status") == "not_found":
        result["notes"] = f"CCC paragraph {paragraph} not found"
        return result

    if "data" in ccc_result and "content" in ccc_result.get("data", {}):
        actual_content = ccc_result["data"]["content"]
        result["actual_text"] = actual_content

        # Check if quoted text appears in the actual content
        similarity = similarity_ratio(quoted_text, actual_content)

        if quoted_text.lower() in actual_content.lower():
            result["verified"] = True
            result["confidence"] = 0.95
            result["notes"] = "Quote found in source"
        elif similarity > 0.7:
            result["verified"] = True
            result["confidence"] = similarity
            result["notes"] = f"High similarity ({similarity:.0%}) with source text"
        elif similarity > 0.4:
            result["verified"] = False
            result["confidence"] = similarity
            result["notes"] = f"Partial match ({similarity:.0%}) - may be paraphrased or misquoted"
        else:
            result["verified"] = False
            result["confidence"] = similarity
            result["notes"] = "Quote does not match source text"

    return result


async def _verify_vatican_citation(
    quoted_text: str,
    claimed_source: str,
    reference: str | None,
    result: dict,
) -> dict:
    """Verify a Vatican document citation."""

    # This would need to fetch the specific document
    # For now, return a partial result
    result["notes"] = (
        "Vatican document verification requires manual URL. "
        "Use fetch_source_content with the document URL."
    )
    result["confidence"] = 0.0

    return result


async def _verify_patristic_citation(
    quoted_text: str,
    claimed_source: str,
    reference: str | None,
    result: dict,
) -> dict:
    """Verify a Church Father citation."""

    result["notes"] = (
        "Patristic citation verification requires searching NewAdvent.org. "
        "Use search_church_fathers to locate the source."
    )
    result["confidence"] = 0.0

    return result


async def _verify_scripture_citation(
    quoted_text: str,
    reference: str | None,
    result: dict,
) -> dict:
    """Verify a Scripture citation."""

    result["notes"] = (
        "Scripture verification not yet implemented. "
        "Consider checking against an approved Catholic Bible translation."
    )
    result["confidence"] = 0.0

    return result


async def fetch_source_content(url: str) -> dict:
    """
    Fetch content from a URL to verify citations.

    Args:
        url: URL to fetch (must be from approved sources)

    Returns:
        Dictionary with page content
    """
    # Validate URL is from approved theological sources
    approved_domains = [
        "vatican.va",
        "newadvent.org",
        "magisterium.com",
        "usccb.org",
        "catholicculture.org",
    ]

    if not any(domain in url for domain in approved_domains):
        return {
            "status": "error",
            "error": f"URL not from approved source. Approved: {', '.join(approved_domains)}",
        }

    # Route to appropriate fetcher
    if "vatican.va" in url:
        return await fetch_vatican_document(url)
    elif "newadvent.org" in url:
        return await fetch_newadvent_content(url)

    # Generic fetch for other approved sources
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                return {"status": "error", "error": f"HTTP {response.status_code}"}

            soup = BeautifulSoup(response.text, "html.parser")

            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            content = soup.get_text(separator="\n", strip=True)

            return {
                "source": url,
                "content": content[:15000],
            }

        except httpx.RequestError as e:
            return {"status": "error", "error": str(e)}


def extract_citations_from_text(text: str) -> list[dict]:
    """
    Extract citations from blog post text.

    Args:
        text: The blog post content

    Returns:
        List of identified citations with their claimed sources
    """
    citations = []

    # Pattern for quoted text with attribution
    # e.g., "quote here" (Source Name)
    # e.g., "quote here" - Source Name
    # e.g., As Source Name said, "quote here"
    patterns = [
        # "quote" (Source)
        r'"([^"]+)"\s*\(([^)]+)\)',
        # "quote" - Source
        r'"([^"]+)"\s*[-–—]\s*([A-Z][^.!?\n]+)',
        # As Source said/wrote/taught, "quote"
        r'(?:As|According to)\s+([A-Z][^,]+),?\s+"([^"]+)"',
        # CCC 1234 or CCC #1234
        r'(?:CCC|Catechism)\s*#?\s*(\d+)',
        # Vatican II, Lumen Gentium, etc.
        r'(Vatican\s+II[^,]*|Lumen\s+Gentium|Gaudium\s+et\s+Spes|Dei\s+Verbum|Sacrosanctum\s+Concilium)',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            groups = match.groups()
            if len(groups) == 2:
                citations.append({
                    "quoted_text": groups[0] if groups[0] else "",
                    "claimed_source": groups[1] if groups[1] else groups[0],
                    "position": match.start(),
                })
            elif len(groups) == 1:
                citations.append({
                    "reference": groups[0],
                    "claimed_source": "CCC" if "CCC" in pattern else "Vatican II",
                    "position": match.start(),
                })

    return citations
