#!/usr/bin/env python3
"""
BOV Website Builder Template — LAAA Team at Marcus & Millichap
==============================================================
This is a TEMPLATE. All placeholders marked # DEAL-SPECIFIC must be
replaced with actual property data before running.

Usage:
  1. Copy this file to C:/Users/gscher/{slug}-bov/build_bov.py
  2. Replace ALL # DEAL-SPECIFIC placeholders
  3. Copy images to {slug}-bov/images/
  4. Run: python build_bov.py
  5. Output: index.html
"""
import base64, json, os, sys, io, math, urllib.request, urllib.parse, statistics

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")
OUTPUT = os.path.join(SCRIPT_DIR, "index.html")

# ============================================================
# DEAL-SPECIFIC CONFIG — Replace these for every build
# ============================================================
SLUG = "18303kittridge"  # DEAL-SPECIFIC
ADDRESS = "18303 Kittridge St"  # DEAL-SPECIFIC
CITY_STATE_ZIP = "Reseda, CA 91335"  # DEAL-SPECIFIC
FULL_ADDRESS = "18303 Kittridge St, Reseda, CA 91335"  # DEAL-SPECIFIC
SUBMARKET = "Reseda"  # DEAL-SPECIFIC
CLIENT_NAME = "Grape Ape, LLC"  # DEAL-SPECIFIC
COVER_MONTH_YEAR = "March 2026"  # DEAL-SPECIFIC
PROPERTY_SUBTITLE = "39-Unit LIHTC Multifamily Investment"  # DEAL-SPECIFIC

BOV_BASE_URL = f"https://{SLUG}.laaa.com"
PDF_WORKER_URL = "https://laaa-pdf-worker.laaa-team.workers.dev"
PDF_FILENAME = f"BOV - {FULL_ADDRESS}.pdf"  # DEAL-SPECIFIC
PDF_LINK = (PDF_WORKER_URL + "/?url=" + urllib.parse.quote(BOV_BASE_URL + "/", safe="")
            + "&filename=" + urllib.parse.quote(PDF_FILENAME, safe=""))

# Section inclusion flags — set per deal
INCLUDE_TRANSACTION_HISTORY = False  # DEAL-SPECIFIC
INCLUDE_DEVELOPMENT_POTENTIAL = False  # DEAL-SPECIFIC
INCLUDE_ADU_OPPORTUNITY = False  # DEAL-SPECIFIC
INCLUDE_ON_MARKET_COMPS = False  # DEAL-SPECIFIC — no LIHTC properties currently listed
PROPERTY_TYPE = "value-add"  # DEAL-SPECIFIC — LIHTC with conversion upside

# Agent lineup — always Glen + Filip minimum
# Add/remove agents as needed per deal
COVER_AGENTS = [  # DEAL-SPECIFIC
    {"name": "Glen Scher", "title": "SMDI", "img_key": "glen"},
    {"name": "Filip Niculete", "title": "SMDI", "img_key": "filip"},
]
FOOTER_AGENTS = [  # DEAL-SPECIFIC
    {
        "name": "Glen Scher",
        "title": "Senior Managing Director of Investments",
        "phone": "(818) 212-2808",
        "email": "Glen.Scher@marcusmillichap.com",
        "license": "01962976",
        "img_key": "glen",
    },
    {
        "name": "Filip Niculete",
        "title": "Senior Managing Director of Investments",
        "phone": "(818) 212-2748",
        "email": "Filip.Niculete@marcusmillichap.com",
        "license": "01905352",
        "img_key": "filip",
    },
]

# ============================================================
# IMAGE LOADING
# ============================================================
def load_image_b64(filename):
    path = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(path):
        print(f"WARNING: Image not found: {path}")
        return ""
    ext = filename.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(ext, "image/png")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    print(f"  Loaded: {filename} ({len(data)//1024}KB)")
    return f"data:{mime};base64,{data}"

print("Loading images...")
IMG = {
    # Standard branding (same for every BOV — copy from LAAA-AI-Prompts/branding/)
    "logo": load_image_b64("LAAA_Team_White.png"),
    "logo_blue": load_image_b64("LAAA_Team_Blue.png"),
    "closings_map": load_image_b64("closings-map.png"),
    # Team headshots (copy from LAAA-AI-Prompts/branding/headshots/)
    "glen": load_image_b64("Glen_Scher.png"),
    "filip": load_image_b64("Filip_Niculete.png"),
    "team_aida": load_image_b64("Aida_Memary_Scher.png"),
    "team_morgan": load_image_b64("Morgan_Wetmore.png"),
    "team_luka": load_image_b64("Luka_Leader.png"),
    "team_logan": load_image_b64("Logan_Ward.png"),
    "team_alexandro": load_image_b64("Alexandro_Tapia.png"),
    "team_blake": load_image_b64("Blake_Lewitt.png"),
    "team_mike": load_image_b64("Mike_Palade.png"),
    "team_tony": load_image_b64("Tony_Dang.png"),
    # Deal-specific photos — DEAL-SPECIFIC filenames
    "hero": load_image_b64("hero.jpg"),  # DEAL-SPECIFIC
    "grid1": load_image_b64("grid1.jpg"),  # DEAL-SPECIFIC
    "buyer_photo": load_image_b64("buyer_photo.jpg"),  # DEAL-SPECIFIC
}

# ============================================================
# GEOCODING — US Census Bureau Geocoder
# ============================================================
def geocode_census(addr):
    url = (f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
           f"?address={urllib.parse.quote(addr)}&benchmark=Public_AR_Current&format=json")
    try:
        data = json.loads(urllib.request.urlopen(url, timeout=15).read())
        m = data["result"]["addressMatches"]
        if not m:
            print(f"  WARNING: No match for: {addr}")
            return None
        lat, lng = m[0]["coordinates"]["y"], m[0]["coordinates"]["x"]
        print(f"  Geocoded: {addr} -> ({lat:.6f}, {lng:.6f})")
        return (lat, lng)
    except Exception as e:
        print(f"  WARNING: Geocode failed for {addr}: {e}")
        return None

print("\nGeocoding addresses...")
SUBJECT_ADDR = FULL_ADDRESS  # Subject property
SUBJECT_COORDS = geocode_census(SUBJECT_ADDR)
if not SUBJECT_COORDS:
    SUBJECT_COORDS = (34.0522, -118.2437)  # LA fallback
    print(f"  Using fallback coords for subject: {SUBJECT_COORDS}")
SUBJECT_LAT, SUBJECT_LNG = SUBJECT_COORDS

# Comp addresses for geocoding
COMP_ADDRESSES = {
    "20234 Roscoe Blvd, Winnetka, CA 91306": (34.2214, -118.5707),
    "1536 N Serrano Ave, Los Angeles, CA 90027": (34.0978, -118.3069),
    "9010 Tobias Ave, Panorama City, CA 91402": (34.2262, -118.4478),
}
RENT_COMP_ADDRESSES = {
}
for addr in COMP_ADDRESSES:
    if COMP_ADDRESSES[addr] is None:
        COMP_ADDRESSES[addr] = geocode_census(addr)
for addr in RENT_COMP_ADDRESSES:
    if RENT_COMP_ADDRESSES[addr] is None:
        RENT_COMP_ADDRESSES[addr] = geocode_census(addr)

# Filter out failed geocodes
failed_comps = [a for a, c in COMP_ADDRESSES.items() if c is None]
if failed_comps:
    print(f"WARNING: Failed to geocode {len(failed_comps)} comp addresses: {failed_comps}")
COMP_ADDRESSES = {k: v for k, v in COMP_ADDRESSES.items() if v is not None}
failed_rent = [a for a, c in RENT_COMP_ADDRESSES.items() if c is None]
if failed_rent:
    print(f"WARNING: Failed to geocode {len(failed_rent)} rent comp addresses: {failed_rent}")
RENT_COMP_ADDRESSES = {k: v for k, v in RENT_COMP_ADDRESSES.items() if v is not None}

# ============================================================
# STATIC MAP GENERATION (Pillow + OSM Tiles)
# ============================================================
from PIL import Image, ImageDraw, ImageFont

def lat_lng_to_tile(lat, lng, zoom):
    n = 2 ** zoom
    x = int((lng + 180) / 360 * n)
    lat_rad = math.radians(lat)
    y = int((1 - math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi) / 2 * n)
    return x, y

