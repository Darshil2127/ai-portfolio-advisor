from flask import Blueprint, request, jsonify, current_app, session, redirect, url_for, render_template
import pandas as pd
import os
import uuid # For generating unique session IDs if needed, or use Flask session
from datetime import datetime
from werkzeug.utils import secure_filename

from src.main import db
from src.models.portfolio_holding import PortfolioHolding

upload_bp = Blueprint("upload_bp", __name__)

ALLOWED_EXTENSIONS = {"csv"}

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route("/upload_portfolio", methods=["POST"])
def handle_portfolio_upload():
    if "portfolio_csv" not in request.files:
        # This case should ideally be caught by frontend validation (required field)
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files["portfolio_csv"]

    if file.filename == "":
        return jsonify({"error": "No file selected for upload"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Instead of saving the file permanently, read it into memory with pandas
        # If you need to save, use a temporary location or a dedicated upload folder
        # For now, we process it directly.

        try:
            df = pd.read_csv(file.stream)
        except Exception as e:
            current_app.logger.error(f"Error reading CSV: {e}")
            return jsonify({"error": f"Could not parse CSV file: {e}"}), 400

        # Validate CSV structure (headers)
        required_columns = ["Ticker", "Quantity"]
        optional_columns = ["PurchasePrice", "PurchaseDate"]
        actual_columns = df.columns.tolist()

        for col in required_columns:
            if col not in actual_columns:
                return jsonify({"error": f"Missing required column in CSV: {col}"}), 400

        # Generate a unique session ID for this upload batch if not already in session
        # Flask session is cookie-based and might have size limits for storing large portfolio data directly.
        # Storing a unique ID to link DB entries is better.
        if "upload_session_id" not in session:
            session["upload_session_id"] = str(uuid.uuid4())
        current_upload_session_id = session["upload_session_id"]

        # Clear previous holdings for this session to avoid duplicates if re-uploading
        PortfolioHolding.query.filter_by(session_id=current_upload_session_id).delete()
        db.session.commit() # Commit the deletion

        processed_rows = 0
        error_rows = []

        for index, row in df.iterrows():
            try:
                ticker = str(row["Ticker"])
                quantity = int(row["Quantity"])

                if not ticker or quantity <= 0:
                    error_rows.append({"row": index + 2, "error": "Ticker cannot be empty and Quantity must be positive."})
                    continue

                purchase_price = None
                if "PurchasePrice" in actual_columns and pd.notna(row["PurchasePrice"]):
                    try:
                        purchase_price = float(row["PurchasePrice"])
                        if purchase_price < 0:
                             error_rows.append({"row": index + 2, "field": "PurchasePrice", "error": "PurchasePrice cannot be negative."})
                             continue
                    except ValueError:
                        error_rows.append({"row": index + 2, "field": "PurchasePrice", "error": "Invalid format for PurchasePrice."})
                        continue
                
                purchase_date = None
                if "PurchaseDate" in actual_columns and pd.notna(row["PurchaseDate"]):
                    try:
                        # Attempt to parse various common date formats
                        purchase_date = pd.to_datetime(row["PurchaseDate"]).date()
                    except Exception:
                        error_rows.append({"row": index + 2, "field": "PurchaseDate", "error": "Invalid format for PurchaseDate. Use YYYY-MM-DD."})
                        continue

                holding = PortfolioHolding(
                    session_id=current_upload_session_id,
                    ticker_symbol=ticker.upper(), # Standardize ticker to uppercase
                    quantity=quantity,
                    purchase_price=purchase_price,
                    purchase_date=purchase_date
                )
                db.session.add(holding)
                processed_rows += 1
            except Exception as e:
                current_app.logger.error(f"Error processing row {index + 2}: {e}")
                error_rows.append({"row": index + 2, "error": str(e)})
        
        if error_rows:
            # Rollback if any row has critical error during its own processing, 
            # or decide if partial success is okay.
            # For now, let's commit successful rows and report errors.
            db.session.commit()
            # It might be better to return JSON with errors for client-side handling
            # For now, let's assume we redirect to a page that can display these errors or a summary.
            # This part needs to be aligned with frontend design for error display.
            # return jsonify({"message": f"{processed_rows} rows processed. Errors in {len(error_rows)} rows.", "errors": error_rows}), 400
            # For now, redirecting to dashboard which should handle this. Or a dedicated error display page.
            session["upload_errors"] = error_rows
            session["processed_rows"] = processed_rows
            return redirect(url_for("view_bp.dashboard_page")) # Assuming view_bp is the name of your views blueprint

        db.session.commit()
        session["processed_rows"] = processed_rows
        session.pop("upload_errors", None) # Clear any previous errors
        
        # Redirect to a dashboard or results page after successful processing
        # The dashboard page will then query holdings based on session_id
        return redirect(url_for("view_bp.dashboard_page")) # Assuming view_bp is the name of your views blueprint

    else:
        return jsonify({"error": "Invalid file type. Please upload a CSV file."}), 400

# Example of how a view blueprint might be structured (in a different file e.g. view_routes.py)
# view_bp = Blueprint("view_bp", __name__, template_folder="../../templates")
# @view_bp.route("/dashboard")
# def dashboard_page():
#     # Fetch data based on session["upload_session_id"]
#     # Display results or errors from session["upload_errors"]
#     return render_template("dashboard.html", ...)

