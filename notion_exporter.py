import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

def lead_to_notion_properties(lead: Dict[str, Any], database_id: str) -> Dict[str, Any]:
    """
    Formats an extracted lead into standard Notion Database page properties.
    Matches standard real estate CRM schema on Notion.
    """
    lead_type = lead.get("lead_type", "UNKNOWN")
    intent = lead.get("intent_summary") or "Real Estate Lead"
    price = lead.get("budget_or_price")
    confidence = lead.get("confidence_score", 0.0)
    
    # Prepare properties mapping
    properties = {
        "Name": {
            "title": [
                {"text": {"content": intent[:95]}}
            ]
        },
        "Lead Type": {
            "select": {
                "name": lead_type
            }
        },
        "Confidence": {
            "number": round(float(confidence), 2)
        },
        "Status": {
            "select": {
                "name": lead.get("status", "NEW")
            }
        },
        "Locality": {
            "rich_text": [
                {"text": {"content": lead.get("location_raw") or lead.get("city") or "Kolkata"}}
            ]
        },
        "Property Type": {
            "select": {
                "name": (lead.get("property_type") or "Apartment")[:40]
            }
        },
        "Source URL": {
            "url": lead.get("source_url")
        }
    }

    if price is not None:
        try:
            properties["Budget/Price (INR)"] = {"number": float(price)}
        except:
            pass

    if lead.get("contact_phone"):
        properties["Phone"] = {"phone_number": lead.get("contact_phone")}
        
    if lead.get("contact_email"):
        properties["Email"] = {"email": lead.get("contact_email")}

    return {
        "parent": {"database_id": database_id},
        "properties": properties,
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"Confidence Rationale: {lead.get('confidence_rationale', '')}\n\nRaw Snippet:\n{lead.get('raw_content_snippet', '')[:800]}"}
                        }
                    ]
                }
            }
        ]
    }

def push_lead_to_notion_api(lead: Dict[str, Any], database_id: str, notion_token: str) -> bool:
    """
    Pushes a single lead to a Notion database via official REST API.
    """
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = lead_to_notion_properties(lead, database_id)
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code in [200, 201]:
            return True
        else:
            print(f"[Notion API Error] Status {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"[Notion API Exception] {e}")
        return False
