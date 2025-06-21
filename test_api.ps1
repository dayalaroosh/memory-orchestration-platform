# Test Memory Orchestration Platform API

Write-Host "Testing Memory Orchestration Platform API..." -ForegroundColor Green

# Test 1: Health Check
Write-Host "`n1. Testing Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://memory-orchestration-platform.onrender.com/health" -Method GET
    Write-Host "✅ Health Check: $($response.status)" -ForegroundColor Green
    Write-Host "   Service: $($response.service)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Test Auth (No authentication required)
Write-Host "`n2. Testing No-Auth Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://memory-orchestration-platform.onrender.com/test-auth" -Method GET
    Write-Host "✅ Test Auth: $($response.status)" -ForegroundColor Green
    Write-Host "   Message: $($response.message)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Test Auth Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Add Memory (with simple API key)
Write-Host "`n3. Testing Add Memory..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "memory-gpt-2025-key"
        "Content-Type" = "application/json"
    }
    $body = @{
        content = "Test memory from PowerShell script - user prefers concise responses"
        metadata = @{
            source = "powershell_test"
            timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        }
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "https://memory-orchestration-platform.onrender.com/gpt/memories" -Method POST -Headers $headers -Body $body
    Write-Host "✅ Add Memory: $($response.message)" -ForegroundColor Green
    Write-Host "   Memory ID: $($response.memory_id)" -ForegroundColor Gray
    $memoryId = $response.memory_id
} catch {
    Write-Host "❌ Add Memory Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Response: $($_.Exception.Response)" -ForegroundColor Red
}

# Test 4: Search Memory
Write-Host "`n4. Testing Search Memory..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "memory-gpt-2025-key"
        "Content-Type" = "application/json"
    }
    $body = @{
        query = "user preferences"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "https://memory-orchestration-platform.onrender.com/gpt/search" -Method POST -Headers $headers -Body $body
    Write-Host "✅ Search Memory: Found $($response.total_results) results" -ForegroundColor Green
    if ($response.results.Count -gt 0) {
        Write-Host "   First result: $($response.results[0].memory.Substring(0, [Math]::Min(50, $response.results[0].memory.Length)))..." -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Search Memory Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 API Testing Complete!" -ForegroundColor Green 