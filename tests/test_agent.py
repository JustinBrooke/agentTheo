"""Tests for the main theological review agent."""

import pytest
from pathlib import Path

from theological_review.agent import get_system_prompt, create_review_agent


class TestAgentConfiguration:
    """Tests for agent configuration."""

    def test_get_system_prompt_returns_content(self):
        """Test that system prompt is loaded."""
        prompt = get_system_prompt()

        assert len(prompt) > 100
        assert "theological" in prompt.lower() or "Catholic" in prompt

    def test_create_review_agent_returns_options(self):
        """Test that agent options are created correctly."""
        options = create_review_agent()

        assert options is not None
        assert options.system_prompt is not None
        assert "Read" in options.allowed_tools


class TestReviewExamples:
    """Test cases with example blog posts."""

    GOOD_POST = """
    Title: The Real Presence of Christ in the Eucharist

    The Catholic Church teaches that in the Eucharist, the bread and wine
    truly become the Body, Blood, Soul, and Divinity of Jesus Christ.
    This is known as transubstantiation.

    As the Catechism of the Catholic Church states:
    "In the most blessed sacrament of the Eucharist 'the body and blood,
    together with the soul and divinity, of our Lord Jesus Christ and,
    therefore, the whole Christ is truly, really, and substantially contained.'"
    (CCC 1374)

    The Council of Trent defined this doctrine infallibly in 1551,
    declaring that the change of the whole substance of bread into the
    substance of the Body of Christ is most aptly called transubstantiation.
    """

    BAD_POST = """
    Title: Understanding the Eucharist

    The Catholic Church teaches that the Eucharist is merely a symbol of
    Christ's presence, as St. Augustine said, "Believe, and you have eaten."
    The Council of Trent declared that the bread "represents" Christ's body.

    CCC 1374 states that Christ is "figuratively" present in the Eucharist,
    similar to how we might say a photo "is" a person.

    The doctrine of the Real Presence was invented in the 13th century
    by St. Thomas Aquinas and was not believed by the early Church.
    """

    def test_good_post_structure(self):
        """Verify good post has proper citations."""
        assert "CCC 1374" in self.GOOD_POST
        assert "Council of Trent" in self.GOOD_POST

    def test_bad_post_has_errors(self):
        """Verify bad post contains theological errors for testing."""
        # These are intentional errors to test detection
        assert "merely a symbol" in self.BAD_POST  # Incorrect teaching
        assert "figuratively" in self.BAD_POST  # Misquote of CCC
        assert "invented in the 13th century" in self.BAD_POST  # Historical error


# Sample posts for integration testing
SAMPLE_POSTS = {
    "eucharist_good": """
        The Real Presence of Christ in the Eucharist is a dogma of the Catholic faith.
        The Catechism teaches: "the body and blood, together with the soul and divinity,
        of our Lord Jesus Christ... is truly, really, and substantially contained" (CCC 1374).
    """,

    "eucharist_bad": """
        Catholics believe the Eucharist is a symbolic remembrance of the Last Supper.
        As Pope Francis said, "the bread represents Christ's spiritual presence."
    """,

    "mary_good": """
        The Blessed Virgin Mary was assumed body and soul into heavenly glory.
        This was solemnly defined by Pope Pius XII in Munificentissimus Deus (1950).
        CCC 966 confirms: "The Immaculate Virgin... was taken up body and soul
        into heavenly glory."
    """,

    "trinity_good": """
        The Holy Trinity is the central mystery of Christian faith. God is one
        in essence but three in Persons: Father, Son, and Holy Spirit.
        As the Council of Constantinople (381) affirmed in the Nicene Creed,
        the Son is "consubstantial with the Father."
    """,
}
