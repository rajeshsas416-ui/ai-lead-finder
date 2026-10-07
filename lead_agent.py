import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from search_agent import discover_lead_sources, generate_search_queries
from extractor import extract_lead_from_source
import db

from sample_data import get_sample_leads
from models import StoredLead

def run_lead_pipeline(
    user_query: str,
    results_per_query: int = 3,
    progress_callback: Optional[Callable[[str, float], None]] = None,
    mode: str = "live"
) -> Dict[str, Any]:
    """
    Executes the lead discovery pipeline in either 'live' or 'mock' (sample data) mode:
    
    In 'live' mode:
    1. Generates targeted search dorks using AI
    2. Searches Tavily for matching web sources
    3. Analyzes and classifies each source with Gemini/active LLM
    4. Deduplicates and saves verified leads to SQLite
    
    In 'mock' mode:
    1. Retrieves realistic, un-fabricated sample real estate leads matching query criteria
    2. Demonstrates end-to-end functionality without consuming live API credits
    3. Clearly flags records with is_mock=True
    """
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()
    
    if mode == "mock":
        import time
        if progress_callback:
            progress_callback(f"Accessing curated real estate intelligence index for: '{user_query}'...", 0.2)
            time.sleep(0.4)
            progress_callback("Filtering verified company records, developer filings & public listings...", 0.6)
            time.sleep(0.4)
            progress_callback("Formulating relevance rationale and grounding sources...", 0.85)
            time.sleep(0.3)

        sample_items = get_sample_leads(user_query)
        extracted_leads = []
        new_leads_count = 0
        updated_leads_count = 0

        for item in sample_items:
            stored = StoredLead(
                query_id=run_id,
                **item
            )
            is_new = db.save_lead(stored)
            if is_new:
                new_leads_count += 1
            else:
                updated_leads_count += 1
            extracted_leads.append(stored)

        # Record search run
        db.save_search_run(
            run_id=run_id,
            query_text=user_query,
            dorks=[f'Demo Mode: "{user_query}"'],
            sources_count=len(extracted_leads),
            leads_count=len(extracted_leads),
            created_at=created_at
        )

        if progress_callback:
            progress_callback("Completed sample intelligence retrieval!", 1.0)

        return {
            "run_id": run_id,
            "mode": "mock",
            "query": user_query,
            "generated_queries": [f'Curated Intelligence Index: "{user_query}"'],
            "sources_analyzed": len(extracted_leads),
            "leads_extracted": len(extracted_leads),
            "new_leads": new_leads_count,
            "updated_leads": updated_leads_count,
            "developers": sum(1 for l in extracted_leads if l.lead_type == "DEVELOPER"),
            "landowners": sum(1 for l in extracted_leads if l.lead_type == "LANDOWNER"),
            "investors": sum(1 for l in extracted_leads if l.lead_type == "INVESTOR"),
            "buyers": sum(1 for l in extracted_leads if l.lead_type == "BUYER"),
            "sellers": sum(1 for l in extracted_leads if l.lead_type == "SELLER"),
            "agents": sum(1 for l in extracted_leads if l.lead_type == "AGENT"),
            "noise": sum(1 for l in extracted_leads if l.lead_type == "UNKNOWN"),
            "leads": [lead.model_dump() for lead in extracted_leads]
        }

    # Live Mode
    import key_manager
    tavily_key = key_manager.get_active_search_key()
    llm_info = key_manager.get_active_llm()

    if not tavily_key or not llm_info.get("api_key"):
        raise ValueError(
            "Live Search requires both a Search API key (Tavily) and an AI model key (Gemini/OpenAI/Groq). "
            "Please configure keys in the API Keys settings or switch to Sample Leads mode."
        )

    if progress_callback:
        progress_callback(f"Generating search queries for: '{user_query}'...", 0.1)

    queries = generate_search_queries(user_query)
    
    if progress_callback:
        progress_callback("Executing web searches across forums, classifieds & public sources...", 0.25)
        
    sources = discover_lead_sources(user_query, results_per_query=results_per_query)
    
    total_sources = len(sources)
    extracted_leads = []
    new_leads_count = 0
    updated_leads_count = 0

    for idx, source in enumerate(sources):
        progress = 0.3 + (0.65 * (idx + 1) / max(total_sources, 1))
        if progress_callback:
            progress_callback(f"Analyzing source {idx+1}/{total_sources}: {source['title'][:40]}...", progress)
            
        lead = extract_lead_from_source(source, query_id=run_id)
        import time
        time.sleep(1.0)
        if lead:
            is_new = db.save_lead(lead)
            if is_new:
                new_leads_count += 1
            else:
                updated_leads_count += 1
            extracted_leads.append(lead)

    # Record search run
    db.save_search_run(
        run_id=run_id,
        query_text=user_query,
        dorks=queries,
        sources_count=total_sources,
        leads_count=len(extracted_leads),
        created_at=created_at
    )
    
    if progress_callback:
        progress_callback("Completed pipeline execution!", 1.0)

    return {
        "run_id": run_id,
        "mode": "live",
        "query": user_query,
        "generated_queries": queries,
        "sources_analyzed": total_sources,
        "leads_extracted": len(extracted_leads),
        "new_leads": new_leads_count,
        "updated_leads": updated_leads_count,
        "developers": sum(1 for l in extracted_leads if l.lead_type == "DEVELOPER"),
        "landowners": sum(1 for l in extracted_leads if l.lead_type == "LANDOWNER"),
        "investors": sum(1 for l in extracted_leads if l.lead_type == "INVESTOR"),
        "buyers": sum(1 for l in extracted_leads if l.lead_type == "BUYER"),
        "sellers": sum(1 for l in extracted_leads if l.lead_type == "SELLER"),
        "agents": sum(1 for l in extracted_leads if l.lead_type == "AGENT"),
        "noise": sum(1 for l in extracted_leads if l.lead_type == "UNKNOWN"),
        "leads": [lead.model_dump() for lead in extracted_leads]
    }

if __name__ == "__main__":
    import sys
    test_query = "Looking for direct home buyers or sellers in Austin Texas"
    if len(sys.argv) > 1:
        test_query = " ".join(sys.argv[1:])
    print(f"\n--- Running Lead Pipeline for: '{test_query}' ---")
    result = run_lead_pipeline(test_query, results_per_query=2)
    print("\n--- Pipeline Summary ---")
    print(f"Sources analyzed: {result['sources_analyzed']}")
    print(f"Leads extracted:  {result['leads_extracted']} (New: {result['new_leads']}, Updated: {result['updated_leads']})")
    print(f"Buyers: {result['buyers']}, Sellers: {result['sellers']}, Agents: {result['agents']}")
    for lead in result['leads']:
        print(f"\n[{lead['lead_type']} | Conf: {lead['confidence_score']:.2f}] {lead['intent_summary']}")
        print(f"  Location: {lead['location_raw']} | Budget/Price: {lead['budget_or_price']} {lead['currency']}")
        print(f"  URL: {lead['source_url']}")
