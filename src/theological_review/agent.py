"""Main theological review agent using Claude Code SDK."""

import os
import json
from pathlib import Path

from dotenv import load_dotenv
from claude_code_sdk import query, ClaudeCodeOptions, Message

from theological_review.tools.magisterium import query_magisterium, query_magisterium_with_context
from theological_review.tools.vatican import (
    search_catechism,
    search_vatican_documents,
    fetch_vatican_document,
)
from theological_review.tools.newadvent import (
    search_church_fathers,
    search_encyclopedia,
    search_summa,
    fetch_newadvent_content,
)
from theological_review.tools.citation import (
    verify_citation,
    fetch_source_content,
    extract_citations_from_text,
)

# Load environment variables
load_dotenv()


def get_system_prompt() -> str:
    """Load the system prompt from file."""
    prompt_path = Path(__file__).parent / "prompts" / "system_prompt.md"
    if prompt_path.exists():
        return prompt_path.read_text()

    # Fallback minimal prompt
    return """You are a Catholic theological review agent. Review blog posts for:
1. Doctrinal accuracy against the Catechism and Magisterium
2. Citation verification
3. Historical accuracy
4. Consistency with Church Fathers
5. Proper Scripture interpretation

Use the available tools to verify all claims and citations."""


def create_review_agent() -> ClaudeCodeOptions:
    """Create and configure the theological review agent."""
    return ClaudeCodeOptions(
        system_prompt=get_system_prompt(),
        allowed_tools=[
            "Read",
            "WebFetch",
            "Grep",
        ],
        max_turns=50,
    )


async def review_blog_post(
    content: str,
    source_url: str | None = None,
    output_format: str = "markdown",
) -> str:
    """
    Review a blog post for theological accuracy.

    Args:
        content: The blog post content (text or URL)
        source_url: Optional URL where the post is published
        output_format: Output format ("markdown", "json")

    Returns:
        The theological review as a string
    """
    # Build the review prompt
    review_prompt = f"""Please conduct a comprehensive theological review of the following Catholic blog post.

## Review Process

1. First, read through the entire post to understand its main theological claims
2. Identify all citations and claimed sources
3. Use your tools to verify each claim against authoritative sources:
   - Query Magisterium.com for relevant Church teaching
   - Search the Catechism for applicable paragraphs
   - Check Vatican.va for relevant documents
   - Search NewAdvent.org for Church Fathers and encyclopedia entries
4. Verify all citations are accurate and not taken out of context
5. Check historical claims for accuracy
6. Provide a structured review following the output format

## Blog Post Content

{content}

"""

    if source_url:
        review_prompt += f"\n## Source URL\n{source_url}\n"

    review_prompt += """
## Instructions

Provide a complete theological review following the structured format in your instructions.
Be thorough but charitable. Focus on substantive issues that affect the faith.
Use your tools to verify claims - do not rely solely on your training data.
"""

    # Create the agent options
    options = create_review_agent()

    # Collect the full response
    full_response = []

    async for message in query(prompt=review_prompt, options=options):
        if isinstance(message, Message):
            # Handle different message types
            if hasattr(message, "content"):
                for block in message.content:
                    if hasattr(block, "text"):
                        full_response.append(block.text)

    return "\n".join(full_response)


async def review_blog_post_url(url: str) -> str:
    """
    Review a blog post from a URL.

    Args:
        url: URL of the blog post to review

    Returns:
        The theological review
    """
    review_prompt = f"""Please review the Catholic blog post at this URL for theological accuracy:

{url}

First, fetch and read the content from the URL, then conduct a comprehensive theological review following your instructions.
"""

    options = create_review_agent()
    full_response = []

    async for message in query(prompt=review_prompt, options=options):
        if isinstance(message, Message):
            if hasattr(message, "content"):
                for block in message.content:
                    if hasattr(block, "text"):
                        full_response.append(block.text)

    return "\n".join(full_response)


async def quick_doctrinal_check(claim: str) -> str:
    """
    Quickly check a single doctrinal claim against Catholic teaching.

    Args:
        claim: The theological claim to verify

    Returns:
        Assessment of the claim's accuracy
    """
    # Use Magisterium.com API directly for quick checks
    result = await query_magisterium(claim)

    if result.get("status") == "success":
        # Return the response content from Magisterium
        return result.get("response", "No response content available")
    else:
        return f"Unable to verify: {result.get('error', 'Unknown error')}"


async def verify_single_citation(
    quote: str,
    source: str,
    reference: str | None = None,
) -> dict:
    """
    Verify a single citation.

    Args:
        quote: The quoted text
        source: The claimed source
        reference: Optional specific reference (paragraph number, etc.)

    Returns:
        Verification result dictionary
    """
    return await verify_citation(quote, source, reference)
