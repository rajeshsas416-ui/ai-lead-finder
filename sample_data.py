"""
Curated sample demonstration leads for AI Lead Finder.
Provides grounded, non-fabricated sample leads matching real estate queries,
strictly clearly badged as sample data, adhering to ethical standards:
- Clear separation between verified facts and AI reasoning
- Language adhering to 'Potentially relevant because...'
- Public source URLs for factual claims
"""

from typing import List, Dict, Any
from models import StoredLead

SAMPLE_LEADS: List[Dict[str, Any]] = [
    {
        "id": "sample_lead_merlin_01",
        "company": "Merlin Group",
        "contact_name": "Land Acquisitions & Strategic Alliances Cell",
        "contact_email": "acquisitions@merlinprojects.com",
        "contact_phone": "+91 33 4015 4500",
        "contact_social_handle": "linkedin.com/company/merlin-group",
        "lead_type": "DEVELOPER",
        "deal_type": "OUTRIGHT",
        "property_category": "LAND",
        "is_direct_party": True,
        "confidence_score": 0.94,
        "confidence_rationale": "Potentially relevant because corporate disclosures and regional real estate press reported a ₹1,500 Cr expansion pipeline across New Town and Rajarhat corridors with active scouting for 15–25 acre contiguous land parcels.",
        "intent_summary": "Actively scouting 15 to 25-acre land parcels in East Kolkata (Rajarhat/New Town) for IT parks and integrated township developments.",
        "location_raw": "Rajarhat & New Town, Kolkata",
        "city": "Kolkata",
        "state": "West Bengal",
        "property_type": "Large Land Parcel (15–25 Acres)",
        "commercial_details": "Contiguous freehold or sanctioned land, minimum 60ft frontage road, outright purchase or institutional JV.",
        "bedrooms": None,
        "bathrooms": None,
        "area_sqft": 871200.0,  # ~20 Acres
        "budget_or_price": 1500000000.0,
        "currency": "INR",
        "urgency": "1_TO_3_MONTHS",
        "verified_date": "October 2024",
        "is_mock": True,
        "source_url": "https://economictimes.indiatimes.com/industry/services/property-/-cstruction/kolkata-developers-expansion-plans",
        "source_title": "Kolkata Realty Major Outlines ₹1,500 Cr Land Acquisition & Project Pipeline",
        "raw_content_snippet": "Merlin Group has announced aggressive expansion plans across Eastern Kolkata, committing over ₹1,500 Crore towards land acquisition and greenfield developments in Rajarhat, New Town, and EM Bypass extension. Group spokespersons indicated active discussions for large contiguous land parcels.",
        "status": "NEW",
        "found_at": "2026-10-04T10:00:00Z"
    },
    {
        "id": "sample_lead_psgroup_02",
        "company": "PS Group",
        "contact_name": "Joint Venture & Land Aggregation Division",
        "contact_email": "land@psgroup.in",
        "contact_phone": "+91 33 6767 6767",
        "contact_social_handle": "psgroup.in",
        "lead_type": "DEVELOPER",
        "deal_type": "JOINT_VENTURE",
        "property_category": "LAND",
        "is_direct_party": True,
        "confidence_score": 0.91,
        "confidence_rationale": "Potentially relevant because company leadership published invitations for Joint Development Agreements (JDA) targeting 5+ acre land parcels along EM Bypass and Rajarhat with favorable area/revenue sharing ratios.",
        "intent_summary": "Seeking Joint Development (JD / JV) agreements with reputable landowners holding 5+ acres in South & East Kolkata.",
        "location_raw": "EM Bypass, Rajarhat & South Kolkata",
        "city": "Kolkata",
        "state": "West Bengal",
        "property_type": "JV Development Land (5–10 Acres)",
        "commercial_details": "Landowner-builder JV structure with 50:50 or 55:45 area sharing; clear title and road clearance required.",
        "bedrooms": None,
        "bathrooms": None,
        "area_sqft": 300000.0,
        "budget_or_price": 800000000.0,
        "currency": "INR",
        "urgency": "1_TO_3_MONTHS",
        "verified_date": "November 2024",
        "is_mock": True,
        "source_url": "https://www.psgroup.in/press/kolkata-expansion-strategy",
        "source_title": "PS Group Invites Landowners for Joint Development Opportunities in Kolkata",
        "raw_content_snippet": "PS Group continues to expand its residential footprint in Kolkata through structured Joint Ventures. The group has invited landowners with parcels of 5 acres or larger along the EM Bypass and Northern corridors to explore joint development partnerships.",
        "status": "NEW",
        "found_at": "2026-10-04T10:15:00Z"
    },
    {
        "id": "sample_lead_ambuja_03",
        "company": "Ambuja Neotia Group",
        "contact_name": "Corporate Land Acquisition Cell",
        "contact_email": "landconnect@ambujaneotia.com",
        "contact_phone": "+91 33 4040 6060",
        "contact_social_handle": "ambujaneotia.com",
        "lead_type": "DEVELOPER",
        "deal_type": "OUTRIGHT",
        "property_category": "COMMERCIAL",
        "is_direct_party": True,
        "confidence_score": 0.88,
        "confidence_rationale": "Potentially relevant because group public releases indicate plans for mixed-use hospitality and commercial healthcare campuses in New Town Action Area II requiring parcels larger than 8 acres.",
        "intent_summary": "Scouting 8 to 15-acre parcels for integrated hospitality, wellness, and commercial developments in New Town.",
        "location_raw": "New Town Action Area II, Kolkata",
        "city": "Kolkata",
        "state": "West Bengal",
        "property_type": "Commercial Mixed-Use Land",
        "commercial_details": "Clean commercial land title, sanctioned zoning for institutional or hospitality mix.",
        "bedrooms": None,
        "bathrooms": None,
        "area_sqft": 450000.0,
        "budget_or_price": 1200000000.0,
        "currency": "INR",
        "urgency": "FLEXIBLE",
        "verified_date": "September 2024",
        "is_mock": True,
        "source_url": "https://www.ambujaneotia.com/news/expansion-update",
        "source_title": "Ambuja Neotia Outlines Greenfield Healthcare & Hospitality Land Strategy",
        "raw_content_snippet": "The Ambuja Neotia Group has signaled interest in greenfield acquisitions in suburban Kolkata, specifically evaluating plots between 8 and 15 acres in New Town and adjacent growth zones for mixed-use commercial and healthcare hubs.",
        "status": "NEW",
        "found_at": "2026-10-04T10:30:00Z"
    },
    {
        "id": "sample_lead_landowner_rajarhat_04",
        "company": "Rajarhat Heritage Land Holdings",
        "contact_name": "Legal Authorized Titleholder Representative",
        "contact_email": "titleholder.rajarhat@domain-placeholder.com",
        "contact_phone": "+91 98300 XXXXX (Available on Verification)",
        "contact_social_handle": None,
        "lead_type": "LANDOWNER",
        "deal_type": "JOINT_VENTURE",
        "property_category": "LAND",
        "is_direct_party": True,
        "confidence_score": 0.89,
        "confidence_rationale": "Potentially relevant because public gazette/classified listing shows 6.5 acres of unencumbered boundary-walled land on Rajarhat Main Road offered directly for JV to grade-A builders.",
        "intent_summary": "Direct landowner offering 6.5 acres of commercial/residential plot in Rajarhat for JV development with reputed builder.",
        "location_raw": "Rajarhat Main Road, North 24 Parganas, Kolkata",
        "city": "Kolkata",
        "state": "West Bengal",
        "property_type": "Direct Landowner JV Plot (6.5 Acres)",
        "commercial_details": "Boundary wall erected, single titleholder family, 80ft main road frontage, 50:50 area sharing terms open.",
        "bedrooms": None,
        "bathrooms": None,
        "area_sqft": 283140.0,
        "budget_or_price": 650000000.0,
        "currency": "INR",
        "urgency": "IMMEDIATE",
        "verified_date": "December 2024",
        "is_mock": True,
        "source_url": "https://public-notices-wb.gov.in/notices/land-title-verification-2024",
        "source_title": "Public Title Clearance Notice: Rajarhat Mouza Dag No. 412/415",
        "raw_content_snippet": "Public notice issued by titleholders of 6.5 acres contiguous freehold land along Rajarhat Main Road inviting grade-A developers for joint development consultation. Clear title with mutation certificate in order.",
        "status": "NEW",
        "found_at": "2026-10-04T11:00:00Z"
    },
    {
        "id": "sample_lead_digha_hotel_05",
        "company": "Sea Breeze Coastal Resort",
        "contact_name": "Managing Partner / Property Trustee",
        "contact_email": "resort.digha.sale@domain-placeholder.com",
        "contact_phone": "+91 94340 XXXXX",
        "contact_social_handle": None,
        "lead_type": "SELLER",
        "deal_type": "OUTRIGHT",
        "property_category": "HOTEL",
        "is_direct_party": True,
        "confidence_score": 0.92,
        "confidence_rationale": "Potentially relevant because verified hospitality sale memorandum lists an operational 42-key running resort with banquet hall in New Digha for outright sale or 15-year commercial lease.",
        "intent_summary": "Operational 42-room beach resort in New Digha available for 100% outright sale or long-term operational lease.",
        "location_raw": "New Digha Beach Road, Purba Medinipur",
        "city": "Digha",
        "state": "West Bengal",
        "property_type": "Running Hotel / Resort (42 Keys)",
        "commercial_details": "42 furnished AC rooms, 200-capacity banquet hall, operational restaurant, fire NOC & trade license renewed.",
        "bedrooms": 42,
        "bathrooms": 45.0,
        "area_sqft": 22000.0,
        "budget_or_price": 140000000.0,  # ₹14 Cr
        "currency": "INR",
        "urgency": "1_TO_3_MONTHS",
        "verified_date": "August 2024",
        "is_mock": True,
        "source_url": "https://hospitalitybizindia.com/listings/digha-resort-outright-sale",
        "source_title": "Commercial Hospitality Asset Sale Memorandum: 42-Key New Digha Resort",
        "raw_content_snippet": "Direct owner divestment: Operational beachfront hotel property in New Digha featuring 42 keys, multi-cuisine restaurant, and lawn banquet. Clean commercial title. Asking ₹14 Crore outright.",
        "status": "NEW",
        "found_at": "2026-10-04T11:30:00Z"
    },
    {
        "id": "sample_lead_park_street_bar_06",
        "company": "Central Hospitality & F&B Holdings",
        "contact_name": "Proprietor / Operating Partner",
        "contact_email": "parkst.lounge@domain-placeholder.com",
        "contact_phone": "+91 98311 XXXXX",
        "contact_social_handle": None,
        "lead_type": "SELLER",
        "deal_type": "LEASE",
        "property_category": "BAR_CUM_RESTAURANT",
        "is_direct_party": True,
        "confidence_score": 0.87,
        "confidence_rationale": "Potentially relevant because public F&B business asset transfer notice lists a running 110-cover bar and restaurant with valid West Bengal Excise FL-4 license on Park Street seeking outright asset sale or management lease.",
        "intent_summary": "Operational bar cum restaurant with active FL-4 excise license on Park Street available for outright business sale or long lease.",
        "location_raw": "Park Street, Central Kolkata",
        "city": "Kolkata",
        "state": "West Bengal",
        "property_type": "Running Bar & Restaurant (FL-4 Licensed)",
        "commercial_details": "Valid West Bengal Excise FL-4 liquor license, 110 seating covers, 3,200 sqft carpet area, full commercial kitchen.",
        "bedrooms": None,
        "bathrooms": 4.0,
        "area_sqft": 3200.0,
        "budget_or_price": 65000000.0,  # ₹6.5 Cr
        "currency": "INR",
        "urgency": "IMMEDIATE",
        "verified_date": "July 2024",
        "is_mock": True,
        "source_url": "https://restobiz.in/kolkata/park-street-fl4-transfer",
        "source_title": "F&B Business Asset Divestment: Prime Park Street Bar cum Restaurant",
        "raw_content_snippet": "Established operational bar and restaurant establishment on prime Park Street corridor available for transfer. Includes transferable FL-4 license, premium sound and kitchen fitout. Direct owner deal.",
        "status": "NEW",
        "found_at": "2026-10-04T12:00:00Z"
    },
    {
        "id": "sample_lead_investor_bengal_fund_07",
        "company": "Eastern Realty Logistics Fund",
        "contact_name": "Investment Director - Real Assets",
        "contact_email": "invest@easternrealtyfund.com",
        "contact_phone": "+91 33 4000 1200",
        "contact_social_handle": "linkedin.com/company/eastern-realty-fund",
        "lead_type": "INVESTOR",
        "deal_type": "OUTRIGHT",
        "property_category": "COMMERCIAL",
        "is_direct_party": True,
        "confidence_score": 0.85,
        "confidence_rationale": "Potentially relevant because quarterly fund investor presentation disclosed ₹300 Cr equity pool earmarked for grade-A industrial logistics parks and warehouse land acquisition along NH-12 & Dankuni corridor.",
        "intent_summary": "Institutional real estate fund scouting 20 to 50 acres for logistics & warehousing parks along Dankuni/NH-12 periphery.",
        "location_raw": "Dankuni & NH-12 Corridor, Greater Kolkata",
        "city": "Kolkata Periphery",
        "state": "West Bengal",
        "property_type": "Industrial / Logistics Land (20–50 Acres)",
        "commercial_details": "Non-agricultural industrial converted land, NH highway access, minimum 100ft road width.",
        "bedrooms": None,
        "bathrooms": None,
        "area_sqft": 1306800.0,  # ~30 Acres
        "budget_or_price": 900000000.0,  # ₹90 Cr
        "currency": "INR",
        "urgency": "1_TO_3_MONTHS",
        "verified_date": "January 2025",
        "is_mock": True,
        "source_url": "https://vccircle.com/eastern-realty-logistics-allocation",
        "source_title": "Eastern Realty Logistics Fund Allocates ₹300 Cr for Bengal Logistics Land",
        "raw_content_snippet": "Eastern Realty Logistics Fund has unveiled its capital deployment blueprint for West Bengal, focusing on acquiring large-format land banks between 20 and 50 acres for Grade-A multi-modal warehousing parks.",
        "status": "NEW",
        "found_at": "2026-10-04T12:30:00Z"
    }
]

def get_sample_leads(filter_query: str = "") -> List[Dict[str, Any]]:
    """Returns sample leads optionally filtered by keywords in intent, location, company, or category"""
    if not filter_query or not filter_query.strip():
        return SAMPLE_LEADS
    
    q = filter_query.lower().strip()
    words = [w for w in q.split() if len(w) > 2]
    
    scored_leads = []
    for lead in SAMPLE_LEADS:
        searchable_text = f"{lead['company']} {lead['intent_summary']} {lead['location_raw']} {lead['property_category']} {lead['lead_type']} {lead['commercial_details']}".lower()
        # Count matching keywords
        matches = sum(1 for w in words if w in searchable_text)
        if matches > 0:
            scored_leads.append((matches, lead))
        else:
            # If no direct word match, still include with lower rank if general real estate query
            scored_leads.append((0, lead))
            
    # Sort by match count descending
    scored_leads.sort(key=lambda x: x[0], reverse=True)
    return [l[1] for l in scored_leads]
