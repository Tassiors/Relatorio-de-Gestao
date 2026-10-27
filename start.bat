@echo off
chcp 65001 >nul
echo ==================================================
echo    🚀 Iniciando Aplicação (Produção / Build Local)
echo ==================================================

echo [1/3] Sincronizando dependências do Frontend...
cd frontend
call npm.cmd install

echo [2/3] Gerando build do Frontend...
call npm.cmd run build
cd ..

echo ==================================================
echo ✨ Aplicação pronta!
echo 🔗 Local:  http://localhost:8000
echo 📚 Docs:   http://localhost:8000/docs
echo ==================================================

.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 0.0.0.0 --port 8000
