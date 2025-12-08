# Catholic Theological Review Agent

An AI-powered agent that reviews Catholic blog posts for theological accuracy, proper citation, and alignment with authentic Church teaching.

## Features

- **Doctrinal Verification**: Checks claims against the Catechism, Magisterium, and official Church documents
- **Citation Verification**: Verifies quotes against their original sources
- **Historical Accuracy**: Validates historical claims about Church history
- **Patristic Consistency**: Cross-references with Church Fathers' writings
- **Scripture Interpretation**: Ensures biblical interpretations align with Catholic hermeneutics

## Sources

The agent verifies content against:

- **Magisterium.com API** - Authoritative Catholic teaching database
- **Vatican.va** - Official Vatican documents, encyclicals, and the CCC
- **NewAdvent.org** - Church Fathers, Catholic Encyclopedia, Summa Theologica
- **Catechism of the Catholic Church** - Full paragraph lookup and search

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/theological-review-agent.git
cd theological-review-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your API keys to `.env`:
   ```
   MAGISTERIUM_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

## Usage

### Review a Blog Post

```bash
# Review a local file
theo-review review ./my-blog-post.md

# Review from URL
theo-review review https://example.com/blog/my-post

# Save review to file
theo-review review ./post.md -o review.md
```

### Quick Doctrinal Check

```bash
theo-review check "The Eucharist is the real presence of Christ"
```

### Verify a Citation

```bash
theo-review verify "Christ is truly present" "CCC" --ref 1374
```

### Look Up Catechism

```bash
theo-review catechism 1374
```

### Search Sources

```bash
# Search all sources
theo-review search "transubstantiation"

# Search specific source
theo-review search "transubstantiation" --source catechism
theo-review search "Augustine" --source fathers
```

## Programmatic Usage

```python
import asyncio
from theological_review import review_blog_post

async def main():
    blog_content = """
    Title: Understanding the Eucharist

    The Catholic Church teaches that in the Eucharist, the bread and wine
    truly become the Body and Blood of Christ. As the Catechism states...
    """

    review = await review_blog_post(blog_content)
    print(review)

asyncio.run(main())
```

## Review Output

The agent produces structured reviews including:

- **Summary** of the post's main theological claims
- **Doctrinal Analysis** table with verification status
- **Citation Verification** results
- **Historical Claims** assessment
- **Critical Issues** that must be corrected
- **Suggested Improvements**
- **Overall Assessment** (Approved / Needs Revision / Major Concerns / Not Recommended)

## Doctrinal Authority Levels

The agent distinguishes between:

| Level | Description |
|-------|-------------|
| **De fide definita** | Defined dogma - must be believed |
| **Sententia certa** | Theologically certain |
| **Sententia communis** | Common teaching |
| **Sententia probabilis** | Probable opinion |
| **Opinio tolerata** | Tolerated opinion |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint code
ruff check src/
```

## License

MIT License - See LICENSE file for details.

## Disclaimer

This tool is intended to assist human reviewers, not replace them. All reviews should be verified by qualified theologians before making publication decisions.
