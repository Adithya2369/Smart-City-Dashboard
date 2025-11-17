import os
from flask import Flask, render_template, abort
import gspread
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
# Set these environment variables before running the app:
#   GOOGLE_SERVICE_ACCOUNT_FILE -> path to your service account JSON file
#   SPREADSHEET_ID -> Google Sheets spreadsheet ID (the part in the URL)
# SERVICE_ACCOUNT_FILE = os.environ.get("A:\IoT Project\gen-lang-client-0435223473-de01b16436aa.json", "service_account.json")
# SPREADSHEET_ID = os.environ.get("1YcOCAYOuccyOocXShAvT6EAQ0MaIJ1xJVu36_NmESFE", None)


SERVICE_ACCOUNT_FILE = "gen-lang-client-0435223473-de01b16436aa.json"
SPREADSHEET_ID = "1YcOCAYOuccyOocXShAvT6EAQ0MaIJ1xJVu36_NmESFE"


if SPREADSHEET_ID is None:
    raise RuntimeError("Please set the SPREADSHEET_ID environment variable to your Google Sheets ID.")

# Sheet names (exact names inside the spreadsheet)
SHEET_NAMES = {
    "weather": "Weather",
    "noise": "Noise",
    "waste": "Waste",
    "air": "AirQuality",
    "complaints": "Complaints"
}

# --- SETUP ---
app = Flask(__name__, static_folder="static", template_folder="templates")

# Initialize gspread client
try:
    # gspread.service_account will use the JSON file you provide
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_key(SPREADSHEET_ID)
except Exception as e:
    # If service account file not found or auth error, fail early but give helpful message
    raise RuntimeError(
        "Failed to initialize Google Sheets client. "
        "Make sure GOOGLE_SERVICE_ACCOUNT_FILE points to a valid service account JSON and "
        "SPREADSHEET_ID is correct. Underlying error: " + str(e)
    )

# --- HELPERS ---
def get_sheet_records(sheet_name):
    """
    Returns a list of dict records from the given worksheet.
    """
    try:
        worksheet = sh.worksheet(sheet_name)
    except Exception:
        # worksheet might not exist
        return None
    records = worksheet.get_all_records(empty2zero=False, head=1)
    return records

def get_live_row_from_records(records):
    """Given get_all_records() output, return last row (or None if empty)."""
    if not records:
        return None
    return records[-1]

def records_to_dataframe(records):
    """Convert records (list of dicts) to pandas DataFrame (safe for templates)."""
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)

# --- ROUTES ---
@app.route("/")
def home():
    """Landing page / home.html"""
    # Optionally show last-updated timestamps for each module
    module_updates = {}
    for key, sheet in SHEET_NAMES.items():
        records = get_sheet_records(sheet)
        if records:
            last = get_live_row_from_records(records)
            # try to extract timestamp column if exists
            ts = None
            for candidate in ("Timestamp", "Time", "timestamp", "time"):
                if isinstance(last, dict) and candidate in last:
                    ts = last[candidate]
                    break
            module_updates[key] = ts or "N/A"
        else:
            module_updates[key] = "No data"
    return render_template("home.html", updates=module_updates)

# ---------- WEATHER ----------
@app.route("/weather/live")
def weather_live():
    records = get_sheet_records(SHEET_NAMES["weather"])
    if records is None:
        abort(404, description="Weather sheet not found.")
    last = get_live_row_from_records(records)
    df = records_to_dataframe(records)
    # get last N rows for charts (if available)
    N = 20
    history_rows = df.tail(N).to_dict(orient="records") if not df.empty else []
    # send columns order to template if needed
    columns = list(df.columns) if not df.empty else []
    return render_template("weather_live.html", live=last, history=history_rows, columns=columns)


@app.route("/weather/history")
def weather_history():
    records = get_sheet_records(SHEET_NAMES["weather"])
    if records is None:
        abort(404, description="Weather sheet not found.")
    df = records_to_dataframe(records)
    # convert DataFrame to records for table rendering
    rows = df.to_dict(orient="records")
    columns = list(df.columns)
    return render_template("history.html", module="Weather", columns=columns, rows=rows)

# ---------- NOISE ----------
@app.route("/noise/live")
def noise_live():
    records = get_sheet_records(SHEET_NAMES["noise"])
    if records is None:
        abort(404, description="Noise sheet not found.")
    last = get_live_row_from_records(records)
    df = records_to_dataframe(records)
    N = 20
    history_rows = df.tail(N).to_dict(orient="records") if not df.empty else []
    columns = list(df.columns) if not df.empty else []
    return render_template("generic_live_table.html", title="Noise - Live", live=last, history=history_rows, columns=columns)

@app.route("/noise/history")
def noise_history():
    records = get_sheet_records(SHEET_NAMES["noise"])
    if records is None:
        abort(404, description="Noise sheet not found.")
    df = records_to_dataframe(records)
    columns = list(df.columns)
    rows = df.to_dict(orient="records")
    return render_template("history.html", module="Noise Compliance", columns=columns, rows=rows)

# ---------- WASTE ----------
@app.route("/waste/live")
def waste_live():
    records = get_sheet_records(SHEET_NAMES["waste"])
    if records is None:
        abort(404, description="Waste sheet not found.")
    last = get_live_row_from_records(records)
    df = records_to_dataframe(records)
    N = 20
    history_rows = df.tail(N).to_dict(orient="records") if not df.empty else []
    columns = list(df.columns) if not df.empty else []
    return render_template("generic_live_table.html", title="Waste - Live", live=last, history=history_rows, columns=columns)

@app.route("/waste/history")
def waste_history():
    records = get_sheet_records(SHEET_NAMES["waste"])
    if records is None:
        abort(404, description="Waste sheet not found.")
    df = records_to_dataframe(records)
    columns = list(df.columns)
    rows = df.to_dict(orient="records")
    return render_template("history.html", module="Waste Management", columns=columns, rows=rows)

# ---------- AIR QUALITY ----------
@app.route("/air/live")
def air_live():
    records = get_sheet_records(SHEET_NAMES["air"])
    if records is None:
        abort(404, description="AirQuality sheet not found.")
    last = get_live_row_from_records(records)
    df = records_to_dataframe(records)
    N = 20
    history_rows = df.tail(N).to_dict(orient="records") if not df.empty else []
    columns = list(df.columns) if not df.empty else []
    return render_template("air_live.html", live=last, history=history_rows, columns=columns)

@app.route("/air/history")
def air_history():
    records = get_sheet_records(SHEET_NAMES["air"])
    if records is None:
        abort(404, description="AirQuality sheet not found.")
    df = records_to_dataframe(records)
    columns = list(df.columns)
    rows = df.to_dict(orient="records")
    return render_template("history.html", module="Air Quality", columns=columns, rows=rows)

# ---------- COMPLAINTS ----------
@app.route("/complaints")
def complaints():
    # For now this is "coming soon" as you requested
    records = get_sheet_records(SHEET_NAMES["complaints"])
    # We won't display the data now, just show coming soon. But include a count if available.
    count = len(records) if records else 0
    return render_template("complaints.html", count=count)

# ---------- ERROR HANDLING ----------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", message=str(e)), 404

# ---------- MAIN ----------
if __name__ == "__main__":
    # Debug true for development. In production, use a WSGI server.
    app.run(host="0.0.0.0", port=5000, debug=True)
