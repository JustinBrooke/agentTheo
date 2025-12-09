"""Tests for theological source tools."""

import pytest
from unittest.mock import AsyncMock, patch

from theological_review.tools.magisterium import query_magisterium
from theological_review.tools.vatican import search_catechism, search_vatican_documents
from theological_review.tools.newadvent import search_church_fathers, search_encyclopedia
from theological_review.tools.citation import verify_citation, extract_citations_from_text


class TestMagisteriumTool:
    """Tests for Magisterium.com API tool."""

    @pytest.mark.asyncio
    async def test_query_magisterium_missing_api_key(self, monkeypatch):
        """Test that missing API key raises an error."""
        monkeypatch.delenv("MAGISTERIUM_API_KEY", raising=False)

        with pytest.raises(ValueError, match="MAGISTERIUM_API_KEY"):
            await query_magisterium("test query")

    @pytest.mark.asyncio
    async def test_query_magisterium_success(self, monkeypatch):
        """Test successful API query."""
        monkeypatch.setenv("MAGISTERIUM_API_KEY", "test_key")

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"answer": "Test response"}

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            result = await query_magisterium("What is the Eucharist?")

        assert result["status"] == "success"


class TestVaticanTools:
    """Tests for Vatican.va tools."""

    @pytest.mark.asyncio
    async def test_search_catechism_requires_parameter(self):
        """Test that search_catechism requires at least one parameter."""
        result = await search_catechism()
        assert "error" in result

    @pytest.mark.asyncio
    async def test_search_catechism_by_paragraph(self):
        """Test CCC paragraph lookup."""
        # This test would need mocking for actual HTTP calls
        pass


class TestNewAdventTools:
    """Tests for NewAdvent.org tools."""

    @pytest.mark.asyncio
    async def test_search_church_fathers(self):
        """Test Church Fathers search."""
        # Would need mocking
        pass


class TestCitationTools:
    """Tests for citation verification tools."""

    def test_extract_citations_quoted_with_parentheses(self):
        """Test extraction of citations with parenthetical attribution."""
        text = 'As the Church teaches, "Faith is a gift of God" (CCC 153).'
        citations = extract_citations_from_text(text)

        assert len(citations) >= 1

    def test_extract_citations_ccc_reference(self):
        """Test extraction of CCC paragraph references."""
        text = "According to CCC 1374, Christ is truly present in the Eucharist."
        citations = extract_citations_from_text(text)

        assert any("1374" in str(c) for c in citations)

    def test_extract_citations_multiple(self):
        """Test extraction of multiple citations."""
        text = '''
        "The Eucharist is the source" (Vatican II, Lumen Gentium).
        CCC 1324 states this is the summit of Christian life.
        As Augustine said, "Believe, and you have eaten."
        '''
        citations = extract_citations_from_text(text)

        assert len(citations) >= 2


class TestCitationVerification:
    """Tests for citation verification logic."""

    @pytest.mark.asyncio
    async def test_verify_citation_catechism(self):
        """Test CCC citation verification."""
        result = await verify_citation(
            quoted_text="Test quote",
            claimed_source="CCC",
            reference="1374",
        )

        assert "quoted_text" in result
        assert "verified" in result

    @pytest.mark.asyncio
    async def test_verify_citation_unknown_source(self):
        """Test verification of unknown source type."""
        result = await verify_citation(
            quoted_text="Some quote",
            claimed_source="Unknown Source",
            reference=None,
        )

        assert result["confidence"] == 0.0
        assert "Unable to verify" in result["notes"]
