import os
import re
import json
import random
import string
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tra-nexus-cybersalamatz-secret-2026")

STATE_FILE = os.environ.get("TRA_NEXUS_STATE_FILE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tra_nexus_state.json"))

def _serialize_users(users):
    out = {}
    for k, v in users.items():
        v2 = dict(v)
        if isinstance(v2.get("registered_at"), datetime):
            v2["registered_at"] = v2["registered_at"].isoformat()
        out[k] = v2
    return out

def _deserialize_users(raw):
    out = {}
    for k, v in raw.items():
        v2 = dict(v)
        if "registered_at" in v2 and isinstance(v2["registered_at"], str):
            v2["registered_at"] = datetime.fromisoformat(v2["registered_at"])
        out[k] = v2
    return out

def save_state():
    try:
        data = {
            "users": _serialize_users(USERS),
            "login_events": LOGIN_EVENTS,
            "unanswered_questions": UNANSWERED_QUESTIONS,
            "qa_database_extra": QA_DATABASE[len(QA_DATABASE_BASE):],
            "chat_history": CHAT_HISTORY,
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        print("Imeshindwa kuhifadhi state:", exc)

def load_state():
    if not os.path.exists(STATE_FILE):
        return
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        USERS.update(_deserialize_users(data.get("users", {})))
        LOGIN_EVENTS.extend(data.get("login_events", []))
        UNANSWERED_QUESTIONS.extend(data.get("unanswered_questions", []))
        QA_DATABASE.extend(data.get("qa_database_extra", []))
        CHAT_HISTORY.update(data.get("chat_history", {}))
    except Exception as exc:
        print("Imeshindwa kupakia state:", exc)

USERS = {
    "TRA-ADMIN": {
        "password_hash": generate_password_hash("Nexus@2026!"),
        "role": "admin",
        "name": "Msimamizi Mkuu wa TRA",
        "email": "admin@tra.go.tz",
        "phone": "0700000000",
        "registered_at": datetime.now() - timedelta(days=40),
        "can_add_officers": True, # Super Admin Pekee
    },
    "142-998-775": {
        "password_hash": generate_password_hash("Kodi@2026!"),
        "role": "taxpayer",
        "name": "Mlipakodi wa Majaribio",
        "email": "mlipakodi@demo.co.tz",
        "phone": "0712000000",
        "registered_at": datetime.now() - timedelta(days=40),
        "can_add_officers": False,
    },
}

LOGIN_EVENTS = []
UNANSWERED_QUESTIONS = []
CHAT_HISTORY = {}

TRA_OFFICES = {
    "Dar es Salaam": {"office": "TRA Kanda ya Dar es Salaam", "address": "📍 Sokoine Drive, Ilala, Dar es Salaam", "phone": "+255 22 211 9591", "x": 78, "y": 62},
    "Mwanza": {"office": "TRA Kanda ya Ziwa - Mwanza", "address": "📍 Kenyatta Road, Mwanza", "phone": "+255 28 250 0751", "x": 40, "y": 22},
    "Arusha": {"office": "TRA Kanda ya Kaskazini - Arusha", "address": "📍 Sokoine Road, Arusha", "phone": "+255 27 254 8261", "x": 58, "y": 12},
    "Dodoma": {"office": "TRA Makao Makuu - Dodoma", "address": "📍 Barabara ya Kikuyu, Dodoma", "phone": "+255 26 232 2683", "x": 55, "y": 42},
    "Geita": {"office": "TRA Kanda ya Ziwa - Geita", "address": "📍 Barabara Kuu, Geita", "phone": "+255 28 252 0110", "x": 35, "y": 28},
    "Mbeya": {"office": "TRA Kanda ya Nyanda za Juu - Mbeya", "address": "📍 Uyole Road, Mbeya", "phone": "+255 25 250 2811", "x": 38, "y": 68},
    "Kilimanjaro": {"office": "TRA Kanda ya Kaskazini - Moshi", "address": "📍 Rindi Lane, Moshi", "phone": "+255 27 275 4221", "x": 63, "y": 14},
    "Tanga": {"office": "TRA Kanda ya Pwani - Tanga", "address": "📍 Independence Avenue, Tanga", "phone": "+255 27 264 4331", "x": 72, "y": 26},
}

BUSINESS_TYPES = ["Duka la Rejareja", "Mgahawa", "Saluni na Kinyozi", "Karakana ya Magari", "Duka la Nguo", "Duka la Simu"]

def mask_middle(value, keep_start=3, keep_end=2):
    if not value: return value
    val_str = str(value)
    if len(val_str) <= keep_start + keep_end:
        return val_str[0] + "*" * max(len(val_str) - 1, 1)
    return val_str[:keep_start] + "***" + val_str[-keep_end:]

def get_taxpayer_profile(identifier, registered_at):
    seed = int(hashlib.md5(identifier.encode("utf-8")).hexdigest(), 16) % (2 ** 32)
    rnd = random.Random(seed)
    mkoa = rnd.choice(list(TRA_OFFICES.keys()))
    business_type = rnd.choice(BUSINESS_TYPES)
    
    weeks = max(0, (datetime.now() - registered_at).days // 7)
    num_receipts = min(4 + weeks, 20)
    receipts = []
    total_sales = 0
    
    for i in range(num_receipts):
        d = (datetime.now() - timedelta(days=i * 2 + 1)).strftime("%Y-%m-%d")
        amt = rnd.randint(50000, 450000)
        vat = int(amt * 0.18) # 18% VAT Kamili
        total_sales += amt
        receipts.append({"date": d, "receipt_no": f"EFD-99{rnd.randint(10000, 99999)}", "amount": amt, "vat": vat})
    
    # Kodi inayohesabiwa inatokana kikamilifu na miamala
    tax_due = int(total_sales * 0.18)
    confidence = min(99, 65 + rnd.randint(0, 15))
    
    return {
        "mkoa": mkoa, "business_type": business_type, "tax_due": tax_due,
        "total_sales": total_sales, "confidence": confidence, "receipts": receipts,
    }

MIKOA_DATA = [
    {"mkoa": "Dar es Salaam", "biashara": 345000, "kodi_base": 24.5, "risk": 42, "trend": "+12%", "size": "Kubwa Sana"},
    {"mkoa": "Mwanza", "biashara": 84912, "kodi_base": 2.8, "risk": 18, "trend": "+7%", "size": "Kubwa"},
    {"mkoa": "Arusha", "biashara": 78000, "kodi_base": 3.9, "risk": 55, "trend": "3%", "size": "Kubwa"},
    {"mkoa": "Dodoma", "biashara": 62000, "kodi_base": 4.1, "risk": 23, "trend": "+15%", "size": "Kubwa"},
    {"mkoa": "Geita", "biashara": 45000, "kodi_base": 3.2, "risk": 30, "trend": "+9%", "size": "Kati"},
    {"mkoa": "Mbeya", "biashara": 51000, "kodi_base": 2.1, "risk": 35, "trend": "+4%", "size": "Kati"},
]

LIVE_EVASION_CASES = [
    {"id": 1, "company": "Al-Amin Vifaa vya Ujenzi", "mkoa": "📍 Kariakoo, DSM", "avg": "73,000,000", "declared": "15,000,000", "type": "EFD Fraud", "status": "Inatafutwa", "signal": "Uwiano wa mauzo dhidi ya matumizi ya LUKU"},
    {"id": 2, "company": "Bahari Textiles Wholesale", "mkoa": "📍 DSM", "avg": "120,000,000", "declared": "45,000,000", "type": "Under-Invoicing", "status": "Inatafutwa", "signal": "Mzunguko wa simu dhidi ya risiti za EFD"},
    {"id": 3, "company": "Mwanza Fishing Grid & Co", "mkoa": "📍 Mwanza", "avg": "95,000,000", "declared": "12,000,000", "type": "Cash-Only Anomaly", "status": "Uchunguzi", "signal": "Miamala mikubwa ya fedha taslimu pekee"},
]

AI_DISCOVERED_BUSINESSES = [
    {"id": 101, "name": "Beda Hardware Tawi la 2", "mkoa": "📍 Mbeya", "reason": "Mzunguko mkubwa wa Lipa Namba bila TIN", "owner_phone": "0712345678", "status": "Imeibuliwa"},
    {"id": 102, "name": "Kariakoo Smart Electronics", "mkoa": "📍 Dar es Salaam", "reason": "Matumizi makubwa ya LUKU yasiyoendana na kodi", "owner_phone": "0655998877", "status": "Imeibuliwa"},
]

QA_DATABASE = [
    {"keywords": ["mambo", "habari", "hello", "hi", "hey", "salamu", "shikamoo"],
     "sw": "Habari! Karibu kwenye AI ASSISTANT wa TRA Tanzania. Naweza kukusaidia kuhusu TIN, VAT, EFD, faini, na maeneo ya ofisi za TRA.",
     "en": "Hello! Welcome to the TRA Tanzania AI ASSISTANT. I can help with TIN, VAT, EFD, penalties, and office locations."},
    {"keywords": ["tin", "namba ya utambulisho", "taxpayer identification"],
     "sw": "TIN ni sharti la kisheria kwa biashara zote Tanzania. Usajili ni bure na unakamilika mtandaoni.",
     "en": "A TIN is legally required for all businesses in Tanzania. Registration is free and completed online."},
    {"keywords": ["vat", "kodi ya ongezeko la thamani"],
     "sw": "VAT ni 18% kwa bidhaa na huduma zote zinazotozwa kodi Tanzania.",
     "en": "VAT is 18% on all taxable goods and services in Tanzania."},
    {"keywords": ["ofisi", "location", "wapi", "anwani", "contact", "simu"],
     "sw": "__OFFICE_LOOKUP__", "en": "__OFFICE_LOOKUP__"},
]
QA_DATABASE_BASE = list(QA_DATABASE)

TR = {
    "sw": {
        "app_name": "TRA NEXUS", "tagline": "Mamlaka ya Mapato Tanzania - Mfumo wa Kidigitali",
        "login_title": "INGIA KWENYE MFUMO WA TRA", "register_title": "USAJILI WA MLIPAKODI MPYA",
        "have_account": "Una akaunti tayari? Ingia", "no_account": "Huna akaunti? Jisajili",
        "id_label": "Kitambulisho (TIN / Staff ID):", "id_placeholder": "Weka TIN au Staff ID",
        "name_label": "Jina Kamili:", "pass_label": "Nenosiri:", "confirm_pass_label": "Thibitisha Nenosiri:",
        "login_btn": "INGIA", "register_btn": "JISAJILI SASA", "logout": "Toka Mfumo",
        "credit": "Imeandaliwa na Mustafa Z. Mambe, Founder & CEO wa CyberSalamaTZ",
        "nav_dashboard": "Dashibodi Kuu", "nav_market": "Ugunduzi wa Soko",
        "nav_ai": "Msaidizi wa Kodi (AI)", "nav_audit": "Kumbukumbu za Ukaguzi",
        "nav_review": "Ukaguzi wa Maswali", "nav_account": "Akaunti Yangu",
        "nav_add_officer": "Sajili Afisa wa TRA",
        "system_title": "Tanzania Revenue Authority (TRA) Ecosystem",
        "status_active": "Hali ya Mfumo: Live / CyberSalamaTZ Secured",
        "revenue_today": "MAKUSANYO YA LEO", "ai_estimate": "MAKADIRIO YA AI", "compliance": "UTII WA KODI KITAIFA",
        "heatmap_title": "📍 Ramani ya Kiuchumi ya Mikoa", "evasion_title": "Live Evasion Stream",
        "search_placeholder": "Chuja Kampuni au Mkoa...",
        "market_title": "Ugunduzi Kiotomatiki wa Soko",
        "market_sub": "Biashara mpya zilizogunduliwa kupitia LUKU, Lipa Namba, na BRELA.",
        "chat_title": "Msaidizi wa Kodi (TRA AI Assistant)",
        "chat_welcome": "Karibu! Uliza swali lolote kuhusu TIN, VAT, EFD, au Maeneo ya Ofisi za TRA.",
        "chat_placeholder": "Andika au tumia sauti...", "chat_send": "TUMA",
        "audit_title": "Kumbukumbu za Ukaguzi (Audit Ledger)",
        "review_title": "Maswali na Majibu ya Ukaguzi wa Admin",
        "review_empty": "Hakuna maswali yanayosubiri ukaguzi kwa sasa.",
        "tin_info": "TAARIFA YA TIN YA BIASHARA YAKO", "tax_due": "KODI INAYOTAKIWA KULIPWA (18% VAT)",
        "pay_now": "Lipa Sasa (GePG)", "confidence": "ALAMA YA UTII",
        "receipts_title": "Risiti na Miamala Yako ya EFD (Jumla ya Miamala vs 18% VAT)",
        "error_mismatch": "Manenosiri hayafanani.", "error_exists": "Kitambulisho hiki kimesajiliwa.",
        "success_register": "Umesajiliwa kikamilifu! Ingia sasa.", "error_login": "Kitambulisho au nenosiri si sahihi.",
        "ai_bot_label": "TRA AI ASSISTANT", "otp_title": "THIBITISHA NAMBA YAKO (OTP)",
        "otp_demo_note": "HALI YA DEMO: Namba ya uthibitisho ni:",
        "otp_label": "Weka OTP:", "otp_verify_btn": "THIBITISHA USAJILI",
        "gepg_modal_title": "Malipo ya Kodi - Lipa Sasa (GePG)",
        "gepg_control_no": "Control Number", "gepg_network": "Mtandao wa Simu",
        "gepg_amount": "Kiasi cha Kulipa (Unaweza Kupunguza):", "gepg_confirm": "THIBITISHA MALIPO",
        "gepg_success": "Malipo yamefanikiwa kikamilifu!",
        "col_mkoa": "Mkoa", "col_size": "Ukubwa", "col_biashara": "Biashara",
        "col_kodi": "Kodi (Bilioni)", "col_risk": "Hatari", "col_trend": "Mwenendo",
        "col_halisi": "HALISI", "col_ripoti": "RIPOTI", "col_ai_kigezo": "Kigezo cha AI",
        "col_tarehe": "Tarehe", "col_risiti": "Risiti No.", "col_kiasi": "Kiasi cha Mauzo",
        "col_hali": "Hali", "col_timestamp": "Muda", "col_blockhash": "Block Hash",
        "col_kitendo": "Kitendo", "col_muhusika": "Muhusika", "col_uhakiki": "Uhakiki",
        "verified": "Umethibitishwa",
    },
    "en": {
        "app_name": "TRA NEXUS", "tagline": "Tanzania Revenue Authority Digital Portal",
        "login_title": "TRA SYSTEM LOGIN", "register_title": "NEW TAXPAYER REGISTRATION",
        "have_account": "Already have an account? Log in", "no_account": "No account? Register",
        "id_label": "Identification (TIN / Staff ID):", "id_placeholder": "Enter TIN or Staff ID",
        "name_label": "Full Name:", "pass_label": "Password:", "confirm_pass_label": "Confirm Password:",
        "login_btn": "LOG IN", "register_btn": "REGISTER NOW", "logout": "Log Out",
        "credit": "Prepared by Mustafa Z. Mambe, Founder & CEO of CyberSalamaTZ",
        "nav_dashboard": "Dashboard", "nav_market": "Market Discovery",
        "nav_ai": "Tax AI Assistant", "nav_audit": "Audit Ledger",
        "nav_review": "Question Review", "nav_account": "My Account",
        "nav_add_officer": "Register TRA Officer",
        "system_title": "Tanzania Revenue Authority (TRA) Ecosystem",
        "status_active": "System Status: Live / CyberSalamaTZ Secured",
        "revenue_today": "TODAY'S COLLECTIONS", "ai_estimate": "AI ESTIMATE", "compliance": "COMPLIANCE SCORE",
        "heatmap_title": "📍 Regional Economic Map", "evasion_title": "Live Evasion Stream",
        "search_placeholder": "Filter Company or Region...",
        "market_title": "Autonomous Market Discovery",
        "market_sub": "Newly discovered businesses via LUKU, mobile pay & BRELA.",
        "chat_title": "TRA AI Assistant",
        "chat_welcome": "Welcome! Ask any questions about TIN, VAT, EFD, or TRA Office Locations.",
        "chat_placeholder": "Type or use voice input...", "chat_send": "SEND",
        "audit_title": "Audit Ledger", "review_title": "Question & Answer Review Panel",
        "review_empty": "No pending questions for review.",
        "tin_info": "YOUR BUSINESS TIN INFO", "tax_due": "TAX DUE (18% VAT)",
        "pay_now": "Pay Now (GePG)", "confidence": "CONFIDENCE SCORE",
        "receipts_title": "EFD Receipts & Sales (Sales vs 18% VAT)",
        "error_mismatch": "Passwords do not match.", "error_exists": "ID already registered.",
        "success_register": "Registration successful! Log in.", "error_login": "Incorrect ID or password.",
        "ai_bot_label": "TRA AI ASSISTANT", "otp_title": "VERIFY PHONE (OTP)",
        "otp_demo_note": "DEMO MODE: Verification code is:",
        "otp_label": "Enter OTP:", "otp_verify_btn": "VERIFY REGISTRATION",
        "gepg_modal_title": "Tax Payment - Pay Now (GePG)",
        "gepg_control_no": "Control Number", "gepg_network": "Mobile Network",
        "gepg_amount": "Amount to Pay (Editable):", "gepg_confirm": "CONFIRM PAYMENT",
        "gepg_success": "Payment completed successfully!",
        "col_mkoa": "Region", "col_size": "Size", "col_biashara": "Businesses",
        "col_kodi": "Tax (Billions)", "col_risk": "Risk", "col_trend": "Trend",
        "col_halisi": "ACTUAL", "col_ripoti": "REPORTED", "col_ai_kigezo": "AI Signal",
        "col_tarehe": "Date", "col_risiti": "Receipt No.", "col_kiasi": "Sales Amount",
        "col_hali": "Status", "col_timestamp": "Timestamp", "col_blockhash": "Block Hash",
        "col_kitendo": "Action", "col_muhusika": "Actor", "col_uhakiki": "Verification",
        "verified": "Verified",
    }
}

def get_lang(): return session.get("lang", "sw")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.app_name }} - Mamlaka ya Mapato Tanzania</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        /* OFFICIAL TRA COLOR PALETTE: Navy Blue (#002B49), Gold (#F4C430), Green (#00875A) */
        body { background-color: #06101E; color: #E2E8F0; font-family: 'Segoe UI', Arial, sans-serif; }
        .tra-card { background: linear-gradient(145deg, #0A1B30, #002B49); border: 1px solid #1E3A66; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .text-tra-gold { color: #F4C430 !important; }
        .text-tra-green { color: #00875A !important; }
        .bg-tra-navy { background-color: #002B49 !important; }
        .bg-tra-gold { background-color: #F4C430 !important; color: #002B49 !important; }
        .btn-tra-gold { background-color: #F4C430; color: #002B49; font-weight: bold; border: none; }
        .btn-tra-gold:hover { background-color: #e0b328; color: #002B49; }
        .btn-tra-green { background-color: #00875A; color: #fff; font-weight: bold; border: none; }
        .btn-tra-green:hover { background-color: #006e49; color: #fff; }
        
        .sidebar { background-color: #040B14; border-right: 1px solid #1E3A66; min-height: 100vh; padding: 20px; }
        .sidebar .nav-link { color: #94A3B8; padding: 12px; border-radius: 8px; margin-bottom: 6px; cursor: pointer; border-left: 4px solid transparent; text-decoration: none; display: block; }
        .sidebar .nav-link:hover, .sidebar .nav-link.active { background: rgba(244, 196, 48, 0.1); color: #F4C430; border-left: 4px solid #F4C430; }
        
        .scrollable-panel { max-height: 380px; overflow-y: auto; }
        .chat-area { height: 320px; overflow-y: auto; background: #040B14; border: 1px solid #1E3A66; border-radius: 8px; padding: 14px; margin-bottom: 12px; }
        
        .auth-box { max-width: 450px; margin: 40px auto; background: linear-gradient(145deg, #0A1B30, #002B49); border: 2px solid #F4C430; border-radius: 16px; padding: 30px; }
        .password-wrap { position: relative; }
        .password-wrap .toggle-eye { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); cursor: pointer; color: #94A3B8; }
        
        .tz-map { position: relative; width: 100%; height: 260px; background: #040B14; border: 1px solid #1E3A66; border-radius: 8px; }
        .tz-pin { position: absolute; width: 14px; height: 14px; margin-left: -7px; margin-top: -7px; border-radius: 50%; background: #F4C430; cursor: pointer; }
        .tz-pin.office-pin { background: #00875A; box-shadow: 0 0 8px #00875A; }
        
        /* Modern Profile Card Styling for Akaunti Yangu */
        .profile-avatar-box { width: 110px; height: 110px; border-radius: 50%; background: #002B49; border: 4px solid #F4C430; display: flex; align-items: center; justify-content: center; font-size: 42px; color: #F4C430; margin: 0 auto 15px auto; }
        
        .tab-panel { display: none; } .tab-panel.active { display: block; }
        .lang-toggle a { color: #94A3B8; text-decoration: none; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
        .lang-toggle a.active-lang { background: #F4C430; color: #002B49; }
    </style>
</head>
<body>

{% if page in ['login', 'register', 'otp', 'add_officer'] %}
<div class="container">
    <div class="text-end pt-3 lang-toggle">
        <a href="/setlang/sw" class="{% if lang=='sw' %}active-lang{% endif %}">SW</a>
        <a href="/setlang/en" class="{% if lang=='en' %}active-lang{% endif %}">EN</a>
    </div>
    <div class="auth-box text-center">
        <h2 class="text-tra-gold mb-1">&#127963;&#65039; {{ t.app_name }}</h2>
        <p class="text-muted small mb-3">{{ t.tagline }}</p>
        <hr style="border-color:#1E3A66;">

        {% if error %}<div class="alert alert-danger py-2 small">{{ error }}</div>{% endif %}
        {% if success %}<div class="alert alert-success py-2 small">{{ success }}</div>{% endif %}

        {% if page == 'login' %}
        <form action="/login" method="POST" class="text-start">
            <div class="mb-3">
                <label class="form-label text-white">{{ t.id_label }}</label>
                <input type="text" name="identifier" class="form-control bg-dark text-white border-secondary" placeholder="{{ t.id_placeholder }}" required>
            </div>
            <div class="mb-4">
                <label class="form-label text-white">{{ t.pass_label }}</label>
                <div class="password-wrap">
                    <input type="password" name="password" id="login-pass" class="form-control bg-dark text-white border-secondary" required>
                    <span class="toggle-eye" onclick="togglePass('login-pass', this)">&#128065;</span>
                </div>
            </div>
            <button type="submit" class="btn btn-tra-gold w-100 py-2">{{ t.login_btn }}</button>
        </form>
        <div class="mt-3"><a href="/register" class="text-tra-gold small">{{ t.no_account }}</a></div>

        {% elif page == 'register' %}
        <form action="/register" method="POST" class="text-start">
            <div class="mb-2"><label class="form-label text-white">{{ t.name_label }}</label><input type="text" name="fullname" class="form-control bg-dark text-white border-secondary" required></div>
            <div class="mb-2"><label class="form-label text-white">{{ t.id_label }}</label><input type="text" name="identifier" class="form-control bg-dark text-white border-secondary" required></div>
            <div class="mb-2"><label class="form-label text-white">Simu:</label><input type="text" name="phone" class="form-control bg-dark text-white border-secondary" placeholder="07XXXXXXXX" required></div>
            <div class="mb-2"><label class="form-label text-white">Barua Pepe:</label><input type="email" name="email" class="form-control bg-dark text-white border-secondary"></div>
            <div class="mb-2">
                <label class="form-label text-white">{{ t.pass_label }}</label>
                <div class="password-wrap">
                    <input type="password" name="password" id="r-pass" class="form-control bg-dark text-white border-secondary" required>
                    <span class="toggle-eye" onclick="togglePass('r-pass', this)">&#128065;</span>
                </div>
            </div>
            <div class="mb-3">
                <label class="form-label text-white">{{ t.confirm_pass_label }}</label>
                <div class="password-wrap">
                    <input type="password" name="confirm_password" id="r-pass2" class="form-control bg-dark text-white border-secondary" required>
                    <span class="toggle-eye" onclick="togglePass('r-pass2', this)">&#128065;</span>
                </div>
            </div>
            <button type="submit" class="btn btn-tra-green w-100 py-2">{{ t.register_btn }}</button>
        </form>
        <div class="mt-3"><a href="/login" class="text-tra-gold small">{{ t.have_account }}</a></div>

        {% elif page == 'otp' %}
        <h5 class="text-tra-gold mb-2">{{ t.otp_title }}</h5>
        <div class="alert alert-warning py-2 text-start small">
            {{ t.otp_demo_note }} <strong style="font-size:18px;">{{ otp_code }}</strong>
        </div>
        <form action="/register/verify" method="POST" class="text-start">
            <div class="mb-3">
                <input type="text" name="otp_input" maxlength="6" class="form-control bg-dark text-white border-secondary text-center" style="font-size:20px; letter-spacing:4px;" required>
            </div>
            <button type="submit" class="btn btn-tra-gold w-100 py-2">{{ t.otp_verify_btn }}</button>
        </form>

        {% elif page == 'add_officer' %}
        <h5 class="text-tra-gold mb-3">&#128104;&#65039;&#8205;&#128188; Sajili Afisa Mpya wa TRA</h5>
        <form action="/admin/add-officer" method="POST" class="text-start">
            <div class="mb-2"><label class="form-label text-white">Jina la Afisa:</label><input type="text" name="fullname" class="form-control bg-dark text-white border-secondary" required></div>
            <div class="mb-2"><label class="form-label text-white">Staff ID / Kitambulisho:</label><input type="text" name="identifier" class="form-control bg-dark text-white border-secondary" required></div>
            <div class="mb-2"><label class="form-label text-white">Simu:</label><input type="text" name="phone" class="form-control bg-dark text-white border-secondary" required></div>
            <div class="mb-3"><label class="form-label text-white">Nenosiri la Mwanzo:</label><input type="password" name="password" class="form-control bg-dark text-white border-secondary" required></div>
            <button type="submit" class="btn btn-tra-gold w-100 fw-bold py-2">HIFADHI AFISA</button>
        </form>
        <div class="mt-3"><a href="/" class="text-tra-gold small">&larr; Kurudi Kwenye Dashibodi</a></div>
        {% endif %}

        <div class="mt-4 text-center">
            <small class="text-muted">{{ t.credit }}</small>
        </div>
    </div>
</div>

{% else %}
<div class="container-fluid">
    <div class="row">
        <!-- Sidebar Navigation -->
        <div class="col-md-3 col-lg-2 sidebar">
            <h4 class="text-tra-gold mb-1">&#127963;&#65039; {{ t.app_name }}</h4>
            <div class="text-muted small mb-2">{{ session['role_name'] }}</div>
            <div class="lang-toggle mb-3">
                <a href="/setlang/sw" class="{% if lang=='sw' %}active-lang{% endif %}">SW</a>
                <a href="/setlang/en" class="{% if lang=='en' %}active-lang{% endif %}">EN</a>
            </div>
            <hr style="border-color:#1E3A66;">
            <a class="nav-link active" data-tab="dashboard" onclick="showTab('dashboard', this)">&#128202; {{ t.nav_dashboard }}</a>
            {% if session['role'] == 'admin' %}
            <a class="nav-link" data-tab="market" onclick="showTab('market', this)">&#128269; {{ t.nav_market }}</a>
            {% endif %}
            <a class="nav-link" data-tab="ai" onclick="showTab('ai', this)">&#128172; {{ t.nav_ai }}</a>
            {% if session['role'] == 'admin' %}
            <a class="nav-link" data-tab="audit" onclick="showTab('audit', this)">&#128274; {{ t.nav_audit }}</a>
            <a class="nav-link" data-tab="review" onclick="showTab('review', this)">&#128269; {{ t.nav_review }}</a>
            {% if session.get('can_add_officers') %}
            <a href="/admin/add-officer" class="nav-link text-tra-gold">&#10010; {{ t.nav_add_officer }}</a>
            {% endif %}
            {% endif %}
            <a class="nav-link" data-tab="account" onclick="showTab('account', this)">&#9881;&#65039; {{ t.nav_account }}</a>
            <hr style="border-color:#1E3A66;">
            <a href="/logout" class="nav-link text-danger">&#128682; {{ t.logout }}</a>
        </div>

        <div class="col-md-9 col-lg-10 p-3 p-md-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h3 class="mb-0 text-white">{{ t.system_title }}</h3>
                    <small class="text-muted">{{ t.status_active }}</small>
                </div>
                <span class="badge bg-tra-gold p-2 fw-bold">CyberSalamaTZ Secured</span>
            </div>

            <!-- TAB: DASHBOARD -->
            <div class="tab-panel active" id="tab-dashboard">
            {% if session['role'] == 'admin' %}
                <div class="row">
                    <div class="col-12 col-md-4"><div class="tra-card">
                        <h6 class="text-muted">{{ t.revenue_today }}</h6>
                        <h3 class="text-tra-green fw-bold" id="live-revenue">TZS 48,312,450,000</h3>
                        <small class="text-tra-gold">+14.2% Jamhuri ya Muungano</small>
                    </div></div>
                    <div class="col-12 col-md-4"><div class="tra-card">
                        <h6 class="text-muted">{{ t.ai_estimate }}</h6>
                        <h3 class="text-tra-gold fw-bold">TZS 51.1B</h3>
                        <small class="text-white">AI Confidence: 96.8%</small>
                    </div></div>
                    <div class="col-12 col-md-4"><div class="tra-card">
                        <h6 class="text-muted">{{ t.compliance }}</h6>
                        <h3 class="text-tra-green fw-bold">87.4%</h3>
                    </div></div>
                </div>
                <div class="row">
                    <div class="col-12 col-lg-7"><div class="tra-card">
                        <h6 class="text-tra-gold mb-3">{{ t.heatmap_title }}</h6>
                        <div class="table-responsive scrollable-panel">
                        <table class="table table-dark table-hover align-middle small">
                            <thead><tr class="text-muted"><th>{{ t.col_mkoa }}</th><th>{{ t.col_size }}</th><th>{{ t.col_biashara }}</th><th>{{ t.col_kodi }}</th><th>{{ t.col_risk }}</th><th>{{ t.col_trend }}</th></tr></thead>
                            <tbody>
                            {% for m in mikoa %}
                                <tr><td class="fw-bold text-white">📍 {{ m.mkoa }}</td><td><span class="badge bg-secondary">{{ m.size }}</span></td>
                                <td>{{ "{:,}".format(m.biashara) }}</td><td class="text-tra-gold fw-bold">{{ m.kodi_base }}B</td>
                                <td><span class="badge {% if m.risk > 50 %}bg-danger{% else %}bg-success{% endif %}">{{ m.risk }}%</span></td>
                                <td class="{% if '-' in m.trend %}text-danger{% else %}text-success{% endif %}">{{ m.trend }}</td></tr>
                            {% endfor %}
                            </tbody>
                        </table>
                        </div>
                    </div></div>
                    <div class="col-12 col-lg-5"><div class="tra-card">
                        <h6 class="text-danger mb-2">&#128680; {{ t.evasion_title }}</h6>
                        <input type="text" id="evasion-search" class="form-control bg-dark text-white border-secondary form-control-sm mb-2" placeholder="{{ t.search_placeholder }}">
                        <div class="scrollable-panel">
                        {% for case in evasion_cases %}
                            <div class="p-2 mb-2 rounded evasion-item" style="background:rgba(255,255,255,0.03); border-left:3px solid #DC2626;">
                                <div class="d-flex justify-content-between"><strong class="text-tra-gold small">{{ case.company }}</strong><span class="badge bg-danger" style="font-size:9px;">{{ case.type }}</span></div>
                                <div class="small text-muted">{{ case.mkoa }} &middot; {{ t.col_ai_kigezo }}: {{ case.signal }}</div>
                                <div class="d-flex justify-content-between mt-1 small"><span>{{ t.col_halisi }}: <b class="text-tra-green">TZS {{ case.avg }}</b></span><span>{{ t.col_ripoti }}: <b class="text-muted">TZS {{ case.declared }}</b></span></div>
                            </div>
                        {% endfor %}
                        </div>
                    </div></div>
                </div>
            {% else %}
                <div class="row">
                    <div class="col-12 col-md-4"><div class="tra-card text-center"><h6 class="text-muted">{{ t.tin_info }}</h6>
                        <h4 class="text-tra-gold fw-bold my-2">TIN: {{ session.get('masked_identifier','') }}</h4>
                        <span class="badge bg-secondary">{{ taxpayer_profile.business_type }} &middot; 📍 {{ taxpayer_profile.mkoa }}</span></div></div>
                    <div class="col-12 col-md-4"><div class="tra-card text-center"><h6 class="text-muted">{{ t.tax_due }}</h6>
                        <h4 class="text-danger fw-bold my-2">TZS {{ "{:,}".format(taxpayer_profile.tax_due) }}</h4>
                        <button class="btn btn-sm btn-tra-green fw-bold" onclick="openGepgModal({{ taxpayer_profile.tax_due }})">{{ t.pay_now }}</button></div></div>
                    <div class="col-12 col-md-4"><div class="tra-card text-center"><h6 class="text-muted">{{ t.confidence }}</h6>
                        <h4 class="text-tra-gold fw-bold my-2">{{ taxpayer_profile.confidence }} / 100</h4>
                        <small class="text-tra-green">Utii wa Hali ya Juu</small></div></div>
                </div>
                <div class="tra-card">
                    <h6 class="text-tra-gold mb-3">&#128203; {{ t.receipts_title }}</h6>
                    <p class="small text-muted mb-2">Jumla ya Miamala: <b>TZS {{ "{:,}".format(taxpayer_profile.total_sales) }}</b> | Kodi ya VAT (18%): <b class="text-tra-gold">TZS {{ "{:,}".format(taxpayer_profile.tax_due) }}</b></p>
                    <div class="table-responsive scrollable-panel">
                    <table class="table table-dark table-bordered small">
                        <thead><tr><th>{{ t.col_tarehe }}</th><th>{{ t.col_risiti }}</th><th>{{ t.col_kiasi }}</th><th>VAT (18%)</th><th>{{ t.col_hali }}</th></tr></thead>
                        <tbody>
                        {% for r in taxpayer_profile.receipts %}
                            <tr><td>{{ r.date }}</td><td>{{ r.receipt_no }}</td><td>TZS {{ "{:,}".format(r.amount) }}</td><td class="text-tra-gold">TZS {{ "{:,}".format(r.vat) }}</td><td class="text-tra-green">Imethibitishwa</td></tr>
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                </div>
            {% endif %}
            </div>

            <!-- TAB: MARKET DISCOVERY -->
            <div class="tab-panel" id="tab-market">
                <div class="tra-card">
                    <h5 class="text-tra-gold mb-1">&#129302; {{ t.market_title }}</h5>
                    <p class="text-muted small mb-3">{{ t.market_sub }}</p>
                    <div class="scrollable-panel">
                    {% for b in discovered %}
                        <div class="p-3 mb-3 rounded" style="background:rgba(255,255,255,0.03); border-left:4px solid #F4C430;">
                            <div class="d-flex justify-content-between"><strong class="text-white h6 mb-1">{{ b.name }}</strong><span class="badge bg-warning text-dark">{{ b.status }}</span></div>
                            <div class="small text-muted mb-1">{{ b.mkoa }} &middot; Kigezo: {{ b.reason }}</div>
                            <div class="small text-tra-gold mb-2">Simu (Faragha): {{ b.masked_phone }}</div>
                            <div class="d-flex gap-2">
                                <a href="https://wa.me/255{{ b.owner_phone[1:] }}?text=Habari%20kutoka%20TRA%20Tanzania,%20tunamtafuta%20mwakilishi%20wa%20{{ b.name }}" target="_blank" class="btn btn-sm btn-tra-green">&#128241; WhatsApp Ujumbe</a>
                                <a href="sms:{{ b.owner_phone }}?body=Habari,%20tafadhali%20wasiliana%20na%20TRA%20kuhusu%20usajili%20wa%20TIN%20ya%20{{ b.name }}" class="btn btn-sm btn-outline-light">&#128233; SMS ya Kawaida</a>
                            </div>
                        </div>
                    {% endfor %}
                    </div>
                </div>
            </div>

            <!-- TAB: AI ASSISTANT -->
            <div class="tab-panel" id="tab-ai">
                <div class="row">
                <div class="col-12 col-lg-8">
                <div class="tra-card">
                    <h5 class="text-tra-gold mb-3">&#128172; {{ t.chat_title }}</h5>
                    <div class="chat-area" id="chat-box">
                        <div class="text-muted small mb-2"><em>{{ t.chat_welcome }}</em></div>
                        {% for m in chat_log %}
                            {% if m.who == 'user' %}
                            <div class="text-end text-tra-gold mb-2"><b>You:</b> {{ m.text }}</div>
                            {% else %}
                            <div class="text-start text-white mb-2" style="background:rgba(255,255,255,0.05); padding:8px; border-radius:6px;"><b>{{ t.ai_bot_label }}:</b> {{ m.text|safe }}</div>
                            {% endif %}
                        {% endfor %}
                    </div>
                    <div class="input-group">
                        <input type="text" id="chat-input" class="form-control bg-dark text-white border-secondary" placeholder="{{ t.chat_placeholder }}">
                        <button class="btn btn-dark border-secondary mic-btn" id="mic-btn" onclick="toggleVoiceInput()">&#127908;</button>
                        <button class="btn btn-tra-gold fw-bold" onclick="sendMessage()">{{ t.chat_send }}</button>
                    </div>
                </div>
                </div>
                <div class="col-12 col-lg-4">
                <div class="tra-card">
                    <h6 class="text-tra-gold mb-2">📍 Ramani ya Ofisi za TRA Nchini</h6>
                    <div class="tz-map mb-2">
                        {% for mkoa, off in tra_offices.items() %}
                        <div class="tz-pin office-pin" style="left:{{ off.x }}%; top:{{ off.y }}%;" title="{{ mkoa }}" onclick="showOfficeInfo('{{ mkoa }}')"></div>
                        {% endfor %}
                    </div>
                    <div id="office-info-box" class="small text-white p-2" style="background:rgba(255,255,255,0.03); border-radius:6px;">
                        Bonyeza mkoa kuona anwani na namba ya simu ya TRA.
                    </div>
                </div>
                </div>
                </div>
            </div>

            <!-- TAB: AUDIT LEDGER -->
            <div class="tab-panel" id="tab-audit">
                <div class="tra-card">
                    <h5 class="text-tra-gold mb-3">&#128274; {{ t.audit_title }}</h5>
                    <div class="table-responsive scrollable-panel">
                    <table class="table table-dark table-striped table-sm text-muted small">
                        <thead><tr><th>{{ t.col_timestamp }}</th><th>{{ t.col_blockhash }}</th><th>{{ t.col_kitendo }}</th><th>{{ t.col_muhusika }}</th><th>{{ t.col_uhakiki }}</th></tr></thead>
                        <tbody>
                            {% for ev in login_log %}
                            <tr><td>{{ ev.time }}</td><td><code class="text-tra-gold">0x{{ ev.hash }}</code></td><td>Mtumiaji "{{ ev.identifier }}" ameingia kwenye mfumo.</td><td>System Login</td><td class="text-tra-green">&#10003; {{ t.verified }}</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    </div>
                </div>
            </div>

            <!-- TAB: QUESTION REVIEW (ADMIN ONLY & DIRECT THREAD REPLY) -->
            <div class="tab-panel" id="tab-review">
                <div class="tra-card">
                    <h5 class="text-tra-gold mb-3">&#128269; {{ t.review_title }}</h5>
                    {% if unanswered|length == 0 %}
                    <p class="text-muted small">{{ t.review_empty }}</p>
                    {% else %}
                    <div class="scrollable-panel">
                    {% for q in unanswered %}
                        <div class="p-3 mb-3 rounded" style="background:rgba(255,255,255,0.03); border-left:4px solid {% if q.answered %}#00875A{% else %}#DC2626{% endif %};">
                            <div class="d-flex justify-content-between small text-muted mb-1">
                                <span>{{ q.time }} &middot; Aliyeuliza: <b class="text-white">{{ q.user }}</b></span>
                                {% if q.answered %}<span class="badge bg-success">Imejibiwa</span>{% else %}<span class="badge bg-danger">Inasubiri Jibu</span>{% endif %}
                            </div>
                            <div class="text-white mt-1"><b>❓ Swali Husika:</b> {{ q.text }}</div>
                            
                            {% if q.answered %}
                            <div class="text-tra-gold small mt-2 p-2 rounded" style="background:rgba(244,196,48,0.1);">
                                <b>↳ Jibu la Admin:</b> {{ q.answer }}
                            </div>
                            {% else %}
                            <div class="input-group input-group-sm mt-3">
                                <input type="text" class="form-control bg-dark text-white border-secondary" id="ans-{{ q.id }}" placeholder="Andika jibu hapa litakaloenda moja kwa moja kwa muulizaji...">
                                <button class="btn btn-sm btn-tra-gold fw-bold" onclick="submitAnswer({{ q.id }})">Tuma Jibu Direct</button>
                            </div>
                            {% endif %}
                        </div>
                    {% endfor %}
                    </div>
                    {% endif %}
                </div>
            </div>

            <!-- TAB: AKAUNTI YANGU (MODERN USER PROFILE DASHBOARD VIEW) -->
            <div class="tab-panel" id="tab-account">
                <div class="row">
                    <div class="col-12 col-md-4">
                        <div class="tra-card text-center">
                            <div class="profile-avatar-box">
                                &#128104;&#65039;&#8205;&#128188;
                            </div>
                            <h5 class="text-white fw-bold mb-1">{{ current_user.name }}</h5>
                            <p class="badge bg-tra-gold mb-2">{{ session.get('role_name') }}</p>
                            <div class="text-muted small">TIN/ID: <b class="text-white">{{ session.get('identifier') }}</b></div>
                            <div class="text-muted small mt-1">Tarehe ya Usajili: {{ current_user.registered_at.strftime('%Y-%m-%d') }}</div>
                        </div>
                    </div>
                    <div class="col-12 col-md-8">
                        <div class="tra-card">
                            <h5 class="text-tra-gold mb-3">&#9881;&#65039; Mipangilio ya Akaunti & Usalama</h5>
                            {% if account_success %}<div class="alert alert-success py-2 small">{{ account_success }}</div>{% endif %}
                            {% if account_error %}<div class="alert alert-danger py-2 small">{{ account_error }}</div>{% endif %}
                            
                            <form action="/account/update" method="POST">
                                <div class="row">
                                    <div class="col-12 col-md-6 mb-3">
                                        <label class="form-label text-white small">Jina Kamili:</label>
                                        <input type="text" name="fullname" value="{{ current_user.name }}" class="form-control bg-dark text-white border-secondary" required>
                                    </div>
                                    <div class="col-12 col-md-6 mb-3">
                                        <label class="form-label text-white small">Barua Pepe:</label>
                                        <input type="email" name="email" value="{{ current_user.get('email','') }}" class="form-control bg-dark text-white border-secondary">
                                    </div>
                                    <div class="col-12 mb-3">
                                        <label class="form-label text-white small">Namba ya Simu:</label>
                                        <input type="text" name="phone" value="{{ current_user.get('phone','') }}" class="form-control bg-dark text-white border-secondary">
                                    </div>
                                </div>
                                <hr style="border-color:#1E3A66;">
                                <h6 class="text-tra-gold mb-3">&#128274; Kubadilisha Nenosiri</h6>
                                <div class="mb-3">
                                    <label class="form-label text-white small">Nenosiri la Awali (Current Password):</label>
                                    <input type="password" name="old_password" class="form-control bg-dark text-white border-secondary" placeholder="Weka nenosiri lako la sasa">
                                </div>
                                <div class="row">
                                    <div class="col-12 col-md-6 mb-3">
                                        <label class="form-label text-white small">Nenosiri Jipya:</label>
                                        <input type="password" name="new_password" class="form-control bg-dark text-white border-secondary" placeholder="Nenosiri jipya">
                                    </div>
                                    <div class="col-12 col-md-6 mb-3">
                                        <label class="form-label text-white small">Thibitisha Nenosiri Jipya:</label>
                                        <input type="password" name="confirm_new_password" class="form-control bg-dark text-white border-secondary" placeholder="Kurudia nenosiri jipya">
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-tra-gold fw-bold px-4">HIFADHI MABADILIKO</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</div>

<!-- Modal ya GePG (Lipa Sasa na Kiasi Anachotaka Mteja) -->
<div class="modal fade" id="gepgModal" tabindex="-1">
    <div class="modal-dialog"><div class="modal-content bg-dark border border-secondary text-white">
        <div class="modal-header border-secondary">
            <h5 class="modal-title text-tra-gold">{{ t.gepg_modal_title }}</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
            <p>{{ t.gepg_control_no }}: <b class="text-tra-gold" id="gepg-control-no"></b></p>
            <div class="mb-3">
                <label class="form-label text-white small">{{ t.gepg_amount }}</label>
                <input type="number" id="gepg-custom-amount" class="form-control bg-dark text-white border-secondary fw-bold" style="color:#F4C430 !important;">
            </div>
            <p>{{ t.gepg_network }}:
                <select id="gepg-network" class="form-select bg-dark text-white border-secondary d-inline-block w-auto">
                    <option>M-Pesa (Vodacom)</option><option>Tigo Pesa</option><option>Airtel Money</option><option>Halo Pesa</option>
                </select>
            </p>
            <div id="gepg-success-msg" class="alert alert-success py-2" style="display:none;">{{ t.gepg_success }}</div>
        </div>
        <div class="modal-footer border-secondary">
            <button class="btn btn-tra-green fw-bold" onclick="confirmGepgPayment()">{{ t.gepg_confirm }}</button>
        </div>
    </div></div>
</div>
{% endif %}

<script>
    function togglePass(id, el) {
        const input = document.getElementById(id);
        if (input.type === 'password') { input.type = 'text'; el.style.color = '#F4C430'; }
        else { input.type = 'password'; el.style.color = '#94A3B8'; }
    }

    function showTab(name, el) {
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        document.getElementById('tab-' + name).classList.add('active');
        document.querySelectorAll('.sidebar .nav-link').forEach(l => l.classList.remove('active'));
        if (el) el.classList.add('active');
    }

    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
        });
    }

    function sendMessage() {
        const input = document.getElementById('chat-input');
        const box = document.getElementById('chat-box');
        if (!input || input.value.trim() === "") return;
        let text = input.value;
        box.innerHTML += `<div class="text-end text-tra-gold mb-2"><b>You:</b> ${text}</div>`;
        box.scrollTop = box.scrollHeight;
        fetch('/api/chat', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({message: text}) })
        .then(res => res.json())
        .then(data => {
            box.innerHTML += `<div class="text-start text-white mb-2" style="background:rgba(255,255,255,0.05); padding:8px; border-radius:6px;"><b>TRA AI ASSISTANT:</b> ${data.response}</div>`;
            box.scrollTop = box.scrollHeight;
        });
        input.value = "";
    }

    let recognizing = false, recognizer = null;
    function toggleVoiceInput() {
        const micBtn = document.getElementById('mic-btn');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) { alert("Kivinjari hiki hakitumii Voice Input. Jaribu Google Chrome."); return; }
        if (recognizing) { recognizer.stop(); return; }
        recognizer = new SpeechRecognition();
        recognizer.lang = "{{ 'sw-TZ' if lang == 'sw' else 'en-US' }}";
        recognizer.onstart = function() { recognizing = true; micBtn.classList.add('listening'); };
        recognizer.onend = function() { recognizing = false; micBtn.classList.remove('listening'); };
        recognizer.onresult = function(e) {
            document.getElementById('chat-input').value = e.results[0][0].transcript;
            sendMessage();
        };
        recognizer.start();
    }

    const TRA_OFFICES_JS = {{ tra_offices|tojson }};
    function showOfficeInfo(mkoa) {
        const off = TRA_OFFICES_JS[mkoa];
        const box = document.getElementById('office-info-box');
        if (off && box) {
            box.innerHTML = `<b class="text-tra-gold">📍 ${mkoa}</b><br>${off.office}<br>${off.address}<br>&#9742; ${off.phone}`;
        }
    }

    function submitAnswer(qid) {
        const val = document.getElementById('ans-' + qid).value.trim();
        if (!val) return;
        fetch('/api/answer-question', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({id: qid, answer: val}) })
        .then(res => res.json()).then(data => { if (data.status === 'success') location.reload(); });
    }

    let gepgModalInstance = null;
    function openGepgModal(fullAmount) {
        document.getElementById('gepg-control-no').innerText = 'TRA99' + Math.floor(10000000 + Math.random() * 90000000);
        document.getElementById('gepg-custom-amount').value = fullAmount; // Mtumiaji anaweza kubadilisha
        gepgModalInstance = new bootstrap.Modal(document.getElementById('gepgModal'));
        gepgModalInstance.show();
    }
    function confirmGepgPayment() {
        document.getElementById('gepg-success-msg').style.display = 'block';
        setTimeout(() => { if (gepgModalInstance) gepgModalInstance.hide(); location.reload(); }, 1500);
    }
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

QUESTION_COUNTER = [0]
def next_question_id():
    QUESTION_COUNTER[0] += 1
    return QUESTION_COUNTER[0]

@app.route('/setlang/<lang_code>')
def set_lang(lang_code):
    if lang_code in ('sw', 'en'): session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    lang = get_lang()
    if 'role' not in session: return redirect(url_for('login'))
    
    identifier = session.get('identifier')
    current_user = USERS.get(identifier, {})
    
    taxpayer_profile = None
    if session['role'] == 'taxpayer':
        taxpayer_profile = get_taxpayer_profile(identifier, current_user.get("registered_at", datetime.now()))

    discovered_display = []
    for b in AI_DISCOVERED_BUSINESSES:
        b2 = dict(b)
        b2["masked_phone"] = mask_middle(b["owner_phone"])
        discovered_display.append(b2)

    chat_log = CHAT_HISTORY.get(identifier, [])

    return render_template_string(
        HTML_TEMPLATE, page='dashboard', lang=lang, t=TR[lang],
        mikoa=MIKOA_DATA, evasion_cases=LIVE_EVASION_CASES, discovered=discovered_display,
        login_log=LOGIN_EVENTS[-10:][::-1], unanswered=UNANSWERED_QUESTIONS[-30:][::-1],
        taxpayer_profile=taxpayer_profile, tra_offices=TRA_OFFICES, chat_log=chat_log,
        current_user=current_user, account_success=session.pop('account_success', None),
        account_error=session.pop('account_error', None)
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = get_lang()
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE, page='login', lang=lang, t=TR[lang], error=None, success=request.args.get('success'))

    identifier = request.form.get('identifier', '').strip()
    password = request.form.get('password', '')
    user = USERS.get(identifier)

    if not user or not check_password_hash(user["password_hash"], password):
        return render_template_string(HTML_TEMPLATE, page='login', lang=lang, t=TR[lang], error=TR[lang]["error_login"], success=None)

    session['role'] = user["role"]
    session['identifier'] = identifier
    session['masked_identifier'] = mask_middle(identifier)
    session['role_name'] = user["name"]
    session['can_add_officers'] = user.get("can_add_officers", False) # Udhibiti wa Access
    
    LOGIN_EVENTS.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "identifier": mask_middle(identifier),
        "role": user["role"],
        "hash": os.urandom(4).hex() + "..." + os.urandom(2).hex(),
    })
    save_state()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = get_lang()
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE, page='register', lang=lang, t=TR[lang], error=None, success=None)

    fullname = request.form.get('fullname', '').strip()
    identifier = request.form.get('identifier', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm = request.form.get('confirm_password', '')

    if password != confirm:
        return render_template_string(HTML_TEMPLATE, page='register', lang=lang, t=TR[lang], error=TR[lang]["error_mismatch"], success=None)
    if identifier in USERS:
        return render_template_string(HTML_TEMPLATE, page='register', lang=lang, t=TR[lang], error=TR[lang]["error_exists"], success=None)

    otp = ''.join(random.choices(string.digits, k=6))
    session['pending_reg'] = {
        "fullname": fullname, "identifier": identifier, "phone": phone,
        "email": email, "password": password, "otp": otp
    }
    return render_template_string(HTML_TEMPLATE, page='otp', lang=lang, t=TR[lang], error=None, otp_code=otp)

@app.route('/register/verify', methods=['POST'])
def register_verify():
    lang = get_lang()
    pending = session.get('pending_reg')
    if not pending: return redirect(url_for('register'))

    submitted = request.form.get('otp_input', '').strip()
    if submitted != pending["otp"]:
        return render_template_string(HTML_TEMPLATE, page='otp', lang=lang, t=TR[lang], error="OTP si sahihi.", otp_code=pending["otp"])

    USERS[pending["identifier"]] = {
        "password_hash": generate_password_hash(pending["password"]),
        "role": "taxpayer",
        "name": pending["fullname"] or pending["identifier"],
        "phone": pending["phone"],
        "email": pending["email"],
        "registered_at": datetime.now(),
        "can_add_officers": False,
    }
    session.pop('pending_reg', None)
    save_state()
    return redirect(url_for('login', success=TR[lang]["success_register"]))

@app.route('/admin/add-officer', methods=['GET', 'POST'])
def add_officer():
    lang = get_lang()
    # Udhibiti: Ni Super Admin Pekee anayeweza kumsajili Afisa mwingine
    if not session.get('can_add_officers'):
        return "Huna ruhusa ya kumsajili Afisa wa TRA.", 403

    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE, page='add_officer', lang=lang, t=TR[lang], error=None, success=None)

    fullname = request.form.get('fullname', '').strip()
    identifier = request.form.get('identifier', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '')

    if identifier in USERS:
        return render_template_string(HTML_TEMPLATE, page='add_officer', lang=lang, t=TR[lang], error="Kitambulisho hiki kipo tayari.", success=None)

    USERS[identifier] = {
        "password_hash": generate_password_hash(password),
        "role": "admin",
        "name": f"Afisa - {fullname}",
        "phone": phone,
        "email": f"{identifier.lower()}@tra.go.tz",
        "registered_at": datetime.now(),
        "can_add_officers": False, # Afisa mpya HANA ruhusa ya kumsajili mwingine
    }
    save_state()
    return render_template_string(HTML_TEMPLATE, page='add_officer', lang=lang, t=TR[lang], error=None, success="Afisa mpya wa TRA amesajiliwa kikamilifu!")

@app.route('/account/update', methods=['POST'])
def account_update():
    if 'identifier' not in session: return redirect(url_for('login'))
    identifier = session['identifier']
    user = USERS[identifier]

    fullname = request.form.get('fullname', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    old_password = request.form.get('old_password', '')
    new_password = request.form.get('new_password', '')
    confirm_new_password = request.form.get('confirm_new_password', '')

    user["name"] = fullname
    user["email"] = email
    user["phone"] = phone
    session['role_name'] = fullname

    # Ukaguzi wa Nenosiri la Awali kabla ya Kubadilisha
    if new_password:
        if not old_password or not check_password_hash(user["password_hash"], old_password):
            session['account_error'] = "Nenosiri la awali si sahihi. Mabadiliko ya nenosiri hayajahifadhiwa."
            return redirect(url_for('index'))
        if new_password != confirm_new_password:
            session['account_error'] = "Manenosiri mapya hayafanani."
            return redirect(url_for('index'))
        user["password_hash"] = generate_password_hash(new_password)
        session['account_success'] = "Taarifa na Nenosiri Jipya zimehifadhiwa kikamilifu."
    else:
        session['account_success'] = "Taarifa za akaunti zimehifadhiwa."

    save_state()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/answer-question', methods=['POST'])
def answer_question():
    if session.get('role') != 'admin': return jsonify({"status": "error"}), 403
    data = request.json or {}
    qid, answer_text = data.get('id'), (data.get('answer') or '').strip()
    
    entry = next((q for q in UNANSWERED_QUESTIONS if q.get("id") == qid), None)
    if not entry or not answer_text: return jsonify({"status": "error"}), 400

    entry["answered"] = True
    entry["answer"] = answer_text
    
    # AI kujifunza jibu jipya
    keywords = [w for w in re.findall(r"\w{4,}", entry["text"].lower())][:5]
    if keywords:
        QA_DATABASE.append({"keywords": keywords, "sw": answer_text, "en": answer_text})

    # Kutuma jibu moja kwa moja kwa mtumiaji aliyewasilisha swali
    asker = entry.get("user")
    if asker:
        CHAT_HISTORY.setdefault(asker, []).append({
            "who": "bot",
            "text": f"<b>[Jibu la Admin kuhusu swali yako: '{entry['text']}']:</b><br>{answer_text}",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    save_state()
    return jsonify({"status": "success"})

@app.route('/api/chat', methods=['POST'])
def chat_bot():
    lang = get_lang()
    identifier = session.get('identifier', 'Asiyejulikana')
    data = request.json or {}
    user_msg = (data.get('message') or '').strip()
    if not user_msg: return jsonify({"response": "Tafadhali andika swali."})

    CHAT_HISTORY.setdefault(identifier, []).append({
        "who": "user", "text": user_msg, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    msg_lower = user_msg.lower()
    bot_reply = None

    for item in QA_DATABASE:
        if any(kw in msg_lower for kw in item["keywords"]):
            if item["sw"] == "__OFFICE_LOOKUP__":
                matched = [f"<b>📍 {m}</b>: {data['office']}, {data['address']} (Simu: {data['phone']})" for m, data in TRA_OFFICES.items() if m.lower() in msg_lower]
                bot_reply = "<br>".join(matched) if matched else "Ofisi kuu za TRA zipo katika kila Makao Makuu ya Mkoa. Bonyeza ramani kulia kuona anwani na alama ya location."
            else:
                bot_reply = item["sw"] if lang == 'sw' else item["en"]
            break

    if not bot_reply:
        bot_reply = "Swali lako limepokelewa na kupelekwa kwa Admin wa TRA. Utapata jibu direct hapa mara tu litakapojibiwa."
        UNANSWERED_QUESTIONS.append({
            "id": next_question_id(), "user": identifier, "text": user_msg,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "answered": False, "answer": None
        })

    CHAT_HISTORY[identifier].append({
        "who": "bot", "text": bot_reply, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_state()
    return jsonify({"response": bot_reply})

load_state()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)