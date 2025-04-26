@echo off
REM 1) Verifica permissão de admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [Erro] Rode este script como administrador!
    pause
    exit /b 1
)

REM 2) Copia o gs para C:\gs
echo Copiando gs para C:\gs...
xcopy "%~dp0gs" "C:\gs" /E /I /Y >nul
if %errorLevel% neq 0 (
    echo [Erro] Falha ao copiar gs.
    pause
    exit /b 1
)

REM 3) Atualiza PATH do USUARIO (persistente)
echo Atualizando PATH...
setx PATH "C:\gs\bin;%%PATH%%" >nul
if %errorLevel% neq 0 (
    echo [Erro] Falha ao atualizar PATH.
    pause
    exit /b 1
)

echo.
echo Ghostscript instalado e PATH atualizado com sucesso!
echo Feche e reabra o terminal antes de usar gswin64c.exe.
pause
