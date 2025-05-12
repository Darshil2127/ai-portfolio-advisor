from flask import Blueprint, render_template, session, redirect, url_for, current_app
from src.models.portfolio_holding import PortfolioHolding
from src.main import db 
from src.data_services.data_aggregator import DataAggregator # Added
from src.ai_engine.main_analyzer import MainAnalyzer # Added

view_bp = Blueprint("view_bp", __name__, template_folder="../templates")

@view_bp.route("/")
def index_page():
    """Serves the main page, which is the portfolio upload page."""
    session.pop("upload_session_id", None)
    session.pop("upload_errors", None)
    session.pop("processed_rows", None)
    session.pop("recommendations", None) # Clear previous recommendations
    current_app.logger.info("Session cleared for new upload.")
    return render_template("index.html")

@view_bp.route("/dashboard")
def dashboard_page():
    """Serves the dashboard page to display analysis results or upload errors."""
    upload_session_id = session.get("upload_session_id")
    upload_errors = session.get("upload_errors", [])
    processed_rows = session.get("processed_rows", 0)
    recommendations = session.get("recommendations") # Try to get recommendations from session first

    current_app.logger.info(f"Dashboard accessed for session: {upload_session_id}")
    current_app.logger.info(f"Upload errors from session: {upload_errors}")
    current_app.logger.info(f"Processed rows from session: {processed_rows}")

    holdings = []
    # Only proceed to fetch holdings and run analysis if there was a valid upload session
    # and no critical errors during the upload itself that prevented data storage.
    if upload_session_id and not upload_errors: 
        holdings = PortfolioHolding.query.filter_by(session_id=upload_session_id).all()
        current_app.logger.info(f"Fetched {len(holdings)} holdings from DB for session {upload_session_id}")

        if holdings and recommendations is None: # Analyze only if holdings exist and no recommendations yet in session
            current_app.logger.info(f"No recommendations in session for {upload_session_id}, proceeding to generate.")
            try:
                data_aggregator = DataAggregator()
                aggregated_data = data_aggregator.get_aggregated_data_for_holdings(holdings)
                current_app.logger.info(f"Data aggregation complete for {len(aggregated_data)} items.")

                if aggregated_data:
                    ai_analyzer = MainAnalyzer()
                    recommendations = ai_analyzer.analyze_portfolio_holdings(aggregated_data)
                    session["recommendations"] = recommendations # Store recommendations in session
                    current_app.logger.info(f"AI analysis complete. Generated {len(recommendations)} recommendations.")
                else:
                    current_app.logger.warning("Aggregated data was empty, no AI analysis performed.")
                    recommendations = [] # Ensure recommendations is an empty list
            except Exception as e:
                current_app.logger.error(f"Error during data aggregation or AI analysis: {e}", exc_info=True)
                # Add an error to display on the dashboard
                upload_errors.append({"row": "N/A", "error": f"System error during analysis: {str(e)}"})
                recommendations = [] # Ensure recommendations is an empty list on error
        elif recommendations is not None:
            current_app.logger.info(f"Using existing recommendations from session for {upload_session_id}")
        elif not holdings:
             current_app.logger.info(f"No holdings found for session {upload_session_id}, skipping analysis.")
             recommendations = []
    elif not upload_session_id:
        current_app.logger.info("No upload session ID found, cannot display holdings or recommendations.")
        recommendations = []
    else: # upload_errors exist
        current_app.logger.info(f"Upload errors present for session {upload_session_id}, skipping analysis.")
        recommendations = []

    return render_template("dashboard.html", 
                           holdings=holdings, 
                           errors=upload_errors, 
                           processed_rows=processed_rows,
                           recommendations=recommendations if recommendations is not None else [],
                           has_results=bool(holdings or upload_errors or processed_rows > 0 or recommendations))

