from typing import Optional, Literal
from pydantic import BaseModel, Field
import hashlib
from datetime import datetime, timezone


LeadType = Literal["DEVELOPER", "LANDOWNER", "INVESTOR", "BUYER", "SELLER", "AGENT", "UNKNOWN"]
DealType = Literal["OUTRIGHT", "JOINT_VENTURE", "LEASE", "RENTAL", "UNKNOWN"]
PropertyCategory = Literal["LAND", "HOTEL", "BAR_CUM_RESTAURANT", "COMMERCIAL", "RESIDENTIAL_APARTMENT", "INDEPENDENT_HOUSE", "OTHER"]
UrgencyType = Literal["IMMEDIATE", "1_TO_3_MONTHS", "FLEXIBLE", "UNKNOWN"]
LeadStatus = Literal["NEW", "VERIFIED", "CONTACTED", "ARCHIVED", "REJECTED"]

class ExtractedLead(BaseModel):
    """Structured extraction output directly from the LLM or sample intelligence generator"""
    company: Optional[str] = Field(
        None,
        description="Company, developer firm, investor fund, or organization name if identified."
    )
    lead_type: str = Field(
        ..., 
        description="DEVELOPER, LANDOWNER, INVESTOR, BUYER, SELLER, AGENT, or UNKNOWN."
    )
    deal_type: DealType = Field(
        "OUTRIGHT",
        description="Deal structure: OUTRIGHT (direct full sale/purchase), JOINT_VENTURE (landowner-builder JV / JD partnership), LEASE (commercial long lease), RENTAL, or UNKNOWN."
    )
    property_category: PropertyCategory = Field(
        "OTHER",
        description="Primary category: LAND (plots, bigha, kottah, commercial land), HOTEL (resort, guest house, lodge), BAR_CUM_RESTAURANT (restaurant, pub, bar with liquor license), COMMERCIAL (office, shop, showroom), RESIDENTIAL_APARTMENT, INDEPENDENT_HOUSE, or OTHER."
    )
    is_direct_party: bool = Field(
        ..., 
        description="True if this is the actual prospective developer, buyer, investor, or direct property/land owner, False if an agent/broker/firm."
    )
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Relevance / Confidence score between 0.0 and 1.0 that this lead matches user query."
    )
    confidence_rationale: str = Field(
        ..., 
        description="Reason for relevance: strictly formatted starting with 'Potentially relevant because...' explaining why the lead fits based on evidence."
    )
    intent_summary: str = Field(
        ..., 
        description="A concise 1-2 sentence description of the lead's verified public need or offer."
    )
    
    # Location details
    location_raw: Optional[str] = Field(None, description="Raw location mentioned (e.g. Park Street, Digha, Salt Lake Sector 5, New Town, Rajarhat, Siliguri)")
    city: Optional[str] = Field(None, description="City or district name if identifiable")
    state: Optional[str] = Field(None, description="State, province, or region")
    
    # Property & Deal details
    property_type: Optional[str] = Field(
        None, 
        description="Detailed type: Commercial Land Parcel, 3-Star Hotel, Running Bar & Restaurant, Joint Venture Land, 3BHK Flat, etc."
    )
    commercial_details: Optional[str] = Field(
        None,
        description="Specific commercial / JV details: e.g. 'Scouting 15-25 acre land parcels', 'Operational bar with on-shop liquor license', '35-key hotel with banquet', '5 Bigha JV land with 50:50 ratio', 'Road frontage 60ft'."
    )
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms or hotel room count if specified")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms if specified")
    area_sqft: Optional[float] = Field(None, description="Square footage or area in sqft if specified")
    budget_or_price: Optional[float] = Field(None, description="Numeric budget (for buyer/developer) or asking price (for seller) in INR")
    currency: Optional[str] = Field("INR", description="Currency symbol or 3-letter code (INR, USD, etc.)")
    
    # Contact info (strictly public)
    contact_name: Optional[str] = Field(None, description="Name of contact person, executive, or public poster")
    contact_email: Optional[str] = Field(None, description="Publicly posted email address if explicitly visible")
    contact_phone: Optional[str] = Field(None, description="Publicly posted phone number if explicitly visible")
    contact_social_handle: Optional[str] = Field(None, description="Reddit/Twitter/LinkedIn/forum username or handle")
    
    urgency: UrgencyType = Field("UNKNOWN", description="Estimated timeline: IMMEDIATE, 1_TO_3_MONTHS, FLEXIBLE, UNKNOWN")
    verified_date: Optional[str] = Field(None, description="Date of source article, publication, or verification")
    is_mock: bool = Field(False, description="True if this is demonstration sample data, False if from live search")

    @property
    def relevance_score(self) -> float:
        return self.confidence_score

    @property
    def reason_for_relevance(self) -> str:
        return self.confidence_rationale

class StoredLead(ExtractedLead):
    """Lead stored in the database with audit provenance and deduplication hash"""
    id: str = Field(..., description="Unique lead identifier (hash or uuid)")
    source_url: str = Field(..., description="URL of the web source where this lead was found")
    source_title: Optional[str] = Field(None, description="Webpage or post title")
    raw_content_snippet: Optional[str] = Field(None, description="Text snippet analyzed by the LLM")
    query_id: Optional[str] = Field(None, description="ID of the search query that discovered this lead")
    status: LeadStatus = Field("NEW", description="Review status of the lead")
    found_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @staticmethod
    def generate_id(url: str, contact_phone: Optional[str] = None, contact_email: Optional[str] = None) -> str:
        """Generate a deterministic deduplication hash"""
        # Primary key based on normalized canonical URL
        key = url.strip().lower()
        # If contact is available, incorporate to track identity
        if contact_email:
            key += f"|email:{contact_email.strip().lower()}"
        elif contact_phone:
            digits = "".join(filter(str.isdigit, contact_phone))
            if len(digits) >= 7:
                key += f"|phone:{digits[-10:]}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
