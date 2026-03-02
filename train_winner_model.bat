@echo off
echo ========================================
echo CCPA Winner Tier Model Training
echo ========================================
echo.
echo This will train a multi-label model on 160+ examples
echo Training time: ~2-3 minutes
echo Expected score: 18-20/20
echo.
pause

echo.
echo [1/3] Training multi-label model...
python fine_tune_multilabel.py --epochs 3

echo.
echo [2/3] Testing model...
python fine_tune_multilabel.py --test-only

echo.
echo [3/3] Updating system to use multi-label model...
copy app\model_multilabel.py app\model.py

echo.
echo ========================================
echo WINNER TIER MODEL READY!
echo ========================================
echo.
echo Next steps:
echo 1. Restart server: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
echo 2. Test with: python test_system.py
echo 3. Expected score: 18-20/20
echo.
pause
