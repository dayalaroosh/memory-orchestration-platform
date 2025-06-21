# Memory Orchestration Platform - MCP Setup Script

Write-Host "🚀 Setting up Memory Orchestration MCP Server..." -ForegroundColor Green

# Check if Node.js is installed
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check if Python is running (memory API)
Write-Host "🔍 Checking if Memory API is running on port 8090..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8090/health" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Memory API is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Memory API not running. Starting it now..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "production_mem0_server.py" -WindowStyle Minimized
    Start-Sleep -Seconds 3
}

# Install dependencies if needed
if (!(Test-Path "node_modules")) {
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "🎯 MCP Server is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Add this to your Cursor MCP settings:" -ForegroundColor White
Write-Host "   File -> Preferences -> MCP Servers" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Use the configuration from mcp-config.json" -ForegroundColor White
Write-Host ""
Write-Host "3. Available MCP tools in Cursor:" -ForegroundColor White
Write-Host "   - remember: Store memories" -ForegroundColor Gray
Write-Host "   - recall: Search memories" -ForegroundColor Gray
Write-Host "   - get_context: Get relevant context" -ForegroundColor Gray
Write-Host "   - sync_from_tool: Sync from external tools" -ForegroundColor Gray
Write-Host ""
Write-Host "Memory API running at: http://localhost:8090" -ForegroundColor Green 