@echo off
title CineMatch Movie Recommender
cd /d "%~dp0"
echo ========================================================
echo   Launching CineMatch Movie Recommendation System...
echo ========================================================
echo.
streamlit run app.py
pause
