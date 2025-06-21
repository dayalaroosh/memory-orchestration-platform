# Simple API Test

Write-Host "Testing API..." -ForegroundColor Green

$headers = @{
    "Authorization" = "memory-gpt-2025-key"
    "Content-Type" = "application/json"
}

# Add memory
Write-Host "Adding memory..." -ForegroundColor Yellow
$addBody = '{"content": "User prefers dark mode and concise responses"}'

try {
    $addResponse = Invoke-RestMethod -Uri "https://memory-orchestration-platform.onrender.com/gpt/memories" -Method POST -Headers $headers -Body $addBody
    Write-Host "Memory added successfully: $($addResponse.memory_id)" -ForegroundColor Green
} catch {
    Write-Host "Failed to add memory: $($_.Exception.Message)" -ForegroundColor Red
}

# Search memory
Write-Host "Searching memory..." -ForegroundColor Yellow
$searchBody = '{"query": "dark mode"}'

try {
    $searchResponse = Invoke-RestMethod -Uri "https://memory-orchestration-platform.onrender.com/gpt/search" -Method POST -Headers $headers -Body $searchBody
    Write-Host "Found $($searchResponse.total_results) results" -ForegroundColor Green
    
    if ($searchResponse.results.Count -gt 0) {
        Write-Host "First result: $($searchResponse.results[0].memory)" -ForegroundColor Gray
    }
} catch {
    Write-Host "Search failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Test complete!" -ForegroundColor Green 