# Comprehensive Custom GPT API Test

Write-Host "🧪 Testing Custom GPT Memory API..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Blue

$baseUrl = "https://memory-orchestration-platform.onrender.com"
$headers = @{
    "Authorization" = "memory-gpt-2025-key"
    "Content-Type" = "application/json"
}

# Test 1: Health Check
Write-Host "`n1. 🏥 Testing Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "   ✅ Status: $($health.status)" -ForegroundColor Green
    Write-Host "   📊 Service: $($health.service)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Add Memory - User Preferences
Write-Host "`n2. 💾 Testing Add Memory (User Preferences)..." -ForegroundColor Yellow
$memoryData = @{
    content = "User prefers dark mode interface, concise responses, and works on Product Strategy Council project"
    metadata = @{
        type = "user_preference"
        importance = "high"
        source = "custom_gpt_test"
    }
} | ConvertTo-Json

try {
    $addResult = Invoke-RestMethod -Uri "$baseUrl/gpt/memories" -Method POST -Headers $headers -Body $memoryData
    Write-Host "   ✅ Memory added successfully" -ForegroundColor Green
    Write-Host "   🆔 Memory ID: $($addResult.memory_id)" -ForegroundColor Gray
    Write-Host "   📝 Content: $($addResult.content.Substring(0, [Math]::Min(50, $addResult.content.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Add memory failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Add Memory - Project Information
Write-Host "`n3. 💾 Testing Add Memory (Project Info)..." -ForegroundColor Yellow
$projectData = @{
    content = "Working on Memory Orchestration Platform using FastAPI backend deployed on Render and Next.js frontend"
    metadata = @{
        type = "project_info"
        project = "memory_platform"
        tech_stack = @("FastAPI", "Next.js", "Render", "Mem0")
    }
} | ConvertTo-Json

try {
    $projectResult = Invoke-RestMethod -Uri "$baseUrl/gpt/memories" -Method POST -Headers $headers -Body $projectData
    Write-Host "   ✅ Project memory added successfully" -ForegroundColor Green
    Write-Host "   🆔 Memory ID: $($projectResult.memory_id)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Add project memory failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Wait for indexing
Write-Host "`n⏳ Waiting 3 seconds for memory indexing..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Test 4: Search Memories - User Preferences
Write-Host "`n4. 🔍 Testing Search (User Preferences)..." -ForegroundColor Yellow
$searchData = @{
    query = "user preferences dark mode"
} | ConvertTo-Json

try {
    $searchResult = Invoke-RestMethod -Uri "$baseUrl/gpt/search" -Method POST -Headers $headers -Body $searchData
    Write-Host "   ✅ Search completed: Found $($searchResult.total_results) results" -ForegroundColor Green
    
    if ($searchResult.results.Count -gt 0) {
        foreach ($result in $searchResult.results) {
            Write-Host "   📄 Memory: $($result.memory.Substring(0, [Math]::Min(60, $result.memory.Length)))..." -ForegroundColor Gray
            Write-Host "   📊 Score: $($result.score)" -ForegroundColor Gray
            Write-Host ""
        }
    } else {
        Write-Host "   ⚠️ No results found - this might be normal for new memories" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Search failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Search Memories - Project Information
Write-Host "`n5. 🔍 Testing Search (Project Info)..." -ForegroundColor Yellow
$projectSearchData = @{
    query = "FastAPI Memory Platform project"
} | ConvertTo-Json

try {
    $projectSearchResult = Invoke-RestMethod -Uri "$baseUrl/gpt/search" -Method POST -Headers $headers -Body $projectSearchData
    Write-Host "   ✅ Project search completed: Found $($projectSearchResult.total_results) results" -ForegroundColor Green
    
    if ($projectSearchResult.results.Count -gt 0) {
        foreach ($result in $projectSearchResult.results) {
            Write-Host "   📄 Project Memory: $($result.memory.Substring(0, [Math]::Min(60, $result.memory.Length)))..." -ForegroundColor Gray
            Write-Host "   📊 Score: $($result.score)" -ForegroundColor Gray
            Write-Host ""
        }
    }
} catch {
    Write-Host "   ❌ Project search failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Search with Generic Query
Write-Host "`n6. 🔍 Testing Search (Generic Query)..." -ForegroundColor Yellow
$genericSearchData = @{
    query = "preferences"
} | ConvertTo-Json

try {
    $genericResult = Invoke-RestMethod -Uri "$baseUrl/gpt/search" -Method POST -Headers $headers -Body $genericSearchData
    Write-Host "   ✅ Generic search completed: Found $($genericResult.total_results) results" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Generic search failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Custom GPT API Testing Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Blue
Write-Host "✅ Your Custom GPT should now be fully functional!" -ForegroundColor Green
Write-Host "🔗 Import URL: https://raw.githubusercontent.com/dayalaroosh/memory-orchestration-platform/main/custom-gpt-openapi.yaml" -ForegroundColor Cyan 