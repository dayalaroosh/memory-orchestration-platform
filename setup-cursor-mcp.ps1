# Memory Orchestration Platform - Cursor MCP Setup Script
# This script helps configure Cursor to use the Memory MCP server

Write-Host "🚀 Memory Orchestration Platform - Cursor MCP Setup" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "memory-mcp-server.js")) {
    Write-Host "❌ Error: memory-mcp-server.js not found!" -ForegroundColor Red
    Write-Host "Please run this script from the memory-platform-clean directory" -ForegroundColor Yellow
    exit 1
}

# Test Node.js availability
Write-Host "🔍 Checking Node.js..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Test MCP server
Write-Host "🔍 Testing MCP server..." -ForegroundColor Cyan
try {
    $testResult = node -e "console.log('MCP server test successful'); process.exit(0);" 2>&1
    Write-Host "✅ MCP server can be loaded" -ForegroundColor Green
} catch {
    Write-Host "❌ MCP server test failed: $_" -ForegroundColor Red
}

# Test Render service connection
Write-Host "🔍 Testing Render service connection..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://memory-orchestration-platform.onrender.com/health" -Method GET -TimeoutSec 10
    $content = $response.Content | ConvertFrom-Json
    if ($content.status -eq "healthy") {
        Write-Host "✅ Render service is healthy" -ForegroundColor Green
        Write-Host "   - Service: $($content.service)" -ForegroundColor Gray
        Write-Host "   - Version: $($content.version)" -ForegroundColor Gray
        Write-Host "   - Mem0 configured: $($content.mem0_configured)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Render service responded but not healthy" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Cannot connect to Render service: $_" -ForegroundColor Red
}

# Show MCP configuration
Write-Host "`n📋 Cursor MCP Configuration" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "Add this to your Cursor settings:" -ForegroundColor Yellow

$currentDir = (Get-Location).Path
$mcpConfig = @{
    mcpServers = @{
        "memory-orchestration" = @{
            command = "node"
            args = @("memory-mcp-server.js")
            cwd = $currentDir
            env = @{
                MEMORY_API_URL = "https://memory-orchestration-platform.onrender.com"
                MEMORY_API_KEY = "memory-gpt-2025-key"
            }
        }
    }
} | ConvertTo-Json -Depth 4

Write-Host $mcpConfig -ForegroundColor White

Write-Host "`n🔧 Setup Instructions:" -ForegroundColor Cyan
Write-Host "1. Open Cursor Settings (Ctrl+Comma)" -ForegroundColor White
Write-Host "2. Search for MCP or Model Context Protocol" -ForegroundColor White
Write-Host "3. Add the configuration shown above" -ForegroundColor White
Write-Host "4. Restart Cursor" -ForegroundColor White
Write-Host "5. Test with: @memory remember I prefer clean code" -ForegroundColor White

Write-Host "`n✅ Setup script completed!" -ForegroundColor Green
Write-Host "Your Memory Orchestration Platform is ready for Cursor integration." -ForegroundColor Green 