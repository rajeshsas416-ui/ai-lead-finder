import streamlit as st
import pandas as pd
import json
import textwrap
from datetime import datetime
from typing import Dict, Any, List

import db
import key_manager
from lead_agent import run_lead_pipeline
from sample_data import SAMPLE_LEADS, get_sample_leads

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Mossrose | AI Lead Finder",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SaaS styling
st.markdown("""
<style>
    /* Header & Branding - vibrant colors for both light and dark themes */
    .brand-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #6366f1 !important;
        letter-spacing: -0.025em;
        margin-bottom: 0.2rem;
    }
    .brand-badge {
        background-color: #4f46e5 !important;
        color: #ffffff !important;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        vertical-align: middle;
        margin-left: 0.5rem;
    }
    .brand-subtitle {
        font-size: 1.05rem;
        margin-bottom: 1.25rem;
        opacity: 0.9;
    }

    /* Badges */
    .badge-developer {
        background-color: #6366f1 !important;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }
    .badge-investor {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }
    .badge-landowner {
        background-color: #059669 !important;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }
    .badge-buyer {
        background-color: #16a34a !important;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }
    .badge-seller {
        background-color: #d97706 !important;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }
    .badge-agent {
        background-color: #dc2626 !important;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }
    .badge-default {
        background-color: #64748b !important;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        display: inline-block;
    }
    .badge-deal {
        background-color: rgba(148, 163, 184, 0.25);
        color: inherit !important;
        border: 1px solid rgba(148, 163, 184, 0.4);
        font-weight: 600;
        font-size: 0.75rem;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        margin-left: 0.35rem;
        display: inline-block;
    }
    .badge-demo {
        background-color: #fef3c7 !important;
        color: #92400e !important;
        border: 1px solid #fde68a;
        font-weight: 700;
        font-size: 0.7rem;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        text-transform: uppercase;
        display: inline-block;
    }
    .badge-live {
        background-color: #dcfce7 !important;
        color: #166534 !important;
        border: 1px solid #bbf7d0;
        font-weight: 700;
        font-size: 0.7rem;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        text-transform: uppercase;
        display: inline-block;
    }

    /* Confidence / Relevance Gauge */
    .relevance-score {
        font-weight: 700;
        font-size: 0.95rem;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
    }

    /* Distinction Sections */
    .verified-fact-box {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin-top: 0.75rem;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
        color: #14532d;
    }
    .ai-reasoning-box {
        background-color: #f5f3ff;
        border-left: 4px solid #8b5cf6;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin-top: 0.75rem;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
        color: #4c1d95;
    }

    /* Metadata strip */
    .lead-meta-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 1.25rem;
        font-size: 0.88rem;
        color: #334155;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        padding: 0.4rem 0;
        border-top: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }

    /* Empty state card */
    .empty-state-box {
        text-align: center;
        padding: 3rem 1.5rem;
        background: #ffffff;
        border-radius: 12px;
        border: 1px dashed #cbd5e1;
        margin: 1.5rem 0;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .brand-title {
            font-size: 1.6rem;
        }
        .lead-meta-strip {
            gap: 0.75rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def format_inr(val):
    if not val:
        return "Budget not disclosed"
    try:
        val = float(val)
        if val >= 10000000:
            return f"₹ {val / 10000000:.2f} Cr"
        elif val >= 100000:
            return f"₹ {val / 100000:.1f} Lakhs"
        else:
            return f"₹ {val:,.0f}"
    except Exception:
        return str(val)

def get_badge_class(lead_type: str) -> str:
    lead_type = (lead_type or "").upper()
    if "DEVELOPER" in lead_type:
        return "badge-developer"
    elif "INVESTOR" in lead_type:
        return "badge-investor"
    elif "LANDOWNER" in lead_type:
        return "badge-landowner"
    elif "BUYER" in lead_type:
        return "badge-buyer"
    elif "SELLER" in lead_type:
        return "badge-seller"
    elif "AGENT" in lead_type:
        return "badge-agent"
    return "badge-default"

# ---------------------------------------------------------
# State Management
# ---------------------------------------------------------
if "search_query" not in st.session_state:
    st.session_state.search_query = "Find real estate developers in Kolkata who may be interested in acquiring large land parcels."

if "last_executed_query" not in st.session_state:
    st.session_state.last_executed_query = None

if "search_mode" not in st.session_state:
    # Auto-detect if API keys exist
    has_keys = bool(key_manager.get_active_search_key() and key_manager.get_active_llm().get("api_key"))
    st.session_state.search_mode = "Live Web & AI Search" if has_keys else "Curated Sample Leads Mode"

# Seed sample leads into DB if database is fresh
stats = db.get_db_stats()
if stats["total_leads"] == 0:
    for item in SAMPLE_LEADS:
        from models import StoredLead
        db.save_lead(StoredLead(query_id="bootstrap_sample", **item))
    stats = db.get_db_stats()

# ---------------------------------------------------------
# Sidebar: System Metrics & Lead Filters
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏢 Mossrose")
    st.caption("AI Lead Finder — Real Estate Intelligence")
    
    # Mode selector in sidebar
    st.markdown("---")
    st.markdown("#### ⚙️ Execution Engine")
    mode_options = ["Curated Sample Leads Mode", "Live Web & AI Search"]
    selected_mode = st.radio(
        "Search Pipeline Mode",
        options=mode_options,
        index=0 if st.session_state.search_mode == "Curated Sample Leads Mode" else 1,
        help="Switch between instant curated demonstration data (no API credits used) or live real-time web search with Tavily and Gemini."
    )
    st.session_state.search_mode = selected_mode

    active_llm = key_manager.get_active_llm()
    active_search = key_manager.get_active_search_key()

    if selected_mode == "Live Web & AI Search":
        if active_search and active_llm.get("api_key"):
            st.success(f"🟢 **Live APIs Active**\n- Search: Tavily (`{key_manager.mask_key(active_search)}`)\n- AI: `{active_llm['model']}`")
        else:
            st.warning("⚠️ Live search keys incomplete. You can configure them in the 'API Settings' tab or switch to Sample mode.")
    else:
        st.info("🔵 **Sample Leads Mode Active**\nRealistic verified demonstration records. Zero API costs.")

    st.markdown("---")
    st.markdown("#### 📊 Database Intelligence")
    col_sb1, col_sb2 = st.columns(2)
    col_sb1.metric("Total Leads", stats["total_leads"])
    col_sb2.metric("Avg Conf.", f"{stats['avg_confidence']*100:.0f}%")

    col_sb3, col_sb4 = st.columns(2)
    col_sb3.metric("Developers", stats.get("developers", 0))
    col_sb4.metric("Landowners", stats.get("landowners", 0))

    col_sb5, col_sb6 = st.columns(2)
    col_sb5.metric("Buyers/Inv", stats.get("buyers", 0) + stats.get("investors", 0))
    col_sb6.metric("Sellers", stats.get("sellers", 0))

    st.markdown("---")
    st.markdown("#### 🔍 Filter Results")
    filter_lead_type = st.selectbox(
        "Lead Type",
        options=["ALL", "DEVELOPER", "LANDOWNER", "INVESTOR", "BUYER", "SELLER", "AGENT"],
        index=0
    )
    filter_deal_type = st.selectbox(
        "Deal Structure",
        options=["ALL", "OUTRIGHT", "JOINT_VENTURE", "LEASE", "RENTAL"],
        index=0
    )
    filter_min_relevance = st.slider(
        "Minimum Relevance",
        min_value=0.0,
        max_value=1.0,
        value=0.30,
        step=0.05,
        format="%.2f"
    )
    filter_status = st.selectbox(
        "Status",
        options=["ALL", "NEW", "VERIFIED", "CONTACTED", "ARCHIVED", "REJECTED"],
        index=0
    )
    filter_keyword = st.text_input("Filter by Keyword / Locality", placeholder="e.g. Rajarhat, Merlin, Land...")

# ---------------------------------------------------------
# Main UI Header & Hero
# ---------------------------------------------------------
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <span class="brand-title">Mossrose</span>
    <span class="brand-badge">AI Lead Finder MVP</span>
    <p class="brand-subtitle">
        Mossrose helps real estate professionals research property developers, buyers, sellers, landowners, and investors using grounded, publicly available web information.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Search Panel (Natural Language Input + Example Queries)
# ---------------------------------------------------------
search_card = st.container()
with search_card:
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        query_input = st.text_input(
            "Natural Language Lead Search Query",
            value=st.session_state.search_query,
            placeholder="e.g. Find real estate developers in Kolkata who may be interested in acquiring large land parcels.",
            label_visibility="collapsed"
        )
    with col_btn:
        search_clicked = st.button("🔍 Find Leads", type="primary", use_container_width=True)

    # Clickable Example Searches (chips)
    st.caption("💡 **Example Searches (Click to populate):**")
    example_queries = [
        "Find real estate developers in Kolkata who may be interested in acquiring large land parcels.",
        "Landowners in Rajarhat seeking Joint Venture (JV) builder partners",
        "Operational hotel or resort for outright sale or lease in Digha or Mandarmani",
        "Hospitality operators or sellers with bar cum restaurant in Park Street",
        "Logistics fund scouting 20+ acres industrial land along Dankuni / NH-12"
    ]

    p_cols = st.columns(len(example_queries))
    for idx, ex_q in enumerate(example_queries):
        btn_label = ex_q[:28] + "..." if len(ex_q) > 28 else ex_q
        if p_cols[idx].button(btn_label, key=f"preset_btn_{idx}", help=ex_q):
            st.session_state.search_query = ex_q
            st.rerun()

# ---------------------------------------------------------
# Search Execution Handling (Live vs Sample Mode)
# ---------------------------------------------------------
if search_clicked:
    if not query_input.strip():
        st.warning("Please enter a search query.")
    else:
        st.session_state.search_query = query_input.strip()
        st.session_state.last_executed_query = query_input.strip()

        mode_flag = "live" if st.session_state.search_mode == "Live Web & AI Search" else "mock"

        # Loading state presentation
        progress_bar = st.progress(0.0)
        status_box = st.empty()

        def on_progress(msg: str, val: float):
            status_box.markdown(f"⏳ **{msg}**")
            progress_bar.progress(val)

        try:
            with st.spinner("AI Lead Finder is researching publicly available sources..."):
                run_res = run_lead_pipeline(
                    user_query=query_input.strip(),
                    results_per_query=3,
                    progress_callback=on_progress,
                    mode=mode_flag
                )
            
            progress_bar.empty()
            status_box.empty()
            
            mode_badge = "Live Web Search" if run_res.get("mode") == "live" else "Curated Demo Index"
            st.success(
                f"✅ **Discovery Complete ({mode_badge})!** Analyzed {run_res['sources_analyzed']} sources. "
                f"Extracted {run_res['leads_extracted']} leads: "
                f"{run_res.get('developers', 0)} Developers, {run_res.get('landowners', 0)} Landowners, "
                f"{run_res.get('investors', 0) + run_res.get('buyers', 0)} Buyers/Investors, {run_res.get('sellers', 0)} Sellers."
            )
        except Exception as e:
            progress_bar.empty()
            status_box.empty()
            st.error(f"""
            ❌ **Error during lead discovery run:**
            
            {str(e)}
            
            👉 **Troubleshooting Tip:** If you don't have API keys set up yet, switch to **'Curated Sample Leads Mode'** in the sidebar to test all MVP features with verified demonstration data!
            """)

st.divider()

# ---------------------------------------------------------
# Results Tabs: Cards View, Data Grid, Export, API Settings
# ---------------------------------------------------------
tab_cards, tab_table, tab_export, tab_settings = st.tabs([
    "📇 Lead Cards", 
    "📋 Structured Data Grid", 
    "💾 Export Leads (CSV/JSON)", 
    "⚙️ API Settings & Architecture"
])

# Query filtered leads from database
leads = db.get_leads(
    lead_type=filter_lead_type,
    deal_type=filter_deal_type,
    min_confidence=filter_min_relevance,
    status=filter_status,
    search_keyword=filter_keyword.strip() if filter_keyword.strip() else None,
    limit=150
)

# ---------------------------------------------------------
# Tab 1: Lead Cards View
# ---------------------------------------------------------
with tab_cards:
    if not leads:
        # Empty State
        st.markdown("""
        <div class="empty-state-box">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">📂</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">No matching leads found</h3>
            <p style="color: #64748b; max-width: 500px; margin: 0 auto 1.5rem auto;">
                No real estate leads matched your current filter criteria. Try broadening your keywords, lowering the minimum relevance threshold, or running a search with one of our preset queries.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Reset Filters to View All Leads"):
            st.rerun()
    else:
        st.markdown(f"Showing **{len(leads)}** verified lead candidate{'s' if len(leads) != 1 else ''}:")

        for lead in leads:
            lead_id = lead.get("id")
            company = lead.get("company") or "Direct Principal / Company Unspecified"
            contact_name = lead.get("contact_name") or "Authorized Representative"
            lead_type = lead.get("lead_type") or "UNKNOWN"
            deal_type = lead.get("deal_type") or "OUTRIGHT"
            category = lead.get("property_category") or "OTHER"
            conf = float(lead.get("confidence_score") or 0.0)
            conf_pct = int(conf * 100)
            is_mock = bool(lead.get("is_mock", 0))
            source_url = lead.get("source_url") or "#"
            source_title = lead.get("source_title") or "Public Web Source"
            verified_date = lead.get("verified_date") or "Recently verified (2024-2026)"
            location = lead.get("location_raw") or lead.get("city") or "Kolkata, West Bengal"
            intent_summary = lead.get("intent_summary") or "Real estate opportunity identified."
            confidence_rationale = lead.get("confidence_rationale") or "Potentially relevant based on public records."
            raw_snippet = lead.get("raw_content_snippet") or "No raw text snippet available."
            status = lead.get("status") or "NEW"

            badge_class = get_badge_class(lead_type)
            score_color = "#10b981" if conf >= 0.85 else ("#3b82f6" if conf >= 0.70 else "#f59e0b")
            data_mode_tag = '<span class="badge-demo">DEMO / SAMPLE DATA</span>' if is_mock else '<span class="badge-live">LIVE VERIFIED SOURCE</span>'

            # Render Lead Card using native Streamlit bordered container
            with st.container(border=True):
                col_top_left, col_top_right = st.columns([3, 1])
                with col_top_left:
                    st.markdown(f"### {company}")
                    badges_line = f'<span class="{badge_class}">{lead_type}</span> <span class="badge-deal">{deal_type}</span> <span class="badge-deal">{category}</span> {data_mode_tag}'
                    st.markdown(badges_line, unsafe_allow_html=True)
                with col_top_right:
                    st.markdown(
                        f'<div style="text-align: right;">'
                        f'<span style="border: 2px solid {score_color}; color: {score_color}; font-weight: 800; padding: 0.3rem 0.65rem; border-radius: 6px; display: inline-block;">★ {conf_pct}% Relevance</span>'
                        f'<div style="font-size: 0.8rem; opacity: 0.75; margin-top: 0.35rem;">Status: <b>{status}</b></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                st.markdown("---")

                # Metadata row 1
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.markdown(f"📍 **Location:** {location}")
                m_col2.markdown(f"👤 **Contact:** {contact_name}")
                m_col3.markdown(f"💰 **Value:** {format_inr(lead.get('budget_or_price'))}")

                # Metadata row 2
                m_col4, m_col5, m_col6 = st.columns(3)
                m_col4.markdown(f"🗓️ **Verified:** {verified_date}")
                m_col5.markdown(f"🏷️ **Property:** {lead.get('property_type') or 'Commercial Land / Realty'}")
                m_col6.markdown(f"⏱️ **Timeline:** {lead.get('urgency') or '1 TO 3 MONTHS'}")

                if lead.get("commercial_details"):
                    st.markdown(f'<div style="background-color: rgba(59, 130, 246, 0.12); border-left: 4px solid #3b82f6; padding: 0.5rem 0.75rem; border-radius: 4px; margin: 0.5rem 0; font-size: 0.9rem;"><b>📋 Commercial / JV Specs:</b> {lead.get("commercial_details")}</div>', unsafe_allow_html=True)

                # Verified Public Fact Box
                st.markdown(f'<div style="background-color: rgba(34, 197, 94, 0.12); border-left: 4px solid #22c55e; padding: 0.75rem 1rem; border-radius: 6px; margin: 0.6rem 0; font-size: 0.92rem;"><b>🟢 Verified Public Fact:</b> {intent_summary}</div>', unsafe_allow_html=True)

                # AI Generated Reasoning Box
                st.markdown(f'<div style="background-color: rgba(139, 92, 246, 0.12); border-left: 4px solid #8b5cf6; padding: 0.75rem 1rem; border-radius: 6px; margin: 0.6rem 0; font-size: 0.92rem;"><b>🟣 AI Relevance Assessment:</b> {confidence_rationale}</div>', unsafe_allow_html=True)

                # Evidence link
                st.markdown(f"🔗 **Evidence Source:** [{source_title[:80]}]({source_url}) ↗")

                # Action buttons and snippet viewer
                col_actions, col_snippet = st.columns([2, 1])
                with col_snippet:
                    with st.expander("📄 View Source Snippet"):
                        st.caption(f"**URL:** `{source_url}`")
                        st.text_area("Snippet Text", value=raw_snippet, height=120, disabled=True, key=f"snip_{lead_id}")

                with col_actions:
                    act1, act2, act3 = st.columns(3)
                    if act1.button("✅ Verify", key=f"btn_v_{lead_id}"):
                        db.update_lead_status(lead_id, "VERIFIED")
                        st.rerun()
                    if act2.button("📞 Contacted", key=f"btn_c_{lead_id}"):
                        db.update_lead_status(lead_id, "CONTACTED")
                        st.rerun()
                    if act3.button("🗑️ Reject", key=f"btn_r_{lead_id}"):
                        db.update_lead_status(lead_id, "REJECTED")
                        st.rerun()

# ---------------------------------------------------------
# Tab 2: Structured Data Grid
# ---------------------------------------------------------
with tab_table:
    if leads:
        df = pd.DataFrame(leads)
        display_columns = [
            "company", "lead_type", "deal_type", "confidence_score", "intent_summary", 
            "confidence_rationale", "location_raw", "city", "budget_or_price", 
            "contact_name", "verified_date", "is_mock", "status", "source_url"
        ]
        available_cols = [c for c in display_columns if c in df.columns]
        
        # Rename for presentation
        renamed_df = df[available_cols].copy()
        if "confidence_score" in renamed_df.columns:
            renamed_df["relevance_score"] = renamed_df["confidence_score"].apply(lambda x: f"{float(x)*100:.0f}%")
        
        st.dataframe(renamed_df, use_container_width=True)
    else:
        st.info("No leads available in grid view for current filters.")

# ---------------------------------------------------------
# Tab 3: Export Leads
# ---------------------------------------------------------
with tab_export:
    st.markdown("### 💾 Export Extracted Leads")
    st.caption("Download your filtered lead dataset for CRM import (HubSpot, Salesforce) or team distribution.")

    if leads:
        df_export = pd.DataFrame(leads)
        csv_bytes = df_export.to_csv(index=False).encode('utf-8')
        json_bytes = json.dumps(leads, indent=2).encode('utf-8')

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 Download Dataset as CSV",
                data=csv_bytes,
                file_name=f"ai_lead_finder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_dl2:
            st.download_button(
                label="📥 Download Dataset as JSON",
                data=json_bytes,
                file_name=f"ai_lead_finder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("No leads currently match your filters to export.")

# ---------------------------------------------------------
# Tab 4: API Settings & Architecture
# ---------------------------------------------------------
with tab_settings:
    st.markdown("### ⚙️ API Configuration & System Settings")
    st.caption("Manage search provider keys, AI models, and review system configuration.")

    curr_llm = key_manager.get_active_llm()
    curr_search = key_manager.get_active_search_key()

    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        st.markdown("#### 🤖 Active AI Reasoning Model")
        st.info(f"""
        - **Model:** `{curr_llm.get('model')}`
        - **Provider:** `{curr_llm.get('provider', '').upper()}`
        - **API Key:** `{key_manager.mask_key(curr_llm.get('api_key', ''))}`
        """)

    with col_cfg2:
        st.markdown("#### 🔍 Active Web Search Engine")
        st.info(f"""
        - **Search Provider:** Tavily Search API
        - **Endpoint:** `https://api.tavily.com/search`
        - **API Key:** `{key_manager.mask_key(curr_search or '')}`
        """)

    st.markdown("---")
    st.markdown("#### ➕ Add or Update Custom API Key")
    with st.form("custom_key_form", clear_on_submit=True):
        f_name = st.text_input("Key Label / Description", placeholder="e.g. My Personal Gemini Key")
        f_provider = st.selectbox("Provider", options=["Google Gemini", "OpenAI", "Groq", "Tavily Search"])
        f_key = st.text_input("API Key Secret", type="password")
        
        if f_provider == "Google Gemini":
            f_model = st.selectbox("Model", options=["gemini-flash-latest", "gemini-2.5-flash", "gemini-3.5-flash-lite", "Custom"])
            p_code = "gemini"
        elif f_provider == "OpenAI":
            f_model = st.selectbox("Model", options=["gpt-4o-mini", "gpt-4o", "Custom"])
            p_code = "openai"
        elif f_provider == "Groq":
            f_model = st.selectbox("Model", options=["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "Custom"])
            p_code = "groq"
        else:
            f_model = "tavily-advanced"
            p_code = "tavily"

        submit_key = st.form_submit_button("💾 Save and Activate API Key")
        if submit_key:
            if not f_name or not f_key:
                st.error("Please enter a key label and API key string.")
            else:
                key_manager.add_api_key(f_name, p_code, f_key, f_model, set_active=True)
                st.success(f"Key '{f_name}' saved and set as active!")
                st.rerun()

    # List of configured keys
    all_keys = key_manager.get_all_keys()
    if all_keys:
        st.markdown("#### Configured Keys in Vault:")
        for k in all_keys:
            col_k1, col_k2, col_k3 = st.columns([3, 2, 1])
            col_k1.write(f"**{k['name']}** ({k['provider'].upper()} • `{k['model']}`)")
            col_k2.write(f"Key: `{key_manager.mask_key(k['api_key'])}` {'🟢 Active' if k['is_active'] else '⚪ Inactive'}")
            if col_k3.button("🗑️ Delete", key=f"del_{k['id']}"):
                key_manager.delete_api_key(k["id"])
                st.rerun()

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 1rem 0;">
    <b>Mossrose</b> • AI Lead Finder MVP &nbsp;|&nbsp; Grounded, evidence-backed real estate intelligence
</div>
""", unsafe_allow_html=True)

