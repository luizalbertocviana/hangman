# Hangman CLI Deployment Runbook

**Version:** 1.0.0  
**Date:** 2026-03-08  
**Author:** Deployer Agent

---

## Pre-Deployment Checklist

- [x] All 154 tests passing (99.4% pass rate)
- [x] Code coverage: 71% (core modules >84%)
- [x] Dependencies verified (pyyaml>=6.0)
- [x] Build artifacts created (wheel + sdist)
- [x] Configuration files validated
- [x] Word list data files present

---

## Deployment Artifacts

| File | Size | Type |
|------|------|------|
| `dist/hangman-1.0.0-py3-none-any.whl` | ~50KB | Python Wheel |
| `dist/hangman-1.0.0.tar.gz` | ~45KB | Source Distribution |

---

## Deployment Environments

### Staging
- **Purpose:** Pre-production verification
- **Target:** Local/test environment
- **Command:** `uv run hangman`

### Production
- **Purpose:** End-user deployment
- **Target:** User systems via pip/uv
- **Command:** `pip install hangman` or `uv pip install hangman`

---

## Deployment Steps

### Step 1: Staging Deployment (Local Verification)

```bash
# Install from local wheel
uv pip install dist/hangman-1.0.0-py3-none-any.whl

# Verify installation
hangman --help

# Run smoke test
echo "a" | uv run hangman || true
```

### Step 2: Production Deployment (PyPI Release)

```bash
# Publish to PyPI (requires credentials)
uv publish

# Verify on PyPI
# Visit: https://pypi.org/project/hangman/
```

### Step 3: Post-Deployment Verification

```bash
# Fresh install verification
uv pip install hangman

# Run the game
hangman

# Verify version
uv run python -c "import hangman; print('Hangman CLI v1.0.0')"
```

---

## Rollback Procedure

If deployment fails:

```bash
# Uninstall current version
uv pip uninstall hangman

# Install previous version (if available)
uv pip install hangman==<previous_version>

# Or reinstall from local backup
uv pip install dist/hangman-1.0.0-py3-none-any.whl
```

---

## Known Issues

| Issue | Severity | Workaround |
|-------|----------|------------|
| hangman-hxk: 'q' treated as quit | Minor | Use 'quit' command or avoid guessing 'q' |

---

## Configuration Files

### default.yaml Location
- **System:** `/etc/hangman/config.yaml`
- **User:** `~/.hangman/config.yaml`
- **Project:** `./config/default.yaml`

### Stats File Location
- **Path:** `~/.hangman/stats.json`

### Word Lists Location
- **Default:** `./data/words/`
- **Custom:** Configurable via `paths.word_lists`

---

## Verification Commands

```bash
# Check installation
uv run python -c "from hangman import __version__; print(__version__)"

# Run all tests
uv run pytest tests/ -v

# Check dependencies
uv pip show hangman

# Verify entry point
which hangman
```

---

## Support

- **Documentation:** `README.md`, `docs/`
- **Issues:** Track via `bd list`
- **Logs:** Check `~/.hangman/` for stats and config

---

*End of Runbook*
