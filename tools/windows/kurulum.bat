@echo off
rem EcoIzge kurulumu ya da guncellemesi (U-01). Cift tiklayarak calisir.
rem Anaconda ortami "ecoizge" (conda-forge: python 3.11, git, poppler); depo %USERPROFILE%\Documents\ecoizge.
rem Gunluk: bu dosyanin yanindaki kurulum.log; ozet: sonuc.txt. Ayrinti: docs/kullanim/ELLE_KONTROL_VE_PILOT.md
setlocal
set "KUR=%~dp0"
set "LOG=%KUR%kurulum.log"
echo Kurulum basladi. Bu pencereyi kapatma; bitince kendisi yazar. Gunluk: %LOG%
call :ana > "%LOG%" 2>&1
echo.
type "%KUR%sonuc.txt"
echo.
echo Bu pencereyi kapatabilirsin.
pause
exit /b

:ana
echo === %DATE% %TIME% basladi
set "CONDA=%USERPROFILE%\anaconda3"
if not exist "%CONDA%\Scripts\activate.bat" (
  echo HATA: Anaconda bulunamadi: %CONDA%
  echo SONUC: HATA anaconda yok> "%KUR%sonuc.txt"
  exit /b 1
)
call "%CONDA%\Scripts\activate.bat" "%CONDA%"
call conda --version
call conda env list | findstr /R /C:"^ecoizge " >nul
if errorlevel 1 (
  echo === ortam olusturuluyor
  call conda create -n ecoizge -c conda-forge --override-channels python=3.11 git poppler -y
  if errorlevel 1 ( echo SONUC: HATA conda create> "%KUR%sonuc.txt" & exit /b 1 )
) else (
  echo === ortam zaten var
)
call conda activate ecoizge
if errorlevel 1 ( echo SONUC: HATA conda activate> "%KUR%sonuc.txt" & exit /b 1 )
python --version
git --version
cd /d "%USERPROFILE%\Documents"
if not exist "ecoizge\.git" (
  echo === depo indiriliyor
  git clone https://github.com/MevoTech/ecoizge
  if errorlevel 1 ( echo SONUC: HATA git clone> "%KUR%sonuc.txt" & exit /b 1 )
) else (
  echo === depo var, guncelleniyor
  git -C ecoizge pull --ff-only
)
cd /d "%USERPROFILE%\Documents\ecoizge"
git log --oneline -3
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
if errorlevel 1 ( echo SONUC: HATA pip install> "%KUR%sonuc.txt" & exit /b 1 )
set PYTHONUTF8=1
echo === kalite kapisi
python tools/check_all.py
set "KAPI=%ERRORLEVEL%"
echo === kalite kapisi cikis kodu %KAPI%
if "%KAPI%"=="0" ( echo SONUC: TAMAM kurulum bitti, kalite kapisi 6/6> "%KUR%sonuc.txt" ) else ( echo SONUC: KISMI kurulum bitti, kalite kapisinda hata var - Claude'a haber ver> "%KUR%sonuc.txt" )
echo === %DATE% %TIME% bitti
exit /b 0
