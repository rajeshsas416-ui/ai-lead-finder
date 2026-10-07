import sqlite3
import json
from typing import List, Optional, Dict, Any
from config import DB_PATH
from models import StoredLead, LeadStatus

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for concurrent read/write performance
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            query_id TEXT,
            lead_type TEXT,
            deal_type TEXT DEFAULT 'OUTRIGHT',
            property_category TEXT DEFAULT 'OTHER',
            is_direct_party INTEGER,
            confidence_score REAL,
            confidence_rationale TEXT,
            intent_summary TEXT,
            location_raw TEXT,
            city TEXT,
            state TEXT,
            property_type TEXT,
            commercial_details TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            area_sqft REAL,
            budget_or_price REAL,
            currency TEXT,
            contact_name TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            contact_social_handle TEXT,
            urgency TEXT,
            source_url TEXT UNIQUE,
            source_title TEXT,
            raw_content_snippet TEXT,
            status TEXT DEFAULT 'NEW',
            found_at TEXT
        );
        """)
        
        # Safely migrate existing databases if columns are missing
        existing_cols = [row[1] for row in conn.execute("PRAGMA table_info(leads)").fetchall()]
        if "deal_type" not in existing_cols:
            conn.execute("ALTER TABLE leads ADD COLUMN deal_type TEXT DEFAULT 'OUTRIGHT';")
        if "property_category" not in existing_cols:
            conn.execute("ALTER TABLE leads ADD COLUMN property_category TEXT DEFAULT 'OTHER';")
        if "commercial_details" not in existing_cols:
            conn.execute("ALTER TABLE leads ADD COLUMN commercial_details TEXT;")
        if "company" not in existing_cols:
            conn.execute("ALTER TABLE leads ADD COLUMN company TEXT;")
        if "verified_date" not in existing_cols:
            conn.execute("ALTER TABLE leads ADD COLUMN verified_date TEXT;")
        if "is_mock" not in existing_cols:
            conn.execute("ALTER TABLE leads ADD COLUMN is_mock INTEGER DEFAULT 0;")

        conn.execute("""
        CREATE TABLE IF NOT EXISTS search_runs (
            id TEXT PRIMARY KEY,
            query_text TEXT,
            generated_dorks TEXT,
            sources_count INTEGER,
            leads_count INTEGER,
            created_at TEXT
        );
        """)
        
        # Indexes for fast filtering
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_type ON leads(lead_type);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_deal_type ON leads(deal_type);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_category ON leads(property_category);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_confidence ON leads(confidence_score);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company);")
    conn.close()

def save_lead(lead: StoredLead) -> bool:
    """
    Saves a lead. If the source_url or id already exists, it updates the record with fresh analysis.
    Returns True if a new record was inserted, False if an existing record was updated.
    """
    conn = get_connection()
    is_new = False
    with conn:
        cursor = conn.execute("SELECT id FROM leads WHERE id = ? OR source_url = ?", (lead.id, lead.source_url))
        row = cursor.fetchone()
        if row is None:
            is_new = True
            conn.execute("""
            INSERT INTO leads (
                id, query_id, company, lead_type, deal_type, property_category, is_direct_party, confidence_score,
                confidence_rationale, intent_summary, location_raw, city, state,
                property_type, commercial_details, bedrooms, bathrooms, area_sqft, budget_or_price,
                currency, contact_name, contact_email, contact_phone,
                contact_social_handle, urgency, verified_date, is_mock, source_url, source_title,
                raw_content_snippet, status, found_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """, (
                lead.id, lead.query_id, lead.company, lead.lead_type, lead.deal_type, lead.property_category,
                1 if lead.is_direct_party else 0, lead.confidence_score, lead.confidence_rationale,
                lead.intent_summary, lead.location_raw, lead.city, lead.state,
                lead.property_type, lead.commercial_details, lead.bedrooms, lead.bathrooms,
                lead.area_sqft, lead.budget_or_price, lead.currency, lead.contact_name,
                lead.contact_email, lead.contact_phone, lead.contact_social_handle,
                lead.urgency, lead.verified_date, 1 if lead.is_mock else 0, lead.source_url, lead.source_title,
                lead.raw_content_snippet, lead.status, lead.found_at
            ))
        else:
            # Update existing with higher confidence or updated details
            conn.execute("""
            UPDATE leads SET
                company = COALESCE(?, company),
                lead_type = COALESCE(?, lead_type),
                deal_type = COALESCE(?, deal_type),
                property_category = COALESCE(?, property_category),
                commercial_details = COALESCE(?, commercial_details),
                confidence_score = MAX(confidence_score, ?),
                confidence_rationale = COALESCE(?, confidence_rationale),
                intent_summary = COALESCE(?, intent_summary),
                location_raw = COALESCE(?, location_raw),
                budget_or_price = COALESCE(?, budget_or_price),
                contact_name = COALESCE(?, contact_name),
                contact_phone = COALESCE(?, contact_phone),
                contact_email = COALESCE(?, contact_email),
                verified_date = COALESCE(?, verified_date),
                is_mock = COALESCE(?, is_mock),
                raw_content_snippet = COALESCE(?, raw_content_snippet)
            WHERE id = ?
            """, (
                lead.company, lead.lead_type, lead.deal_type, lead.property_category, lead.commercial_details,
                lead.confidence_score, lead.confidence_rationale, lead.intent_summary,
                lead.location_raw, lead.budget_or_price, lead.contact_name,
                lead.contact_phone, lead.contact_email, lead.verified_date,
                1 if lead.is_mock else 0, lead.raw_content_snippet,
                row["id"]
            ))
    conn.close()
    return is_new

def get_leads(
    lead_type: Optional[str] = None,
    property_category: Optional[str] = None,
    deal_type: Optional[str] = None,
    min_confidence: float = 0.0,
    status: Optional[str] = None,
    search_keyword: Optional[str] = None,
    query_id: Optional[str] = None,
    is_mock: Optional[bool] = None,
    limit: int = 150
) -> List[Dict[str, Any]]:
    conn = get_connection()
    query = "SELECT * FROM leads WHERE confidence_score >= ?"
    params: List[Any] = [min_confidence]

    if query_id:
        query += " AND query_id = ?"
        params.append(query_id)

    if is_mock is not None:
        query += " AND is_mock = ?"
        params.append(1 if is_mock else 0)

    if lead_type and lead_type != "ALL":
        query += " AND lead_type = ?"
        params.append(lead_type)

    if property_category and property_category != "ALL":
        query += " AND property_category = ?"
        params.append(property_category)

    if deal_type and deal_type != "ALL":
        query += " AND deal_type = ?"
        params.append(deal_type)

    if status and status != "ALL":
        query += " AND status = ?"
        params.append(status)

    if search_keyword:
        query += " AND (company LIKE ? OR intent_summary LIKE ? OR location_raw LIKE ? OR city LIKE ? OR raw_content_snippet LIKE ? OR commercial_details LIKE ?)"
        wildcard = f"%{search_keyword}%"
        params.extend([wildcard, wildcard, wildcard, wildcard, wildcard, wildcard])

    query += " ORDER BY confidence_score DESC, found_at DESC LIMIT ?"
    params.append(limit)

    cursor = conn.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def update_lead_status(lead_id: str, new_status: str):
    conn = get_connection()
    with conn:
        conn.execute("UPDATE leads SET status = ? WHERE id = ?", (new_status, lead_id))
    conn.close()

def save_search_run(run_id: str, query_text: str, dorks: List[str], sources_count: int, leads_count: int, created_at: str):
    conn = get_connection()
    with conn:
        conn.execute("""
        INSERT INTO search_runs (id, query_text, generated_dorks, sources_count, leads_count, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (run_id, query_text, json.dumps(dorks), sources_count, leads_count, created_at))
    conn.close()

def get_db_stats() -> Dict[str, Any]:
    conn = get_connection()
    total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    developers = conn.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'DEVELOPER'").fetchone()[0]
    landowners = conn.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'LANDOWNER'").fetchone()[0]
    investors = conn.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'INVESTOR'").fetchone()[0]
    buyers = conn.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'BUYER'").fetchone()[0]
    sellers = conn.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'SELLER'").fetchone()[0]
    agents = conn.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'AGENT'").fetchone()[0]
    
    jv_deals = conn.execute("SELECT COUNT(*) FROM leads WHERE deal_type = 'JOINT_VENTURE'").fetchone()[0]
    hotels = conn.execute("SELECT COUNT(*) FROM leads WHERE property_category = 'HOTEL'").fetchone()[0]
    bars = conn.execute("SELECT COUNT(*) FROM leads WHERE property_category = 'BAR_CUM_RESTAURANT'").fetchone()[0]
    land = conn.execute("SELECT COUNT(*) FROM leads WHERE property_category = 'LAND'").fetchone()[0]

    avg_conf = conn.execute("SELECT AVG(confidence_score) FROM leads").fetchone()[0] or 0.0
    conn.close()
    return {
        "total_leads": total_leads,
        "developers": developers,
        "landowners": landowners,
        "investors": investors,
        "buyers": buyers,
        "sellers": sellers,
        "agents": agents,
        "jv_deals": jv_deals,
        "hotels": hotels,
        "bars": bars,
        "land": land,
        "avg_confidence": round(avg_conf, 2)
    }

# Automatically initialize database when db module is imported
init_db()
