import requests
import json
from typing import Optional, Dict, Any
from config import GEMINI_API_KEY, ACTIVE_GEMINI_MODELS, get_gemini_endpoint
from models import ExtractedLead, StoredLead

EXTRACTION_SYSTEM_INSTRUCTION = """
You are a precision AI Lead Extraction and Verification specialist for Indian Real Estate, focusing on Kolkata, West Bengal, and requested regional markets (e.g. Digha, Siliguri, Howrah).
Your task is to analyze web snippets and extract structured real estate lead signals across Residential, Commercial, Land, Hotel, Bar/Restaurant, and Joint Venture (JV) deals.

Strict Rules:
1. Deal Types:
   - "OUTRIGHT": Clean title 100% full sale or purchase of property, land, hotel, or commercial unit.
   - "JOINT_VENTURE": Landowner looking for a builder/developer to construct in partnership (or developer seeking JV land). Joint development agreements, profit/area sharing.
   - "LEASE": Long-term commercial lease or operational transfer (e.g. operational hotel on lease, running bar/restaurant lease).
   - "RENTAL": Standard rental.
   - "UNKNOWN": Unspecified deal structure.

2. Property Categories:
   - "LAND": Plots, raw land, commercial land, industrial plot, bigha, kottah, acres.
   - "HOTEL": Running hotel, boutique hotel, resort, guest house, lodge.
   - "BAR_CUM_RESTAURANT": Bar & restaurant with liquor license, pub, lounge, operational food & beverage establishment.
   - "COMMERCIAL": Office space, IT park floor, commercial building, showroom, retail shop.
   - "RESIDENTIAL_APARTMENT": Flat, 1BHK, 2BHK, 3BHK, 4BHK apartment.
   - "INDEPENDENT_HOUSE": Standalone building, bungalow, villa.
   - "OTHER": Farmhouse, warehouse, etc.

3. Lead Classification:
   - "DEVELOPER": Real estate developer, builder, or construction group acquiring land parcels or seeking JV development.
   - "LANDOWNER": Direct property/land owner, titleholder offering land for outright sale or JV development.
   - "INVESTOR": Institutional realty fund, private equity, or commercial investor looking for land or commercial assets.
   - "BUYER": Prospective commercial or residential buyer or tenant.
   - "SELLER": Direct business/property owner selling hotel, bar/restaurant, commercial building, or house.
   - "AGENT": Commercial broker, dealer, or agency pitching representation for commission.
   - "UNKNOWN": Generic blog, news article, or irrelevant discussion.

4. Factual Grounding & Tone Principles:
   - DO NOT fabricate leads, companies, contact information, transactions, or property requirements.
   - DO NOT claim that a company is interested in buying property unless there is concrete evidence in the snippet supporting that conclusion.
   - Always formulate `confidence_rationale` using careful language: "Potentially relevant because..." followed strictly by what the evidence indicates.

5. Geographic Location Extraction:
   - Extract the specific locality or town (e.g. "Park Street", "Digha", "Salt Lake Sector 5", "New Town Action Area 1", "Rajarhat", "Siliguri", "Ballygunge", "Kalyani", "Howrah").
   - If the snippet clearly relates to a foreign or non-Indian city, mark confidence_score = 0.0.

6. Pricing & Conversion:
   - Convert Indian price notations into full numeric INR:
     - 45 Lakhs -> 4500000
     - 1.5 Crore -> 15000000
     - 15 Crore -> 150000000
   - Currency: Default to "INR".
"""

