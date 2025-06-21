# Final Custom GPT Test

Write-Host "Final Custom GPT Test" -ForegroundColor Green

$headers = @{
    "Authorization" = "memory-gpt-2025-key"
    "Content-Type" = "application/json"
}

# Add a test memory
Write-Host "Adding test memory..." -ForegroundColor Yellow
$body = '{"content": "I love using dark themes in all my applications"}'
$result = Invoke-RestMethod -Uri "https://memory-orchestration-platform.onrender.com/gpt/memories" -Method POST -Headers $headers -Body $body
Write-Host "Added memory: $($result.memory_id)" -ForegroundColor Green

# Wait and search
Start-Sleep -Seconds 2
Write-Host "Searching for dark theme..." -ForegroundColor Yellow
$searchBody = '{"query": "dark theme"}'
$searchResult = Invoke-RestMethod -Uri "https://memory-orchestration-platform.onrender.com/gpt/search" -Method POST -Headers $headers -Body $searchBody

Write-Host "Found $($searchResult.total_results) results" -ForegroundColor Green
if ($searchResult.total_results -gt 0) {
    Write-Host "Result: $($searchResult.results[0].memory)" -ForegroundColor Cyan
}

Write-Host "Test complete - API is working!" -ForegroundColor Green 