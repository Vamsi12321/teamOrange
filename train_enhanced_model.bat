@echo off
echo ================================================================================
echo TRAINING ENHANCED CCPA MODEL - 6600+ Examples
echo ================================================================================
echo.
echo This will:
echo   1. Generate 6600+ training examples (3000+ more than before)
echo   2. Focus on reducing false positives
echo   3. Include contrast pairs, realistic safe examples, questions
echo   4. Train for 5 epochs (~90-120 minutes)
echo.
echo Enhancements:
echo   - Contrast pairs (same keywords, different outcomes)
echo   - Realistic business practices (complex safe examples)
echo   - Questions/hypotheticals (NOT violations)
echo   - Security statements (NOT CCPA violations)
echo   - Neutral collection statements (compliant practices)
echo.
echo ================================================================================
pause

echo.
echo [1/3] Generating enhanced training data (6600+ examples)...
python generate_training_data.py

if errorlevel 1 (
    echo ERROR: Failed to generate training data
    pause
    exit /b 1
)

echo.
echo [2/3] Training multi-label model (5 epochs, ~90-120 minutes)...
echo.
python train_2k_model.py --data ccpa_training_data_6600.json --epochs 5 --output ./ccpa_model_multilabel_enhanced

if errorlevel 1 (
    echo ERROR: Training failed
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo [3/3] TRAINING COMPLETE!
echo ================================================================================
echo.
echo Model saved to: ./ccpa_model_multilabel_enhanced
echo.
echo NEXT STEPS:
echo   1. Update app/model.py to load the new model:
echo      - Change model path from "./ccpa_model_multilabel" to "./ccpa_model_multilabel_enhanced"
echo.
echo   2. Restart server:
echo      python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo   3. Test with examples that were giving false positives
echo.
echo EXPECTED IMPROVEMENTS:
echo   - Fewer false positives (safe sentences predicted as harmful)
echo   - Better understanding of context (keywords alone don't mean violation)
echo   - Improved accuracy on edge cases
echo   - More balanced predictions
echo.
echo ================================================================================
pause
