@echo off
rem EcoIzge calisma ekranlarini acar (U-02). Cift tiklayarak calisir; tarayici kendiliginden acilir.
rem Kapatmak icin bu pencerede Ctrl+C. Ayrinti: docs/kullanim/ELLE_KONTROL_VE_PILOT.md
call "%USERPROFILE%\anaconda3\Scripts\activate.bat" "%USERPROFILE%\anaconda3"
call conda activate ecoizge
cd /d "%USERPROFILE%\Documents\ecoizge"
set PYTHONUTF8=1
start "" cmd /c "timeout /t 6 >nul & start http://localhost:8501"
python -m streamlit run services/review-ui/app.py --server.headless true --browser.gatherUsageStats false
pause
