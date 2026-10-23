@echo off
rem EcoIzge calisma ekranlarini acar (U-02). Cift tiklayarak calisir; tarayici kendiliginden acilir.
rem Kapatmak icin bu pencerede Ctrl+C. Yeniden cift tiklamak eski arayuzu kapatip yenisini acar. Ayrinti: docs/kullanim/ELLE_KONTROL_VE_PILOT.md
rem Onceki bir arayuz hala calisiyorsa kapatilir: guncelleme sonrasi eski kod bellekte kalmasin.
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":8501 .*LISTENING"') do taskkill /PID %%p /F >nul 2>&1
call "%USERPROFILE%\anaconda3\Scripts\activate.bat" "%USERPROFILE%\anaconda3"
call conda activate ecoizge
cd /d "%USERPROFILE%\Documents\ecoizge"
set PYTHONUTF8=1
start "" cmd /c "timeout /t 6 >nul & start http://localhost:8501"
python -m streamlit run services/review-ui/app.py --server.headless true --browser.gatherUsageStats false
pause
