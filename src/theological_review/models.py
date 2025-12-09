"""Pydantic models for structured theological review output."""

from enum import Enum
from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    """Overall status of a theological review."""
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    MAJOR_CONCERNS = "major_concerns"
    NOT_RECOMMENDED = "not_recommended"


class DoctrinalLevel(str, Enum):
    """Levels of Catholic doctrinal authority."""
    DE_FIDE = "de_fide"  # Defined dogma - must be believed
    SENTENTIA_CERTA = "sententia_certa"  # Theologically certain
    SENTENTIA_COMMUNIS = "sententia_communis"  # Common teaching
    SENTENTIA_PROBABILIS = "sententia_probabilis"  # Probable opinion
    THEOLOGICAL_OPINION = "theological_opinion"  # Acceptable speculation


class VerificationStatus(str, Enum):
    """Status of a verification check."""
    VERIFIED = "verified"
    WARNING = "warning"
    ERROR = "error"
    UNABLE_TO_VERIFY = "unable_to_verify"


class DoctrinalIssue(BaseModel):
    """A single doctrinal claim and its verification status."""
    claim: str = Field(description="The doctrinal claim made in the blog post")
    source_checked: str = Field(description="The authoritative source used to verify")
    status: VerificationStatus = Field(description="Verification status")
    doctrinal_level: DoctrinalLevel | None = Field(
        default=None, description="Level of doctrinal authority if applicable"
    )
    catechism_reference: str | None = Field(
        default=None, description="Relevant CCC paragraph number"
    )
    explanation: str = Field(description="Detailed explanation of the finding")


class CitationIssue(BaseModel):
    """A citation verification result."""
    quoted_text: str = Field(description="The text as quoted in the blog post")
    claimed_source: str = Field(description="The source claimed by the author")
    claimed_reference: str | None = Field(
        default=None, description="Specific paragraph, page, or section cited"
    )
    status: VerificationStatus = Field(description="Whether the citation is accurate")
    actual_text: str | None = Field(
        default=None, description="What the source actually says, if different"
    )
    notes: str = Field(description="Explanation of any discrepancies")


class HistoricalIssue(BaseModel):
    """A historical claim verification result."""
    claim: str = Field(description="The historical claim made")
    status: VerificationStatus = Field(description="Verification status")
    correct_information: str | None = Field(
        default=None, description="Accurate information if the claim is wrong"
    )
    sources: list[str] = Field(default_factory=list, description="Sources consulted")
    notes: str = Field(description="Additional context or explanation")


class TheologicalReview(BaseModel):
    """Complete theological review of a blog post."""
    title: str = Field(description="Title of the reviewed blog post")
    summary: str = Field(description="Brief summary of the post's main theological claims")

    doctrinal_issues: list[DoctrinalIssue] = Field(
        default_factory=list, description="Doctrinal claims and their verification"
    )
    citation_issues: list[CitationIssue] = Field(
        default_factory=list, description="Citation verification results"
    )
    historical_issues: list[HistoricalIssue] = Field(
        default_factory=list, description="Historical claim verification results"
    )

    critical_errors: list[str] = Field(
        default_factory=list, description="Issues that must be corrected before publishing"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Recommended improvements"
    )
    additional_sources: list[str] = Field(
        default_factory=list, description="Suggested sources to cite for stronger support"
    )

    overall_status: ReviewStatus = Field(description="Overall review status")
    reviewer_notes: str = Field(
        default="", description="Additional notes from the review"
    )
