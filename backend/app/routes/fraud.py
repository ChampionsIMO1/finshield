from fastapi import APIRouter, HTTPException
import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel

router = APIRouter(prefix="/fraud", tags=["fraud"])

model = joblib.load("../ml/models/fraud_model.pkl")
explainer = joblib.load("../ml/models/shap_explainer.pkl")

class TransactionInput(BaseModel):
    amount: float
    time: float
    v1: float
    v2: float
    v3: float
    v4: float
    v5: float
    v6: float
    v7: float
    v8: float
    v9: float
    v10: float
    v11: float
    v12: float
    v13: float
    v14: float
    v15: float
    v16: float
    v17: float
    v18: float
    v19: float
    v20: float
    v21: float
    v22: float
    v23: float
    v24: float
    v25: float
    v26: float
    v27: float
    v28: float

@router.post("/score")
def score_transaction(transaction: TransactionInput):
    try:
        data = pd.DataFrame([transaction.dict()])

        # rename to match training columns
        column_mapping = {'amount': 'Amount', 'time': 'Time'}
        for i in range(1, 29):
            column_mapping[f'v{i}'] = f'V{i}'
        data = data.rename(columns=column_mapping)

        # reorder to match training data
        cols = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        data = data[cols]

        fraud_score = model.predict_proba(data)[0][1]
        shap_vals = explainer.shap_values(data)[0]
        feature_names = data.columns.tolist()
        shap_dict = dict(zip(feature_names, shap_vals))
        top_reasons = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        return {
            "fraud_score": float(fraud_score),
            "is_flagged": bool(fraud_score > 0.5),
            "top_reasons": [{"feature": k, "impact": float(v)} for k, v in top_reasons]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))