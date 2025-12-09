"""Magisterium.com API integration for authoritative Catholic teaching."""

import os
import httpx
from diskcache import Cache

# Initialize cache for API responses (24-hour expiry)
_cache = Cache("/tmp/theological_cache/magisterium")
CACHE_EXPIRY = 86400  # 24 hours

# API Configuration - OpenAI-compatible chat completions endpoint
API_URL = "https://www.magisterium.com/api/v1/chat/completions"
MODEL = "magisterium-1"


def get_api_key() -> str:
    """Get the Magisterium API key from environment."""
    key = os.getenv("MAGISTERIUM_API_KEY")
    if not key:
        raise ValueError(
            "MAGISTERIUM_API_KEY environment variable not set. "
            "Please add it to your .env file."
        )
    return key


async def query_magisterium(query: str, system_context: str | None = None) -> dict:
    """
    Query the Magisterium.com API for authoritative Catholic teaching.

    Uses the OpenAI-compatible chat completions endpoint.

    Args:
        query: The theological question or topic to search for
        system_context: Optional system message for additional context

    Returns:
        Dictionary containing the API response with authoritative teaching
    """
    cache_key = f"magisterium:{query}:{system_context or ''}"

    # Check cache first
    cached = _cache.get(cache_key)
    if cached is not None:
        return {"source": "cache", "data": cached}

    api_key = get_api_key()

    # Build messages array
    messages = []
    if system_context:
        messages.append({
            "role": "system",
            "content": system_context
        })
    messages.append({
        "role": "user",
        "content": query
    })

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "messages": messages,
                    "stream": False,
                },
            )

            if response.status_code == 200:
                data = response.json()
                # Extract the response content
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    content = message.get("content", "")

                    result = {
                        "source": "magisterium_api",
                        "status": "success",
                        "query": query,
                        "response": content,
                        "raw_data": data,
                    }

                    # Cache successful responses
                    _cache.set(cache_key, result, expire=CACHE_EXPIRY)
                    return result
                else:
                    return {
                        "source": "magisterium_api",
                        "status": "error",
                        "error": "Unexpected response format from API",
                        "raw_data": data,
                    }
            elif response.status_code == 401:
                return {
                    "source": "magisterium_api",
                    "status": "error",
                    "error": "Invalid API key. Please check your MAGISTERIUM_API_KEY.",
                }
            elif response.status_code == 429:
                return {
                    "source": "magisterium_api",
                    "status": "error",
                    "error": "Rate limit exceeded. Please try again later.",
                }
            else:
                return {
                    "source": "magisterium_api",
                    "status": "error",
                    "error": f"API error: {response.status_code} - {response.text}",
                }

        except httpx.TimeoutException:
            return {
                "source": "magisterium_api",
                "status": "error",
                "error": "Request timed out. Please try again.",
            }
        except httpx.RequestError as e:
            return {
                "source": "magisterium_api",
                "status": "error",
                "error": f"Request failed: {str(e)}",
            }


async def query_magisterium_with_context(
    query: str,
    context: str = "",
) -> dict:
    """
    Query Magisterium.com with additional context from the blog post.

    Args:
        query: The theological question
        context: Additional context from the blog post being reviewed

    Returns:
        Dictionary containing the API response
    """
    system_context = None
    if context:
        system_context = (
            "You are reviewing a Catholic blog post for theological accuracy. "
            f"Here is context from the post being reviewed:\n\n{context}"
        )

    return await query_magisterium(query, system_context)


async def verify_doctrine(claim: str) -> dict:
    """
    Verify a specific doctrinal claim against Catholic teaching.

    Args:
        claim: The doctrinal claim to verify

    Returns:
        Dictionary with verification result
    """
    verification_prompt = f"""Please verify the following claim against Catholic teaching.
Indicate whether it is:
- Accurate (consistent with Catholic doctrine)
- Inaccurate (contradicts Catholic doctrine)
- Partially accurate (contains some truth but also errors or misleading elements)
- Opinion (a theological opinion not defined doctrine)

Claim to verify: "{claim}"

Provide specific references to the Catechism, Church documents, or other authoritative sources."""

    return await query_magisterium(verification_prompt)
