"""
routes.py — Tier 2 (Application Layer)

All Flask routes.  Weather data is loaded once at startup using MyModule's
csv_fetcher, then each request runs analysis through data_analyzer and logs
the query to the SQLite database (Tier 3) via the QueryLog model.
"""

import io
import os
import sys
import base64
import logging

import matplotlib
matplotlib.use("Agg")           # Non-interactive backend — required for servers
import matplotlib.pyplot as plt
import pandas as pd
from flask import Blueprint, render_template, request, abort

# MyModule lives in the project root, so add it to the path before importing.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import MyModule as my  # noqa: E402
from .models import db, QueryLog  # noqa: E402

main = Blueprint("main", __name__)
logger = logging.getLogger(__name__)

# ── Load weather data once at startup ─────────────────────────────────────────
_DATA_PATH = os.path.join(ROOT, "data", "Weather Training Data.csv")
try:
    _df: pd.DataFrame = my.csv_fetcher(_DATA_PATH).fetch()
    logger.info("Weather data loaded: %d rows, %d columns", *_df.shape)
except Exception as exc:
    logger.error("Failed to load weather data: %s", exc)
    _df = pd.DataFrame()   # Empty fallback so the app still starts

_analyzer = my.data_analyzer(_df)

# Pre-compute dropdown options once
_NUM_COLUMNS  = list(_df.select_dtypes(include="number").columns)
_ALL_COLUMNS  = list(_df.columns)
_LOCATIONS    = (
    sorted(_df["Location"].dropna().unique().tolist())
    if "Location" in _df.columns else []
)
_PREDICTOR_SOURCE_FEATURES = [
    column
    for column in [
        "MinTemp",
        "Rainfall",
        "WindGustSpeed",
        "WindSpeed9am",
        "WindSpeed3pm",
        "Humidity9am",
        "Humidity3pm",
        "Pressure9am",
        "Pressure3pm",
        "Cloud9am",
        "Cloud3pm",
        "Temp9am",
        "Temp3pm",
        "MaxTemp",
    ]
    if column in _df.columns
]
_predictor = my.Predictor(_df, model=None) if not _df.empty else None


