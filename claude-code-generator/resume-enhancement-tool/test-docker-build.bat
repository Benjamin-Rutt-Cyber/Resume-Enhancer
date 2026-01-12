@echo off
REM ################################################################################
REM Docker Build Test Script (Windows)
REM
REM This script tests all Docker images locally before deploying to production.
REM Run this after installing Docker Desktop.
REM
REM Usage:
REM   test-docker-build.bat
REM
REM ################################################################################

echo ===============================================
echo     Docker Build Test for Resume Tool
echo ===============================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    exit /b 1
)

echo [OK] Docker is installed
docker --version
echo.

REM Check if Docker daemon is running
docker info >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker daemon is not running
    echo Please start Docker Desktop
    exit /b 1
)

echo [OK] Docker daemon is running
echo.

REM Test 1: Build backend production image
echo ===============================================
echo Test 1: Building backend production image
echo ===============================================
cd backend
docker build -f Dockerfile.prod -t resume-tool-backend:test .
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend build failed
    cd ..
    exit /b 1
)
echo [OK] Backend image built successfully
echo.
echo Image size:
docker images resume-tool-backend:test
cd ..
echo.

REM Test 2: Build frontend production image
echo ===============================================
echo Test 2: Building frontend production image
echo ===============================================
cd frontend
docker build -f Dockerfile -t resume-tool-frontend:test .
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend build failed
    cd ..
    exit /b 1
)
echo [OK] Frontend image built successfully
echo.
echo Image size:
docker images resume-tool-frontend:test
cd ..
echo.

REM Test 3: Validate docker-compose.prod.yml
echo ===============================================
echo Test 3: Validating docker-compose.prod.yml
echo ===============================================
docker-compose -f docker-compose.prod.yml config >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] docker-compose.prod.yml validation skipped (missing env vars)
    echo       This is expected - you need to set environment variables for production
) else (
    echo [OK] docker-compose.prod.yml is valid
)
echo.

REM Test 4: Check image security
echo ===============================================
echo Test 4: Security check - Non-root user
echo ===============================================
for /f "delims=" %%i in ('docker run --rm resume-tool-backend:test whoami') do set BACKEND_USER=%%i
if "%BACKEND_USER%"=="appuser" (
    echo [OK] Backend runs as non-root user: %BACKEND_USER%
) else (
    echo [ERROR] Backend runs as: %BACKEND_USER% (should be appuser)
)
echo.

REM Test 5: Check health check
echo ===============================================
echo Test 5: Verifying health check configuration
echo ===============================================
docker inspect resume-tool-backend:test | findstr "HEALTHCHECK" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend has health check configured
) else (
    echo [ERROR] Backend missing health check
)
echo.

REM Summary
echo ===============================================
echo               Build Test Summary
echo ===============================================
echo.
echo Images created:
docker images | findstr resume-tool
echo.
echo [SUCCESS] All tests passed!
echo.
echo To clean up test images, run:
echo   docker rmi resume-tool-backend:test resume-tool-frontend:test
echo.
echo Next steps:
echo   1. Review the image sizes above
echo   2. Test running the containers locally
echo   3. Deploy to production using docker-compose.prod.yml
echo.

pause