def extract_lead_from_source(source: Dict[str, Any], query_id: Optional[str] = None) -> Optional[StoredLead]:
    """
    Analyzes a web source (title + content snippet + url) with LLM
    and produces a validated StoredLead instance.
    """
    title = source.get("title", "")
    content = source.get("content", "")
    url = source.get("url", "")
    
    if not content or len(content.strip()) < 30:
        return None

    prompt = f"""
Analyze the following web source for real estate developer, landowner, buyer, seller, or investor signals:

Title: {title}
URL: {url}
Content Snippet:
\"\"\"
{content}
\"\"\"

Extract the lead details into this exact JSON structure:
{{
  "company": "Company, developer firm, investor fund, or organization name if identified or null",
  "lead_type": "DEVELOPER" | "LANDOWNER" | "INVESTOR" | "BUYER" | "SELLER" | "AGENT" | "UNKNOWN",
  "deal_type": "OUTRIGHT" | "JOINT_VENTURE" | "LEASE" | "RENTAL" | "UNKNOWN",
  "property_category": "LAND" | "HOTEL" | "BAR_CUM_RESTAURANT" | "COMMERCIAL" | "RESIDENTIAL_APARTMENT" | "INDEPENDENT_HOUSE" | "OTHER",
  "is_direct_party": boolean,
  "confidence_score": float between 0.0 and 1.0,
  "confidence_rationale": "Must start with 'Potentially relevant because...' followed by factual evidence from snippet",
  "intent_summary": "1-2 sentence description of the person's specific need or offer",
  "location_raw": "Specific locality or town (e.g. Park Street, Digha, Salt Lake Sector 5, New Town, Rajarhat, Siliguri) or null",
  "city": "City or district name (e.g. Kolkata, Purba Medinipur, Darjeeling/Siliguri)",
  "state": "West Bengal",
  "property_type": "Specific type: Large Land Parcel, Commercial Land, 3-Star Hotel, Running Bar & Restaurant, 3BHK Flat, etc.",
  "commercial_details": "Key commercial specifications if applicable: liquor license status, hotel room/key count, land size in Cottah/Bigha/Acres, JV ratio, road frontage or null",
  "bedrooms": integer (or room/key count for hotel) or null,
  "bathrooms": float or null,
  "area_sqft": float or null,
  "budget_or_price": float numeric value in INR (e.g. 25000000 for 2.5 Crore) or null,
  "currency": "INR",
  "contact_name": "poster or executive name/handle or null",
  "contact_email": "public email if present or null",
  "contact_phone": "public phone if present or null",
  "contact_social_handle": "Reddit/LinkedIn/Twitter handle or null",
  "urgency": "IMMEDIATE" | "1_TO_3_MONTHS" | "FLEXIBLE" | "UNKNOWN",
  "verified_date": "Date of publication or source if mentioned (e.g. October 2024) or null"
}}
"""

    import key_manager
    from config import ACTIVE_GEMINI_MODELS, get_gemini_endpoint

    active_llm = key_manager.get_active_llm()
    provider = active_llm.get("provider", "gemini")
    active_key = active_llm.get("api_key", "")
    active_model = active_llm.get("model", "gemini-flash-latest")

    data = None

    if provider in ["openai", "groq"]:
        endpoint = "https://api.openai.com/v1/chat/completions" if provider == "openai" else "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {active_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": active_model,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_INSTRUCTION},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }
        try:
            res = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                content_str = res.json()["choices"][0]["message"]["content"]
                data = json.loads(content_str)
        except Exception as e:
            print(f"[{provider.upper()} Extraction Error] {e}")

    elif provider == "gemini":
        models_to_try = [active_model] + [m for m in ACTIVE_GEMINI_MODELS if m != active_model]
        for model in models_to_try:
            api_url = f"{get_gemini_endpoint(model)}?key={active_key}"
            payload = {
                "contents": [
                    {"parts": [{"text": EXTRACTION_SYSTEM_INSTRUCTION + "\n\n" + prompt}]}
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2
                }
            }
            try:
                res = requests.post(api_url, json=payload, timeout=30)
                if res.status_code == 200:
                    result_text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    data = json.loads(result_text)
                    break
                elif res.status_code == 429:
                    continue
            except Exception:
                continue

    if not data:
        return None

    if isinstance(data, list):
        if len(data) > 0 and isinstance(data[0], dict):
            data = data[0]
        else:
            return None

    try:
        # Validate through Pydantic
        extracted = ExtractedLead(**data)
        
        # Reject if not relevant to India / Kolkata
        if extracted.lead_type == "UNKNOWN" and extracted.confidence_score <= 0.1:
            return None

        # Generate deduplication ID
        lead_id = StoredLead.generate_id(
            url=url,
            contact_phone=extracted.contact_phone,
            contact_email=extracted.contact_email
        )
        
        stored_lead = StoredLead(
            id=lead_id,
            query_id=query_id,
            source_url=url,
            source_title=title,
            raw_content_snippet=content[:1500],
            **extracted.model_dump()
        )
        return stored_lead
    except Exception as e:
        print(f"[Lead Parsing Error] {e}")
        return None