# ── Helper ─────────────────────────────────────────────────────────────────────
def _fig_to_b64(fig) -> str:
    """Save a Matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def _get_trained_predictor():
    """Train the scikit-learn predictor on first use and reuse it afterwards."""
    if _predictor is None:
        raise ValueError("Weather data is not available for prediction.")

    if _predictor.model is None:
        _predictor.train_sklearn_max_temp_model(
            feature_columns=[column for column in _PREDICTOR_SOURCE_FEATURES if column != "MaxTemp"],
            target_column="MaxTemp",
            group_column="Location",
            sort_columns=None,
        )
    return _predictor


# ── Routes ─────────────────────────────────────────────────────────────────────

@main.route("/")
def index():
    """Home page — show the analysis form (Tier 1 entry point)."""
    return render_template(
        "index.html",
        columns=_NUM_COLUMNS,
        all_columns=_ALL_COLUMNS,
        locations=_LOCATIONS,
    )


@main.route("/analyze", methods=["POST"])
def analyze():
    """
    Receive form submission, run analysis via data_analyzer (Tier 2),
    persist the query in SQLite (Tier 3), and render results (Tier 1).
    """
    analysis_type = request.form.get("analysis_type", "describe")
    column        = request.form.get("column", "")
    second_column = request.form.get("second_column", "").strip()
    location      = request.form.get("location", "").strip() or None
    predicted_max_temp = None
    predictor_features = None

    # ── Input validation ──────────────────────────────────────────────────────
    if analysis_type == "predict_max_temp":
        column = "MaxTemp"
        second_column = ""
        if not location:
            abort(400, description="Select a location to predict tomorrow's max temperature.")
        if location not in _LOCATIONS:
            abort(400, description=f"Location '{location}' does not exist in the dataset.")
    elif column not in _ALL_COLUMNS:
        abort(400, description=f"Column '{column}' does not exist in the dataset.")

    if analysis_type == "scatter" and second_column not in _ALL_COLUMNS:
        abort(400, description=f"Second column '{second_column}' does not exist in the dataset.")

    # ── Persist query to SQLite ───────────────────────────────────────────────
    entry = QueryLog(
        analysis_type=analysis_type,
        column_name=column,
        second_column=second_column if second_column else None,
        location_filter=location,
    )
    db.session.add(entry)
    db.session.commit()

    # ── Run analysis ──────────────────────────────────────────────────────────
    chart_b64    = None
    stats_html   = None
    missing_total = None

    try:
        if analysis_type == "describe":
            stats = _df[column].describe()
            stats_html = stats.to_frame().to_html(classes="stats-table")

        elif analysis_type == "missing":
            missing_series = _df.isnull().sum()
            missing_total  = int(missing_series.sum())
            stats_html = (
                missing_series
                .to_frame(name="Missing Values")
                .to_html(classes="stats-table")
            )

        elif analysis_type == "histogram":
            df_plot = _df[_df["Location"] == location] if location else _df
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(df_plot[column].dropna(), bins=20, edgecolor="black", color="#4a90d9")
            ax.set_title(
                f"Histogram of {column}" + (f"  —  {location}" if location else ""),
                fontsize=14,
            )
            ax.set_xlabel(column)
            ax.set_ylabel("Frequency")
            ax.grid(axis="y", alpha=0.6)
            plt.tight_layout()
            chart_b64 = _fig_to_b64(fig)

        elif analysis_type == "scatter":
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.scatter(_df[column], _df[second_column], alpha=0.35, color="#4a90d9", s=10)
            ax.set_title(f"{column}  vs  {second_column}", fontsize=14)
            ax.set_xlabel(column)
            ax.set_ylabel(second_column)
            ax.grid(True, alpha=0.4)
            plt.tight_layout()
            chart_b64 = _fig_to_b64(fig)

        elif analysis_type == "bar":
            if "Location" not in _df.columns:
                abort(400, description="Dataset has no 'Location' column.")
            totals = _df.groupby("Location")[column].sum().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(13, 5))
            ax.bar(totals.index, totals.values, color="#4a90d9", edgecolor="white")
            ax.set_title(f"Total  {column}  by Location", fontsize=14)
            ax.set_xlabel("Location")
            ax.set_ylabel(f"Total {column}")
            ax.grid(axis="y", alpha=0.6)
            plt.xticks(rotation=75, ha="right")
            plt.tight_layout()
            chart_b64 = _fig_to_b64(fig)

        elif analysis_type == "predict_max_temp":
            predictor = _get_trained_predictor()
            prediction_input = predictor.build_tomorrow_prediction_input(
                feature_columns=_PREDICTOR_SOURCE_FEATURES,
                location=location,
                group_column="Location",
                sort_columns=None,
            )
            prediction_frame = prediction_input[predictor.training_feature_columns_]
            predicted_max_temp = float(predictor.predict_max_temp_tomorrow(prediction_frame)[0])
            predictor_features = predictor.training_feature_columns_

    except ValueError as exc:
        abort(400, description=str(exc))

    return render_template(
        "results.html",
        analysis_type=analysis_type,
        column=column,
        second_column=second_column,
        location=location,
        stats_html=stats_html,
        missing_total=missing_total,
        chart_b64=chart_b64,
        predicted_max_temp=predicted_max_temp,
        predictor_features=predictor_features,
    )


@main.route("/history")
def history():
    """Query history page — reads all past queries from SQLite (Tier 3)."""
    entries = QueryLog.query.order_by(QueryLog.timestamp.desc()).all()
    return render_template("history.html", entries=entries)


# ── Error handlers ─────────────────────────────────────────────────────────────

@main.app_errorhandler(400)
def bad_request(exc):
    return render_template("error.html", code=400, message=exc.description), 400


@main.app_errorhandler(404)
def not_found(exc):
    return render_template("error.html", code=404, message="Page not found."), 404


@main.app_errorhandler(500)
def server_error(exc):
    return render_template("error.html", code=500, message="An internal server error occurred."), 500