def generate_static_map(center_lat, center_lng, markers, width=800, height=400, zoom=14):
    cx, cy = lat_lng_to_tile(center_lat, center_lng, zoom)
    tiles_x = math.ceil(width / 256) + 2
    tiles_y = math.ceil(height / 256) + 2
    start_x = cx - tiles_x // 2
    start_y = cy - tiles_y // 2
    big = Image.new("RGB", (tiles_x * 256, tiles_y * 256), (220, 220, 220))
    for tx in range(tiles_x):
        for ty in range(tiles_y):
            tile_url = f"https://tile.openstreetmap.org/{zoom}/{start_x + tx}/{start_y + ty}.png"
            req = urllib.request.Request(tile_url, headers={"User-Agent": "LAAA-BOV-Builder/1.0"})
            try:
                tile_data = urllib.request.urlopen(req, timeout=10).read()
                tile_img = Image.open(io.BytesIO(tile_data))
                big.paste(tile_img, (tx * 256, ty * 256))
            except Exception:
                pass
    n = 2 ** zoom
    offset_px = (center_lng + 180) / 360 * n * 256 - width / 2
    lat_rad = math.radians(center_lat)
    offset_py = (1 - math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi) / 2 * n * 256 - height / 2
    crop_left = int(offset_px - start_x * 256)
    crop_top = int(offset_py - start_y * 256)
    cropped = big.crop((crop_left, crop_top, crop_left + width, crop_top + height))
    draw = ImageDraw.Draw(cropped)
    for m in markers:
        lat, lng, label, color = m["lat"], m["lng"], m.get("label", ""), m.get("color", "#1B3A5C")
        px = int((lng + 180) / 360 * n * 256 - offset_px)
        py = int((1 - math.log(math.tan(math.radians(lat)) + 1/math.cos(math.radians(lat))) / math.pi) / 2 * n * 256 - offset_py)
        r = 14 if label == "★" else 11
        draw.ellipse([px - r, py - r, px + r, py + r], fill=color, outline="white", width=2)
        if label:
            try:
                font = ImageFont.truetype("arial.ttf", 12 if label == "★" else 10)
            except Exception:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((px - tw // 2, py - th // 2 - 1), label, fill="white", font=font)
    buf = io.BytesIO()
    cropped.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    print(f"  Static map generated: {width}x{height}, {len(markers)} markers, {len(b64)//1024}KB")
    return f"data:image/png;base64,{b64}"

def calc_auto_zoom(markers, width=800, height=300, padding_pct=0.10):
    if len(markers) <= 1:
        return 15
    lats = [m["lat"] for m in markers]
    lngs = [m["lng"] for m in markers]
    lat_span = max(lats) - min(lats)
    lng_span = max(lngs) - min(lngs)
    lat_span = max(lat_span * (1 + padding_pct * 2), 0.002)
    lng_span = max(lng_span * (1 + padding_pct * 2), 0.002)
    zoom_lat = math.log2(height / 256 * 360 / lat_span) if lat_span > 0 else 18
    zoom_lng = math.log2(width / 256 * 360 / lng_span) if lng_span > 0 else 18
    zoom = int(min(zoom_lat, zoom_lng))
    return max(10, min(zoom, 16))

def build_markers_from_comps(comps, addr_dict, comp_color, subject_lat, subject_lng):
    """Build map markers. Tier 1-2 comps get full color, Tier 3 gets muted gray."""
    markers = [{"lat": subject_lat, "lng": subject_lng, "label": "★", "color": "#C5A258"}]
    tier3_color = "#9E9E9E"  # Muted gray for Tier 3 / reference comps
    for i, c in enumerate(comps):
        for a, coords in addr_dict.items():
            if coords and c["addr"].lower() in a.lower():
                color = tier3_color if c.get("tier", 1) == 3 else comp_color
                markers.append({"lat": coords[0], "lng": coords[1], "label": str(i + 1), "color": color})
                break
    return markers

# ============================================================
# FINANCIAL CONSTANTS — DEAL-SPECIFIC (replace ALL)
# ============================================================
LIST_PRICE = 5_950_000  # DEAL-SPECIFIC — approved 2026-03-19
UNITS = 39  # DEAL-SPECIFIC
SF = 36_058  # DEAL-SPECIFIC
LOT_SF = 36_678  # DEAL-SPECIFIC
LOT_ACRES = 0.84  # DEAL-SPECIFIC (LOT_SF / 43560)
YEAR_BUILT = 1961  # DEAL-SPECIFIC
TAX_RATE = 0.0  # DEAL-SPECIFIC — LIHTC tax exempt per CA Rev & Tax Code 214
GSR = 619_752  # DEAL-SPECIFIC — corrected: unit-by-unit (occupied actual + vacant/mgr at market)
PF_GSR = 1_272_036  # DEAL-SPECIFIC — S8 payment standards for all 39 units annualized
VACANCY_PCT = 0.05  # DEAL-SPECIFIC
OTHER_INCOME = 11_844  # DEAL-SPECIFIC — laundry $9,882 + RSO/SCEP pass-throughs $1,962
NON_TAX_CUR_EXP = 243_500  # DEAL-SPECIFIC — all expenses (tax exempt). Verified in 06_Final_Build_Calculations.md
NON_TAX_PF_EXP = 269_591  # DEAL-SPECIFIC — PF expenses (mgmt at 4% of PF GSR $1,272,036 = $50,881; all other same)

# Financing
INTEREST_RATE = 0.0585  # DEAL-SPECIFIC — matches Serrano comp (IO)
AMORTIZATION_YEARS = 30  # IO loan — template uses this for amort calc but actual is IO
MAX_LTV = 0.65  # DEAL-SPECIFIC — matches Serrano comp
MIN_DCR = 1.25  # DEAL-SPECIFIC

# Trade range
TRADE_RANGE_LOW = 5_700_000  # DEAL-SPECIFIC
TRADE_RANGE_HIGH = 6_200_000  # DEAL-SPECIFIC

# ============================================================
# FINANCIAL HELPER FUNCTIONS
# ============================================================
def calc_loan_constant(rate, amort):
    r = rate / 12
    n = amort * 12
    monthly = r * (1 + r)**n / ((1 + r)**n - 1)
    return monthly * 12

LOAN_CONSTANT = calc_loan_constant(INTEREST_RATE, AMORTIZATION_YEARS)

def calc_principal_reduction_yr1(loan_amount, annual_rate, amort_years):
    r = annual_rate / 12
    n = amort_years * 12
    monthly_pmt = loan_amount * (r * (1 + r)**n) / ((1 + r)**n - 1)
    balance = loan_amount
    total_principal = 0
    for _ in range(12):
        interest = balance * r
        principal = monthly_pmt - interest
        total_principal += principal
        balance -= principal
    return total_principal

def calc_metrics(price):
    taxes = price * TAX_RATE
    cur_egi = GSR * (1 - VACANCY_PCT) + OTHER_INCOME
    pf_egi = PF_GSR * (1 - VACANCY_PCT) + OTHER_INCOME
    cur_exp = NON_TAX_CUR_EXP + taxes
    pf_exp = NON_TAX_PF_EXP + taxes
    cur_noi = cur_egi - cur_exp
    pf_noi = pf_egi - pf_exp
    ltv_max_loan = price * MAX_LTV
    dcr_max_loan = cur_noi / (MIN_DCR * LOAN_CONSTANT) if LOAN_CONSTANT > 0 else ltv_max_loan
    loan_amount = min(ltv_max_loan, dcr_max_loan)
    actual_ltv = loan_amount / price if price > 0 else 0
    loan_constraint = "LTV" if ltv_max_loan <= dcr_max_loan else "DCR"
    down_payment = price - loan_amount
    debt_service = loan_amount * LOAN_CONSTANT
    net_cf_cur = cur_noi - debt_service
    net_cf_pf = pf_noi - debt_service
    coc_cur = net_cf_cur / down_payment * 100 if down_payment > 0 else 0
    coc_pf = net_cf_pf / down_payment * 100 if down_payment > 0 else 0
    dcr_cur = cur_noi / debt_service if debt_service > 0 else 0
    dcr_pf = pf_noi / debt_service if debt_service > 0 else 0
    prin_red = calc_principal_reduction_yr1(loan_amount, INTEREST_RATE, AMORTIZATION_YEARS)
    return {
        "price": price, "taxes": taxes,
        "cur_noi": cur_noi, "pf_noi": pf_noi,
        "cur_egi": cur_egi, "pf_egi": pf_egi,
        "cur_exp": cur_exp, "pf_exp": pf_exp,
        "per_unit": price / UNITS if UNITS > 0 else 0,
        "per_sf": price / SF if SF > 0 else 0,
        "cur_cap": cur_noi / price * 100 if price > 0 else 0,
        "pf_cap": pf_noi / price * 100 if price > 0 else 0,
        "grm": price / GSR if GSR > 0 else 0,
        "pf_grm": price / PF_GSR if PF_GSR > 0 else 0,
        "loan_amount": loan_amount, "down_payment": down_payment,
        "actual_ltv": actual_ltv, "loan_constraint": loan_constraint,
        "debt_service": debt_service,
        "net_cf_cur": net_cf_cur, "net_cf_pf": net_cf_pf,
        "coc_cur": coc_cur, "coc_pf": coc_pf,
        "dcr_cur": dcr_cur, "dcr_pf": dcr_pf,
        "prin_red": prin_red,
        "total_return_pct_cur": (net_cf_cur + prin_red) / down_payment * 100 if down_payment > 0 else 0,
        "total_return_pct_pf": (net_cf_pf + prin_red) / down_payment * 100 if down_payment > 0 else 0,
    }

# ============================================================
# PRICING MATRIX
# ============================================================
# Dynamic increment: gap = LIST_PRICE - TRADE_RANGE_LOW
# min_inc = gap/4, max_inc = gap/3
# Pick smallest clean value in [min_inc, max_inc]: 25K, 50K, 75K, 100K, 150K, 200K, 250K
INCREMENT = 100_000  # DEAL-SPECIFIC
# Custom range: $6M down to $5M plus suggested list at $5,950,000
MATRIX_PRICES = [6_000_000, 5_950_000, 5_900_000, 5_800_000, 5_700_000, 5_600_000, 5_500_000, 5_400_000, 5_300_000, 5_200_000, 5_100_000, 5_000_000]
MATRIX = [calc_metrics(p) for p in MATRIX_PRICES]
AT_LIST = calc_metrics(LIST_PRICE)

if LIST_PRICE > 0:
    print(f"\nFinancials at list ${LIST_PRICE:,}: Cap {AT_LIST['cur_cap']:.2f}%, GRM {AT_LIST['grm']:.2f}x, NOI ${AT_LIST['cur_noi']:,.0f}")

# ============================================================
# DATA PLACEHOLDERS — DEAL-SPECIFIC (replace ALL)
# ============================================================

# Rent Roll — 6-tuple: (unit, type, sf, current_rent, scheduled_rent, proforma_rent)
# Current = actual collected ($0 for vacants/manager)
# Scheduled = GSR basis (vacants + manager at LIHTC max)
# Pro Forma = Section 8 Payment Standards for 91335
RENT_ROLL = [
    ("01", "2BR/1BA", 850, 1167, 1167, 2887),
    ("02", "3BR/1.5BA", 1335, 1297, 1297, 3668),
    ("03", "2BR/1BA", 1335, 1307, 1307, 2887),
    ("04", "2BR/1BA", 850, 1222, 1222, 2887),
    ("05", "3BR/1.5BA", 1050, 1297, 1297, 3668),
    ("06", "2BR/1BA", 850, 1134, 1134, 2887),
    ("07", "2BR/1BA", 850, 1307, 1307, 2887),
    ("08", "2BR/1BA", 850, 1440, 1440, 2887),
    ("09", "2BR/1BA", 850, 1759, 1759, 2887),
    ("10", "3BR/1.5BA", 1050, 1519, 1519, 3668),
    ("11", "2BR/1BA", 850, 1210, 1210, 2887),
    ("12", "2BR/1BA", 850, 0, 1952, 2887),
    ("14", "3BR/1.5BA", 1050, 2240, 2240, 3668),
    ("15", "2BR/1BA", 850, 1167, 1167, 2887),
    ("16", "2BR/1BA", 850, 1122, 1122, 2887),
    ("17", "Studio", 500, 1674, 1674, 2041),
    ("18", "1BR/1BA", 700, 1718, 1718, 2289),
    ("19", "2BR/1BA", 850, 1086, 1086, 2887),
    ("20", "1BR/1BA", 700, 1087, 1087, 2289),
    ("21", "2BR/1BA (Mgr)", 850, 0, 1952, 2887),
    ("22", "1BR/1BA", 700, 993, 993, 2289),
    ("23", "1BR/1BA", 700, 1129, 1129, 2289),
    ("24", "1BR/1BA", 700, 1201, 1201, 2289),
    ("25", "2BR/1BA", 850, 1271, 1271, 2887),
    ("26", "2BR/1BA", 850, 1238, 1238, 2887),
    ("27", "Studio", 500, 915, 915, 2041),
    ("28", "2BR/1BA", 850, 1100, 1100, 2887),
    ("29", "1BR/1BA", 700, 1464, 1464, 2289),
    ("30", "1BR/1BA", 700, 0, 1631, 2289),
    ("31", "2BR/1BA", 850, 1269, 1269, 2887),
    ("32", "2BR/1BA", 850, 1029, 1029, 2887),
    ("33", "1BR/1BA", 700, 839, 839, 2289),
    ("34", "1BR/1BA", 700, 1087, 1087, 2289),
    ("35", "1BR/1BA", 700, 1268, 1268, 2289),
    ("36", "2BR/1BA", 850, 1307, 1307, 2887),
    ("37", "1BR/1BA", 700, 0, 1631, 2289),
    ("38", "2BR/1BA", 850, 979, 979, 2887),
    ("39", "1BR/1BA", 700, 1668, 1668, 2289),
    ("40", "Studio", 500, 970, 970, 2041),
]

# Sale Comps
# Fields: num, addr, units, yr, sf, price, ppu, psf, cap, grm, date, dom, notes, tier, laaa
# - cap: verified cap rate (recalculated from NOI / sale price). Use "--" if NOI unavailable.
# - tier: 1 (primary), 2 (supporting), 3 (reference) — from COMP_ANALYSIS_PROTOCOL.md
# - laaa: True if Glen/Filip/LAAA Team sold this comp (gets gold badge in table)
SALE_COMPS = [
    {"num": 1, "addr": "20234 Roscoe Blvd, Winnetka", "units": 25, "yr": "1964/1997", "sf": 24176, "price": 5000000, "ppu": 200000, "psf": 207, "cap": 5.24, "grm": 10.41, "date": "In Escrow", "dom": "--", "notes": "9% LIHTC, 55yr through 2050. Fannie assumption at 2.98%.", "tier": 1, "laaa": True},
    {"num": 2, "addr": "1536 N Serrano Ave, Los Angeles", "units": 42, "yr": "1969/1997", "sf": 60525, "price": 7600000, "ppu": 180952, "psf": 126, "cap": 6.38, "grm": 9.06, "date": "02/2026", "dom": "--", "notes": "9% LIHTC, 55yr through 2052. Free & clear, new IO at 5.85%.", "tier": 1, "laaa": True},
    {"num": 3, "addr": "9010 Tobias Ave (Azzi Portfolio), Panorama City", "units": 596, "yr": "1954-72", "sf": 478070, "price": 85000000, "ppu": 142617, "psf": 178, "cap": 5.85, "grm": 9.65, "date": "12/2024", "dom": "--", "notes": "596-unit LIHTC portfolio, 24 buildings. Portfolio discount.", "tier": 3, "laaa": False},
]

# On-Market Comps
ON_MARKET_COMPS = []  # No LIHTC properties currently listed for sale in SFV

# Rent Comps
RENT_COMPS = [
    {"addr": "18317 Kittridge St (Vista Park)", "type": "Studio", "sf": 500, "rent": 1500, "rent_sf": 3.00, "source": "Apartments.com"},
    {"addr": "18317 Kittridge St (Vista Park)", "type": "1BR/1BA", "sf": 700, "rent": 1700, "rent_sf": 2.43, "source": "Apartments.com"},
    {"addr": "18317 Kittridge St (Vista Park)", "type": "2BR/1BA", "sf": 900, "rent": 2100, "rent_sf": 2.33, "source": "Apartments.com"},
    {"addr": "7650 Reseda Blvd", "type": "Studio", "sf": 460, "rent": 1554, "rent_sf": 3.38, "source": "Zumper"},
    {"addr": "6425 Reseda Blvd (Park Terrace)", "type": "1BR/1BA", "sf": 534, "rent": 1899, "rent_sf": 3.56, "source": "Apartments.com"},
    {"addr": "6425 Reseda Blvd (Park Terrace)", "type": "2BR/1BA", "sf": 875, "rent": 2299, "rent_sf": 2.63, "source": "Apartments.com"},
    {"addr": "7722 Reseda Blvd (Villa La Paloma)", "type": "1BR/1BA", "sf": 615, "rent": 1795, "rent_sf": 2.92, "source": "Apartments.com"},
    {"addr": "7650 Reseda Blvd", "type": "3BR", "sf": 1100, "rent": 3150, "rent_sf": 2.86, "source": "Apartments.com"},
]

# Expense line items — (label, current_value, note_number)
# Max 12 items. Taxes calculated dynamically from price.
expense_lines = [
    ("Real Estate Taxes", 0, 4),
    ("Insurance", 28_723, 5),
    ("On-Site Manager Credit", 24_000, 6),
    ("Water/Sewer", 65_996, 7),
    ("Trash Removal", 34_655, 8),
    ("Gas", 1_645, 9),
    ("Common Area Electric", 3_379, 10),
    ("Repairs & Maintenance", 34_250, 11),
    ("Contract Services", 10_725, 12),
    ("Management (4%)", 24_790, 13),
    ("Administrative", 3_900, 14),
    ("Reserves", 7_800, 15),
    ("RSO/SCEP Fees", 1_687, 16),
    ("Other/Misc", 1_950, 17),
]

# Operating Statement Notes — unique numbers, no duplicates
# Notes 1-3 reserved for income lines
OS_NOTES = {
    1: "Gross Scheduled Rent per Scheduled column of rent roll. Includes vacant units and manager unit at LIHTC maximum rents.",
    2: "5% economic vacancy applied per broker underwriting standards. LIHTC waitlist supports lower actual vacancy.",
    3: "Other income includes laundry ($9,882) and RSO/SCEP pass-throughs ($1,962).",
    4: "LIHTC Tax Exempt per CA Revenue &amp; Tax Code 214. If reassessed at purchase price (1.17%), tax would be ~$69,615, reducing NOI to ~$287,493 (4.83% cap).",
    5: "Insurance per seller's actual policy. 13.5 KW solar PV system (2011) reduces common area energy costs.",
    6: "On-site manager rent credit at $2,000/mo. CA law requires on-site manager for 16+ units.",
    7: "Water/Sewer per seller T-12. Owner pays all water/sewer. Pool, on-site laundry, and landscaping included.",
    8: "Trash per seller T-12. Current LA hauler rates.",
    9: "Gas per seller T-12. Owner pays common area gas.",
    10: "Electric per seller T-12. Solar PV offsets common area electric costs.",
    11: "R&M normalized to Tier 4 benchmark ($750/unit + pool). Soft story retrofit (2021) and roof (2009) completed.",
    12: "Contract services include landscaping, pest control, pool service, and janitorial ($275/unit).",
    13: "Management at 4% of Gross Scheduled Rent. Professional third-party management.",
    14: "Administrative costs at $100/unit benchmark. Covers accounting, legal, office, and licensing.",
    15: "Replacement reserves at $200/unit. CapEx credit applied for completed roof and soft story retrofit.",
    16: "LA RSO registration and SCEP fees at approximately $43/unit.",
    17: "Miscellaneous operating costs at $50/unit benchmark.",
}

# ============================================================
# NARRATIVE CONTENT — DEAL-SPECIFIC (replace ALL)
# ============================================================

# Investment Overview (2-3 paragraphs, ~80 words each)
INVESTMENT_OVERVIEW_P1 = "The LAAA Team is pleased to present Kittridge Park Villas, a 39-unit multifamily community situated on 0.84 acres in Reseda. Originally constructed in 1961 and substantially rehabilitated in 1997 under the Low-Income Housing Tax Credit (LIHTC) program, the property features a diverse unit mix of three studios, twelve one-bedrooms, twenty two-bedrooms, and four three-bedrooms across 36,058 square feet of rentable area. The two-story, wood-frame buildings are served by central air conditioning, on-site laundry facilities, a swimming pool, and covered parking."

INVESTMENT_OVERVIEW_P2 = "Kittridge Park Villas operates under a 4% LIHTC regulatory agreement (CTCAC CA-1996-915) with an extended use period expiring in approximately December 2027. All 38 non-manager units are income-restricted at 60% of Area Median Income. The property is professionally managed by Solari Enterprises, a firm specializing in affordable housing compliance with over 40 years of experience. Recent capital improvements include a completed soft-story seismic retrofit (2021), a 13.5 KW solar photovoltaic system (2011), EV charger installations (2024), and a Class A/B roof replacement (2009)."

INVESTMENT_OVERVIEW_P3 = "With LIHTC restrictions set to expire in under two years, Kittridge Park Villas presents a rare dual-path investment opportunity. A resyndication buyer can pursue new 4% tax credits, tax-exempt bonds, and LAHD grants to recapitalize the property while maintaining its affordable mission and LIHTC property tax exemption. Alternatively, a market-conversion buyer can position for post-restriction rent increases on unit turnover, with unrestricted market rents in Reseda currently 10% to 31% above current LIHTC maximums. This dual optionality, combined with the LAAA Team's direct transactional experience with comparable LIHTC assets in the San Fernando Valley, provides buyers with a well-understood acquisition basis."

# Investment Highlights (5-6 items, ~30 words each)
HIGHLIGHTS = [
    ("Expiring LIHTC Restrictions", "4% LIHTC regulatory agreement expires approximately December 2027, creating dual-path optionality for resyndication or market-rate conversion on unit turnover."),
    ("LAAA Team Comp Intelligence", "The LAAA Team has closed or is in escrow on two directly comparable LIHTC transactions in the San Fernando Valley, providing first-hand pricing intelligence and an active buyer network."),
    ("Post-Conversion Rent Upside", "Unrestricted market rents in Reseda currently exceed LIHTC maximum rents by 10% to 31% across all unit types, with two-bedroom units showing the greatest upside potential."),
    ("Capital Improvements Completed", "Soft-story seismic retrofit (2021), 13.5 KW solar PV system (2011), EV chargers (2024), and Class A/B roof (2009) reduce near-term buyer capital requirements."),
    ("TOC Tier 1 Designation", "Transit Oriented Communities Tier 1 and Housing Element Site designations reflect strong transit access and the City's commitment to multifamily density in this corridor."),
    ("Section 8 Voucher Income", "Five units currently benefit from Housing Choice Voucher subsidies, providing a stable, government-backed income stream that insulates against collection risk."),
]

# Location Overview (2-3 paragraphs, ~80 words each)
LOCATION_P1 = "The subject property is situated in the Reseda community of the central San Fernando Valley, a densely rented, transit-accessible neighborhood within the City of Los Angeles. The immediate corridor along Kittridge Street benefits from a Walk Score of 77, with everyday retail, grocery, and pharmacy options concentrated along the adjacent Reseda Boulevard commercial spine. Median household income within one mile reaches $77,733, reflecting a stable working-class renter base well-suited to income-restricted housing at AMI-qualified rent levels."

LOCATION_P2 = "Bus service via Metro Local Lines 164, 165, and 240 connects residents to employment centers throughout the Valley, while the Metro G Line (Orange) Reseda Station on Roscoe Boulevard provides rapid transit access to the broader Metro system. Reseda Park and the Sepulveda Basin recreational corridor, including Lake Balboa, provide nearby open space amenities within the neighborhood. The property's proximity to major employers along the Ventura Boulevard and Sherman Way corridors supports consistent renter demand."

LOCATION_P3 = "Reseda is experiencing meaningful public investment through the 'Reseda Rising' initiative, which has directed over $100 million in public and private capital to the corridor. Completed projects include the $21 million Reseda Boulevard Complete Street and a $26 million partnership with the LA Kings for the Reseda Skate Rink. New affordable housing developments totaling over 225 units are under construction within one mile. The property's R3-1-RIO zoning and TOC Tier 1 designation confirm the City's commitment to multifamily density in this corridor, providing regulatory certainty for long-term asset stewardship."

# Location Details Table rows
LOCATION_TABLE_ROWS = [
    ("Walk Score", "77 / Very Walkable"),
    ("Transit Score", "50 / Good Transit"),
    ("Bike Score", "60 / Bikeable"),
    ("Neighborhood", "Reseda"),
    ("Council District", "CD 4 (Nithya Raman)"),
    ("Nearest Transit", "Metro Local Lines 164, 165, 240 (0.2-0.3 mi)"),
    ("Nearest Rail", "Metro G Line Reseda Station (~2 mi)"),
    ("Median HH Income (1 mi)", "$77,733"),
    ("Median Home Value (1 mi)", "$746,715"),
    ("SFV Vacancy Rate", "4.8% (Q3 2025)"),
]

# Mission paragraphs for Track Record (~60 words each)
MISSION_P1 = "We Didn't Invent Great Service, We Just Work Relentlessly to Provide It."

MISSION_P2 = "The LAAA Team brings direct, first-hand transactional experience to the LIHTC multifamily market in the San Fernando Valley. Our team recently closed 1536 N Serrano Avenue, a 42-unit LIHTC property, at $180,952 per unit with a 6.38% cap rate, and is currently in escrow on 20234 Roscoe Boulevard, a 25-unit LIHTC property, at $200,000 per unit with a 5.24% cap rate. These transactions, both involving properties within the same ownership circle, demonstrate our deep understanding of LIHTC asset valuation, resyndication buyer dynamics, and the regulatory framework governing these sales."

MISSION_P3 = "With over 500 closed transactions and $1.6 billion in sales volume since 2013, the LAAA Team at Marcus &amp; Millichap is among the most active multifamily brokerage groups in Southern California. Our proprietary buyer network includes institutional acquirers, LIHTC syndicators, and private investors who understand the unique capital stack and regulatory requirements of affordable housing transactions."

# Buyer Profile
BUYER_TYPES = [
    ("LIHTC Resyndication Buyers", "Syndicators and developers seeking new 4% tax credit allocations, tax-exempt bond financing, and LAHD grants. The Roscoe Boulevard buyer at $206,000/unit employed this exact strategy, applying for new CDLAC bonds and CTCAC credits while securing an LAHD grant."),
    ("Market Conversion Investors", "Private investors positioning to raise rents to unrestricted market levels after LIHTC restrictions expire in December 2027. With RSO vacancy decontrol, market-rate rents can be achieved on unit turnover, generating 10-31% income growth over time."),
    ("Affordable Housing Operators", "Mission-driven organizations and nonprofits seeking stabilized affordable housing assets with established tenant bases, Section 8 voucher income, and professional management infrastructure already in place."),
]
BUYER_OBJECTIONS = [
    ("Why are LIHTC properties trading below conventional multifamily per-unit pricing?", "LIHTC properties operate under income restrictions that compress current NOI relative to market-rate assets. However, LIHTC buyers underwrite to tax credit equity, bond proceeds, and soft financing rather than traditional cap rate analysis. The Roscoe Boulevard comparable sold 13% above list price, demonstrating strong demand from resyndication buyers who access capital unavailable to conventional investors."),
    ("How does the RSO status affect post-conversion rent growth?", "After LIHTC restrictions expire, the property reverts to LA RSO regulation. In-place tenants receive RSO-capped annual increases of approximately 3-4%. However, under Costa-Hawkins vacancy decontrol, units can be reset to unrestricted market rent upon tenant turnover. With current market rents 10-31% above LIHTC maximums, each turnover event generates meaningful income growth."),
    ("What is the Right of First Refusal (ROFR) process?", "California law grants qualified nonprofits and public agencies a Right of First Refusal for LIHTC properties within five years of restriction expiration. This window is currently open through December 2027. The ROFR process is a standard regulatory step, not a barrier to sale. The LAAA Team has direct experience navigating ROFR compliance on comparable transactions."),
]
BUYER_CLOSING = "Kittridge Park Villas offers a rare combination of current affordable housing cash flow, near-term restriction expiration, and post-conversion upside. Whether pursuing resyndication, market conversion, or mission-driven acquisition, this 39-unit community in Reseda's improving corridor presents a compelling basis for investment."

# Comp Narratives — HTML string with one <p class="narrative"> per comp
# Order: Tier 1 comps first (LAAA sales first within Tier 1), then Tier 2. Tier 3 omitted.
# Tier 1 narratives ~100 words, Tier 2 ~60 words. See RESEARCH_TO_NARRATIVE_MAP.md.
COMP_NARRATIVES = """<p class="narrative"><strong>20234 Roscoe Boulevard, Winnetka (LAAA Team — In Escrow)</strong> — This 25-unit LIHTC property, built in 1964 and rehabilitated in 1997, is under contract at $5,000,000 ($200,000/unit) with a 5.24% cap rate on current restricted NOI of $261,897. The buyer is assuming an existing Fannie Mae loan at 2.98% interest-only, producing a 3.35x debt coverage ratio. Roscoe carries a permanent 55-year regulatory agreement through 2050 with 10 of 24 restricted units (42%) leased to Section 8 voucher holders. As an LAAA Team transaction within the same ownership circle as Kittridge, this comp provides the most direct pricing intelligence available.</p>
<p class="narrative"><strong>1536 N Serrano Avenue, Los Angeles (LAAA Team — Closed February 2026)</strong> — This 42-unit LIHTC property in East Hollywood closed at $7,600,000 ($180,952/unit) with a 6.38% cap rate on current NOI of $484,908. The property was listed at $7,995,000 and closed at a 4.9% discount. The buyer placed new interest-only financing at 5.85% ($4,940,000 / 65% LTV). Serrano carries a permanent 55-year restriction through 2052 with 25 of 41 restricted units (61%) leased to Section 8 voucher holders. The LAAA Team's direct involvement in this closing provides verified financial data, buyer feedback, and market-rate comparable intelligence.</p>
<p class="narrative"><strong>9010 Tobias Avenue (Azzi Portfolio), Panorama City — Closed December 2024</strong> — This 596-unit LIHTC portfolio across 24 buildings in the San Fernando Valley closed at $85,000,000 ($142,617/unit) with a 5.85% cap rate, representing a 17.2% discount from its $102.65 million list price. The portfolio discount and scattered-site structure place this comp at the lower bound of LIHTC pricing. It confirms institutional demand for SFV affordable housing while reflecting the per-unit discount inherent in large portfolio transactions versus single-asset sales.</p>"""

# On-Market Narrative (~150 words)
ON_MARKET_NARRATIVE = ""  # No LIHTC properties currently listed

# Pricing Rationale (2-3 paragraphs, anchored to tier-weighted comp analysis)
# P1: Anchor to Tier 1 weighted average. P2: Most recent data + confidence. P3 (optional): Limitations.
PRICING_RATIONALE = """We are recommending a list price of $5,950,000, or $152,564 per unit, which positions the property below every comparable sale in the dataset. Our team's Serrano Avenue closing in February 2026 traded at $180,952 per unit, and our Roscoe Boulevard escrow is at $200,000 per unit. Both of those properties carry permanent LIHTC restrictions through 2050 and beyond. Kittridge's restrictions expire in approximately 21 months, giving buyers something neither of those comps offered: a clear path to market rents. That optionality, priced at a discount, is the core value proposition.</p>
<p class='narrative'>The current NOI of $357,108 delivers a 6.00% cap rate at list price with a 1.58x debt service coverage ratio on 65% LTV interest-only financing at 5.85%, modeled directly off the Serrano loan terms. Cash-on-cash return starts at 5.50% on day one. Post-expiration, Section 8 payment standards in the 91335 zip code range from $2,041 to $3,668 per month, roughly double the current restricted rents. At those payment standards, the pro forma NOI reaches $950,687, pushing returns above 30% cash-on-cash. Vista Park Apartments next door already achieves $1,500 to $2,100 in unrestricted rents, confirming the submarket supports these levels.</p>
<p class='narrative'>The $5,700,000 to $6,200,000 trade range accounts for buyer type. A syndicator pursuing resyndication will underwrite to restricted rents and pay toward the lower end. A private buyer underwriting to Section 8 conversion will see a generational basis at under $153,000 per unit in a neighborhood absorbing over $100M in public investment. Either way, the property clears the market inside this range."""

# Comp analysis confidence level — from COMP_ANALYSIS_PROTOCOL.md
# "HIGH", "MODERATE", or "LOW" — displayed as badge in pricing section
COMP_CONFIDENCE = ""  # Removed — pricing rationale speaks for itself

# Assumptions & Conditions disclaimer
ASSUMPTIONS_DISCLAIMER = "This analysis is based on information provided by the owner and third-party sources deemed reliable. Actual results may vary. Buyer should independently verify all information. Pro forma projections are estimates and not guaranteed."

# Property Info Tables (4 tables for Property Details page)
PROP_OVERVIEW = [
    ("Address", FULL_ADDRESS),
    ("Property Name", "Kittridge Park Villas"),
    ("Units", "39 (38 restricted + 1 manager)"),
    ("Unit Mix", "3 Studios, 12 1BR, 20 2BR, 4 3BR"),
    ("Year Built", "1961 (Rehab 1997)"),
    ("Building SF", "36,058"),
    ("Lot Size", "36,678 SF (0.84 AC)"),
    ("Stories", "2"),
    ("Parking", "Carports/Garages"),
    ("Occupancy", "92.3% (36 of 39)"),
]
PROP_SITE_ZONING = [
    ("APN", "2125-017-017"),
    ("Zoning", "R3-1-RIO"),
    ("General Plan", "Medium Residential"),
    ("TOC Tier", "1"),
    ("TOIA", "1"),
    ("Housing Element Site", "Yes"),
    ("TCAC Opportunity Area", "Moderate"),
    ("High Quality Transit Corridor", "Yes (within 1/2 mile)"),
    ("Base Density (by-right)", "~45 units"),
    ("Max Density (TOC Tier 1)", "~67 units"),
]
PROP_BUILDING = [
    ("Construction", "Wood Frame"),
    ("HVAC", "Central A/C, Electric Heat"),
    ("Water Heaters", "Electric"),
    ("Laundry", "On-Site Facility"),
    ("Pool", "Yes"),
    ("Solar PV", "13.5 KW (2011)"),
    ("EV Chargers", "60 AMP / 240V (2024)"),
    ("Roof", "Class A/B (2009)"),
    ("Soft Story Retrofit", "Completed 12/2021"),
    ("Earthquake Shutoff Valve", "Installed (2021)"),
]
PROP_REGULATORY = [
    ("Rent Control", "LA RSO (APN verified via ZIMAS)"),
    ("LIHTC Type", "4% Federal Credits (CA-1996-915)"),
    ("LIHTC Expiration", "~December 2027 (30-year extended use)"),
    ("Affordability", "100% at 60% AMI (38 of 39 units)"),
    ("Section 8 Vouchers", "5 units (13%)"),
    ("Management", "Solari Enterprises, Inc."),
    ("Ellis Act", "No"),
    ("Just Cause (JCO)", "No (per ZIMAS)"),
    ("Housing Crisis Act", "Yes"),
    ("Flood Zone", "Outside"),
    ("Liquefaction", "Yes (retrofit completed)"),
]

# Transaction History (optional)
TRANSACTION_ROWS = []  # DEAL-SPECIFIC — list of dicts
TRANSACTION_NARRATIVE = ""  # DEAL-SPECIFIC

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def fc(n):
    """Format currency."""
    if n is None or n == "--":
        return "--"
    return f"${n:,.0f}"

def fp(n):
    """Format percentage."""
    if n is None:
        return "--"
    return f"{n:.2f}%"

# ============================================================
# LEAFLET JS MAP GENERATOR
# ============================================================
def build_map_js(map_id, comps, comp_color, addr_dict, subject_lat, subject_lng, subject_label=None):
    if subject_label is None:
        subject_label = ADDRESS
    js = f"var {map_id} = L.map('{map_id}');\n"
    js += f"L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{attribution: '&copy; OpenStreetMap'}}).addTo({map_id});\n"
    js += f"var {map_id}Markers = [];\n"
    js += f"""var {map_id}Sub = L.marker([{subject_lat}, {subject_lng}], {{icon: L.divIcon({{className: 'custom-marker', html: '<div style="background:#C5A258;color:#fff;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);">&#9733;</div>', iconSize: [32, 32], iconAnchor: [16, 16]}})}})\n.addTo({map_id}).bindPopup('<b>{subject_label}</b><br>Subject Property<br>{UNITS} Units | {SF:,} SF');\n{map_id}Markers.push({map_id}Sub);\n"""
    tier3_color = "#9E9E9E"  # Muted gray for Tier 3 / reference comps
    for i, c in enumerate(comps):
        lat, lng = None, None
        for a, coords in addr_dict.items():
            if coords and c["addr"].lower() in a.lower():
                lat, lng = coords
                break
        if lat is None:
            continue
        label = str(i + 1)
        marker_color = tier3_color if c.get("tier", 1) == 3 else comp_color
        price_str = fc(c.get("price", 0))
        tier_label = f" (Tier {c.get('tier', '')})" if c.get("tier") else ""
        popup = f"<b>#{label}: {c['addr']}</b><br>{c.get('units', '')} Units | {price_str}{tier_label}"
        js += f"""var {map_id}M{label} = L.marker([{lat}, {lng}], {{icon: L.divIcon({{className: 'custom-marker', html: '<div style="background:{marker_color};color:#fff;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;border:2px solid #fff;box-shadow:0 2px 4px rgba(0,0,0,0.3);">{label}</div>', iconSize: [26, 26], iconAnchor: [13, 13]}})}})\n.addTo({map_id}).bindPopup('{popup}');\n{map_id}Markers.push({map_id}M{label});\n"""
    js += f"var {map_id}Group = L.featureGroup({map_id}Markers);\n"
    js += f"{map_id}.fitBounds({map_id}Group.getBounds().pad(0.1));\n"
    return js

# Generate Leaflet JS for each comp section
sale_map_js = build_map_js("saleMap", SALE_COMPS, "#1B3A5C", COMP_ADDRESSES, SUBJECT_LAT, SUBJECT_LNG)
if INCLUDE_ON_MARKET_COMPS:
    active_map_js = build_map_js("activeMap", ON_MARKET_COMPS, "#2E7D32", COMP_ADDRESSES, SUBJECT_LAT, SUBJECT_LNG)
else:
    active_map_js = ""
rent_comps_for_map = [{"addr": rc["addr"], "units": "", "price": 0} for rc in RENT_COMPS]
rent_map_js = build_map_js("rentMap", rent_comps_for_map, "#1B3A5C", RENT_COMP_ADDRESSES, SUBJECT_LAT, SUBJECT_LNG)

# ============================================================
# GENERATE STATIC MAPS
# ============================================================
print("\nGenerating static maps...")
IMG["loc_map"] = generate_static_map(SUBJECT_LAT, SUBJECT_LNG,
    [{"lat": SUBJECT_LAT, "lng": SUBJECT_LNG, "label": "★", "color": "#C5A258"}],
    width=800, height=220, zoom=15)

sale_markers = build_markers_from_comps(SALE_COMPS, COMP_ADDRESSES, "#1B3A5C", SUBJECT_LAT, SUBJECT_LNG)
IMG["sale_map_static"] = generate_static_map(SUBJECT_LAT, SUBJECT_LNG, sale_markers,
    width=800, height=300, zoom=calc_auto_zoom(sale_markers))

if INCLUDE_ON_MARKET_COMPS:
    active_markers = build_markers_from_comps(ON_MARKET_COMPS, COMP_ADDRESSES, "#2E7D32", SUBJECT_LAT, SUBJECT_LNG)
    IMG["active_map_static"] = generate_static_map(SUBJECT_LAT, SUBJECT_LNG, active_markers,
        width=800, height=300, zoom=calc_auto_zoom(active_markers))

rent_markers = build_markers_from_comps(rent_comps_for_map, RENT_COMP_ADDRESSES, "#1B3A5C", SUBJECT_LAT, SUBJECT_LNG)
IMG["rent_map_static"] = generate_static_map(SUBJECT_LAT, SUBJECT_LNG, rent_markers,
    width=800, height=300, zoom=calc_auto_zoom(rent_markers))

# ============================================================
# GENERATE DYNAMIC TABLE HTML
# ============================================================

# Rent Roll — 3-column format (Current / Scheduled / Pro Forma)
rent_roll_html = ""
total_current = 0
total_scheduled = 0
total_proforma = 0
total_sf = 0
for unit, utype, sf, cur_rent, sched_rent, pf_rent in RENT_ROLL:
    total_current += cur_rent
    total_scheduled += sched_rent
    total_proforma += pf_rent
    total_sf += sf
    cur_display = f'${cur_rent:,}' if cur_rent > 0 else '<span style="color:#999">$0</span>'
    rent_roll_html += f'<tr><td>{unit}</td><td>{utype}</td><td class="num">{sf:,}</td><td class="num">{cur_display}</td><td class="num">${sched_rent:,}</td><td class="num">${pf_rent:,}</td></tr>\n'
rent_roll_html += f'<tr style="background:#1B3A5C;color:#fff;font-weight:700;"><td>Total</td><td>{len(RENT_ROLL)} Units</td><td class="num">{total_sf:,}</td><td class="num">${total_current:,}</td><td class="num">${total_scheduled:,}</td><td class="num">${total_proforma:,}</td></tr>\n'
rent_roll_html += f'<tr style="background:#1B3A5C;color:#C5A258;font-weight:700;"><td></td><td>Annualized</td><td></td><td class="num">${total_current*12:,}</td><td class="num">${total_scheduled*12:,}</td><td class="num">${total_proforma*12:,}</td></tr>\n'

# Sale Comp Table — sorted by tier (Tier 1 first, LAAA sales first within tier)
sale_comp_html = ""
sorted_comps = sorted(SALE_COMPS, key=lambda c: (c.get("tier", 1), 0 if c.get("laaa") else 1))
for c in sorted_comps:
    grm_str = f'{c["grm"]:.1f}x' if c.get("grm") not in (None, "--") else "--"
    cap_str = f'{c["cap"]:.2f}%' if c.get("cap") not in (None, "--") else "--"
    psf_str = f'${c["psf"]:,}' if c.get("psf") not in (None, "--") else "--"
    dom_str = f'{c["dom"]:,}' if c.get("dom") not in (None, "--") else "--"
    sf_str = f'{c["sf"]:,}' if c.get("sf") not in (None, "--") else "--"
    # LAAA Team badge + tier indicator in address cell
    addr_display = c["addr"]
    if c.get("laaa"):
        addr_display += ' <span style="background:#C5A258;color:#fff;font-size:8px;font-weight:700;padding:1px 4px;border-radius:2px;vertical-align:middle;">LAAA TEAM</span>'
    sale_comp_html += f'<tr><td>{c["num"]}</td><td>{addr_display}</td><td class="num">{c["units"]}</td>'
    sale_comp_html += f'<td>{c["yr"]}</td><td class="num">{sf_str}</td>'
    sale_comp_html += f'<td class="num">{fc(c["price"])}</td><td class="num">{fc(c["ppu"])}</td>'
    sale_comp_html += f'<td class="num">{psf_str}</td><td class="num">{cap_str}</td>'
    sale_comp_html += f'<td class="num">{grm_str}</td>'
    sale_comp_html += f'<td>{c["date"]}</td><td class="num">{dom_str}</td></tr>\n'

# Average, median, and Tier 1 average summary rows
if SALE_COMPS:
    sc_prices = [c["price"] for c in SALE_COMPS]
    sc_ppus = [c["ppu"] for c in SALE_COMPS]
    sc_psfs = [c["psf"] for c in SALE_COMPS if c.get("psf") not in (None, "--")]
    sc_caps = [c["cap"] for c in SALE_COMPS if c.get("cap") not in (None, "--")]
    sc_grms = [c["grm"] for c in SALE_COMPS if c.get("grm") not in (None, "--")]
    sc_doms = [c["dom"] for c in SALE_COMPS if c.get("dom") not in (None, "--")]

    avg_price = statistics.mean(sc_prices)
    avg_ppu = statistics.mean(sc_ppus)
    avg_psf = statistics.mean(sc_psfs) if sc_psfs else 0
    avg_cap_str = f'{statistics.mean(sc_caps):.2f}%' if sc_caps else "--"
    avg_grm_str = f'{statistics.mean(sc_grms):.1f}x' if sc_grms else "--"
    avg_dom_str = f'{statistics.mean(sc_doms):.0f}' if sc_doms else "--"
    med_price = statistics.median(sc_prices)
    med_ppu = statistics.median(sc_ppus)
    med_psf = statistics.median(sc_psfs) if sc_psfs else 0
    med_cap_str = f'{statistics.median(sc_caps):.2f}%' if sc_caps else "--"
    med_grm_str = f'{statistics.median(sc_grms):.1f}x' if sc_grms else "--"
    med_dom_str = f'{statistics.median(sc_doms):.0f}' if sc_doms else "--"

    # Tier 1 average (if any Tier 1 comps exist)
    t1_comps = [c for c in SALE_COMPS if c.get("tier") == 1]
    t1_row = ""
    if t1_comps:
        t1_ppus = [c["ppu"] for c in t1_comps]
        t1_psfs = [c["psf"] for c in t1_comps if c.get("psf") not in (None, "--")]
        t1_caps = [c["cap"] for c in t1_comps if c.get("cap") not in (None, "--")]
        t1_grms = [c["grm"] for c in t1_comps if c.get("grm") not in (None, "--")]
        t1_ppu = statistics.mean(t1_ppus)
        t1_psf_str = f'${statistics.mean(t1_psfs):,.0f}' if t1_psfs else "--"
        t1_cap_str = f'{statistics.mean(t1_caps):.2f}%' if t1_caps else "--"
        t1_grm_str = f'{statistics.mean(t1_grms):.1f}x' if t1_grms else "--"
        t1_style = 'style="background:#E8F0E8;font-weight:600;"'
        t1_row = f'<tr {t1_style}><td></td><td>Tier 1 Average</td><td class="num"></td><td></td><td class="num"></td>'
        t1_row += f'<td class="num"></td><td class="num">{fc(t1_ppu)}</td>'
        t1_row += f'<td class="num">{t1_psf_str}</td><td class="num">{t1_cap_str}</td>'
        t1_row += f'<td class="num">{t1_grm_str}</td>'
        t1_row += f'<td></td><td class="num"></td></tr>\n'

    summary_row_style = 'style="background:#FFF8E7;font-weight:600;"'
    sale_comp_html += f'<tr {summary_row_style}><td></td><td>Average</td><td class="num"></td><td></td><td class="num"></td>'
    sale_comp_html += f'<td class="num">{fc(avg_price)}</td><td class="num">{fc(avg_ppu)}</td>'
    sale_comp_html += f'<td class="num">${avg_psf:,.0f}</td><td class="num">{avg_cap_str}</td>'
    sale_comp_html += f'<td class="num">{avg_grm_str}</td>'
    sale_comp_html += f'<td></td><td class="num">{avg_dom_str}</td></tr>\n'
    sale_comp_html += f'<tr {summary_row_style}><td></td><td>Median</td><td class="num"></td><td></td><td class="num"></td>'
    sale_comp_html += f'<td class="num">{fc(med_price)}</td><td class="num">{fc(med_ppu)}</td>'
    sale_comp_html += f'<td class="num">${med_psf:,.0f}</td><td class="num">{med_cap_str}</td>'
    sale_comp_html += f'<td class="num">{med_grm_str}</td>'
    sale_comp_html += f'<td></td><td class="num">{med_dom_str}</td></tr>\n'
    if t1_row:
        sale_comp_html += t1_row

# On-Market Comp Table
on_market_html = ""
for c in ON_MARKET_COMPS:
    psf_str = f'${c["psf"]}' if c.get("psf") and c["psf"] != "--" else "--"
    sf_str = f'{c["sf"]:,}' if c.get("sf") and c["sf"] != "--" else "--"
    on_market_html += f'<tr><td>{c["num"]}</td><td>{c["addr"]}</td><td class="num">{c["units"]}</td>'
    on_market_html += f'<td>{c["yr"]}</td><td class="num">{sf_str}</td>'
    on_market_html += f'<td class="num">{fc(c["price"])}</td><td class="num">{fc(c["ppu"])}</td>'
    on_market_html += f'<td class="num">{psf_str}</td><td class="num">{c["dom"]}</td>'
    on_market_html += f'<td>{c["notes"]}</td></tr>\n'

# Rent Comp Table
rent_comp_html = ""
for i, rc in enumerate(RENT_COMPS, 1):
    rent_comp_html += f'<tr><td>{i}</td><td>{rc["addr"]}</td><td>{rc["type"]}</td>'
    rent_comp_html += f'<td class="num">{rc["sf"]:,}</td><td class="num">${rc["rent"]:,}</td>'
    rent_comp_html += f'<td class="num">${rc["rent_sf"]:.2f}</td><td>{rc["source"]}</td></tr>\n'

# Operating Statement
TAXES_AT_LIST = AT_LIST["taxes"]
CUR_EGI = AT_LIST["cur_egi"]

os_income_html = ""
vacancy_amt = GSR * VACANCY_PCT
eri = GSR - vacancy_amt
os_income_html += f'<tr><td>Gross Scheduled Rent</td><td class="num">${GSR:,.0f}</td><td class="num">${GSR/UNITS:,.0f}</td><td class="num">${GSR/SF:.2f}</td><td class="num"> - </td></tr>\n'
os_income_html += f'<tr><td>Less: Vacancy ({VACANCY_PCT*100:.0f}%)</td><td class="num">$({vacancy_amt:,.0f})</td><td class="num">$({vacancy_amt/UNITS:,.0f})</td><td class="num">$({vacancy_amt/SF:.2f})</td><td class="num"> - </td></tr>\n'
if OTHER_INCOME > 0:
    os_income_html += f'<tr><td>Other Income <span class="note-ref">[1]</span></td><td class="num">${OTHER_INCOME:,.0f}</td><td class="num">${OTHER_INCOME/UNITS:,.0f}</td><td class="num">${OTHER_INCOME/SF:.2f}</td><td class="num"> - </td></tr>\n'
os_income_html += f'<tr class="summary"><td><strong>Effective Gross Income</strong></td><td class="num"><strong>${CUR_EGI:,.0f}</strong></td><td class="num"><strong>${CUR_EGI/UNITS:,.0f}</strong></td><td class="num"><strong>${CUR_EGI/SF:.2f}</strong></td><td class="num"><strong>100.0%</strong></td></tr>\n'

os_expense_html = ""
total_exp_calc = 0
for label, val, note_num in expense_lines:
    total_exp_calc += val
    ref = f' <span class="note-ref">[{note_num}]</span>' if note_num else ""
    os_expense_html += f'<tr><td>{label}{ref}</td><td class="num">${val:,.0f}</td><td class="num">${val/UNITS:,.0f}</td><td class="num">${val/SF:.2f}</td><td class="num">{val/CUR_EGI*100:.1f}%</td></tr>\n'

NOI_AT_LIST = CUR_EGI - total_exp_calc
os_expense_html += f'<tr class="summary"><td><strong>Total Expenses</strong></td><td class="num"><strong>${total_exp_calc:,.0f}</strong></td><td class="num"><strong>${total_exp_calc/UNITS:,.0f}</strong></td><td class="num"><strong>${total_exp_calc/SF:.2f}</strong></td><td class="num"><strong>{total_exp_calc/CUR_EGI*100:.1f}%</strong></td></tr>\n'
os_expense_html += f'<tr class="summary"><td><strong>Net Operating Income</strong></td><td class="num"><strong>${NOI_AT_LIST:,.0f}</strong></td><td class="num"><strong>${NOI_AT_LIST/UNITS:,.0f}</strong></td><td class="num"><strong>${NOI_AT_LIST/SF:.2f}</strong></td><td class="num"><strong>{NOI_AT_LIST/CUR_EGI*100:.1f}%</strong></td></tr>\n'

# OS Notes HTML
os_notes_html = ""
for num in sorted(OS_NOTES.keys()):
    os_notes_html += f'<p><strong>[{num}]</strong> {OS_NOTES[num]}</p>\n'

# Pricing Matrix
matrix_html = ""
if PROPERTY_TYPE == "value-add":
    for m in MATRIX:
        cls = ' class="highlight"' if m["price"] == LIST_PRICE else ""
        matrix_html += f'<tr{cls}><td class="num">${m["price"]:,}</td>'
        matrix_html += f'<td class="num">{m["cur_cap"]:.2f}%</td>'
        matrix_html += f'<td class="num">{m["pf_cap"]:.2f}%</td>'
        matrix_html += f'<td class="num">{m["coc_cur"]:.2f}%</td>'
        matrix_html += f'<td class="num">${m["per_sf"]:.0f}</td>'
        matrix_html += f'<td class="num">${m["per_unit"]:,.0f}</td>'
        matrix_html += f'<td class="num">{m["pf_grm"]:.2f}x</td></tr>\n'
else:
    for m in MATRIX:
        cls = ' class="highlight"' if m["price"] == LIST_PRICE else ""
        matrix_html += f'<tr{cls}><td class="num">${m["price"]:,}</td>'
        matrix_html += f'<td class="num">{m["cur_cap"]:.2f}%</td>'
        matrix_html += f'<td class="num">{m["coc_cur"]:.2f}%</td>'
        matrix_html += f'<td class="num">${m["per_unit"]:,.0f}</td>'
        matrix_html += f'<td class="num">${m["per_sf"]:.0f}</td>'
        matrix_html += f'<td class="num">{m["grm"]:.2f}x</td>'
        matrix_html += f'<td class="num">{m["dcr_cur"]:.2f}x</td></tr>\n'

# Summary page expense rows
sum_expense_html = ""
for label, val, _ in expense_lines:
    label_clean = label.replace("&amp;", "&")
    sum_expense_html += f'<tr><td>{label_clean}</td><td class="num">${val:,.0f}</td></tr>\n'

if LIST_PRICE > 0:
    print(f"NOI at list (reassessed): ${NOI_AT_LIST:,.0f}")
    print(f"Total expenses: ${total_exp_calc:,.0f}")

# ============================================================
# HTML ASSEMBLY
# ============================================================
html_parts = []

# HEAD
html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="Broker Opinion of Value - {FULL_ADDRESS}">
<meta property="og:description" content="{PROPERTY_SUBTITLE} - {CITY_STATE_ZIP} | LAAA Team - Marcus &amp; Millichap">
<meta property="og:image" content="{BOV_BASE_URL}/preview.png">
<meta property="og:url" content="{BOV_BASE_URL}/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Broker Opinion of Value - {FULL_ADDRESS}">
<meta name="twitter:description" content="{PROPERTY_SUBTITLE} - {CITY_STATE_ZIP} | LAAA Team - Marcus &amp; Millichap">
<meta name="twitter:image" content="{BOV_BASE_URL}/preview.png">
<title>BOV - {FULL_ADDRESS} | LAAA Team</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
""")

# ============================================================
# DESKTOP CSS (verbatim from blueprint)
# ============================================================
html_parts.append("""
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; color: #333; line-height: 1.6; background: #fff; }
html { scroll-padding-top: 50px; }
p { margin-bottom: 16px; font-size: 14px; line-height: 1.7; }

/* Cover */
.cover { position: relative; min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; color: #fff; overflow: hidden; }
.cover-bg { position: absolute; inset: 0; background-size: cover; background-position: center; filter: brightness(0.45); z-index: 0; }
.cover-content { position: relative; z-index: 2; padding: 60px 40px; max-width: 860px; }
.cover-logo { width: 320px; margin: 0 auto 30px; display: block; filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3)); }
.cover-label { font-size: 13px; font-weight: 500; letter-spacing: 3px; text-transform: uppercase; color: #C5A258; margin-bottom: 18px; }
.cover-title { font-size: 46px; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px; text-shadow: 0 2px 12px rgba(0,0,0,0.3); }
.cover-stats { display: flex; gap: 32px; justify-content: center; flex-wrap: wrap; margin-bottom: 32px; }
.cover-stat-value { display: block; font-size: 26px; font-weight: 600; color: #fff; }
.cover-stat-label { display: block; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1.5px; color: #C5A258; margin-top: 4px; }
.cover-headshots { display: flex; justify-content: center; gap: 40px; margin-top: 24px; margin-bottom: 16px; }
.cover-headshot { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #C5A258; object-fit: cover; box-shadow: 0 4px 16px rgba(0,0,0,0.4); }
.cover-headshot-name { font-size: 12px; font-weight: 600; margin-top: 6px; color: #fff; }
.cover-headshot-title { font-size: 10px; color: #C5A258; }
.cover-headshot-wrap { text-align: center; }
.cover-stat { text-align: center; }
.cover-address { font-size: 16px; font-weight: 400; letter-spacing: 1px; color: rgba(255,255,255,0.85); margin-top: 4px; }
.client-greeting { font-size: 14px; font-weight: 500; color: #C5A258; letter-spacing: 1px; margin-top: 16px; }
.gold-line { height: 3px; background: #C5A258; margin: 20px 0; }

/* PDF Download Button */
.pdf-float-btn { position: fixed; bottom: 24px; right: 24px; z-index: 9999; padding: 14px 28px; background: #C5A258; color: #1B3A5C; font-size: 14px; font-weight: 700; text-decoration: none; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.35); display: flex; align-items: center; gap: 8px; }
.pdf-float-btn:hover { background: #fff; transform: translateY(-2px); }
.pdf-float-btn svg { width: 18px; height: 18px; fill: currentColor; }

/* TOC Nav */
.toc-nav { background: #1B3A5C; padding: 0 12px; display: flex; flex-wrap: nowrap; justify-content: center; align-items: stretch; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.15); overflow-x: auto; scrollbar-width: none; }
.toc-nav::-webkit-scrollbar { display: none; }
.toc-nav a { color: rgba(255,255,255,0.85); text-decoration: none; font-size: 11px; font-weight: 500; letter-spacing: 0.3px; text-transform: uppercase; padding: 12px 8px; border-bottom: 2px solid transparent; white-space: nowrap; display: flex; align-items: center; }
.toc-nav a:hover { color: #fff; background: rgba(197,162,88,0.12); border-bottom-color: rgba(197,162,88,0.4); }
.toc-nav a.toc-active { color: #C5A258; font-weight: 600; border-bottom-color: #C5A258; }

/* Sections */
.section { padding: 50px 40px; max-width: 1100px; margin: 0 auto; }
.section-alt { background: #f8f9fa; }
.section-title { font-size: 26px; font-weight: 700; color: #1B3A5C; margin-bottom: 6px; }
.section-subtitle { font-size: 13px; color: #C5A258; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 16px; font-weight: 500; }
.section-divider { width: 60px; height: 3px; background: #C5A258; margin-bottom: 30px; }
.sub-heading { font-size: 18px; font-weight: 600; color: #1B3A5C; margin: 30px 0 16px; }

/* Metrics */
.metrics-grid, .metrics-grid-4 { display: grid; gap: 16px; margin-bottom: 30px; }
.metrics-grid { grid-template-columns: repeat(3, 1fr); }
.metrics-grid-4 { grid-template-columns: repeat(4, 1fr); }
.metric-card { background: #1B3A5C; border-radius: 12px; padding: 24px; text-align: center; color: #fff; }
.metric-value { display: block; font-size: 28px; font-weight: 700; }
.metric-label { display: block; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,0.6); margin-top: 6px; }
.metric-sub { display: block; font-size: 12px; color: #C5A258; margin-top: 4px; }

/* Tables */
table { width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 13px; }
th { background: #1B3A5C; color: #fff; padding: 10px 12px; text-align: left; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
td { padding: 8px 12px; border-bottom: 1px solid #eee; }
tr:nth-child(even) { background: #f5f5f5; }
tr.highlight { background: #FFF8E7 !important; border-left: 3px solid #C5A258; }
td.num, th.num { text-align: right; }
.table-scroll { overflow-x: auto; margin-bottom: 24px; }
.table-scroll table { min-width: 700px; margin-bottom: 0; }
.info-table td { padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
.info-table td:first-child { font-weight: 600; color: #1B3A5C; width: 40%; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }

/* Track Record */
.tr-tagline { font-size: 24px; font-weight: 600; color: #1B3A5C; text-align: center; padding: 16px 24px; margin-bottom: 20px; border-left: 4px solid #C5A258; background: #FFF8E7; border-radius: 0 4px 4px 0; font-style: italic; }
.tr-map-print { display: none; }
.tr-service-quote { margin: 24px 0; }
.tr-service-quote h3 { font-size: 18px; font-weight: 700; color: #1B3A5C; margin-bottom: 8px; }
.tr-service-quote p { font-size: 14px; line-height: 1.7; }
.bio-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 24px 0; }
.bio-card { display: flex; gap: 16px; align-items: flex-start; }
.bio-headshot { width: 100px; height: 100px; border-radius: 50%; border: 3px solid #C5A258; object-fit: cover; flex-shrink: 0; }
.bio-name { font-size: 16px; font-weight: 700; color: #1B3A5C; }
.bio-title { font-size: 11px; color: #C5A258; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.bio-text { font-size: 13px; line-height: 1.6; color: #444; }
.team-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 12px 0; }
.team-card { text-align: center; padding: 8px; }
.team-headshot { width: 60px; height: 60px; border-radius: 50%; border: 2px solid #C5A258; object-fit: cover; margin: 0 auto 4px; display: block; }
.team-card-name { font-size: 13px; font-weight: 700; color: #1B3A5C; }
.team-card-title { font-size: 10px; color: #C5A258; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }
.costar-badge { text-align: center; background: #FFF8E7; border: 2px solid #C5A258; border-radius: 8px; padding: 20px 24px; margin: 30px auto 24px; max-width: 600px; }
.costar-badge-title { font-size: 22px; font-weight: 700; color: #1B3A5C; }
.costar-badge-sub { font-size: 12px; color: #C5A258; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-top: 6px; }
.condition-note { background: #FFF8E7; border-left: 4px solid #C5A258; padding: 16px 20px; margin: 24px 0; border-radius: 0 4px 4px 0; font-size: 13px; line-height: 1.6; }
.condition-note-label { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #C5A258; margin-bottom: 8px; }
.achievements-list { font-size: 13px; line-height: 1.8; }
.note-ref { font-size: 9px; color: #C5A258; font-weight: 700; vertical-align: super; }

/* Marketing */
.mkt-quote { background: #FFF8E7; border-left: 4px solid #C5A258; padding: 16px 24px; margin: 20px 0; border-radius: 0 4px 4px 0; font-size: 15px; font-style: italic; line-height: 1.6; color: #1B3A5C; }
.mkt-channels { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
.mkt-channel { background: #f0f4f8; border-radius: 8px; padding: 16px 20px; }
.mkt-channel h4 { color: #1B3A5C; font-size: 14px; margin-bottom: 8px; }
.mkt-channel li { font-size: 13px; line-height: 1.5; margin-bottom: 4px; }
.perf-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
.perf-card { background: #f0f4f8; border-radius: 8px; padding: 16px 20px; }
.perf-card h4 { color: #1B3A5C; font-size: 14px; margin-bottom: 8px; }
.perf-card li { font-size: 13px; line-height: 1.5; margin-bottom: 4px; }
.platform-strip { display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap; margin-top: 24px; padding: 14px 20px; background: #1B3A5C; border-radius: 6px; }
.platform-strip-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #C5A258; font-weight: 600; }
.platform-name { font-size: 12px; font-weight: 600; color: #fff; }

/* Press Strip */
.press-strip { display: flex; justify-content: center; align-items: center; gap: 28px; flex-wrap: wrap; margin: 16px 0 0; padding: 12px 20px; background: #f0f4f8; border-radius: 6px; }
.press-strip-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #888; font-weight: 600; }
.press-logo { font-size: 13px; font-weight: 700; color: #1B3A5C; letter-spacing: 0.5px; }

/* Investment Overview */
.inv-split { display: grid; grid-template-columns: 50% 50%; gap: 24px; }
.inv-left .metrics-grid-4 { grid-template-columns: repeat(2, 1fr); }
.inv-text p { font-size: 13px; line-height: 1.6; margin-bottom: 10px; }
.inv-logo { display: none; }
.inv-right { display: flex; flex-direction: column; gap: 16px; padding-top: 70px; }
.inv-photo { height: 280px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.inv-photo img { width: 100%; height: 100%; object-fit: cover; object-position: center; }
.inv-highlights { background: #f0f4f8; border: 1px solid #dce3eb; border-radius: 8px; padding: 16px 20px; flex: 1; }
.inv-highlights h4 { color: #1B3A5C; font-size: 13px; margin-bottom: 8px; }
.inv-highlights li { font-size: 12px; line-height: 1.5; margin-bottom: 5px; }

/* Location */
.loc-grid { display: grid; grid-template-columns: 58% 42%; gap: 28px; align-items: start; }
.loc-left { max-height: 480px; overflow: hidden; }
.loc-left p { font-size: 13.5px; line-height: 1.7; margin-bottom: 14px; }
.loc-right { display: block; max-height: 480px; overflow: hidden; }
.loc-wide-map { width: 100%; height: 200px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-top: 20px; }
.loc-wide-map img { width: 100%; height: 100%; object-fit: cover; object-position: center; }

/* Property Details */
.prop-grid-4 { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: auto auto; gap: 20px; }

/* Operating Statement */
.os-two-col { display: grid; grid-template-columns: 55% 45%; gap: 24px; align-items: stretch; margin-bottom: 24px; }
.os-left { }
.os-right { font-size: 10.5px; line-height: 1.45; color: #555; background: #f8f9fb; border: 1px solid #e0e4ea; border-radius: 6px; padding: 16px 20px; }
.os-right h3 { font-size: 13px; margin: 0 0 8px; }
.os-right p { margin-bottom: 4px; }

/* Financial Summary */
.summary-page { margin-top: 24px; border: 1px solid #dce3eb; border-radius: 8px; padding: 20px; background: #fff; }
.summary-banner { text-align: center; background: #1B3A5C; color: #fff; padding: 10px 16px; font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; border-radius: 4px; margin-bottom: 16px; }
.summary-two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }
.summary-left { }
.summary-right { }
.summary-table { width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 12px; border: 1px solid #dce3eb; }
.summary-table th, .summary-table td { padding: 4px 8px; border-bottom: 1px solid #e8ecf0; }
.summary-header { background: #1B3A5C; color: #fff; padding: 5px 8px !important; font-size: 10px !important; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; }
.summary-table tr.summary td { border-top: 2px solid #1B3A5C; font-weight: 700; background: #f0f4f8; }
.summary-table tr:nth-child(even) { background: #fafbfc; }
.summary-trade-range { text-align: center; margin: 24px auto; padding: 16px 24px; border: 2px solid #1B3A5C; border-radius: 6px; max-width: 480px; }
.summary-trade-label { font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #555; font-weight: 600; margin-bottom: 6px; }
.summary-trade-prices { font-size: 26px; font-weight: 700; color: #1B3A5C; }

/* Price Reveal */
.price-reveal { margin-top: 24px; }

/* Track Record Page 2 */
.tr-page2 { padding: 50px 40px; max-width: 1100px; margin: 0 auto; }

/* Buyer Profile & Objections */
.buyer-split { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; align-items: start; }
.buyer-split-left { }
.buyer-split-right { }
.obj-item { margin-bottom: 16px; }
.obj-q { font-weight: 700; color: #1B3A5C; margin-bottom: 4px; font-size: 14px; }
.obj-a { font-size: 13px; color: #444; line-height: 1.6; }
.bp-closing { font-size: 13px; color: #444; margin-top: 12px; font-style: italic; }
.buyer-photo { width: 100%; height: 220px; border-radius: 8px; overflow: hidden; margin-top: 24px; }
.buyer-photo img { width: 100%; height: 100%; object-fit: cover; }

/* Narrative paragraphs */
.narrative { font-size: 14px; line-height: 1.7; color: #444; margin-bottom: 16px; }

/* Maps */
.leaflet-map { height: 400px; border-radius: 4px; border: 1px solid #ddd; margin-bottom: 30px; z-index: 1; }
.map-fallback { display: none; }
.comp-map-print { display: none; }
.embed-map-wrap { position: relative; width: 100%; margin-bottom: 20px; border-radius: 8px; overflow: hidden; }
.embed-map-wrap iframe { display: block; width: 100%; height: 420px; border: 0; }

/* Misc */
.page-break-marker { height: 4px; background: repeating-linear-gradient(90deg, #ddd 0, #ddd 8px, transparent 8px, transparent 16px); }
.photo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 30px; overflow: hidden; }
.photo-grid img { width: 100%; height: 180px; object-fit: cover; border-radius: 4px; }
.highlight-box { background: #f0f4f8; border: 1px solid #dce3eb; border-radius: 8px; padding: 20px 24px; margin: 24px 0; }
.img-float-right { float: right; width: 48%; margin: 0 0 16px 20px; border-radius: 8px; overflow: hidden; }
.img-float-right img { width: 100%; display: block; }

/* Footer */
.footer { background: #1B3A5C; color: #fff; padding: 50px 40px; text-align: center; }
.footer-logo { width: 180px; margin-bottom: 30px; }
.footer-team { display: flex; justify-content: center; gap: 40px; margin-bottom: 30px; flex-wrap: wrap; }
.footer-person { text-align: center; flex: 1; min-width: 280px; }
.footer-headshot { width: 70px; height: 70px; border-radius: 50%; border: 2px solid #C5A258; object-fit: cover; }
.footer-name { font-size: 16px; font-weight: 600; }
.footer-title { font-size: 12px; color: #C5A258; margin-bottom: 8px; }
.footer-contact { font-size: 12px; color: rgba(255,255,255,0.7); line-height: 1.8; }
.footer-contact a { color: rgba(255,255,255,0.7); text-decoration: none; }
.footer-disclaimer { font-size: 10px; color: rgba(255,255,255,0.35); margin-top: 20px; max-width: 800px; margin-left: auto; margin-right: auto; }
""")

# ============================================================
# MOBILE CSS (verbatim from blueprint)
# ============================================================
html_parts.append("""
@media (max-width: 768px) {
  .cover-content { padding: 30px 20px; }
  .cover-title { font-size: 32px; }
  .cover-logo { width: 220px; }
  .cover-headshots { gap: 24px; }
  .cover-headshot { width: 60px; height: 60px; }
  .section { padding: 30px 16px; }
  .photo-grid { grid-template-columns: 1fr; }
  .two-col, .buyer-split, .inv-split, .os-two-col, .loc-grid { grid-template-columns: 1fr; }
  .metrics-grid, .metrics-grid-4 { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .metric-card { padding: 14px 10px; }
  .metric-value { font-size: 22px; }
  .mkt-channels, .perf-grid { grid-template-columns: 1fr; }
  .summary-two-col, .prop-grid-4 { grid-template-columns: 1fr; }
  .pdf-float-btn { padding: 10px 18px; font-size: 12px; bottom: 16px; right: 16px; }
  .toc-nav { padding: 0 6px; }
  .toc-nav a { font-size: 10px; padding: 10px 6px; letter-spacing: 0.2px; }
  .leaflet-map { height: 300px; }
  .embed-map-wrap iframe { height: 320px; }
  .loc-wide-map { height: 180px; margin-top: 16px; }
  .table-scroll table { min-width: 560px; }
  .bio-grid { grid-template-columns: 1fr; gap: 16px; }
  .bio-headshot { width: 60px; height: 60px; }
  .footer-team { flex-direction: column; align-items: center; }
  .press-strip { gap: 16px; }
  .press-logo { font-size: 11px; }
  .costar-badge-title { font-size: 18px; }
  .img-float-right { float: none; width: 100%; margin: 0 0 16px 0; }
  .inv-photo { height: 240px; }
}
@media (max-width: 420px) {
  .cover-title { font-size: 26px; }
  .cover-stat-value { font-size: 20px; }
  .cover-headshots { gap: 16px; }
  .cover-headshot { width: 50px; height: 50px; }
  .metrics-grid-4 { grid-template-columns: 1fr 1fr; }
  .metric-value { font-size: 18px; }
  .section { padding: 20px 12px; }
}
""")

# ============================================================
# PRINT CSS (verbatim from blueprint)
# ============================================================
html_parts.append("""
@media print {
  @page { size: letter landscape; margin: 0.4in 0.5in; }
  body { font-size: 11px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  p { font-size: 11px; line-height: 1.5; margin-bottom: 8px; }
  .pdf-float-btn, .toc-nav, .leaflet-map, .embed-map-wrap, .page-break-marker, .map-fallback { display: none !important; }
  .cover { min-height: 7.5in; page-break-after: always; }
  .cover-bg { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .cover-headshots { display: flex !important; }
  .cover-headshot { width: 55px; height: 55px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .cover-logo { width: 240px; }
  .section { padding: 20px 0; page-break-before: always; }
  .section-title { font-size: 20px; margin-bottom: 4px; }
  .section-subtitle { font-size: 11px; margin-bottom: 10px; }
  .section-divider { margin-bottom: 16px; }
  .metric-card { padding: 12px 8px; border-radius: 6px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .metric-value { font-size: 20px; }
  .metric-label { font-size: 9px; }
  table { font-size: 11px; }
  th { padding: 6px 8px; font-size: 9px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  td { padding: 5px 8px; }
  tr.highlight { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .tr-tagline { font-size: 15px; padding: 8px 14px; margin-bottom: 8px; }
  .tr-map-print { display: block; width: 100%; height: 240px; border-radius: 4px; overflow: hidden; margin-bottom: 8px; }
  .tr-map-print img { width: 100%; height: 100%; object-fit: cover; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .tr-service-quote { margin: 10px 0; }
  .tr-service-quote h3 { font-size: 13px; margin-bottom: 4px; }
  .tr-service-quote p { font-size: 11px; line-height: 1.45; }
  .tr-page2 .section-title { font-size: 18px; margin-bottom: 2px; }
  .tr-page2 .section-divider { margin-bottom: 8px; }
  .bio-grid { gap: 12px; margin: 8px 0; }
  .bio-card { gap: 10px; }
  .bio-headshot { width: 75px; height: 75px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .bio-text { font-size: 11px; }
  .team-grid { gap: 6px; margin: 8px 0; }
  .team-headshot { width: 45px; height: 45px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .team-card-name { font-size: 11px; }
  .team-card-title { font-size: 9px; }
  .costar-badge { padding: 8px 12px; margin: 8px auto; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .costar-badge-title { font-size: 16px; }
  .condition-note { padding: 8px 14px; margin-top: 8px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .achievements-list { font-size: 11px; line-height: 1.5; }
  .press-strip { padding: 6px 12px; gap: 16px; margin-top: 8px; }
  .press-logo { font-size: 10px; }
  #marketing { page-break-before: always; }
  #marketing .section-title { font-size: 18px; margin-bottom: 2px; }
  #marketing .section-subtitle { font-size: 11px; margin-bottom: 4px; }
  #marketing .section-divider { margin-bottom: 6px; }
  #marketing .metrics-grid-4 { gap: 8px; margin-bottom: 8px; grid-template-columns: repeat(4, 1fr); }
  #marketing .metric-card { padding: 8px 6px; }
  #marketing .metric-value { font-size: 18px; }
  #marketing .metric-label { font-size: 8px; }
  .mkt-quote { padding: 8px 14px; margin: 8px 0; font-size: 11px; line-height: 1.4; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .mkt-channels { gap: 10px; margin-top: 8px; grid-template-columns: 1fr 1fr; }
  .mkt-channel { padding: 8px 12px; border-radius: 6px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .mkt-channel h4 { font-size: 11px; margin-bottom: 4px; }
  .mkt-channel li { font-size: 10px; line-height: 1.4; margin-bottom: 2px; }
  .perf-grid { gap: 10px; margin-top: 8px; grid-template-columns: 1fr 1fr; }
  .perf-card { padding: 8px 12px; border-radius: 6px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .perf-card h4 { font-size: 11px; margin-bottom: 4px; }
  .perf-card li { font-size: 10px; line-height: 1.4; margin-bottom: 2px; }
  .platform-strip { padding: 6px 12px; gap: 12px; margin-top: 8px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .platform-strip-label { font-size: 8px; }
  .platform-strip img { height: 18px; }
  .inv-text p { font-size: 11px; line-height: 1.5; margin-bottom: 6px; }
  .inv-logo { display: none !important; }
  .inv-right { padding-top: 30px; }
  .inv-photo { height: 220px; }
  .inv-photo img { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .inv-highlights { padding: 10px 14px; }
  .inv-highlights h4 { font-size: 11px; margin-bottom: 4px; }
  .inv-highlights li { font-size: 10px; line-height: 1.4; margin-bottom: 2px; }
  .loc-grid { display: grid; grid-template-columns: 58% 42%; gap: 14px; page-break-inside: avoid; }
  .loc-left { max-height: 340px; overflow: hidden; }
  .loc-left p { font-size: 10.5px; line-height: 1.4; margin-bottom: 5px; }
  .loc-right { max-height: 340px; overflow: hidden; }
  .loc-right table { font-size: 10px; }
  .loc-right th { font-size: 9px; padding: 4px 6px; }
  .loc-right td { padding: 4px 6px; font-size: 10px; }
  .loc-wide-map { height: 220px; margin-top: 8px; }
  .loc-wide-map img { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  #prop-details { page-break-before: always; }
  .prop-grid-4 { gap: 12px; }
  .prop-grid-4 table { font-size: 10px; }
  .prop-grid-4 th { font-size: 9px; padding: 4px 6px; }
  .prop-grid-4 td { padding: 4px 6px; font-size: 10px; }
  .os-two-col { page-break-before: always; align-items: stretch; gap: 16px; }
  .os-left table { font-size: 10px; }
  .os-left th { font-size: 9px; padding: 4px 6px; }
  .os-left td { padding: 4px 6px; }
  .os-right { font-size: 9.5px; line-height: 1.3; padding: 10px 12px; }
  .os-right p { margin-bottom: 4px; font-size: 9.5px; }
  .os-right .sub-heading { font-size: 12px; margin-bottom: 6px; }
  .summary-page { page-break-before: always; padding: 12px; }
  .summary-banner { font-size: 12px; padding: 6px 12px; margin-bottom: 10px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .summary-two-col { gap: 12px; }
  .summary-table { font-size: 8px; margin-bottom: 8px; }
  .summary-table td { padding: 2px 4px; }
  .summary-table th { padding: 2px 4px; }
  .summary-header { font-size: 7px !important; padding: 3px 4px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .obj-q { font-size: 11px; margin-bottom: 2px; }
  .obj-a { font-size: 10px; line-height: 1.4; }
  .obj-item { margin-bottom: 8px; }
  .bp-closing { font-size: 10px; }
  .buyer-photo { height: 180px; }
  .buyer-photo img { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  #sale-comps, #on-market, #rent-comps { page-break-before: always; }
  .comp-narratives p.narrative { font-size: 10.5px; line-height: 1.4; margin-bottom: 6px; page-break-inside: avoid; }
  .comp-narratives p.narrative strong { font-size: 10.5px; }
  .comp-map-print { display: block !important; height: 280px; border-radius: 4px; overflow: hidden; margin-bottom: 10px; }
  .comp-map-print img { width: 100%; height: 100%; object-fit: cover; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .tr-page2 { page-break-before: always; }
  .footer { page-break-before: always; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .footer-headshot { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .price-reveal { page-break-before: always; }
  #property-info { page-break-before: always; }

  /* --- Page-break discipline --- */
  p { orphans: 3; widows: 3; }
  table { page-break-inside: avoid; }
  .section-title, .section-subtitle, .section-divider { page-break-after: avoid; }
  .metrics-grid { page-break-inside: avoid; }
  .metric-card { page-break-inside: avoid; }
  .highlight-box { page-break-inside: avoid; }
  .obj-item { page-break-inside: avoid; }
  .bio-card { page-break-inside: avoid; }
  .inv-highlights { page-break-inside: avoid; }
  .photo-grid { page-break-inside: avoid; }
  .prop-grid-4 { page-break-inside: avoid; }
  .loc-grid { page-break-inside: avoid; }
  .feature-item { page-break-inside: avoid; }
  .mkt-channel { page-break-inside: avoid; }
  .perf-card { page-break-inside: avoid; }
  .team-grid { page-break-inside: avoid; }
  .costar-badge { page-break-inside: avoid; }
  .press-strip { page-break-inside: avoid; }
  .summary-two-col { page-break-inside: avoid; }
  #pdfOverlay { display: none !important; }
}
""")

# Close style and head
html_parts.append("</style>\n</head>\n<body>\n")

# ============================================================
# PAGE 1: COVER
# ============================================================
cover_headshots = ""
for agent in COVER_AGENTS:
    cover_headshots += f'''<div class="cover-headshot-wrap">
        <img class="cover-headshot" src="{IMG[agent['img_key']]}" alt="{agent['name']}">
        <div class="cover-headshot-name">{agent['name']}</div>
        <div class="cover-headshot-title">{agent['title']}</div>
    </div>\n'''

html_parts.append(f"""
<div class="cover">
  <div class="cover-bg" style="background-image:url('{IMG["hero"]}');"></div>
  <div class="cover-content">
    <img src="{IMG['logo']}" class="cover-logo" alt="LAAA Team">
    <div class="cover-label">Confidential Broker Opinion of Value</div>
    <div class="cover-title">{ADDRESS}</div>
    <div class="cover-address">{CITY_STATE_ZIP}</div>
    <div class="gold-line" style="width:80px;margin:0 auto 24px;"></div>
    <div class="cover-stats">
      <div class="cover-stat"><span class="cover-stat-value">{UNITS}</span><span class="cover-stat-label">Units</span></div>
      <div class="cover-stat"><span class="cover-stat-value">{SF:,}</span><span class="cover-stat-label">Square Feet</span></div>
      <div class="cover-stat"><span class="cover-stat-value">{YEAR_BUILT}</span><span class="cover-stat-label">Year Built</span></div>
      <div class="cover-stat"><span class="cover-stat-value">{LOT_ACRES:.2f}</span><span class="cover-stat-label">Acres</span></div>
    </div>
    <div class="cover-headshots">
      {cover_headshots}
    </div>
    <p class="client-greeting" id="client-greeting">Prepared Exclusively for {CLIENT_NAME}</p>
    <p style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:8px;">{COVER_MONTH_YEAR}</p>
  </div>
</div>
""")

# ============================================================
# TOC NAV
# ============================================================
toc_links = '<a href="#track-record">Track Record</a>'
toc_links += '<a href="#marketing">Marketing</a>'
toc_links += '<a href="#investment">Investment</a>'
toc_links += '<a href="#location">Location</a>'
toc_links += '<a href="#prop-details">Property</a>'
toc_links += '<a href="#property-info">Buyer Profile</a>'
toc_links += '<a href="#sale-comps">Sale Comps</a>'
if INCLUDE_ON_MARKET_COMPS:
    toc_links += '<a href="#on-market">On-Market</a>'
toc_links += '<a href="#rent-comps">Rent Comps</a>'
toc_links += '<a href="#financials">Financials</a>'
toc_links += '<a href="#contact">Contact</a>'

html_parts.append(f'<nav class="toc-nav" id="toc-nav">{toc_links}</nav>\n')

# ============================================================
# PAGE 2: TRACK RECORD P1
# ============================================================
html_parts.append(f"""
<div class="section section-alt" id="track-record">
  <div class="section-title">Team Track Record</div>
  <div class="section-subtitle">LA Apartment Advisors at Marcus &amp; Millichap</div>
  <div class="section-divider"></div>
  <div class="tr-tagline">
    <span style="display:block;font-size:1.2em;font-weight:700;margin-bottom:4px;">LAAA Team of Marcus &amp; Millichap</span>
    Expertise, Execution, Excellence.
  </div>
  <div class="metrics-grid-4">
    <div class="metric-card"><span class="metric-value">501</span><span class="metric-label">Closed Transactions</span></div>
    <div class="metric-card"><span class="metric-value">$1.6B</span><span class="metric-label">Total Sales Volume</span></div>
    <div class="metric-card"><span class="metric-value">5,000+</span><span class="metric-label">Units Sold</span></div>
    <div class="metric-card"><span class="metric-value">34</span><span class="metric-label">Median DOM</span></div>
  </div>
  <div class="embed-map-wrap">
    <iframe src="https://www.google.com/maps/d/embed?mid=1ewCjzE3QX9p6m2MqK-md8b6fZitfIzU&ehbc=2E312F&noprof=1" loading="lazy" allowfullscreen></iframe>
  </div>
  <div class="tr-map-print"><img src="{IMG['closings_map']}" alt="LAAA Closings Map"></div>
  <div class="tr-service-quote">
    <h3>"We Didn't Invent Great Service, We Just Work Relentlessly to Provide It."</h3>
    <p>{MISSION_P1}</p>
    <p>{MISSION_P2}</p>
    <p>{MISSION_P3}</p>
  </div>
</div>
""")

# ============================================================
# PAGE 3: TRACK RECORD P2 (Our Team)
# ============================================================
# Team grid — all members except Glen and Filip (who get bio cards)
team_members = [
    ("Aida Memary Scher", "Associate", "team_aida"),
    ("Morgan Wetmore", "Associate", "team_morgan"),
    ("Luka Leader", "Associate", "team_luka"),
    ("Logan Ward", "Associate", "team_logan"),
    ("Alexandro Tapia", "Associate", "team_alexandro"),
    ("Blake Lewitt", "Associate", "team_blake"),
    ("Mike Palade", "Associate", "team_mike"),
    ("Tony H. Dang", "Associate", "team_tony"),
]

team_grid_html = ""
for name, title, img_key in team_members:
    team_grid_html += f'''<div class="team-card">
      <img class="team-headshot" src="{IMG[img_key]}" alt="{name}">
      <div class="team-card-name">{name}</div>
      <div class="team-card-title">{title}</div>
    </div>\n'''

# Glen and Filip bios — DEAL-SPECIFIC (update from team_bios.md)
GLEN_BIO = "Glen Scher is a Senior Managing Director of Investments at Marcus &amp; Millichap, specializing in multifamily investment sales throughout the Greater Los Angeles area. With over a decade of experience and 500+ closed transactions totaling $1.6B+ in volume, Glen provides data-driven advisory services to private investors and institutions."  # DEAL-SPECIFIC
FILIP_BIO = "Filip Niculete is a Senior Managing Director of Investments at Marcus &amp; Millichap. Filip and Glen co-lead the LAAA Team, combining deep market expertise with institutional-grade analytics to deliver results for multifamily investors across LA County."  # DEAL-SPECIFIC

html_parts.append(f"""
<div class="tr-page2">
  <div style="text-align:center;margin-bottom:8px;">
    <div class="section-title" style="margin-bottom:4px;">Our Team</div>
    <div class="section-divider" style="margin:0 auto 12px;"></div>
  </div>
  <div class="costar-badge" style="margin-top:4px;margin-bottom:8px;">
    <div class="costar-badge-title">#1 Most Active Multifamily Sales Team in LA County</div>
    <div class="costar-badge-sub">CoStar &bull; 2019, 2020, 2021 &bull; #4 in California</div>
  </div>
  <div class="bio-grid">
    <div class="bio-card">
      <img class="bio-headshot" src="{IMG['glen']}" alt="Glen Scher">
      <div>
        <div class="bio-name">Glen Scher</div>
        <div class="bio-title">Senior Managing Director</div>
        <div class="bio-text">{GLEN_BIO}</div>
      </div>
    </div>
    <div class="bio-card">
      <img class="bio-headshot" src="{IMG['filip']}" alt="Filip Niculete">
      <div>
        <div class="bio-name">Filip Niculete</div>
        <div class="bio-title">Senior Managing Director</div>
        <div class="bio-text">{FILIP_BIO}</div>
      </div>
    </div>
  </div>
  <div class="team-grid">
    {team_grid_html}
  </div>
  <div class="condition-note" style="margin-top:20px;">
    <div class="condition-note-label">Key Achievements</div>
    <p class="achievements-list">
      &bull; <strong>Chairman's Club</strong> - a top-tier annual honor at Marcus &amp; Millichap<br>
      &bull; <strong>National Achievement Award</strong> - Consistent top national performer<br>
      &bull; <strong>CoStar #1 Team</strong> - Most active multifamily sales team in LA County<br>
      &bull; <strong>500+ Transactions</strong> - Over $1.6 billion in career sales volume<br>
      &bull; <strong>34-Day Median DOM</strong> - Properties sell faster than market average
    </p>
  </div>
  <div class="press-strip">
    <span class="press-strip-label">As Featured In</span>
    <span class="press-logo">BISNOW</span>
    <span class="press-logo">YAHOO FINANCE</span>
    <span class="press-logo">CONNECT CRE</span>
    <span class="press-logo">SFVBJ</span>
    <span class="press-logo">THE PINNACLE LIST</span>
  </div>
</div>
""")

# ============================================================
# PAGE 4: MARKETING & RESULTS (standard — same for every BOV)
# ============================================================
html_parts.append("""
<div class="page-break-marker"></div>
<div class="section" id="marketing">
  <div class="section-title">Our Marketing Approach &amp; Results</div>
  <div class="section-subtitle">Data-Driven Marketing + Proven Performance</div>
  <div class="section-divider"></div>
  <div class="metrics-grid-4">
    <div class="metric-card"><span class="metric-value">30K+</span><span class="metric-label">Targeted Emails</span></div>
    <div class="metric-card"><span class="metric-value">10K+</span><span class="metric-label">Listing Views</span></div>
    <div class="metric-card"><span class="metric-value">3.7</span><span class="metric-label">Avg Offers / Listing</span></div>
    <div class="metric-card"><span class="metric-value">18</span><span class="metric-label">Avg Days to Escrow</span></div>
  </div>
  <div class="mkt-quote">"We are PROACTIVE marketers, not reactive. Every listing gets a custom campaign designed to maximize exposure, create urgency, and drive competitive offers."</div>
  <div class="mkt-channels">
    <div class="mkt-channel"><h4>Direct Phone Outreach</h4><ul>
      <li>500+ targeted calls per listing</li>
      <li>Focus: active buyers in submarket</li>
      <li>Personal follow-up within 48 hours</li>
    </ul></div>
    <div class="mkt-channel"><h4>Email Campaigns</h4><ul>
      <li>30,000+ qualified investor contacts</li>
      <li>Segmented by geography and deal size</li>
      <li>Multi-touch drip campaigns</li>
    </ul></div>
    <div class="mkt-channel"><h4>Online Platforms</h4><ul>
      <li>MarcusMillichap.com, CoStar, Crexi</li>
      <li>LoopNet, CREXi, Ten-X</li>
      <li>Custom property websites</li>
    </ul></div>
    <div class="mkt-channel"><h4>Additional Channels</h4><ul>
      <li>Office-wide agent blast (100+ agents)</li>
      <li>Industry networking events</li>
      <li>Strategic broker co-marketing</li>
    </ul></div>
  </div>
  <div class="metrics-grid-4" style="margin-top:16px;">
    <div class="metric-card"><span class="metric-value">97.6%</span><span class="metric-label">Avg SP/LP Ratio</span></div>
    <div class="metric-card"><span class="metric-value">21%</span><span class="metric-label">Sold Above Ask</span></div>
    <div class="metric-card"><span class="metric-value">10</span><span class="metric-label">Avg Day Contingency</span></div>
    <div class="metric-card"><span class="metric-value">61%</span><span class="metric-label">1031 Exchange Buyers</span></div>
  </div>
  <div class="perf-grid">
    <div class="perf-card"><h4>Pricing Accuracy</h4><ul>
      <li>97.6% average sale-to-list ratio</li>
      <li>21% of listings sold above asking</li>
      <li>Data-driven comp analysis</li>
    </ul></div>
    <div class="perf-card"><h4>Marketing Speed</h4><ul>
      <li>18 average days to accepted offer</li>
      <li>34-day median days on market</li>
      <li>Strategic pricing drives urgency</li>
    </ul></div>
    <div class="perf-card"><h4>Contract Strength</h4><ul>
      <li>10-day average contingency period</li>
      <li>Pre-qualified buyer verification</li>
      <li>Streamlined due diligence process</li>
      <li>98% close rate on accepted offers</li>
    </ul></div>
    <div class="perf-card"><h4>Exchange Expertise</h4><ul>
      <li>61% of buyers are 1031 exchangers</li>
      <li>Dedicated exchange buyer database</li>
      <li>Timeline management expertise</li>
      <li>85% higher cash flow for exchangers</li>
    </ul></div>
  </div>
  <div class="platform-strip">
    <span class="platform-strip-label">Advertised On</span>
    <span class="platform-name">CREXI</span>
    <span class="platform-name">COSTAR</span>
    <span class="platform-name">LOOPNET</span>
    <span class="platform-name">ZILLOW</span>
    <span class="platform-name">REALTOR</span>
    <span class="platform-name">M&amp;M</span>
    <span class="platform-name">APARTMENTS.COM</span>
    <span class="platform-name">REDFIN</span>
    <span class="platform-name">TEN-X</span>
  </div>
</div>
""")

# ============================================================
# PAGE 5: INVESTMENT OVERVIEW
# ============================================================
highlights_html = ""
for bold, text in HIGHLIGHTS:
    highlights_html += f'<li><strong>{bold}</strong> - {text}</li>\n'

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="investment">
  <div class="section-title">Investment Overview</div>
  <div class="section-subtitle">{SUBMARKET} - {ADDRESS}</div>
  <div class="section-divider"></div>
  <div class="inv-split">
    <div class="inv-left">
      <div class="metrics-grid-4">
        <div class="metric-card"><span class="metric-value">{UNITS}</span><span class="metric-label">Units</span></div>
        <div class="metric-card"><span class="metric-value">{SF:,}</span><span class="metric-label">Square Feet</span></div>
        <div class="metric-card"><span class="metric-value">{LOT_ACRES:.2f}</span><span class="metric-label">Lot Acres</span></div>
        <div class="metric-card"><span class="metric-value">{YEAR_BUILT}</span><span class="metric-label">Year Built</span></div>
      </div>
      <div class="inv-text">
        <p>{INVESTMENT_OVERVIEW_P1}</p>
        <p>{INVESTMENT_OVERVIEW_P2}</p>
        <p>{INVESTMENT_OVERVIEW_P3}</p>
      </div>
    </div>
    <div class="inv-right">
      <div class="inv-photo"><img src="{IMG['grid1']}" alt="Property"></div>
      <div class="inv-highlights">
        <h4>Investment Highlights</h4>
        <ul>
          {highlights_html}
        </ul>
      </div>
    </div>
  </div>
</div>
""")

# ============================================================
# PAGE 6: LOCATION OVERVIEW
# ============================================================
loc_table_rows = ""
for label, value in LOCATION_TABLE_ROWS:
    loc_table_rows += f'<tr><td>{label}</td><td>{value}</td></tr>\n'

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="location">
  <div class="section-title">Location Overview</div>
  <div class="section-subtitle">{SUBMARKET} - {CITY_STATE_ZIP.split(",")[1].strip() if "," in CITY_STATE_ZIP else CITY_STATE_ZIP}</div>
  <div class="section-divider"></div>
  <div class="loc-grid">
    <div class="loc-left">
      <p>{LOCATION_P1}</p>
      <p>{LOCATION_P2}</p>
      <p>{LOCATION_P3}</p>
    </div>
    <div class="loc-right">
      <table class="info-table">
        <thead><tr><th colspan="2">Location Details</th></tr></thead>
        <tbody>
          {loc_table_rows}
        </tbody>
      </table>
    </div>
  </div>
  <div class="loc-wide-map"><img src="{IMG['loc_map']}" alt="Location Map"></div>
</div>
""")

# ============================================================
# PAGE 7: PROPERTY DETAILS
# ============================================================
def build_info_table(title, rows, colspan=2):
    html = f'<table class="info-table"><thead><tr><th colspan="{colspan}">{title}</th></tr></thead><tbody>\n'
    for row in rows:
        if len(row) == 2:
            html += f'<tr><td>{row[0]}</td><td>{row[1]}</td></tr>\n'
        elif len(row) == 3:
            html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>\n'
    html += '</tbody></table>\n'
    return html

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="prop-details">
  <div class="section-title">Property Details</div>
  <div class="section-subtitle">{FULL_ADDRESS}</div>
  <div class="section-divider"></div>
  <div class="prop-grid-4">
    <div>{build_info_table("Property Overview", PROP_OVERVIEW)}</div>
    <div>{build_info_table("Site &amp; Zoning", PROP_SITE_ZONING)}</div>
    <div>{build_info_table("Building Systems &amp; Capital Improvements", PROP_BUILDING, 3)}</div>
    <div>{build_info_table("Regulatory &amp; Compliance", PROP_REGULATORY)}</div>
  </div>
</div>
""")

# ============================================================
# OPTIONAL: TRANSACTION HISTORY
# ============================================================
if INCLUDE_TRANSACTION_HISTORY and TRANSACTION_ROWS:
    tx_rows_html = ""
    for tx in TRANSACTION_ROWS:
        tx_rows_html += f'<tr><td>{tx.get("date","")}</td><td>{tx.get("parties","")}</td><td class="num">{fc(tx.get("price",0))}</td><td class="num">{fc(tx.get("ppu",0))}</td><td class="num">{fc(tx.get("psf",0))}</td><td>{tx.get("notes","")}</td></tr>\n'
    html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="transactions">
  <div class="section-title">Transaction History</div>
  <div class="section-subtitle">Ownership &amp; Sale Record</div>
  <div class="section-divider"></div>
  <div class="table-scroll"><table>
    <thead><tr><th>Date</th><th>Grantor / Grantee</th><th class="num">Sale Price</th><th class="num">$/Unit</th><th class="num">$/SF</th><th>Notes</th></tr></thead>
    <tbody>{tx_rows_html}</tbody>
  </table></div>
  <p>{TRANSACTION_NARRATIVE}</p>
</div>
""")

# ============================================================
# PAGE 8: BUYER PROFILE & OBJECTIONS
# ============================================================
buyer_types_html = ""
for btype, desc in BUYER_TYPES:
    buyer_types_html += f'''<div class="obj-item">
        <p class="obj-q">{btype}</p>
        <p class="obj-a">{desc}</p>
    </div>\n'''

buyer_obj_html = ""
for question, answer in BUYER_OBJECTIONS:
    buyer_obj_html += f'''<div class="obj-item">
        <p class="obj-q">"{question}"</p>
        <p class="obj-a">{answer}</p>
    </div>\n'''

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="property-info">
  <div class="section-title">Buyer Profile &amp; Anticipated Objections</div>
  <div class="section-subtitle">Target Investors &amp; Data-Backed Responses</div>
  <div class="section-divider"></div>
  <div class="buyer-split">
    <div class="buyer-split-left">
      <h3 class="sub-heading">Target Buyer Profile</h3>
      {buyer_types_html}
      <p class="bp-closing">{BUYER_CLOSING}</p>
    </div>
    <div class="buyer-split-right">
      <h3 class="sub-heading">Anticipated Buyer Objections</h3>
      {buyer_obj_html}
    </div>
  </div>
  <div class="buyer-photo"><img src="{IMG['buyer_photo']}" alt="Property"></div>
</div>
""")

# ============================================================
# PAGES 9-11: COMP SECTIONS
# ============================================================

# Sale Comps
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="sale-comps">
  <div class="section-title">Comparable Sales</div>
  <div class="section-subtitle">Closed Multifamily Transactions</div>
  <div class="section-divider"></div>
  <div class="leaflet-map" id="saleMap"></div>
  <div class="comp-map-print"><img src="{IMG['sale_map_static']}" alt="Sale Comps Map"></div>
  <div class="table-scroll"><table>
    <thead><tr><th>#</th><th>Address</th><th class="num">Units</th><th>Year</th><th class="num">SF</th><th class="num">Price</th><th class="num">$/Unit</th><th class="num">$/SF</th><th class="num">Cap</th><th class="num">GRM</th><th>Date</th><th class="num">DOM</th></tr></thead>
    <tbody>{sale_comp_html}</tbody>
  </table></div>
  <div class="comp-narratives">
    {COMP_NARRATIVES}
  </div>
</div>
""")

# On-Market Comps (conditional)
if INCLUDE_ON_MARKET_COMPS:
    html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="on-market">
  <div class="section-title">On-Market Comparables</div>
  <div class="section-subtitle">Active Multifamily Listings</div>
  <div class="section-divider"></div>
  <div class="leaflet-map" id="activeMap"></div>
  <div class="comp-map-print"><img src="{IMG.get('active_map_static', '')}" alt="On-Market Comps Map"></div>
  <div class="table-scroll"><table>
    <thead><tr><th>#</th><th>Address</th><th class="num">Units</th><th>Year</th><th class="num">SF</th><th class="num">Price</th><th class="num">$/Unit</th><th class="num">$/SF</th><th class="num">DOM</th><th>Notes</th></tr></thead>
    <tbody>{on_market_html}</tbody>
  </table></div>
  <p>{ON_MARKET_NARRATIVE}</p>
</div>
""")

# Rent Comps
html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section" id="rent-comps">
  <div class="section-title">Rent Comparables</div>
  <div class="section-subtitle">Active Rental Listings in Submarket</div>
  <div class="section-divider"></div>
  <div class="leaflet-map" id="rentMap"></div>
  <div class="comp-map-print"><img src="{IMG['rent_map_static']}" alt="Rent Comps Map"></div>
  <div class="table-scroll"><table>
    <thead><tr><th>#</th><th>Address</th><th>Type</th><th class="num">SF</th><th class="num">Rent</th><th class="num">$/SF</th><th>Source</th></tr></thead>
    <tbody>{rent_comp_html}</tbody>
  </table></div>
</div>
""")

# ============================================================
# PAGE 12: FINANCIAL ANALYSIS — RENT ROLL
# ============================================================
if PROPERTY_TYPE == "value-add":
    rr_header = '<thead><tr><th>Unit</th><th>Type</th><th class="num">SF</th><th class="num">Current</th><th class="num">Scheduled</th><th class="num">Pro Forma (S8)</th></tr></thead>'
else:
    rr_header = '<thead><tr><th>Unit</th><th>Type</th><th class="num">SF</th><th class="num">Rent/Mo</th><th class="num">Rent/SF</th><th>Status</th><th>Notes</th></tr></thead>'

html_parts.append(f"""
<div class="page-break-marker"></div>
<div class="section section-alt" id="financials">
  <div class="section-title">Financial Analysis</div>
  <div class="section-subtitle">Investment Underwriting</div>
  <div class="section-divider"></div>
  <h3 class="sub-heading">Unit Mix &amp; Rent Roll</h3>
  <div class="table-scroll"><table>
    {rr_header}
    <tbody>{rent_roll_html}</tbody>
  </table></div>
""")

# ============================================================
# PAGE 13: OPERATING STATEMENT + NOTES
# ============================================================
html_parts.append(f"""
  <div class="os-two-col">
    <div class="os-left">
      <h3 class="sub-heading">Operating Statement</h3>
      <table>
        <thead><tr><th>Income</th><th class="num">Annual</th><th class="num">Per Unit</th><th class="num">$/SF</th><th class="num">% EGI</th></tr></thead>
        <tbody>{os_income_html}</tbody>
      </table>
      <table>
        <thead><tr><th>Expenses</th><th class="num">Annual</th><th class="num">Per Unit</th><th class="num">$/SF</th><th class="num">% EGI</th></tr></thead>
        <tbody>{os_expense_html}</tbody>
      </table>
    </div>
    <div class="os-right">
      <h3 class="sub-heading">Notes to Operating Statement</h3>
      {os_notes_html}
    </div>
  </div>
""")

# ============================================================
# PAGE 14: FINANCIAL SUMMARY
# ============================================================
m = AT_LIST
down_pct = m["down_payment"] / m["price"] * 100 if m["price"] > 0 else 0

if PROPERTY_TYPE == "value-add":
    returns_label_1, returns_label_2 = "Current", "Pro Forma"
else:
    returns_label_1, returns_label_2 = "Reassessed", ""

html_parts.append(f"""
  <div class="summary-page">
    <div class="summary-banner">Summary</div>
    <div class="summary-two-col">
      <div class="summary-left">
        <table class="summary-table">
          <thead><tr><th colspan="2" class="summary-header">OPERATING DATA</th></tr></thead>
          <tbody>
            <tr><td>Price</td><td class="num">${LIST_PRICE:,}</td></tr>
            <tr><td>Down Payment ({down_pct:.0f}%)</td><td class="num">${m['down_payment']:,.0f}</td></tr>
            <tr><td>Number of Units</td><td class="num">{UNITS}</td></tr>
            <tr><td>Price / Unit</td><td class="num">${m['per_unit']:,.0f}</td></tr>
            <tr><td>Price / SF</td><td class="num">${m['per_sf']:,.0f}</td></tr>
            <tr><td>Gross SF</td><td class="num">{SF:,}</td></tr>
            <tr><td>Lot Size</td><td class="num">{LOT_SF:,} SF ({LOT_ACRES:.2f} ac)</td></tr>
            <tr><td>Year Built</td><td class="num">{YEAR_BUILT}</td></tr>
          </tbody>
        </table>
        <table class="summary-table">
          <thead><tr><th class="summary-header">Returns</th><th class="summary-header num">{returns_label_1}</th>{"<th class='summary-header num'>" + returns_label_2 + "</th>" if returns_label_2 else ""}</tr></thead>
          <tbody>
            <tr><td>Cap Rate</td><td class="num">{m['cur_cap']:.2f}%</td>{"<td class='num'>" + f"{m['pf_cap']:.2f}%" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>GRM</td><td class="num">{m['grm']:.2f}x</td>{"<td class='num'>" + f"{m['pf_grm']:.2f}x" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>Cash-on-Cash</td><td class="num">{m['coc_cur']:.2f}%</td>{"<td class='num'>" + f"{m['coc_pf']:.2f}%" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>DSCR</td><td class="num">{m['dcr_cur']:.2f}x</td>{"<td class='num'>" + f"{m['dcr_pf']:.2f}x" + "</td>" if returns_label_2 else ""}</tr>
          </tbody>
        </table>
        <table class="summary-table">
          <thead><tr><th colspan="2" class="summary-header">FINANCING</th></tr></thead>
          <tbody>
            <tr><td>Loan Amount</td><td class="num">${m['loan_amount']:,.0f}</td></tr>
            <tr><td>Loan Type</td><td class="num">Fixed</td></tr>
            <tr><td>Interest Rate</td><td class="num">{INTEREST_RATE*100:.2f}%</td></tr>
            <tr><td>Amortization</td><td class="num">{AMORTIZATION_YEARS} Years</td></tr>
            <tr><td>Loan Constant</td><td class="num">{LOAN_CONSTANT*100:.2f}%</td></tr>
            <tr><td>LTV ({m['loan_constraint']})</td><td class="num">{m['actual_ltv']*100:.1f}%</td></tr>
            <tr><td>DSCR</td><td class="num">{m['dcr_cur']:.2f}x</td></tr>
          </tbody>
        </table>
      </div>
      <div class="summary-right">
        <table class="summary-table">
          <thead><tr><th class="summary-header">Income</th><th class="summary-header num">{returns_label_1}</th>{"<th class='summary-header num'>" + returns_label_2 + "</th>" if returns_label_2 else ""}</tr></thead>
          <tbody>
            <tr><td>GSR</td><td class="num">${GSR:,}</td>{"<td class='num'>$" + f"{PF_GSR:,}" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>Vacancy ({VACANCY_PCT*100:.0f}%)</td><td class="num">$({GSR*VACANCY_PCT:,.0f})</td>{"<td class='num'>$(" + f"{PF_GSR*VACANCY_PCT:,.0f}" + ")</td>" if returns_label_2 else ""}</tr>
            <tr><td>Other Income</td><td class="num">${OTHER_INCOME:,}</td>{"<td class='num'>$" + f"{OTHER_INCOME:,}" + "</td>" if returns_label_2 else ""}</tr>
            <tr class="summary"><td><strong>EGI</strong></td><td class="num"><strong>${m['cur_egi']:,.0f}</strong></td>{"<td class='num'><strong>$" + f"{m['pf_egi']:,.0f}" + "</strong></td>" if returns_label_2 else ""}</tr>
          </tbody>
        </table>
        <table class="summary-table">
          <thead><tr><th class="summary-header">Cash Flow</th><th class="summary-header num">{returns_label_1}</th>{"<th class='summary-header num'>" + returns_label_2 + "</th>" if returns_label_2 else ""}</tr></thead>
          <tbody>
            <tr><td>NOI</td><td class="num">${m['cur_noi']:,.0f}</td>{"<td class='num'>$" + f"{m['pf_noi']:,.0f}" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>Debt Service</td><td class="num">$({m['debt_service']:,.0f})</td>{"<td class='num'>$(" + f"{m['debt_service']:,.0f}" + ")</td>" if returns_label_2 else ""}</tr>
            <tr class="summary"><td><strong>Net Cash Flow</strong></td><td class="num"><strong>${m['net_cf_cur']:,.0f}</strong></td>{"<td class='num'><strong>$" + f"{m['net_cf_pf']:,.0f}" + "</strong></td>" if returns_label_2 else ""}</tr>
            <tr><td>CoC Return</td><td class="num">{m['coc_cur']:.2f}%</td>{"<td class='num'>" + f"{m['coc_pf']:.2f}%" + "</td>" if returns_label_2 else ""}</tr>
            <tr><td>Principal Reduction</td><td class="num">${m['prin_red']:,.0f}</td>{"<td class='num'>$" + f"{m['prin_red']:,.0f}" + "</td>" if returns_label_2 else ""}</tr>
            <tr class="summary"><td><strong>Total Return</strong></td><td class="num"><strong>{m['total_return_pct_cur']:.2f}%</strong></td>{"<td class='num'><strong>" + f"{m['total_return_pct_pf']:.2f}%" + "</strong></td>" if returns_label_2 else ""}</tr>
          </tbody>
        </table>
        <table class="summary-table">
          <thead><tr><th colspan="2" class="summary-header">EXPENSES</th></tr></thead>
          <tbody>
            {sum_expense_html}
            <tr class="summary"><td><strong>Total Expenses</strong></td><td class="num"><strong>${total_exp_calc:,.0f}</strong></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
""")

# ============================================================
# PAGE 15: PRICE REVEAL + PRICING MATRIX
# ============================================================
if PROPERTY_TYPE == "value-add":
    matrix_header = '<thead><tr><th class="num">Purchase Price</th><th class="num">Current Cap</th><th class="num">Pro Forma Cap</th><th class="num">Cash-on-Cash</th><th class="num">$/SF</th><th class="num">$/Unit</th><th class="num">PF GRM</th></tr></thead>'
else:
    matrix_header = '<thead><tr><th class="num">Purchase Price</th><th class="num">Cap Rate</th><th class="num">Cash-on-Cash</th><th class="num">$/Unit</th><th class="num">$/SF</th><th class="num">GRM</th><th class="num">DSCR</th></tr></thead>'

html_parts.append(f"""
  <div class="price-reveal">
    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-size:13px;text-transform:uppercase;letter-spacing:2px;color:#C5A258;font-weight:600;margin-bottom:8px;">Suggested List Price</div>
      <div style="font-size:56px;font-weight:700;color:#1B3A5C;line-height:1;">${LIST_PRICE:,}</div>
    </div>
    <div class="metrics-grid metrics-grid-4">
      <div class="metric-card"><span class="metric-value">${m['per_unit']:,.0f}</span><span class="metric-label">Price / Unit</span></div>
      <div class="metric-card"><span class="metric-value">${m['per_sf']:,.0f}</span><span class="metric-label">Price / SF</span></div>
      <div class="metric-card"><span class="metric-value">{m['cur_cap']:.2f}%</span><span class="metric-label">Current Cap Rate</span></div>
      <div class="metric-card"><span class="metric-value">{m['grm']:.2f}x</span><span class="metric-label">Current GRM</span></div>
    </div>
    <h3 class="sub-heading">Pricing Matrix</h3>
    <div class="table-scroll"><table>
      {matrix_header}
      <tbody>{matrix_html}</tbody>
    </table></div>
    <div class="summary-trade-range">
      <div class="summary-trade-label">A TRADE PRICE IN THE CURRENT INVESTMENT ENVIRONMENT OF</div>
      <div class="summary-trade-prices">${TRADE_RANGE_LOW:,} &mdash; ${TRADE_RANGE_HIGH:,}</div>
    </div>
    <h3 class="sub-heading">Pricing Rationale</h3>
    <div style="margin-bottom:8px;"><span style="display:inline-block;padding:3px 10px;border-radius:3px;font-size:11px;font-weight:600;letter-spacing:0.5px;color:#fff;background:{'#2E7D32' if COMP_CONFIDENCE == 'HIGH' else '#E65100' if COMP_CONFIDENCE == 'LOW' else '#1565C0'};">{COMP_CONFIDENCE} CONFIDENCE</span> <span style="font-size:11px;color:#666;">Based on comparable sales analysis</span></div>
    <p>{PRICING_RATIONALE}</p>
    <div class="condition-note"><strong>Assumptions &amp; Conditions:</strong> {ASSUMPTIONS_DISCLAIMER}</div>
  </div>
</div>
""")

# ============================================================
# PAGE 16: FOOTER
# ============================================================
footer_agents_html = ""
for agent in FOOTER_AGENTS:
    footer_agents_html += f'''<div class="footer-person">
      <img src="{IMG[agent['img_key']]}" class="footer-headshot" alt="{agent['name']}">
      <div class="footer-name">{agent['name']}</div>
      <div class="footer-title">{agent['title']}</div>
      <div class="footer-contact">
        <a href="tel:{agent['phone']}">{agent['phone']}</a><br>
        <a href="mailto:{agent['email']}">{agent['email']}</a><br>
        CA License: {agent['license']}
      </div>
    </div>\n'''

html_parts.append(f"""
<div class="footer" id="contact">
  <img src="{IMG['logo']}" class="footer-logo" alt="LAAA Team">
  <div class="footer-team">
    {footer_agents_html}
  </div>
  <div class="footer-office">16830 Ventura Blvd, Ste. 100, Encino, CA 91436 | marcusmillichap.com/laaa-team</div>
  <div class="footer-disclaimer">This information has been secured from sources we believe to be reliable, but we make no representations or warranties, expressed or implied, as to the accuracy of the information. Buyer must verify the information and bears all risk for any inaccuracies. Marcus &amp; Millichap Real Estate Investment Services, Inc. | License: CA 01930580.</div>
</div>
""")

# PDF Download Button
html_parts.append(f"""
<a href="{PDF_LINK}" class="pdf-float-btn" id="pdfBtn" target="_blank">
  <svg viewBox="0 0 24 24"><path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M12,19L8,15H10.5V12H13.5V15H16L12,19Z"/></svg>
  Download PDF
</a>
<div id="pdfOverlay" style="display:none;position:fixed;inset:0;background:rgba(27,58,92,0.85);z-index:99999;justify-content:center;align-items:center;flex-direction:column;gap:12px;">
  <div style="width:48px;height:48px;border:4px solid rgba(197,162,88,0.3);border-top-color:#C5A258;border-radius:50%;animation:pdfSpin 0.8s linear infinite;"></div>
  <div style="color:#fff;font-size:20px;font-weight:700;letter-spacing:0.5px;">Generating PDF</div>
  <div style="color:#C5A258;font-size:13px;">This typically takes 15–30 seconds. A new tab will open with your download.</div>
</div>
<style>@keyframes pdfSpin {{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}</style>
""")

# ============================================================
# JAVASCRIPT
# ============================================================
html_parts.append(f"""
<script>
// Client personalization
var params = new URLSearchParams(window.location.search);
var client = params.get('client');
if (client) {{
  var el = document.getElementById('client-greeting');
  if (el) el.textContent = 'Prepared Exclusively for ' + client;
}}

// TOC smooth scroll
document.querySelectorAll('.toc-nav a').forEach(function(link) {{
  link.addEventListener('click', function(e) {{
    e.preventDefault();
    var target = document.querySelector(this.getAttribute('href'));
    if (target) {{
      var navHeight = document.getElementById('toc-nav').offsetHeight;
      window.scrollTo({{ top: target.getBoundingClientRect().top + window.pageYOffset - navHeight - 4, behavior: 'smooth' }});
    }}
  }});
}});

// Active TOC highlighting
var tocLinks = document.querySelectorAll('.toc-nav a');
var tocSections = [];
tocLinks.forEach(function(link) {{
  var section = document.getElementById(link.getAttribute('href').substring(1));
  if (section) tocSections.push({{ link: link, section: section }});
}});
function updateActiveTocLink() {{
  var navHeight = document.getElementById('toc-nav').offsetHeight + 20;
  var scrollPos = window.pageYOffset + navHeight;
  var current = null;
  tocSections.forEach(function(item) {{ if (item.section.offsetTop <= scrollPos) current = item.link; }});
  tocLinks.forEach(function(link) {{ link.classList.remove('toc-active'); }});
  if (current) current.classList.add('toc-active');
}}
window.addEventListener('scroll', updateActiveTocLink);
updateActiveTocLink();

// PDF button loading overlay
var pdfBtn = document.getElementById('pdfBtn');
var pdfOverlay = document.getElementById('pdfOverlay');
if (pdfBtn && pdfOverlay) {{
  pdfBtn.addEventListener('click', function() {{
    pdfOverlay.style.display = 'flex';
    setTimeout(function() {{ pdfOverlay.style.display = 'none'; }}, 8000);
  }});
}}

// Leaflet Maps
{sale_map_js}
{active_map_js}
{rent_map_js}
</script>
</body>
</html>
""")

# ============================================================
# WRITE OUTPUT FILE
# ============================================================
print(f"\nAssembling HTML...")
html = "".join(html_parts)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)
file_size = os.path.getsize(OUTPUT)
print(f"Done! Wrote {OUTPUT}")
print(f"File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
print(f"URL: {BOV_BASE_URL}/?client={urllib.parse.quote(CLIENT_NAME)}")
