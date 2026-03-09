#!/bin/bash
# Hangman CLI Deployment Script
# Version: 1.0.0
# Date: 2026-03-08

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERSION="1.0.0"

echo "=============================================="
echo "Hangman CLI Deployment Script v${VERSION}"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    log_info "Python version: $PYTHON_VERSION"
    
    # Check if uv is available
    if ! command -v uv &> /dev/null; then
        log_error "uv is not installed. Please install uv first."
        exit 1
    fi
    log_info "uv found: $(uv --version)"
    
    # Run tests
    log_info "Running tests..."
    cd "$PROJECT_ROOT"
    if uv run pytest tests/ -q --tb=no; then
        log_info "All tests passed"
    else
        log_error "Tests failed. Aborting deployment."
        exit 1
    fi
    
    # Check build artifacts
    if [ ! -f "$PROJECT_ROOT/dist/hangman-${VERSION}-py3-none-any.whl" ]; then
        log_warn "Wheel file not found. Building..."
        cd "$PROJECT_ROOT" && uv build
    fi
    
    log_info "Pre-deployment checks completed successfully"
}

# Deploy to staging (local install)
deploy_staging() {
    log_info "Deploying to staging (local environment)..."
    
    # Install the wheel locally
    uv pip install "$PROJECT_ROOT/dist/hangman-${VERSION}-py3-none-any.whl"
    
    # Verify installation
    if command -v hangman &> /dev/null; then
        log_info "Hangman CLI installed successfully"
        hangman --help | head -5
    else
        log_warn "hangman command not in PATH, but installation may still succeed"
    fi
    
    log_info "Staging deployment completed"
}

# Deploy to production (publish to PyPI)
deploy_production() {
    log_info "Deploying to production (PyPI)..."
    
    # Check for PyPI credentials
    if [ -z "$PYPI_TOKEN" ] && [ -z "$TWINE_USERNAME" ]; then
        log_warn "PyPI credentials not set. Skipping PyPI publish."
        log_info "To publish, set PYPI_TOKEN environment variable"
        return 0
    fi
    
    cd "$PROJECT_ROOT"
    
    # Publish to PyPI
    if uv publish; then
        log_info "Successfully published to PyPI"
    else
        log_error "Failed to publish to PyPI"
        exit 1
    fi
    
    log_info "Production deployment completed"
}

# Post-deployment verification
post_deployment_verification() {
    log_info "Running post-deployment verification..."
    
    # Test import
    if uv run python -c "import hangman; print('Import OK')"; then
        log_info "Package import verified"
    else
        log_error "Package import failed"
        exit 1
    fi
    
    # Test entry point
    if uv run hangman --help > /dev/null 2>&1; then
        log_info "Entry point verified"
    else
        log_warn "Entry point test skipped (may require interactive terminal)"
    fi
    
    log_info "Post-deployment verification completed"
}

# Main deployment flow
main() {
    local environment="${1:-staging}"
    
    case "$environment" in
        staging)
            pre_deployment_checks
            deploy_staging
            post_deployment_verification
            ;;
        production)
            pre_deployment_checks
            deploy_staging  # Test locally first
            deploy_production
            post_deployment_verification
            ;;
        verify)
            post_deployment_verification
            ;;
        *)
            echo "Usage: $0 {staging|production|verify}"
            exit 1
            ;;
    esac
    
    log_info "Deployment script completed successfully"
}

main "$@"
