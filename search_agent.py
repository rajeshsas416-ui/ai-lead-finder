import os
import requests
import json
from typing import List, Dict, Any
from config import TAVILY_API_KEY, GEMINI_API_KEY, ACTIVE_GEMINI_MODELS, get_gemini_endpoint

def generate_search_queries(user_query: str) -> List[str]:
    """
    Uses Gemini to translate a natural language query into 3 distinct, high-signal
    search queries designed to uncover genuine buyer/seller signals while suppressing agent spam.
    """
    prompt = f"""
    You are an expert real estate lead generation specialist for India, focusing on Kolkata and West Bengal (or any specific location requested by the user).
    Convert this user search request into 3 focused search queries for web search engines to uncover genuine buyer, seller, landowner, or investor leads.
    
    CRITICAL INSTRUCTIONS:
    1. LOCATION ANCHOR:
       - Detect any specific location in the query (e.g. "Park Street", "Salt Lake Sector 5", "Digha", "New Town", "Rajarhat", "Siliguri", "Ballygunge", "Kalyani", "Howrah", etc.).
       - If a specific location is provided, EVERY search query MUST include that location in quotes (e.g. \\"Park Street\\", \\"Digha\\", \\"Salt Lake\\").
       - If no location is specified, anchor to "Kolkata" or "West Bengal".
    
       - **Developers & Land Acquisition**: search for "real estate developer" AND ("land parcel" OR "land acquisition" OR "acquiring land" OR "land bank"), "builder acquiring land", "realty group investments"
       - **Land / Plot**: search for "land for sale", "commercial land", "bigha", "kottah", "plot", "outright land"
       - **Hotel / Resort**: search for "hotel for sale", "hotel on lease", "running hotel", "resort", "guest house"
       - **Bar cum Restaurant**: search for "bar cum restaurant", "bar & restaurant", "liquor license", "pub for sale", "running restaurant"
       - **Joint Venture (JV)**: search for "joint venture" OR "JV", "joint development", "landowner looking for builder", "builder developer JV"
       - **Investors & Funds**: search for "realty fund", "real estate private equity", "warehousing logistics land investment"
       - **Outright Property**: search for "outright sale", "outright purchase", "outright commercial", "clean title"
       - **Residential**: 2BHK/3BHK flats, resale, without broker, direct owner
    
    3. NEGATIVE FILTERS:
       - Suppress brokers, booking portals, directory spam (-commission -zomato -swiggy -booking.com -tripadvisor)
    
    User Query: "{user_query}"
    
    Format: Return ONLY a valid JSON array of 3 search queries. Example:
    [
      "\\"Digha\\" \\"hotel for sale\\" OR \\"hotel on lease\\" direct owner -booking.com",
      "\\"Park Street\\" \\"bar cum restaurant\\" OR \\"liquor license\\" for sale OR lease",
      "\\"New Town\\" \\"joint venture\\" OR \\"JV\\" land developer landowner"
    ]
    """
    
    import key_manager
    from config import ACTIVE_GEMINI_MODELS, get_gemini_endpoint

    active_llm = key_manager.get_active_llm()
    provider = active_llm.get("provider", "gemini")
    active_key = active_llm.get("api_key", "")
    active_model = active_llm.get("model", "gemini-flash-latest")

    if provider in ["openai", "groq"]:
        endpoint = "https://api.openai.com/v1/chat/completions" if provider == "openai" else "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {active_key}", "Content-Type": "application/json"}
        payload = {
            "model": active_model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        try:
            res = requests.post(endpoint, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                raw_json = json.loads(res.json()["choices"][0]["message"]["content"])
                if isinstance(raw_json, list):
                    return raw_json[:3]
                elif isinstance(raw_json, dict) and "queries" in raw_json:
                    return raw_json["queries"][:3]
        except Exception:
            pass

    elif provider == "gemini":
        models_to_try = [active_model] + [m for m in ACTIVE_GEMINI_MODELS if m != active_model]
        for model in models_to_try:
            try:
                url = f"{get_gemini_endpoint(model)}?key={active_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
                res = requests.post(url, json=payload, timeout=15)
                if res.status_code == 200:
                    content = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    queries = json.loads(content)
                    if isinstance(queries, list) and len(queries) > 0:
                        return queries[:3]
                elif res.status_code == 429:
                    continue
            except Exception:
                continue

    # Fallback heuristic queries if LLM call fails
    cleaned = user_query.replace('"', '').strip()
    return [
        f'site:reddit.com/r/kolkata "{cleaned}" -broker -dealer',
        f'Kolkata "{cleaned}" ("direct owner" OR "without broker") -brokerage',
        f'Kolkata flat "{cleaned}" budget Lakhs forum -agent'
    ]

# Real estate & booking directory aggregators to exclude so we get authentic human deal posts
EXCLUDED_DOMAINS = [
    "magicbricks.com", "99acres.com", "housing.com", "makaan.com",
    "commonfloor.com", "squareyards.com", "proptiger.com", "nobroker.in",
    "quikr.com", "olx.in", "zillow.com", "redfin.com", "trulia.com",
    "realtor.com", "homes.com", "wikipedia.org", "youtube.com", "facebook.com/ads",
    "booking.com", "tripadvisor.com", "zomato.com", "swiggy.com",
    "makemytrip.com", "goibibo.com", "agoda.com", "oyorooms.com", "expedia.com"
]

def search_tavily(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Searches the web using the active Tavily Search API key with aggregator exclusions.
    Returns cleaned title, url, and content snippet for each result.
    """
    import key_manager
    tavily_key = key_manager.get_active_search_key()
    if not tavily_key:
        raise ValueError("Tavily API Key is not configured in Key Manager or .env")

    api_url = "https://api.tavily.com/search"
    payload = {
        "api_key": tavily_key,
        "query": query,
        "search_depth": "advanced",
        "include_raw_content": False,
        "max_results": max_results,
        "exclude_domains": EXCLUDED_DOMAINS
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        else:
            print(f"[Tavily Error] Status {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"[Tavily Request Exception] {e}")
        return []

def discover_lead_sources(user_query: str, results_per_query: int = 4) -> List[Dict[str, Any]]:
    """
    Orchestrates search generation and executes queries across Tavily,
    deduplicating URLs before returning candidate sources.
    """
    queries = generate_search_queries(user_query)
    print(f"[Search Engine] Generated {len(queries)} targeted queries: {queries}")
    
    seen_urls = set()
    aggregated_sources = []
    
    for q in queries:
        results = search_tavily(q, max_results=results_per_query)
        for item in results:
            url = item.get("url", "").strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            aggregated_sources.append({
                "url": url,
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "search_query": q
            })
            
    print(f"[Search Engine] Collected {len(aggregated_sources)} unique web candidates.")
    return aggregated_sources
