# Test Search Functionality

Write-Host "Testing Search Functionality..." -ForegroundColor Green

$headers = @{
    "Authorization" = "memory-gpt-2025-key"
    "Content-Type" = "application/json"
}

# Add a specific memory first
Write-Host "`n1. Adding a specific memory..." -ForegroundColor Yellow
$addBody = @{
    content = "User strongly prefers dark mode interface and concise responses"
    metadata = @{
        preference_type = "ui_preference"
        importance = "high"
    }
} | ConvertTo-Json

try {
    $addResponse = Invoke-RestMethod -Uri "https://memory-orchestration-platform.onrender.com/gpt/memories" -Method POST -Headers $headers -Body $addBody
    Write-Host "✅ Memory added: $($addResponse.memory_id)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to add memory: $($_.Exception.Message)" -ForegroundColor Red
}

# Wait a moment for processing
Start-Sleep -Seconds 2

# Try different search queries
$searchQueries = @(
    "dark mode",
    "user preferences", 
    "concise",
    "interface",
    "preferences"
)

foreach ($query in $searchQueries) {
    Write-Host "`n2. Searching for: '$query'" -ForegroundColor Yellow
    $searchBody = @{
        query = $query
    } | ConvertTo-Json
    
    try {
        $searchResponse = Invoke-RestMethod -Uri "https://memory-orchestration-platform.onrender.com/gpt/search" -Method POST -Headers $headers -Body $searchBody
        Write-Host "   Found $($searchResponse.total_results) results" -ForegroundColor Cyan
        
        if ($searchResponse.results.Count -gt 0) {
            foreach ($result in $searchResponse.results) {
                Write-Host "   📝 $($result.memory)" -ForegroundColor Gray
                Write-Host "   📊 Score: $($result.score)" -ForegroundColor Gray
                Write-Host "" 
            }
        }
    } catch {
        Write-Host "   ❌ Search failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n🔍 Search Testing Complete!" -ForegroundColor Green 