from flask import Flask, render_template_string, redirect, url_for, request, session
import sys
import uuid
from datetime import datetime

from EmbeddedSQL import *
from actions import *
from buyer import *
from seller import *

app = Flask(__name__)
app.secret_key = "ebay_gui_secret"
db = None

# ── Base layout ────────────────────────────────────────────────────────────────

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eBay DB Interface</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'DM Sans', sans-serif; }
        .mono { font-family: 'DM Mono', monospace; }
        .fade-in { animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        table { border-collapse: collapse; width: 100%; }
        th { background: #f8f8f8; font-weight: 500; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #666; }
        td, th { padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: #fafafa; }
        input[type=text], input[type=password], input[type=number], textarea, select {
            width: 100%; border: 1px solid #e0e0e0; border-radius: 8px;
            padding: 10px 14px; font-size: 0.9rem; font-family: 'DM Sans', sans-serif;
            outline: none; transition: border-color 0.2s;
            background: white; color: #111;
        }
        input:focus, textarea:focus, select:focus { border-color: #111; }
        textarea { resize: vertical; min-height: 80px; }
        .btn-primary {
            display: inline-block; background: #111; color: white;
            padding: 10px 20px; border-radius: 8px; font-size: 0.9rem;
            font-weight: 500; cursor: pointer; border: none;
            transition: background 0.2s; width: 100%;
        }
        .btn-primary:hover { background: #333; }
        .btn-secondary {
            display: inline-block; background: white; color: #111;
            padding: 10px 20px; border-radius: 8px; font-size: 0.9rem;
            font-weight: 500; cursor: pointer; border: 1px solid #e0e0e0;
            transition: background 0.2s; width: 100%;
        }
        .btn-secondary:hover { background: #f5f5f5; }
        .btn-danger {
            display: inline-block; background: white; color: #dc2626;
            padding: 7px 16px; border-radius: 6px; font-size: 0.85rem;
            font-weight: 500; cursor: pointer; border: 1px solid #fca5a5;
            transition: all 0.2s;
        }
        .btn-danger:hover { background: #fef2f2; }
        .btn-action {
            display: inline-block; background: #111; color: white;
            padding: 7px 16px; border-radius: 6px; font-size: 0.85rem;
            font-weight: 500; cursor: pointer; border: none;
            transition: background 0.2s;
        }
        .btn-action:hover { background: #333; }
        .tag {
            display: inline-block; padding: 2px 8px; border-radius: 4px;
            font-size: 0.75rem; font-weight: 500;
        }
        .tag-active { background: #dcfce7; color: #166534; }
        .tag-closed { background: #f3f4f6; color: #374151; }
        .tag-available { background: #dbeafe; color: #1e40af; }
        .tag-sold { background: #fef3c7; color: #92400e; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">

    <!-- Navbar -->
    <nav style="background:white; border-bottom:1px solid #eee;" class="px-6 py-4 mb-8">
        <div style="max-width:960px; margin:0 auto; display:flex; justify-content:space-between; align-items:center;">
            <a href="/" style="text-decoration:none;">
                <span style="font-size:1.1rem; font-weight:600; color:#111; letter-spacing:-0.02em;">eBay <span style="color:#aaa; font-weight:300;">DB</span></span>
            </a>
            {% if session_login %}
            <div style="display:flex; align-items:center; gap:16px;">
                <span style="font-size:0.85rem; color:#888;">
                    {% if session_role == "Buyer" %}🛒{% elif session_role == "Seller" %}🏪{% else %}⚙️{% endif %}
                    <strong style="color:#111;">{{ session_login }}</strong>
                </span>
                <a href="/dashboard" style="font-size:0.85rem; color:#555; text-decoration:none;">Dashboard</a>
                <a href="/logout" style="font-size:0.85rem; color:#dc2626; text-decoration:none;">Logout</a>
            </div>
            {% endif %}
        </div>
    </nav>

    <!-- Page content -->
    <div style="max-width:960px; margin:0 auto; padding:0 24px 48px;" class="fade-in">
        CONTENT_PLACEHOLDER
    </div>

</body>
</html>"""


def render(content, **kwargs):
    from flask import session as s
    html = BASE.replace("CONTENT_PLACEHOLDER", content)
    return render_template_string(
        html,
        session_login=s.get("login"),
        session_role=s.get("role"),
        **kwargs
    )


def card(content, max_width="480px"):
    return f"""
    <div style="background:white; border:1px solid #eee; border-radius:16px;
                padding:40px; max-width:{max_width}; margin:40px auto; box-shadow:0 1px 4px rgba(0,0,0,0.04);">
        {content}
    </div>"""


def page_header(title, back_url="/dashboard", back_label="Dashboard"):
    return f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:28px;">
        <a href="{back_url}" style="color:#aaa; text-decoration:none; font-size:0.85rem;">← {back_label}</a>
        <span style="color:#eee;">|</span>
        <h1 style="font-size:1.4rem; font-weight:600; color:#111; margin:0;">{title}</h1>
    </div>"""


def alert(msg, kind="error"):
    color = "#dc2626" if kind == "error" else "#16a34a"
    bg = "#fef2f2" if kind == "error" else "#f0fdf4"
    border = "#fca5a5" if kind == "error" else "#86efac"
    return f"""<div style="background:{bg}; border:1px solid {border}; border-radius:8px;
                            padding:12px 16px; margin-bottom:16px; color:{color}; font-size:0.875rem;">
                {msg}</div>"""


def form_field(label, input_html, required=False):
    star = ' <span style="color:#dc2626;">*</span>' if required else ""
    return f"""
    <div style="margin-bottom:16px;">
        <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">{label}{star}</label>
        {input_html}
    </div>"""


# ── Templates ──────────────────────────────────────────────────────────────────

MAIN_MENU = card("""
    <div style="margin-bottom:32px;">
        <h1 style="font-size:1.8rem; font-weight:600; color:#111; margin:0 0 8px;">Welcome back</h1>
        <p style="color:#888; font-size:0.9rem; margin:0;">Sign in to browse and bid on auctions.</p>
    </div>
    <div style="display:flex; flex-direction:column; gap:10px;">
        <a href="/login" style="text-decoration:none;"><button class="btn-primary">Login</button></a>
        <a href="/register" style="text-decoration:none;"><button class="btn-secondary">Register</button></a>
    </div>
""")

LOGIN_PAGE = card("""
    <h1 style="font-size:1.5rem; font-weight:600; color:#111; margin:0 0 24px;">Login</h1>
    {% if error_html %}{{ error_html|safe }}{% endif %}
    <form method="POST">
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Username <span style="color:#dc2626;">*</span></label>
            <input type="text" name="login" required>
        </div>
        <div style="margin-bottom:24px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Password <span style="color:#dc2626;">*</span></label>
            <input type="password" name="password" required>
        </div>
        <button type="submit" class="btn-primary">Login</button>
    </form>
    <p style="text-align:center; margin-top:16px; font-size:0.85rem; color:#888;">
        No account? <a href="/register" style="color:#111; font-weight:500;">Register</a>
    </p>
""")

REGISTER_PAGE = card("""
    <h1 style="font-size:1.5rem; font-weight:600; color:#111; margin:0 0 4px;">Create Account</h1>
    <p style="color:#888; font-size:0.85rem; margin:0 0 24px;">New accounts start as Buyer. Seller access can be granted by an admin.</p>
    {% if error_html %}{{ error_html|safe }}{% endif %}
    {% if success_html %}{{ success_html|safe }}{% endif %}
    <form method="POST">
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Username <span style="color:#dc2626;">*</span></label>
            <input type="text" name="login" required>
        </div>
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Phone</label>
            <input type="text" name="phone">
        </div>
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Password <span style="color:#dc2626;">*</span></label>
            <input type="password" name="password" required>
        </div>
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Address</label>
            <input type="text" name="address">
        </div>
        <div style="margin-bottom:24px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Favorite Category</label>
            <input type="text" name="favorite_category">
        </div>
        <button type="submit" class="btn-primary" style="margin-bottom:10px;">Create Account</button>
    </form>
    <a href="/login" style="text-decoration:none;"><button class="btn-secondary">Already have an account? Login</button></a>
""")

BUYER_MENU = """
    <div style="margin-bottom:32px;">
        <p style="color:#888; font-size:0.85rem; margin:0 0 4px;">Buyer account</p>
        <h1 style="font-size:1.8rem; font-weight:600; color:#111; margin:0;">Hello, {{ login }} 👋</h1>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
        <a href="/browse" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">🔍</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Browse Auctions</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View all active listings</div>
            </div>
        </a>
        <a href="/search" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">🔎</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Search</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">Find by keyword</div>
            </div>
        </a>
        <a href="/place_bid" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">💰</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Place Bid</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">Bid on an auction</div>
            </div>
        </a>
        <a href="/my_bids" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">📋</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">My Bids</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View bid history</div>
            </div>
        </a>
        <a href="/won_auctions" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">🏆</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Won Auctions</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">Items you've won</div>
            </div>
        </a>
        <a href="/make_payment" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">💳</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Make Payment</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">Pay for won items</div>
            </div>
        </a>
        <a href="/profile" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">👤</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Profile</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View & edit info</div>
            </div>
        </a>
    </div>
"""

SELLER_MENU = """
    <div style="margin-bottom:32px;">
        <p style="color:#888; font-size:0.85rem; margin:0 0 4px;">Seller account</p>
        <h1 style="font-size:1.8rem; font-weight:600; color:#111; margin:0;">Hello, {{ login }} 👋</h1>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
        <a href="/browse" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">🔍</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Browse Auctions</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View all active listings</div>
            </div>
        </a>
        <a href="/create_item" style="text-decoration:none;">
            <div style="background:#111; border:1px solid #111; border-radius:12px; padding:20px; cursor:pointer; transition:opacity 0.2s;"
                 onmouseover="this.style.opacity='0.85'" onmouseout="this.style.opacity='1'">
                <div style="font-size:1.4rem; margin-bottom:8px;">➕</div>
                <div style="font-weight:500; color:white; font-size:0.9rem;">Create Auction</div>
                <div style="color:#888; font-size:0.8rem; margin-top:2px;">List a new item</div>
            </div>
        </a>
        <a href="/place_bid" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">💰</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Place Bid</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">Bid on an auction</div>
            </div>
        </a>
        <a href="/my_bids" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">📋</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">My Bids</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View bid history</div>
            </div>
        </a>
        <a href="/my_items" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">📦</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">My Items</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View your inventory</div>
            </div>
        </a>
        <a href="/my_auctions" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">🏷️</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">My Auctions</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">Track your listings</div>
            </div>
        </a>
        <a href="/won_auctions" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">🏆</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Won Auctions</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">Items you've won</div>
            </div>
        </a>
        <a href="/make_payment" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">💳</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Make Payment</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">Pay for won items</div>
            </div>
        </a>
        <a href="/end_auction" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">🔒</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">End Auction</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">Close a listing</div>
            </div>
        </a>
        <a href="/create_shipment" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">🚚</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Create Shipment</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">Ship paid orders</div>
            </div>
        </a>
        <a href="/profile" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">👤</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Profile</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View & edit info</div>
            </div>
        </a>
    </div>
"""

ADMIN_MENU = """
    <div style="margin-bottom:32px;">
        <p style="color:#888; font-size:0.85rem; margin:0 0 4px;">Admin account</p>
        <h1 style="font-size:1.8rem; font-weight:600; color:#111; margin:0;">Hello, {{ login }} ⚙️</h1>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
        <a href="/admin/users" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">👥</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Manage Users</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View and promote accounts</div>
            </div>
        </a>
        <a href="/admin/auctions" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">🏷️</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Monitor Auctions</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View all listings</div>
            </div>
        </a>
        <a href="/browse" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">🔍</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Browse Auctions</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View active listings</div>
            </div>
        </a>
        <a href="/profile" style="text-decoration:none;">
            <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; cursor:pointer; transition:box-shadow 0.2s;"
                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
                <div style="font-size:1.4rem; margin-bottom:8px;">👤</div>
                <div style="font-weight:500; color:#111; font-size:0.9rem;">Profile</div>
                <div style="color:#aaa; font-size:0.8rem; margin-top:2px;">View & edit info</div>
            </div>
        </a>
    </div>
"""

TABLE_WRAPPER_START = """
<div style="background:white; border:1px solid #eee; border-radius:16px; overflow:hidden; box-shadow:0 1px 4px rgba(0,0,0,0.04);">
<table>"""

TABLE_WRAPPER_END = """</table></div>"""

BROWSE_PAGE = """
    {{ header|safe }}
    {% if auctions %}
        """ + TABLE_WRAPPER_START + """
        <tr>
            <th>Auction ID</th><th>Item</th><th>Category</th>
            <th>Condition</th><th>Starting</th><th>Highest Bid</th><th>Seller</th>
        </tr>
        {% for row in auctions %}
        <tr>
            <td>
                <span class="mono" style="font-size:0.78rem; color:#888;">{{ row[0]|truncate(16, true, '…') }}</span>
                <button onclick="copyText('{{ row[0] }}', this)"
                        style="margin-left:6px; background:none; border:1px solid #e0e0e0;
                               border-radius:4px; padding:2px 6px; font-size:0.7rem;
                               color:#888; cursor:pointer;"
                        title="Copy Auction ID">
                    Copy
                </button>
            </td>
            <td>
                <span onclick="showDetail('{{ row[1] }}', '{{ row[3]|replace("'", "\\'") }}', '{{ row[2] }}', '{{ row[8] or "" }}')"
                      style="font-weight:500; color:#111; cursor:pointer; border-bottom:1px dashed #ccc;">
                    {{ row[1] }}
                </span>
            </td>
            <td style="color:#555;">{{ row[2] }}</td>
            <td><span class="tag tag-{{ row[4] }}">{{ row[4] }}</span></td>
            <td style="color:#555;">${{ "%.2f"|format(row[5]) }}</td>
            <td style="font-weight:500; color:#111;">
                {% if row[6] %} ${{ "%.2f"|format(row[6]) }} {% else %}
                <span style="color:#aaa; font-size:0.85rem;">No bids</span>{% endif %}
            </td>
            <td style="color:#555;">{{ row[7] }}</td>
        </tr>
        {% endfor %}
        """ + TABLE_WRAPPER_END + """
    {% else %}
        <div style="text-align:center; padding:48px; color:#aaa;">No active auctions found.</div>
    {% endif %}

    <!-- Modal -->
    <div id="modal-overlay"
         onclick="closeModal()"
         style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.3);
                z-index:100; backdrop-filter:blur(2px);">
    </div>
    <div id="modal"
         style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);
                background:white; border-radius:16px; padding:32px; width:480px; max-width:90vw;
                box-shadow:0 20px 60px rgba(0,0,0,0.15); z-index:101;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
            <h2 id="modal-title" style="font-size:1.2rem; font-weight:600; color:#111; margin:0;"></h2>
            <button onclick="closeModal()"
                    style="background:none; border:none; font-size:1.2rem; color:#aaa;
                           cursor:pointer; padding:0; line-height:1;">✕</button>
        </div>
        <div id="modal-category"
             style="font-size:0.8rem; color:#888; margin-bottom:16px;"></div>
        <p id="modal-description"
           style="font-size:0.9rem; color:#444; line-height:1.6; margin:0 0 20px;"></p>
        <div id="modal-url-wrapper" style="display:none;">
            <a id="modal-url" href="#" target="_blank"
               style="font-size:0.85rem; color:#111; font-weight:500; text-decoration:underline;">
                View Image →
            </a>
        </div>
    </div>

    <script>
    function showDetail(name, description, category, imageUrl) {
        document.getElementById('modal-title').innerText = name;
        document.getElementById('modal-category').innerText = '📂 ' + category;
        document.getElementById('modal-description').innerText = description || 'No description available.';

        const urlWrapper = document.getElementById('modal-url-wrapper');
        const urlLink    = document.getElementById('modal-url');
        if (imageUrl && imageUrl.trim() !== '') {
            urlLink.href = imageUrl;
            urlWrapper.style.display = 'block';
        } else {
            urlWrapper.style.display = 'none';
        }

        document.getElementById('modal-overlay').style.display = 'block';
        document.getElementById('modal').style.display = 'block';
    }

    function closeModal() {
        document.getElementById('modal-overlay').style.display = 'none';
        document.getElementById('modal').style.display = 'none';
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeModal();
    });

    function copyText(text, btn) {
        navigator.clipboard.writeText(text).then(function() {
            btn.innerText = 'Copied!';
            btn.style.color = '#16a34a';
            btn.style.borderColor = '#86efac';
            setTimeout(function() {
                btn.innerText = 'Copy';
                btn.style.color = '#888';
                btn.style.borderColor = '#e0e0e0';
            }, 1500);
        });
    }
    </script>
"""

SEARCH_PAGE = """
    {{ header|safe }}
    <div style="background:white; border:1px solid #eee; border-radius:12px; padding:20px; margin-bottom:24px;">
        <form method="POST" style="display:flex; gap:10px; align-items:flex-end;">
            <div style="flex:1;">
                <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Search keyword</label>
                <input type="text" name="keyword" placeholder="e.g. guitar, vintage, electronics" required>
            </div>
            <button type="submit" class="btn-action" style="white-space:nowrap; padding:10px 20px;">Search</button>
        </form>
    </div>
    {% if results is not none %}
        {% if results %}
            """ + TABLE_WRAPPER_START + """
            <tr><th>Auction ID</th><th>Item</th><th>Category</th><th>Description</th><th>Highest Bid</th><th>Status</th><th>Seller</th></tr>
            {% for row in results %}
            <tr>
                <td class="mono" style="font-size:0.78rem; color:#888;">{{ row[0]|truncate(16, true, '…') }}</td>
                <td style="font-weight:500; color:#111;">{{ row[1] }}</td>
                <td style="color:#555;">{{ row[2] }}</td>
                <td style="color:#555; max-width:200px;">{{ row[3]|truncate(60) }}</td>
                <td style="font-weight:500;">${{ "%.2f"|format(row[4]) }}</td>
                <td><span class="tag tag-{{ row[5] }}">{{ row[5] }}</span></td>
                <td style="color:#555;">{{ row[6] }}</td>
            </tr>
            {% endfor %}
            """ + TABLE_WRAPPER_END + """
        {% else %}
            <div style="text-align:center; padding:48px; color:#aaa;">No auctions matched your search.</div>
        {% endif %}
    {% endif %}
"""

PLACE_BID_PAGE = card("""
    {{ header|safe }}
    {% if error_html %}{{ error_html|safe }}{% endif %}
    {% if success_html %}{{ success_html|safe }}{% endif %}
    <form method="POST">
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Auction ID <span style="color:#dc2626;">*</span></label>
            <input type="text" name="auction_id" required placeholder="e.g. AUC000000000001">
        </div>
        <div style="margin-bottom:24px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Bid Amount <span style="color:#dc2626;">*</span></label>
            <div style="position:relative;">
                <span style="position:absolute; left:12px; top:50%; transform:translateY(-50%); color:#888; font-weight:500;">$</span>
                <input type="number" step="0.01" name="bid_amount" required style="padding-left:28px;">
            </div>
        </div>
        <button type="submit" class="btn-primary">Place Bid</button>
    </form>
""", max_width="440px")

VIEW_BIDS_PAGE = """
    {{ header|safe }}
    {% if bids %}
        """ + TABLE_WRAPPER_START + """
        <tr><th>Bid ID</th><th>Item</th><th>My Bid</th><th>Highest Bid</th><th>Status</th><th>Time</th></tr>
        {% for row in bids %}
        <tr>
            <td class="mono" style="font-size:0.78rem; color:#888;">{{ row[0]|truncate(16, true, '…') }}</td>
            <td style="font-weight:500; color:#111;">{{ row[2] }}</td>
            <td style="font-weight:500; color:#111;">${{ "%.2f"|format(row[3]) }}</td>
            <td style="color:#555;">
                {% if row[3] == row[4] %}
                    <span style="color:#16a34a; font-weight:500;">${{ "%.2f"|format(row[4]) }} ✓ Winning</span>
                {% else %}
                    <span style="color:#dc2626;">${{ "%.2f"|format(row[4]) }} Outbid</span>
                {% endif %}
            </td>
            <td><span class="tag tag-{{ row[5] }}">{{ row[5] }}</span></td>
            <td style="color:#888; font-size:0.82rem;">{{ row[6] }}</td>
        </tr>
        {% endfor %}
        """ + TABLE_WRAPPER_END + """
    {% else %}
        <div style="text-align:center; padding:48px; color:#aaa;">You have not placed any bids yet.</div>
    {% endif %}
"""

WON_AUCTIONS_PAGE = """
    {{ header|safe }}
    {% if auctions %}
        """ + TABLE_WRAPPER_START + """
        <tr><th>Auction ID</th><th>Item</th><th>Final Price</th><th>Status</th><th>Seller</th></tr>
        {% for row in auctions %}
        <tr>
            <td class="mono" style="font-size:0.78rem; color:#888;">{{ row[0]|truncate(16, true, '…') }}</td>
            <td style="font-weight:500; color:#111;">{{ row[1] }}</td>
            <td style="font-weight:500; color:#111;">${{ "%.2f"|format(row[2]) }}</td>
            <td><span class="tag tag-{{ row[3] }}">{{ row[3] }}</span></td>
            <td style="color:#555;">{{ row[4] }}</td>
        </tr>
        {% endfor %}
        """ + TABLE_WRAPPER_END + """
    {% else %}
        <div style="text-align:center; padding:48px; color:#aaa;">You have not won any auctions yet.</div>
    {% endif %}
"""

MAKE_PAYMENT_PAGE = """
    {{ header|safe }}
    {% if error_html %}{{ error_html|safe }}{% endif %}
    {% if success_html %}{{ success_html|safe }}{% endif %}
    {% if auctions %}
        """ + TABLE_WRAPPER_START + """
        <tr><th>Auction ID</th><th>Item</th><th>Amount Due</th><th>Seller</th><th>Action</th></tr>
        {% for row in auctions %}
        <tr>
            <td class="mono" style="font-size:0.78rem; color:#888;">{{ row[0]|truncate(16, true, '…') }}</td>
            <td style="font-weight:500; color:#111;">{{ row[1] }}</td>
            <td style="font-weight:600; color:#111; font-size:1rem;">${{ "%.2f"|format(row[2]) }}</td>
            <td style="color:#555;">{{ row[3] }}</td>
            <td>
                <form method="POST">
                    <input type="hidden" name="auction_id" value="{{ row[0] }}">
                    <input type="hidden" name="amount" value="{{ row[2] }}">
                    <button type="submit" class="btn-action">Pay Now</button>
                </form>
            </td>
        </tr>
        {% endfor %}
        """ + TABLE_WRAPPER_END + """
    {% else %}
        <div style="text-align:center; padding:48px; color:#aaa;">No pending payments.</div>
    {% endif %}
"""

PROFILE_PAGE = card("""
    {{ header|safe }}
    {% if profile %}
    <div style="display:flex; flex-direction:column; gap:12px; margin-bottom:24px;">
        {% set labels = ['Login', 'Phone', 'Role', 'Address', 'Favorite Category'] %}
        {% for i in range(5) %}
        <div style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #f0f0f0;">
            <span style="font-size:0.82rem; color:#888; font-weight:500;">{{ labels[i] }}</span>
            <span style="font-size:0.9rem; color:#111; font-weight:{% if i == 0 %}600{% else %}400{% endif %};">
                {{ profile[i] or '—' }}
            </span>
        </div>
        {% endfor %}
    </div>
    <a href="/edit_profile" style="text-decoration:none;"><button class="btn-primary">Edit Profile</button></a>
    {% endif %}
""", max_width="480px")

EDIT_PROFILE_PAGE = card("""
    {{ header|safe }}
    {% if success_html %}{{ success_html|safe }}{% endif %}
    <form method="POST">
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Phone</label>
            <input type="text" name="phone" value="{{ profile[1] or '' }}">
        </div>
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Address</label>
            <input type="text" name="address" value="{{ profile[3] or '' }}">
        </div>
        <div style="margin-bottom:24px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Favorite Category</label>
            <input type="text" name="favorite_category" value="{{ profile[4] or '' }}">
        </div>
        <button type="submit" class="btn-primary">Save Changes</button>
    </form>
""", max_width="480px")

CREATE_ITEM_PAGE = card("""
    {{ header|safe }}
    {% if error_html %}{{ error_html|safe }}{% endif %}
    {% if success_html %}{{ success_html|safe }}{% endif %}
    <form method="POST">
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Item Name <span style="color:#dc2626;">*</span></label>
            <input type="text" name="item_name" required>
        </div>
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Category</label>
            <input type="text" name="category">
        </div>
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Image URL (optional)</label>
            <input type="text" name="image_url">
        </div>
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Condition</label>
            <select name="condition">
                <option value="available">Available</option>
                <option value="sold">Sold</option>
                <option value="removed">Removed</option>
            </select>
        </div>
        <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Starting Price <span style="color:#dc2626;">*</span></label>
            <div style="position:relative;">
                <span style="position:absolute; left:12px; top:50%; transform:translateY(-50%); color:#888; font-weight:500;">$</span>
                <input type="number" step="0.01" name="starting_price" required style="padding-left:28px;">
            </div>
        </div>
        <div style="margin-bottom:24px;">
            <label style="display:block; font-size:0.8rem; font-weight:500; color:#555; margin-bottom:6px;">Description <span style="color:#dc2626;">*</span></label>
            <textarea name="description" required></textarea>
        </div>
        <button type="submit" class="btn-primary">Create Listing</button>
    </form>
""", max_width="520px")

END_AUCTION_PAGE = """
    {{ header|safe }}
    {% if error_html %}{{ error_html|safe }}{% endif %}
    {% if success_html %}{{ success_html|safe }}{% endif %}
    {% if auctions %}
        """ + TABLE_WRAPPER_START + """
        <tr><th>Auction ID</th><th>Item</th><th>Category</th><th>Highest Bid</th><th>Action</th></tr>
        {% for row in auctions %}
        <tr>
            <td class="mono" style="font-size:0.78rem; color:#888;">{{ row[0]|truncate(16, true, '…') }}</td>
            <td style="font-weight:500; color:#111;">{{ row[1] }}</td>
            <td style="color:#555;">{{ row[2] }}</td>
            <td style="font-weight:500;">
                {% if row[3] %} ${{ "%.2f"|format(row[3]) }}
                {% else %}<span style="color:#aaa;">No bids</span>{% endif %}
            </td>
            <td>
                <form method="POST">
                    <input type="hidden" name="auction_id" value="{{ row[0] }}">
                    <button type="submit" class="btn-danger">End Auction</button>
                </form>
            </td>
        </tr>
        {% endfor %}
        """ + TABLE_WRAPPER_END + """
    {% else %}
        <div style="text-align:center; padding:48px; color:#aaa;">You have no active auctions.</div>
    {% endif %}
"""

MY_ITEMS_PAGE = """
    {{ header|safe }}
    {% if items %}
        """ + TABLE_WRAPPER_START + """
        <tr><th>Item ID</th><th>Name</th><th>Category</th><th>Condition</th><th>Starting Price</th><th>Description</th></tr>
        {% for row in items %}
        <tr>
            <td class="mono" style="font-size:0.78rem; color:#888;">{{ row[0]|truncate(16, true, '…') }}</td>
            <td style="font-weight:500; color:#111;">{{ row[1] }}</td>
            <td style="color:#555;">{{ row[2] }}</td>
            <td><span class="tag tag-{{ row[3] }}">{{ row[3] }}</span></td>
            <td style="color:#555;">${{ "%.2f"|format(row[4]) }}</td>
            <td style="color:#888; font-size:0.85rem;">{{ row[5]|truncate(60) }}</td>
        </tr>
        {% endfor %}
        """ + TABLE_WRAPPER_END + """
    {% else %}
        <div style="text-align:center; padding:48px; color:#aaa;">You have no items yet.</div>
    {% endif %}
"""

MY_AUCTIONS_PAGE = """
    {{ header|safe }}
    {% if auctions %}
        """ + TABLE_WRAPPER_START + """
        <tr><th>Auction ID</th><th>Item</th><th>Category</th><th>Highest Bid</th><th>Status</th><th>Winner</th></tr>
        {% for row in auctions %}
        <tr>
            <td class="mono" style="font-size:0.78rem; color:#888;">{{ row[0]|truncate(16, true, '…') }}</td>
            <td style="font-weight:500; color:#111;">{{ row[1] }}</td>
            <td style="color:#555;">{{ row[2] }}</td>
            <td style="font-weight:500;">
                {% if row[3] %} ${{ "%.2f"|format(row[3]) }}
                {% else %}<span style="color:#aaa;">No bids</span>{% endif %}
            </td>
            <td><span class="tag tag-{{ row[4] }}">{{ row[4] }}</span></td>
            <td style="color:#555;">{{ row[5] or '—' }}</td>
        </tr>
        {% endfor %}
        """ + TABLE_WRAPPER_END + """
    {% else %}
        <div style="text-align:center; padding:48px; color:#aaa;">You have no auctions yet.</div>
    {% endif %}
"""

CREATE_SHIPMENT_PAGE = """
    {{ header|safe }}
    {% if error_html %}{{ error_html|safe }}{% endif %}
    {% if success_html %}{{ success_html|safe }}{% endif %}
    {% if auctions %}
        """ + TABLE_WRAPPER_START + """
        <tr><th>Auction ID</th><th>Item</th><th>Winner</th><th>Final Price</th><th>Shipping Details</th></tr>
        {% for row in auctions %}
        <tr>
            <td class="mono" style="font-size:0.78rem; color:#888;">{{ row[0]|truncate(16, true, '…') }}</td>
            <td style="font-weight:500; color:#111;">{{ row[1] }}</td>
            <td style="color:#555;">{{ row[2] }}</td>
            <td style="font-weight:500;">${{ "%.2f"|format(row[3]) }}</td>
            <td>
                <form method="POST" style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                    <input type="hidden" name="auction_id" value="{{ row[0] }}">
                    <input type="text" name="address" placeholder="Shipping address" required style="width:160px; font-size:0.82rem; padding:6px 10px;">
                    <input type="number" name="tracking_number" placeholder="Tracking # (opt.)" style="width:130px; font-size:0.82rem; padding:6px 10px;">
                    <button type="submit" class="btn-action">Ship</button>
                </form>
            </td>
        </tr>
        {% endfor %}
        """ + TABLE_WRAPPER_END + """
    {% else %}
        <div style="text-align:center; padding:48px; color:#aaa;">No eligible auctions for shipment.</div>
    {% endif %}
"""

ADMIN_USERS_PAGE = """
    {{ header|safe }}
    {% if error_html %}{{ error_html|safe }}{% endif %}
    {% if success_html %}{{ success_html|safe }}{% endif %}
    """ + TABLE_WRAPPER_START + """
    <tr>
        <th>Login</th><th>Phone</th><th>Role</th><th>Address</th><th>Favorite Category</th><th>Action</th>
    </tr>
    {% for row in users %}
    <tr>
        <td style="font-weight:500; color:#111;">{{ row[0] }}</td>
        <td style="color:#555;">{{ row[1] or '—' }}</td>
        <td>
            {% if row[2] == 'Admin' %}
                <span class="tag" style="background:#fce7f3; color:#9d174d;">Admin</span>
            {% elif row[2] == 'Seller' %}
                <span class="tag" style="background:#ede9fe; color:#5b21b6;">Seller</span>
            {% else %}
                <span class="tag tag-available">Buyer</span>
            {% endif %}
        </td>
        <td style="color:#555;">{{ row[3] or '—' }}</td>
        <td style="color:#555;">{{ row[4] or '—' }}</td>
        <td>
            {% if row[2] != 'Admin' %}
            <form method="POST" style="display:flex; gap:6px; align-items:center;">
                <input type="hidden" name="target_login" value="{{ row[0] }}">
                <select name="new_role" style="font-size:0.82rem; padding:5px 8px; width:auto;">
                    <option value="Buyer"  {% if row[2] == 'Buyer'  %}selected{% endif %}>Buyer</option>
                    <option value="Seller" {% if row[2] == 'Seller' %}selected{% endif %}>Seller</option>
                    <option value="Admin"  {% if row[2] == 'Admin'  %}selected{% endif %}>Admin</option>
                </select>
                <button type="submit" class="btn-action">Update</button>
            </form>
            {% else %}
                <span style="color:#aaa; font-size:0.82rem;">—</span>
            {% endif %}
        </td>
    </tr>
    {% endfor %}
    """ + TABLE_WRAPPER_END + """
"""

ADMIN_AUCTIONS_PAGE = """
    {{ header|safe }}
    {% if auctions %}
        """ + TABLE_WRAPPER_START + """
        <tr>
            <th>Auction ID</th><th>Item</th><th>Category</th>
            <th>Seller</th><th>Highest Bid</th><th>Status</th><th>Winner</th>
        </tr>
        {% for row in auctions %}
        <tr>
            <td class="mono" style="font-size:0.78rem; color:#888;">{{ row[0]|truncate(16, true, '…') }}</td>
            <td style="font-weight:500; color:#111;">{{ row[1] }}</td>
            <td style="color:#555;">{{ row[2] }}</td>
            <td style="color:#555;">{{ row[3] }}</td>
            <td style="font-weight:500;">
                {% if row[4] %} ${{ "%.2f"|format(row[4]) }}
                {% else %}<span style="color:#aaa;">No bids</span>{% endif %}
            </td>
            <td><span class="tag tag-{{ row[5] }}">{{ row[5] }}</span></td>
            <td style="color:#555;">{{ row[6] or '—' }}</td>
        </tr>
        {% endfor %}
        """ + TABLE_WRAPPER_END + """
    {% else %}
        <div style="text-align:center; padding:48px; color:#aaa;">No auctions found.</div>
    {% endif %}
"""


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def main_menu():
    return render(MAIN_MENU)


@app.route("/login", methods=["GET", "POST"])
def login():
    error_html = None
    if request.method == "POST":
        login_input = request.form["login"].strip()
        password    = request.form["password"].strip()
        user = db.fetch_one('SELECT login, role FROM "User" WHERE login = %s AND password = %s;',
                            (login_input, password))
        if user is None:
            error_html = alert("Invalid login or password.")
        else:
            session["login"] = user[0].strip()
            session["role"]  = user[1].strip()
            return redirect(url_for("dashboard"))
    return render(LOGIN_PAGE, error_html=error_html)


@app.route("/register", methods=["GET", "POST"])
def register():
    error_html = None
    success_html = None
    if request.method == "POST":
        login_val    = request.form["login"].strip()
        phone        = request.form["phone"].strip()
        password     = request.form["password"].strip()
        address      = request.form["address"].strip()
        fav_category = request.form["favorite_category"].strip()
        if not login_val or not password:
            error_html = alert("Login and password are required.")
        else:
            ok = db.execute_update(
                'INSERT INTO "User" (login, phoneNum, role, password, address, favoriteCategory) VALUES (%s, %s, \'Buyer\', %s, %s, %s);',
                (login_val, phone, password, address, fav_category)
            )
            if ok:
                success_html = alert(f"Account '{login_val}' created! You can now log in.", "success")
            else:
                error_html = alert("Username already taken or an error occurred.")
    return render(REGISTER_PAGE, error_html=error_html, success_html=success_html)


@app.route("/dashboard")
def dashboard():
    if "login" not in session:
        return redirect(url_for("main_menu"))
    role = session["role"]
    if role == "Buyer":
        return render(BUYER_MENU, login=session["login"])
    elif role == "Seller":
        return render(SELLER_MENU, login=session["login"])
    elif role == "Admin":
        return render(ADMIN_MENU, login=session["login"])
    return redirect(url_for("main_menu"))


@app.route("/profile")
def profile():
    if "login" not in session:
        return redirect(url_for("main_menu"))
    data = db.fetch_one('SELECT login, phoneNum, role, address, favoriteCategory FROM "User" WHERE login = %s;',
                        (session["login"],))
    h = page_header("My Profile")
    return render(PROFILE_PAGE, profile=data, header=h)


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "login" not in session:
        return redirect(url_for("main_menu"))
    success_html = None
    data = db.fetch_one('SELECT login, phoneNum, role, address, favoriteCategory FROM "User" WHERE login = %s;',
                        (session["login"],))
    if request.method == "POST":
        phone        = request.form["phone"].strip()
        address      = request.form["address"].strip()
        fav_category = request.form["favorite_category"].strip()
        db.execute_update('UPDATE "User" SET phoneNum = %s, address = %s, favoriteCategory = %s WHERE login = %s;',
                          (phone, address, fav_category, session["login"]))
        success_html = alert("Profile updated!", "success")
        data = db.fetch_one('SELECT login, phoneNum, role, address, favoriteCategory FROM "User" WHERE login = %s;',
                            (session["login"],))
    h = page_header("Edit Profile", "/profile", "Profile")
    return render(EDIT_PROFILE_PAGE, profile=data, success_html=success_html, header=h)


@app.route("/browse")
def browse():
    if "login" not in session:
        return redirect(url_for("main_menu"))
    auctions = db.fetch_all("""
        SELECT Auction.auctionID, Item.itemName, Item.category, Item.description,
            Item.condition, Item.startingPrice, Auction.currentHighestBid,
            Auction.sellerLogin, Item.imageURL
        FROM Auction JOIN Item ON Auction.itemID = Item.itemID
        WHERE Auction.auctionStatus = 'active' ORDER BY Auction.auctionID;
    """)
    h = page_header("Active Auctions")
    return render(BROWSE_PAGE, auctions=auctions, header=h)


@app.route("/search", methods=["GET", "POST"])
def search():
    if "login" not in session:
        return redirect(url_for("main_menu"))
    results = None
    if request.method == "POST":
        keyword = request.form["keyword"].strip()
        pattern = f"%{keyword}%"
        results = db.fetch_all("""
            SELECT Auction.auctionID, Item.itemName, Item.category, Item.description,
                   Auction.currentHighestBid, Auction.auctionStatus, Auction.sellerLogin
            FROM Auction JOIN Item ON Auction.itemID = Item.itemID
            WHERE Auction.auctionStatus = 'active'
              AND (LOWER(Item.itemName) LIKE LOWER(%s)
                OR LOWER(Item.category) LIKE LOWER(%s)
                OR LOWER(Item.description) LIKE LOWER(%s))
            ORDER BY Auction.currentHighestBid;
        """, (pattern, pattern, pattern))
    h = page_header("Search Auctions")
    return render(SEARCH_PAGE, results=results, header=h)


@app.route("/place_bid", methods=["GET", "POST"])
def place_bid():
    if "login" not in session or session["role"] not in ("Buyer", "Seller"):
        return redirect(url_for("main_menu"))
    error_html = None
    success_html = None
    if request.method == "POST":
        auction_id  = request.form["auction_id"].strip()
        buyer_login = session["login"]
        try:
            bid_amount = float(request.form["bid_amount"])
        except ValueError:
            error_html = alert("Invalid bid amount.")
            h = page_header("Place Bid")
            return render(PLACE_BID_PAGE, error_html=error_html, success_html=None, header=h)
        auction = db.fetch_one("SELECT sellerLogin, currentHighestBid, auctionStatus FROM Auction WHERE auctionID = %s;",
                               (auction_id,))
        if auction is None:
            error_html = alert("Auction not found.")
        elif auction[2] != "active":
            error_html = alert("This auction is not active.")
        elif auction[0].strip() == buyer_login:
            error_html = alert("You cannot bid on your own auction.")
        elif auction[1] is not None and bid_amount <= float(auction[1]):
            error_html = alert(f"Bid must be greater than current highest bid (${auction[1]:.2f}).")
        else:
            bid_id = ("BID" + uuid.uuid4().hex)[:30]
            ok = db.execute_transaction([
                ("INSERT INTO Bid (bidId, bidAmount, bidTimestamp, buyerLogin, auctionID) VALUES (%s, %s, %s, %s, %s);",
                 (bid_id, bid_amount, datetime.now(), buyer_login, auction_id)),
                ("UPDATE Auction SET currentHighestBid = %s WHERE auctionID = %s;",
                 (bid_amount, auction_id))
            ])
            if ok:
                success_html = alert(f"Bid of ${bid_amount:.2f} placed successfully!", "success")
            else:
                error_html = alert("Something went wrong.")
    h = page_header("Place Bid")
    return render(PLACE_BID_PAGE, error_html=error_html, success_html=success_html, header=h)


@app.route("/my_bids")
def my_bids():
    if "login" not in session or session["role"] not in ("Buyer", "Seller"):
        return redirect(url_for("main_menu"))
    bids = db.fetch_all("""
        SELECT Bid.bidId, Bid.auctionID, Item.itemName, Bid.bidAmount,
               Auction.currentHighestBid, Auction.auctionStatus, Bid.bidTimestamp
        FROM Bid JOIN Auction ON Bid.auctionID = Auction.auctionID
        JOIN Item ON Auction.itemID = Item.itemID
        WHERE Bid.buyerLogin = %s ORDER BY Bid.bidTimestamp DESC;
    """, (session["login"],))
    h = page_header("My Bids")
    return render(VIEW_BIDS_PAGE, bids=bids, header=h)


@app.route("/won_auctions")
def won_auctions():
    if "login" not in session or session["role"] not in ("Buyer", "Seller"):
        return redirect(url_for("main_menu"))
    auctions = db.fetch_all("""
        SELECT Auction.auctionID, Item.itemName, Auction.currentHighestBid,
               Auction.auctionStatus, Auction.sellerLogin
        FROM Auction JOIN Item ON Auction.itemID = Item.itemID
        WHERE Auction.buyerLogin = %s ORDER BY Auction.auctionID;
    """, (session["login"],))
    h = page_header("Auctions I Won")
    return render(WON_AUCTIONS_PAGE, auctions=auctions, header=h)


@app.route("/make_payment", methods=["GET", "POST"])
def make_payment():
    if "login" not in session or session["role"] not in ("Buyer", "Seller"):
        return redirect(url_for("main_menu"))
    error_html = None
    success_html = None
    buyer_login = session["login"]
    if request.method == "POST":
        auction_id = request.form["auction_id"].strip()
        amount     = float(request.form["amount"])
        auction = db.fetch_one("SELECT currentHighestBid, buyerLogin, auctionStatus FROM Auction WHERE auctionID = %s;",
                               (auction_id,))
        if auction is None:
            error_html = alert("Auction not found.")
        elif auction[1] is None or auction[1].strip() != buyer_login:
            error_html = alert("You are not the winner of this auction.")
        elif auction[2] != "closed":
            error_html = alert("Auction must be closed before payment.")
        else:
            existing = db.fetch_one("SELECT paymentID FROM Payment WHERE auctionID = %s;", (auction_id,))
            if existing:
                error_html = alert("Payment already made for this auction.")
            else:
                payment_id = ("PAY" + uuid.uuid4().hex)[:30]
                ok = db.execute_update("INSERT INTO Payment (paymentID, amount, paymentStatus, buyerLogin, auctionID) VALUES (%s, %s, 'completed', %s, %s);",
                                       (payment_id, amount, buyer_login, auction_id))
                if ok:
                    success_html = alert(f"Payment of ${amount:.2f} completed!", "success")
                else:
                    error_html = alert("Something went wrong.")
    auctions = db.fetch_all("""
        SELECT Auction.auctionID, Item.itemName, Auction.currentHighestBid, Auction.sellerLogin
        FROM Auction JOIN Item ON Auction.itemID = Item.itemID
        LEFT JOIN Payment ON Auction.auctionID = Payment.auctionID
        WHERE Auction.buyerLogin = %s AND Auction.auctionStatus = 'closed' AND Payment.paymentID IS NULL;
    """, (buyer_login,))
    h = page_header("Make Payment")
    return render(MAKE_PAYMENT_PAGE, auctions=auctions, error_html=error_html, success_html=success_html, header=h)


@app.route("/create_item", methods=["GET", "POST"])
def create_item():
    if "login" not in session or session["role"] != "Seller":
        return redirect(url_for("main_menu"))
    error_html = None
    success_html = None
    if request.method == "POST":
        item_name    = request.form["item_name"].strip()
        category     = request.form["category"].strip()
        image_url    = request.form["image_url"].strip()
        condition    = request.form["condition"]
        description  = request.form["description"].strip()
        seller_login = session["login"]
        try:
            starting_price = float(request.form["starting_price"])
        except ValueError:
            error_html = alert("Invalid starting price.")
            h = page_header("Create Item & Auction")
            return render(CREATE_ITEM_PAGE, error_html=error_html, success_html=None, header=h)
        item_id    = ("ITEM" + uuid.uuid4().hex)[:20]
        auction_id = ("AUC"  + uuid.uuid4().hex)[:30]
        ok = db.execute_transaction([
            ("INSERT INTO Item (itemID, itemName, category, imageURL, condition, startingPrice, description, sellerLogin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
             (item_id, item_name, category, image_url, condition, starting_price, description, seller_login)),
            ("INSERT INTO Auction (auctionID, auctionStatus, currentHighestBid, sellerLogin, itemID, buyerLogin) VALUES (%s, 'active', %s, %s, %s, NULL);",
             (auction_id, starting_price, seller_login, item_id))
        ])
        if ok:
            success_html = alert(f"Listing created! Auction ID: {auction_id}", "success")
        else:
            error_html = alert("Something went wrong.")
    h = page_header("Create Item & Auction")
    return render(CREATE_ITEM_PAGE, error_html=error_html, success_html=success_html, header=h)


@app.route("/end_auction", methods=["GET", "POST"])
def end_auction():
    if "login" not in session or session["role"] != "Seller":
        return redirect(url_for("main_menu"))
    error_html = None
    success_html = None
    if request.method == "POST":
        auction_id   = request.form["auction_id"].strip()
        seller_login = session["login"]
        auction = db.fetch_one("SELECT auctionID FROM Auction WHERE auctionID = %s AND sellerLogin = %s AND auctionStatus = 'active';",
                               (auction_id, seller_login))
        if auction is None:
            error_html = alert("Auction not found, not yours, or already closed.")
        else:
            winner = db.fetch_one("SELECT buyerLogin FROM Bid WHERE auctionID = %s ORDER BY bidAmount DESC, bidTimestamp ASC LIMIT 1;",
                                  (auction_id,))
            winner_login = winner[0].strip() if winner else None
            statements = [("UPDATE Auction SET auctionStatus = 'closed', buyerLogin = %s WHERE auctionID = %s;",
                           (winner_login, auction_id))]
            if winner_login:
                statements.append(("UPDATE Item SET condition = 'sold' WHERE itemID = (SELECT itemID FROM Auction WHERE auctionID = %s);",
                                   (auction_id,)))
            ok = db.execute_transaction(statements)
            if ok:
                msg = f"Auction closed. Winner: {winner_login}" if winner_login else "Auction closed. No bids were placed."
                success_html = alert(msg, "success")
            else:
                error_html = alert("Something went wrong.")
    auctions = db.fetch_all("""
        SELECT Auction.auctionID, Item.itemName, Item.category, Auction.currentHighestBid
        FROM Auction JOIN Item ON Auction.itemID = Item.itemID
        WHERE Auction.sellerLogin = %s AND Auction.auctionStatus = 'active' ORDER BY Auction.auctionID;
    """, (session["login"],))
    h = page_header("End Auction")
    return render(END_AUCTION_PAGE, auctions=auctions, error_html=error_html, success_html=success_html, header=h)


@app.route("/my_items")
def my_items():
    if "login" not in session or session["role"] != "Seller":
        return redirect(url_for("main_menu"))
    items = db.fetch_all("SELECT itemID, itemName, category, condition, startingPrice, description FROM Item WHERE sellerLogin = %s ORDER BY itemID;",
                         (session["login"],))
    h = page_header("My Items")
    return render(MY_ITEMS_PAGE, items=items, header=h)


@app.route("/my_auctions")
def my_auctions():
    if "login" not in session or session["role"] != "Seller":
        return redirect(url_for("main_menu"))
    auctions = db.fetch_all("""
        SELECT Auction.auctionID, Item.itemName, Item.category,
               Auction.currentHighestBid, Auction.auctionStatus, Auction.buyerLogin
        FROM Auction JOIN Item ON Auction.itemID = Item.itemID
        WHERE Auction.sellerLogin = %s ORDER BY Auction.auctionID;
    """, (session["login"],))
    h = page_header("My Auctions")
    return render(MY_AUCTIONS_PAGE, auctions=auctions, header=h)


@app.route("/create_shipment", methods=["GET", "POST"])
def create_shipment():
    if "login" not in session or session["role"] != "Seller":
        return redirect(url_for("main_menu"))
    error_html = None
    success_html = None
    seller_login = session["login"]
    if request.method == "POST":
        auction_id     = request.form["auction_id"].strip()
        address        = request.form["address"].strip()
        tracking_input = request.form["tracking_number"].strip()
        tracking_number = None
        if tracking_input:
            try:
                tracking_number = int(tracking_input)
            except ValueError:
                error_html = alert("Tracking number must be numeric.")
        if not error_html:
            result = db.fetch_one("""
                SELECT Auction.auctionID FROM Auction
                JOIN Payment ON Auction.auctionID = Payment.auctionID
                WHERE Auction.auctionID = %s AND Auction.sellerLogin = %s
                  AND Auction.auctionStatus = 'closed' AND Payment.paymentStatus = 'completed';
            """, (auction_id, seller_login))
            if result is None:
                error_html = alert("Auction not eligible for shipment.")
            else:
                existing = db.fetch_one("SELECT ShipmentID FROM Shipment WHERE auctionID = %s;", (auction_id,))
                if existing:
                    error_html = alert("Shipment already created for this auction.")
                else:
                    shipment_id = ("SHIP" + uuid.uuid4().hex)[:30]
                    ok = db.execute_update("INSERT INTO Shipment (ShipmentID, address, shipmentStatus, trackingNumber, auctionID) VALUES (%s, %s, 'pending', %s, %s);",
                                          (shipment_id, address, tracking_number, auction_id))
                    if ok:
                        success_html = alert(f"Shipment created! ID: {shipment_id}", "success")
                    else:
                        error_html = alert("Something went wrong.")
    auctions = db.fetch_all("""
        SELECT Auction.auctionID, Item.itemName, Auction.buyerLogin, Auction.currentHighestBid
        FROM Auction JOIN Item ON Auction.itemID = Item.itemID
        JOIN Payment ON Auction.auctionID = Payment.auctionID
        LEFT JOIN Shipment ON Auction.auctionID = Shipment.auctionID
        WHERE Auction.sellerLogin = %s AND Auction.auctionStatus = 'closed'
          AND Payment.paymentStatus = 'completed' AND Shipment.ShipmentID IS NULL;
    """, (seller_login,))
    h = page_header("Create Shipment")
    return render(CREATE_SHIPMENT_PAGE, auctions=auctions, error_html=error_html, success_html=success_html, header=h)


@app.route("/admin/users", methods=["GET", "POST"])
def admin_users():
    if "login" not in session or session["role"] != "Admin":
        return redirect(url_for("main_menu"))
    error_html = None
    success_html = None
    if request.method == "POST":
        target_login = request.form["target_login"].strip()
        new_role     = request.form["new_role"].strip()
        if new_role not in ("Buyer", "Seller", "Admin"):
            error_html = alert("Invalid role.")
        else:
            ok = db.execute_update(
                'UPDATE "User" SET role = %s WHERE login = %s;',
                (new_role, target_login)
            )
            if ok:
                success_html = alert(f"'{target_login}' updated to {new_role}.", "success")
            else:
                error_html = alert("Update failed.")
    users = db.fetch_all(
        'SELECT login, phoneNum, role, address, favoriteCategory FROM "User" ORDER BY role, login;'
    )
    h = page_header("Manage Users", "/dashboard", "Dashboard")
    return render(ADMIN_USERS_PAGE, users=users, error_html=error_html, success_html=success_html, header=h)


@app.route("/admin/auctions")
def admin_auctions():
    if "login" not in session or session["role"] != "Admin":
        return redirect(url_for("main_menu"))
    auctions = db.fetch_all("""
        SELECT Auction.auctionID, Item.itemName, Item.category,
               Auction.sellerLogin, Auction.currentHighestBid,
               Auction.auctionStatus, Auction.buyerLogin
        FROM Auction JOIN Item ON Auction.itemID = Item.itemID
        ORDER BY Auction.auctionStatus, Auction.auctionID;
    """)
    h = page_header("Monitor Auctions", "/dashboard", "Dashboard")
    return render(ADMIN_AUCTIONS_PAGE, auctions=auctions, header=h)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main_menu"))


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    global db
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <dbname> <port> <user>", file=sys.stderr)
        return
    dbname, dbport, user = sys.argv[1], sys.argv[2], sys.argv[3]
    db = EmbeddedSQL(dbname, dbport, user, "")
    print("Open your browser: http://localhost:5000")
    app.run(debug=False, port=5000)


if __name__ == "__main__":
    main()