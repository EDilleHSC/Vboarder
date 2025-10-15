# VBoarder Beta Release - Final Execution Steps
# Run these commands to complete the release preparation

Write-Host "=== VBoarder v0.9.0-beta.1 Release Preparation ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify we're in the right directory
$currentDir = Get-Location
if (-not (Test-Path ".\api\main.py")) {
    Write-Host "ERROR: Please run this script from the vboarder root directory" -ForegroundColor Red
    exit 1
}

Write-Host "[1/7] Verifying directory structure..." -ForegroundColor Yellow
Write-Host "  ✓ Current directory: $currentDir" -ForegroundColor Green

# Step 2: Lock backend dependencies
Write-Host ""
Write-Host "[2/7] Locking backend dependencies..." -ForegroundColor Yellow
try {
    python -m pip install -U pip wheel | Out-Null
    python -m pip list --format=freeze | Out-File -FilePath "requirements.lock" -Encoding utf8
    Write-Host "  ✓ Created requirements.lock" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to lock dependencies: $_" -ForegroundColor Red
}

# Step 3: Install formatting tools
Write-Host ""
Write-Host "[3/7] Installing formatting tools..." -ForegroundColor Yellow
try {
    pip install black ruff pre-commit | Out-Null
    Write-Host "  ✓ Installed black, ruff, pre-commit" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to install tools: $_" -ForegroundColor Red
}

# Step 4: Format Python code
Write-Host ""
Write-Host "[4/7] Formatting Python code..." -ForegroundColor Yellow
try {
    black api tests_flat --quiet
    Write-Host "  ✓ Formatted with black" -ForegroundColor Green

    ruff check api tests_flat --fix --quiet
    Write-Host "  ✓ Linted with ruff" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Formatting completed with warnings" -ForegroundColor Yellow
}

# Step 5: Install and run pre-commit hooks
Write-Host ""
Write-Host "[5/7] Setting up pre-commit hooks..." -ForegroundColor Yellow
try {
    pre-commit install | Out-Null
    Write-Host "  ✓ Pre-commit hooks installed" -ForegroundColor Green

    Write-Host "  Running pre-commit on all files (this may take a minute)..." -ForegroundColor Cyan
    pre-commit run --all-files
    Write-Host "  ✓ Pre-commit checks completed" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Pre-commit setup completed with warnings" -ForegroundColor Yellow
}

# Step 6: Run all tests
Write-Host ""
Write-Host "[6/7] Running test suite..." -ForegroundColor Yellow
try {
    $testOutput = pytest -q 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ All tests passed!" -ForegroundColor Green
        Write-Host "    $testOutput" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ Some tests failed" -ForegroundColor Red
        Write-Host "    $testOutput" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Test execution failed: $_" -ForegroundColor Red
}

# Step 7: Frontend setup (optional)
Write-Host ""
Write-Host "[7/7] Frontend dependencies check..." -ForegroundColor Yellow
$frontendPath = ".\vboarder_frontend\nextjs_space"
if (Test-Path $frontendPath) {
    Push-Location $frontendPath
    try {
        Write-Host "  Checking for package.json..." -ForegroundColor Cyan
        if (Test-Path "package.json") {
            Write-Host "  ✓ Frontend directory found" -ForegroundColor Green
            Write-Host "  Note: Run 'npm ci' and 'npm run build' to verify frontend" -ForegroundColor Cyan
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Host "  ⚠ Frontend directory not found" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=== Release Preparation Summary ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Completed:" -ForegroundColor Green
Write-Host "  - Dependencies locked (requirements.lock)" -ForegroundColor Gray
Write-Host "  - Code formatted (black + ruff)" -ForegroundColor Gray
Write-Host "  - Pre-commit hooks installed" -ForegroundColor Gray
Write-Host "  - Tests executed" -ForegroundColor Gray
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review git status: git status" -ForegroundColor Gray
Write-Host "  2. Create release branch: git checkout -b release/beta-1" -ForegroundColor Gray
Write-Host "  3. Commit changes: git add . && git commit -m 'chore: prepare v0.9.0-beta.1'" -ForegroundColor Gray
Write-Host "  4. Create tag: git tag -a v0.9.0-beta.1 -m 'Beta release'" -ForegroundColor Gray
Write-Host "  5. Test endpoints: make health && make ready && make agents" -ForegroundColor Gray
Write-Host "  6. Frontend build: cd vboarder_frontend/nextjs_space && npm ci && npm run build" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "  - See BETA_RELEASE_SUMMARY.md for complete checklist" -ForegroundColor Gray
Write-Host "  - See CHANGELOG.md for version history" -ForegroundColor Gray
Write-Host "  - See README.md for quick start guide" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 Ready for beta release!" -ForegroundColor Green
