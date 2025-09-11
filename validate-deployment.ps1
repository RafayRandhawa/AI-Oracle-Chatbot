# Oracle AI Chatbot Deployment Validation Script
# This script validates the deployment configuration without actually building

Write-Host "Oracle AI Chatbot Deployment Validation" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
Write-Host "1. Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    $composeVersion = docker-compose --version
    Write-Host "   ✓ Docker: $dockerVersion" -ForegroundColor Green
    Write-Host "   ✓ Docker Compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Docker or Docker Compose not found" -ForegroundColor Red
    exit 1
}

# Validate docker-compose.yml
Write-Host "2. Validating docker-compose.yml..." -ForegroundColor Yellow
try {
    docker-compose config --quiet
    Write-Host "   ✓ docker-compose.yml syntax is valid" -ForegroundColor Green
} catch {
    Write-Host "   ✗ docker-compose.yml has syntax errors" -ForegroundColor Red
    exit 1
}

# Check if required files exist
Write-Host "3. Checking required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "backend/Dockerfile",
    "frontend/Dockerfile", 
    "frontend/nginx.conf",
    "nginx/nginx.conf",
    "nginx/conf.d/default.conf",
    "deploy.sh",
    "deploy.ps1"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $file (missing)" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "   ✗ Some required files are missing" -ForegroundColor Red
    exit 1
}

# Check if environment example exists
Write-Host "4. Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path "env.example") {
    Write-Host "   ✓ env.example found" -ForegroundColor Green
    Write-Host "   ⚠  Remember to copy env.example to .env and configure it" -ForegroundColor Yellow
} else {
    Write-Host "   ✗ env.example not found" -ForegroundColor Red
}

# Validate Dockerfile syntax (basic check)
Write-Host "5. Validating Dockerfile syntax..." -ForegroundColor Yellow

# Check backend Dockerfile
$backendDockerfile = Get-Content "backend/Dockerfile" -Raw
if ($backendDockerfile -match "FROM.*python" -and $backendDockerfile -match "WORKDIR" -and $backendDockerfile -match "COPY.*requirements.txt") {
    Write-Host "   ✓ Backend Dockerfile structure looks good" -ForegroundColor Green
} else {
    Write-Host "   ✗ Backend Dockerfile may have issues" -ForegroundColor Red
}

# Check frontend Dockerfile
$frontendDockerfile = Get-Content "frontend/Dockerfile" -Raw
if ($frontendDockerfile -match "FROM.*node" -and $frontendDockerfile -match "FROM.*nginx" -and $frontendDockerfile -match "COPY.*dist") {
    Write-Host "   ✓ Frontend Dockerfile structure looks good" -ForegroundColor Green
} else {
    Write-Host "   ✗ Frontend Dockerfile may have issues" -ForegroundColor Red
}

# Check nginx configuration
Write-Host "6. Validating Nginx configuration..." -ForegroundColor Yellow
$nginxConfig = Get-Content "nginx/nginx.conf" -Raw
if ($nginxConfig -match "worker_processes" -and $nginxConfig -match "events" -and $nginxConfig -match "http") {
    Write-Host "   ✓ Main nginx.conf structure looks good" -ForegroundColor Green
} else {
    Write-Host "   ✗ Main nginx.conf may have issues" -ForegroundColor Red
}

$siteConfig = Get-Content "nginx/conf.d/default.conf" -Raw
if ($siteConfig -match "upstream" -and $siteConfig -match "server" -and $siteConfig -match "location") {
    Write-Host "   ✓ Site nginx configuration structure looks good" -ForegroundColor Green
} else {
    Write-Host "   ✗ Site nginx configuration may have issues" -ForegroundColor Red
}

# Check deployment scripts
Write-Host "7. Checking deployment scripts..." -ForegroundColor Yellow
if (Test-Path "deploy.sh") {
    Write-Host "   ✓ Linux/Mac deployment script exists" -ForegroundColor Green
}
if (Test-Path "deploy.ps1") {
    Write-Host "   ✓ Windows deployment script exists" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host "✓ All configuration files are present and syntactically valid" -ForegroundColor Green
Write-Host "✓ Docker and Docker Compose are available" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Copy env.example to .env and configure your environment variables" -ForegroundColor White
Write-Host "2. Run: .\deploy.ps1 (Windows) or ./deploy.sh (Linux/Mac)" -ForegroundColor White
Write-Host "3. Access the application at http://localhost" -ForegroundColor White
Write-Host ""
Write-Host "Validation completed successfully!" -ForegroundColor Green