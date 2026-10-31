# LoanGuard v2 merge

- Existing frontend/backend files are preserved.
- `app/ml/loan_model.pkl` is preserved as the v1 backup.
- The 91% model is added as `app/ml/loan_model_v2.pkl` and `model_metrics_v2.json`.
- `app/ml/predict.py` now loads `loan_model_v2.pkl`; its previous version is `predict.py.v1_backup`.
- v2 dataset is stored as `data/LoanGuard_AI_Final_Preprocessed_Dataset_v2.csv`.
- v2 training scripts are isolated under `ml_v2_training/` and are not run by the application.
- Recommendation starter module is under `app/recommendations/` and does not retrain the model.

Next integration step: add Applicant Type (Student/Startup/Investor/Individual) to the application flow and connect the recommendation engine to the result page.
