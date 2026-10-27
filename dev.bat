@echo off
chcp 65001 >nul
echo ==================================================
echo    🛠️  Modo Desenvolvimento: Portal de Relatórios
echo ==================================================

echo [1/3] Verificando ambiente Python...
if not exist ".venv" (
    echo Criando ambiente virtual...
    python -m venv .venv
)

echo [2/3] Sincronizando Frontend (Node.js)...
cd frontend
call npm.cmd install
cd ..

echo ==================================================
echo 🚀 Iniciando servidores em paralelo...
echo 📡 Backend:  http://127.0.0.1:8000 (API & Docs: /docs)
echo 🎨 Frontend: http://localhost:5173 (Vite Dev Server)
echo ==================================================

start "Backend FastAPI (Porta 8000)" cmd /k ".\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload"
cd frontend
call npm.cmd run dev -- --port 5173
