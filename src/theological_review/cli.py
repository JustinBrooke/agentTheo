"""Command-line interface for the theological review agent."""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from theological_review.agent import (
    review_blog_post,
    review_blog_post_url,
    quick_doctrinal_check,
    verify_single_citation,
)

app = typer.Typer(
    name="theo-review",
    help="Catholic theological review agent for blog posts",
    add_completion=False,
)
console = Console()


def print_review(review: str) -> None:
    """Print a formatted review to the console."""
    console.print()
    console.print(Panel(
        Markdown(review),
        title="[bold blue]Theological Review[/bold blue]",
        border_style="blue",
    ))


@app.command()
def review(
    source: str = typer.Argument(
        ...,
        help="File path or URL of the blog post to review",
    ),
    output: Path | None = typer.Option(
        None,
        "--output", "-o",
        help="Save review to file",
    ),
) -> None:
    """
    Review a Catholic blog post for theological accuracy.

    Checks doctrine, citations, historical claims, and more against
    authoritative Catholic sources including the Catechism, Vatican
    documents, and Church Fathers.

    Examples:
        theo-review ./my-blog-post.md
        theo-review https://example.com/blog/my-post
        theo-review ./post.txt -o review.md
    """
    console.print()
    console.print(Panel(
        "[bold]Catholic Theological Review Agent[/bold]\n\n"
        "Reviewing against:\n"
        "  • Magisterium.com API\n"
        "  • Catechism of the Catholic Church\n"
        "  • Vatican.va Documents\n"
        "  • Church Fathers (NewAdvent.org)\n"
        "  • Summa Theologica",
        title="[blue]Starting Review[/blue]",
        border_style="blue",
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing blog post...", total=None)

        # Determine if source is URL or file
        if source.startswith(("http://", "https://")):
            progress.update(task, description="Fetching blog post from URL...")
            review_text = asyncio.run(review_blog_post_url(source))
        else:
            # Read from file
            source_path = Path(source)
            if not source_path.exists():
                console.print(f"[red]Error: File not found: {source}[/red]")
                raise typer.Exit(1)

            progress.update(task, description="Reading blog post file...")
            content = source_path.read_text()

            progress.update(task, description="Conducting theological review...")
            review_text = asyncio.run(review_blog_post(content))

        progress.update(task, description="Review complete!")

    # Output the review
    print_review(review_text)

    # Save to file if requested
    if output:
        output.write_text(review_text)
        console.print(f"\n[green]Review saved to: {output}[/green]")


@app.command()
def check(
    claim: str = typer.Argument(
        ...,
        help="The doctrinal claim to verify",
    ),
) -> None:
    """
    Quick check a single doctrinal claim against Catholic teaching.

    Uses the Magisterium.com API for rapid verification.

    Example:
        theo-review check "The Eucharist is the real presence of Christ"
    """
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking claim against Magisterium...", total=None)
        result = asyncio.run(quick_doctrinal_check(claim))

    console.print(Panel(
        f"[bold]Claim:[/bold] {claim}\n\n"
        f"[bold]Result:[/bold]\n{result}",
        title="[blue]Doctrinal Check[/blue]",
        border_style="blue",
    ))


@app.command()
def verify(
    quote: str = typer.Argument(..., help="The quoted text to verify"),
    source: str = typer.Argument(..., help="The claimed source (e.g., 'CCC', 'Augustine')"),
    reference: str | None = typer.Option(
        None,
        "--ref", "-r",
        help="Specific reference (e.g., paragraph number)",
    ),
) -> None:
    """
    Verify a specific citation against its source.

    Example:
        theo-review verify "Christ is truly present" "CCC" --ref 1374
    """
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Verifying citation...", total=None)
        result = asyncio.run(verify_single_citation(quote, source, reference))

    status_color = "green" if result.get("verified") else "red"
    status_text = "VERIFIED" if result.get("verified") else "NOT VERIFIED"

    console.print(Panel(
        f"[bold]Quote:[/bold] \"{quote}\"\n"
        f"[bold]Source:[/bold] {source}\n"
        f"[bold]Reference:[/bold] {reference or 'N/A'}\n\n"
        f"[bold]Status:[/bold] [{status_color}]{status_text}[/{status_color}]\n"
        f"[bold]Confidence:[/bold] {result.get('confidence', 0):.0%}\n"
        f"[bold]Notes:[/bold] {result.get('notes', 'N/A')}",
        title="[blue]Citation Verification[/blue]",
        border_style="blue",
    ))


@app.command()
def catechism(
    paragraph: int = typer.Argument(..., help="CCC paragraph number to look up"),
) -> None:
    """
    Look up a specific Catechism paragraph.

    Example:
        theo-review catechism 1374
    """
    from theological_review.tools.vatican import search_catechism

    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Fetching CCC {paragraph}...", total=None)
        result = asyncio.run(search_catechism(paragraph=paragraph))

    if "data" in result:
        content = result["data"].get("content", "Content not found")
        console.print(Panel(
            f"[bold]CCC {paragraph}[/bold]\n\n{content}",
            title="[blue]Catechism of the Catholic Church[/blue]",
            border_style="blue",
        ))
    else:
        console.print(f"[red]Could not fetch CCC {paragraph}: {result.get('error', 'Unknown error')}[/red]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Topic to search for"),
    source: str = typer.Option(
        "all",
        "--source", "-s",
        help="Source to search (catechism, fathers, encyclopedia, summa, all)",
    ),
) -> None:
    """
    Search theological sources for a topic.

    Example:
        theo-review search "transubstantiation" --source catechism
    """
    from theological_review.tools.vatican import search_catechism
    from theological_review.tools.newadvent import (
        search_church_fathers,
        search_encyclopedia,
        search_summa,
    )

    console.print()

    results = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        if source in ("all", "catechism"):
            task = progress.add_task("Searching Catechism...", total=None)
            results["catechism"] = asyncio.run(search_catechism(query=query))

        if source in ("all", "fathers"):
            progress.update(task, description="Searching Church Fathers...")
            results["fathers"] = asyncio.run(search_church_fathers(query=query))

        if source in ("all", "encyclopedia"):
            progress.update(task, description="Searching Catholic Encyclopedia...")
            results["encyclopedia"] = asyncio.run(search_encyclopedia(query=query))

        if source in ("all", "summa"):
            progress.update(task, description="Searching Summa Theologica...")
            results["summa"] = asyncio.run(search_summa(query=query))

    # Display results
    for source_name, result in results.items():
        if "results" in result and result["results"]:
            console.print(f"\n[bold blue]{source_name.title()}[/bold blue]")
            for item in result["results"][:5]:
                title = item.get("title") or item.get("topic", "Unknown")
                url = item.get("url", "")
                console.print(f"  • {title}")
                if url:
                    console.print(f"    [dim]{url}[/dim]")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
