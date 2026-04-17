from flask import Flask, render_template, request
import joblib
import pandas as pd
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR) if os.path.basename(BASE_DIR) == "app" else BASE_DIR
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

# Load models
diabetes_model = joblib.load(os.path.join(MODELS_DIR, "diabetes_model.joblib"))
heart_model = joblib.load(os.path.join(MODELS_DIR, "heart_model.joblib"))
kidney_model = joblib.load(os.path.join(MODELS_DIR, "kidney_model.joblib"))

# Load feature columns
heart_feature_columns = joblib.load(os.path.join(MODELS_DIR, "heart_feature_columns.joblib"))
kidney_feature_columns = joblib.load(os.path.join(MODELS_DIR, "kidney_feature_columns.joblib"))

# Optional diabetes columns
diabetes_feature_columns_path = os.path.join(MODELS_DIR, "diabetes_feature_columns.joblib")
diabetes_feature_columns = joblib.load(diabetes_feature_columns_path) if os.path.exists(diabetes_feature_columns_path) else None


def safe_float(value, default=0):
    try:
        return float(value)
    except:
        return default


def build_base_input(form):
    base = {
        "AGE": safe_float(form.get("age")),
        "HEALTHCARE_EXPENSES": safe_float(form.get("healthcare_expenses")),
        "HEALTHCARE_COVERAGE": safe_float(form.get("healthcare_coverage")),
        "glucose": safe_float(form.get("glucose")),
        "bmi": safe_float(form.get("bmi")),
        "systolic_bp": safe_float(form.get("systolic_bp")),
        "diastolic_bp": safe_float(form.get("diastolic_bp")),
        "hba1c": safe_float(form.get("hba1c")),
        "GENDER_M": 1 if form.get("gender") == "M" else 0,
        "MARITAL_M": 1 if form.get("marital") == "M" else 0,
    }

    # Safe fill for missing encoded cols
    for col in [
        "race_white", "race_black", "race_native", "race_other",
        "ethnicity_hispanic", "ethnicity_nonhispanic"
    ]:
        base[col] = 0

    return base


def align_features(input_data, feature_columns):
    df = pd.DataFrame([input_data])
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    return df[feature_columns]


def get_specialist(model):
    return {
        "diabetes": "Endocrinologist",
        "heart": "Cardiologist",
        "kidney": "Nephrologist"
    }.get(model, "General Physician")


def get_hospitals(location, model):
    specialist = get_specialist(model)
    if not location:
        return ["Enter location to find hospitals."]
    return [
        f"Location: {location}",
        f"Recommended: {specialist}",
        "Nearby hospital API coming next"
    ]


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    risk_label = None
    active_tab = "diabetes"
    specialist = None
    hospital_results = []
    location = ""
    error_message = None

    if request.method == "POST":
        try:
            active_tab = request.form.get("model_type", "diabetes")
            print("Selected model:", active_tab)

            location = request.form.get("location", "")
            base_input = build_base_input(request.form)

            if active_tab == "diabetes":
                if diabetes_feature_columns:
                    df = align_features(base_input, diabetes_feature_columns)
                else:
                    df = pd.DataFrame([{
                        "AGE": base_input["AGE"],
                        "HEALTHCARE_EXPENSES": base_input["HEALTHCARE_EXPENSES"],
                        "HEALTHCARE_COVERAGE": base_input["HEALTHCARE_COVERAGE"],
                        "glucose": base_input["glucose"],
                        "bmi": base_input["bmi"],
                        "systolic_bp": base_input["systolic_bp"],
                        "diastolic_bp": base_input["diastolic_bp"],
                        "hba1c": base_input["hba1c"],
                    }])
                model = diabetes_model

            elif active_tab == "heart":
                df = align_features(base_input, heart_feature_columns)
                model = heart_model

            elif active_tab == "kidney":
                df = align_features(base_input, kidney_feature_columns)
                model = kidney_model

            prediction = model.predict(df)[0]
            probability = model.predict_proba(df)[0][1] if hasattr(model, "predict_proba") else None

            risk_label = "High Risk" if prediction == 1 else "Low Risk"
            specialist = get_specialist(active_tab)
            hospital_results = get_hospitals(location, active_tab)

            result = {
                "prediction": int(prediction),
                "probability": round(probability * 100, 2) if probability else None,
                "model_type": active_tab
            }

        except Exception as e:
            error_message = str(e)

    return render_template(
        "index.html",
        result=result,
        risk_label=risk_label,
        active_tab=active_tab,
        specialist=specialist,
        hospital_results=hospital_results,
        location=location,
        error_message=error_message
    )


if __name__ == "__main__":
    app.run(debug=True)
    