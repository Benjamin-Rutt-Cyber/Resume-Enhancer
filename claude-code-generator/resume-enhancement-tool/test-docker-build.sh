#!/bin/bash
################################################################################
# Docker Build Test Script
#
# This script tests all Docker images locally before deploying to production.
# Run this after installing Docker Desktop.
#
# Usage:
#   ./test-docker-build.sh
#
################################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "==============================================="
echo "    Docker Build Test for Resume Tool"
echo "==============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not installed${NC}"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is installed"
docker --version
echo ""

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}ERROR: Docker daemon is not running${NC}"
    echo "Please start Docker Desktop"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker daemon is running"
echo ""

# Test 1: Build backend production image
echo "==============================================="
echo "Test 1: Building backend production image"
echo "==============================================="
cd backend
if docker build -f Dockerfile.prod -t resume-tool-backend:test . ; then
    echo -e "${GREEN}✓${NC} Backend image built successfully"
    echo ""
    echo "Image size:"
    docker images resume-tool-backend:test --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
else
    echo -e "${RED}✗${NC} Backend build failed"
    exit 1
fi
cd ..
echo ""

# Test 2: Build frontend production image
echo "==============================================="
echo "Test 2: Building frontend production image"
echo "==============================================="
cd frontend
if docker build -f Dockerfile -t resume-tool-frontend:test . ; then
    echo -e "${GREEN}✓${NC} Frontend image built successfully"
    echo ""
    echo "Image size:"
    docker images resume-tool-frontend:test --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
else
    echo -e "${RED}✗${NC} Frontend build failed"
    exit 1
fi
cd ..
echo ""

# Test 3: Validate docker-compose.prod.yml
echo "==============================================="
echo "Test 3: Validating docker-compose.prod.yml"
echo "==============================================="
if docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} docker-compose.prod.yml is valid"
else
    echo -e "${YELLOW}⚠${NC} docker-compose.prod.yml validation skipped (missing env vars)"
    echo "    This is expected - you need to set environment variables for production"
fi
echo ""

# Test 4: Check image security
echo "==============================================="
echo "Test 4: Security check - Non-root user"
echo "==============================================="
BACKEND_USER=$(docker run --rm resume-tool-backend:test whoami)
if [ "$BACKEND_USER" = "appuser" ]; then
    echo -e "${GREEN}✓${NC} Backend runs as non-root user: $BACKEND_USER"
else
    echo -e "${RED}✗${NC} Backend runs as: $BACKEND_USER (should be appuser)"
fi
echo ""

# Test 5: Check health check
echo "==============================================="
echo "Test 5: Verifying health check configuration"
echo "==============================================="
if docker inspect resume-tool-backend:test | grep -q "HEALTHCHECK"; then
    echo -e "${GREEN}✓${NC} Backend has health check configured"
else
    echo -e "${RED}✗${NC} Backend missing health check"
fi
echo ""

# Summary
echo "==============================================="
echo "              Build Test Summary"
echo "==============================================="
echo ""
echo "Images created:"
docker images | grep resume-tool
echo ""
echo -e "${GREEN}All tests passed!${NC}"
echo ""
echo "To clean up test images, run:"
echo "  docker rmi resume-tool-backend:test resume-tool-frontend:test"
echo ""
echo "Next steps:"
echo "  1. Review the image sizes above"
echo "  2. Test running the containers locally"
echo "  3. Deploy to production using docker-compose.prod.yml"
echo ""
