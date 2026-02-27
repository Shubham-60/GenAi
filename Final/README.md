# Diabetes Predictor (Streamlit UI)

## Setup

1. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

2. Export model artifacts (from project root)

   ```bash
   python Research/Final-\(model\)/export_model.py
   ```

   This creates:
   - `Final/models/lr_model.pkl`
   - `Final/models/scaler.pkl`
   - `Final/models/model_metadata.json`

3. Run app

   ```bash
   streamlit run streamlit_app.py
   ```

## Notes

- Inference uses feature order from `model_metadata.json`.
- Age entered in years is converted to BRFSS age category (1-13) before inference.
- Default classification threshold is `0.58`.
