# Simple Custom GPT API Test

Write-Host "Testing Custom GPT Memory API..." -ForegroundColor Green

$baseUrl = "https://memory-orchestration-platform.onrender.com"
$headers = @{
    "Authorization" = "memory-gpt-2025-key"
    "Content-Type" = "application/json"
}

# Test 1: Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Add Memory
Write-Host "`n2. Adding Memory..." -ForegroundColor Yellow
$memoryJson = '{"content": "User prefers dark mode and concise responses", "metadata": {"type": "preference"}}'

try {
    $addResult = Invoke-RestMethod -Uri "$baseUrl/gpt/memories" -Method POST -Headers $headers -Body $memoryJson
    Write-Host "Memory added: $($addResult.memory_id)" -ForegroundColor Green
} catch {
    Write-Host "Add memory failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Search Memory
Write-Host "`n3. Searching Memory..." -ForegroundColor Yellow
$searchJson = '{"query": "user preferences"}'

try {
    $searchResult = Invoke-RestMethod -Uri "$baseUrl/gpt/search" -Method POST -Headers $headers -Body $searchJson
    Write-Host "Found $($searchResult.total_results) results" -ForegroundColor Green
    
    if ($searchResult.total_results -gt 0) {
        Write-Host "First result: $($searchResult.results[0].memory)" -ForegroundColor Gray
    }
} catch {
    Write-Host "Search failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nCustom GPT API Test Complete!" -ForegroundColor Green 