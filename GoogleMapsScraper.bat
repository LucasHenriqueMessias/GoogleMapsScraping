@echo off
title Google Maps Scraper - Busca de Estabelecimentos
cd /d "%~dp0"

REM Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERRO: Python não encontrado!
    echo.
    echo 📥 Por favor, instale o Python 3.8+ em:
    echo    https://www.python.org/downloads/
    echo.
    echo ⚠️  Lembre-se de marcar "Add Python to PATH" durante a instalação
    echo.
    pause
    exit /b 1
)

REM Verifica se as bibliotecas estão instaladas
echo 📦 Verificando dependências...
python -c "import requests, pandas, openpyxl" 2>nul
if errorlevel 1 (
    echo.
    echo 📥 Instalando bibliotecas necessárias...
    echo.
    pip install requests pandas openpyxl
    if errorlevel 1 (
        echo.
        echo ❌ Erro ao instalar bibliotecas!
        echo 💡 Tente executar como administrador
        echo.
        pause
        exit /b 1
    )
)

REM Executa o script
echo.
echo ✅ Dependências OK! Iniciando programa...
echo.
timeout /t 2 /nobreak >nul

python GoogleMapsScraper_Interactive.py

REM Pausa no final para ver resultados
echo.
pause
