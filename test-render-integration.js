#!/usr/bin/env node

/**
 * Render Integration Test Script
 * 
 * This script helps you:
 * 1. Test your current Render service
 * 2. Identify the correct service URL
 * 3. Verify all endpoints work
 * 4. Test MCP integration
 */

import axios from 'axios';
import { spawn } from 'child_process';

// Common Render service patterns
const POSSIBLE_URLS = [
  'https://memory-orchestration-platform.onrender.com',
  'https://memory-platform.onrender.com', 
  'https://memory-orchestration.onrender.com',
  'https://mem0-server.onrender.com',
  'https://production-mem0-server.onrender.com'
];

const API_KEY = 'memory-gpt-2025-key';

class RenderIntegrationTester {
  constructor() {
    this.foundUrl = null;
    this.testResults = [];
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = {
      'info': '📋',
      'success': '✅',
      'error': '❌',
      'warning': '⚠️'
    }[type] || '📋';
    
    console.log(`${prefix} [${timestamp}] ${message}`);
    this.testResults.push({ timestamp, type, message });
  }

  async discoverRenderService() {
    this.log('🔍 Discovering your Render service URL...', 'info');
    
    for (const url of POSSIBLE_URLS) {
      try {
        this.log(`Testing: ${url}`, 'info');
        
        const response = await axios.get(`${url}/health`, {
          headers: {
            'Authorization': `Bearer ${API_KEY}`
          },
          timeout: 10000
        });

        if (response.status === 200) {
          this.foundUrl = url;
          this.log(`✅ Found working service: ${url}`, 'success');
          this.log(`Service info: ${JSON.stringify(response.data, null, 2)}`, 'info');
          return url;
        }
      } catch (error) {
        this.log(`❌ ${url} - ${error.message}`, 'error');
      }
    }

    this.log('❌ Could not find working Render service from common URLs', 'error');
    this.log('Please check your Render Dashboard for the correct URL', 'warning');
    return null;
  }

  async testCustomUrl(url) {
    this.log(`🔍 Testing custom URL: ${url}`, 'info');
    
    try {
      const response = await axios.get(`${url}/health`, {
        headers: {
          'Authorization': `Bearer ${API_KEY}`
        },
        timeout: 10000
      });

      if (response.status === 200) {
        this.foundUrl = url;
        this.log(`✅ Custom URL works: ${url}`, 'success');
        this.log(`Service info: ${JSON.stringify(response.data, null, 2)}`, 'info');
        return url;
      }
    } catch (error) {
      this.log(`❌ Custom URL failed: ${error.message}`, 'error');
      return null;
    }
  }

  async testEndpoints(baseUrl) {
    this.log(`🧪 Testing API endpoints on ${baseUrl}`, 'info');
    
    const endpoints = [
      { path: '/health', method: 'GET', description: 'Health check' },
      { path: '/', method: 'GET', description: 'Root endpoint' },
      { path: '/gpt/memories', method: 'POST', description: 'Memory storage', 
        data: { memory: 'Test memory from integration test', metadata: { source: 'test' } } },
      { path: '/gpt/search', method: 'POST', description: 'Memory search',
        data: { query: 'test', limit: 5 } }
    ];

    const results = [];

    for (const endpoint of endpoints) {
      try {
        const config = {
          method: endpoint.method,
          url: `${baseUrl}${endpoint.path}`,
          headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json'
          },
          timeout: 10000
        };

        if (endpoint.data) {
          config.data = endpoint.data;
        }

        const response = await axios(config);
        
        this.log(`✅ ${endpoint.description} (${endpoint.method} ${endpoint.path}) - Status: ${response.status}`, 'success');
        results.push({ endpoint: endpoint.path, status: 'success', statusCode: response.status });
        
        if (endpoint.path === '/gpt/memories' && response.data) {
          this.log(`   Memory stored: ${JSON.stringify(response.data)}`, 'info');
        }
        
        if (endpoint.path === '/gpt/search' && response.data) {
          this.log(`   Search results: ${response.data.results?.length || 0} found`, 'info');
        }

      } catch (error) {
        this.log(`❌ ${endpoint.description} (${endpoint.method} ${endpoint.path}) - ${error.message}`, 'error');
        results.push({ endpoint: endpoint.path, status: 'failed', error: error.message });
      }
    }

    return results;
  }

  async testMCPIntegration(apiUrl) {
    this.log('🔗 Testing MCP server integration...', 'info');
    
    // Create temporary .env file for testing
    const envContent = `MEMORY_API_URL=${apiUrl}\nMEMORY_API_KEY=${API_KEY}\n`;
    
    try {
      const { writeFileSync } = await import('fs');
      writeFileSync('.env.test', envContent);
      
      this.log('Created temporary test environment', 'info');
      
      // Test MCP server with environment
      const testMessage = {
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/list',
        params: {}
      };

      return new Promise((resolve) => {
        const mcpProcess = spawn('node', ['memory-mcp-server.js'], {
          stdio: ['pipe', 'pipe', 'pipe'],
          env: { ...process.env, MEMORY_API_URL: apiUrl, MEMORY_API_KEY: API_KEY }
        });

        let output = '';
        let errorOutput = '';
        
        mcpProcess.stdout.on('data', (data) => {
          output += data.toString();
        });

        mcpProcess.stderr.on('data', (data) => {
          errorOutput += data.toString();
          if (data.toString().includes('Memory Orchestration MCP Server running')) {
            this.log('✅ MCP Server started successfully', 'success');
            
            // Send test message
            mcpProcess.stdin.write(JSON.stringify(testMessage) + '\n');
            
            setTimeout(() => {
              mcpProcess.kill();
              this.log('✅ MCP Server test completed', 'success');
              resolve(true);
            }, 3000);
          }
        });

        mcpProcess.on('error', (error) => {
          this.log(`❌ MCP Server error: ${error.message}`, 'error');
          resolve(false);
        });

        setTimeout(() => {
          if (!mcpProcess.killed) {
            mcpProcess.kill();
            this.log('⚠️ MCP Server test timeout', 'warning');
            resolve(false);
          }
        }, 10000);
      });

    } catch (error) {
      this.log(`❌ MCP integration test failed: ${error.message}`, 'error');
      return false;
    }
  }

  generateConfig(apiUrl) {
    this.log('📝 Generating configuration files...', 'info');
    
    const envConfig = `# Environment Configuration for Memory Platform
MEMORY_API_URL=${apiUrl}
MEMORY_API_KEY=memory-gpt-2025-key
PORT=8090
NODE_ENV=development`;

    const mcpConfig = {
      mcpServers: {
        "memory-orchestration": {
          command: "node",
          args: ["memory-mcp-server.js"],
          cwd: ".",
          env: {
            MEMORY_API_URL: apiUrl,
            MEMORY_API_KEY: "memory-gpt-2025-key"
          }
        }
      }
    };

    this.log('📄 .env file content:', 'info');
    console.log(envConfig);
    
    this.log('📄 mcp-config.json content:', 'info');
    console.log(JSON.stringify(mcpConfig, null, 2));

    return { envConfig, mcpConfig };
  }

  async generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      foundService: !!this.foundUrl,
      serviceUrl: this.foundUrl,
      summary: {
        total_tests: this.testResults.filter(r => r.type === 'info').length,
        passed: this.testResults.filter(r => r.type === 'success').length,
        failed: this.testResults.filter(r => r.type === 'error').length,
        warnings: this.testResults.filter(r => r.type === 'warning').length
      },
      results: this.testResults
    };

    this.log('=== Render Integration Test Report ===', 'info');
    this.log(`Service Found: ${report.foundService ? '✅ YES' : '❌ NO'}`, report.foundService ? 'success' : 'error');
    if (report.serviceUrl) {
      this.log(`Service URL: ${report.serviceUrl}`, 'success');
    }
    this.log(`Tests Passed: ${report.summary.passed}`, 'success');
    this.log(`Tests Failed: ${report.summary.failed}`, report.summary.failed > 0 ? 'error' : 'success');
    this.log(`Warnings: ${report.summary.warnings}`, report.summary.warnings > 0 ? 'warning' : 'success');

    return report;
  }

  async runFullTest(customUrl = null) {
    this.log('🚀 Starting Render Integration Test Suite...', 'info');
    
    try {
      // Step 1: Discover or test service URL
      let serviceUrl = customUrl;
      if (customUrl) {
        serviceUrl = await this.testCustomUrl(customUrl);
      } else {
        serviceUrl = await this.discoverRenderService();
      }

      if (!serviceUrl) {
        this.log('❌ Cannot proceed without a working service URL', 'error');
        return await this.generateReport();
      }

      // Step 2: Test all endpoints
      this.log('🧪 Testing API endpoints...', 'info');
      const endpointResults = await this.testEndpoints(serviceUrl);

      // Step 3: Test MCP integration
      this.log('🔗 Testing MCP integration...', 'info');
      const mcpResults = await this.testMCPIntegration(serviceUrl);

      // Step 4: Generate configuration
      this.log('📝 Generating configuration...', 'info');
      const configs = this.generateConfig(serviceUrl);

      // Step 5: Generate final report
      const report = await this.generateReport();

      if (report.foundService && report.summary.failed === 0) {
        this.log('🎉 All tests passed! Your Render integration is working.', 'success');
        this.log(`Next steps:`, 'info');
        this.log(`1. Copy the .env configuration above to your .env file`, 'info');
        this.log(`2. Update your mcp-config.json with the configuration above`, 'info');
        this.log(`3. Restart Cursor to load the new MCP configuration`, 'info');
      } else {
        this.log('❌ Some tests failed. Please check the errors above.', 'error');
      }

      return report;

    } catch (error) {
      this.log(`❌ Test suite crashed: ${error.message}`, 'error');
      return await this.generateReport();
    }
  }
}

// Main execution
const tester = new RenderIntegrationTester();

// Check if custom URL was provided as command line argument
const customUrl = process.argv[2];

if (customUrl) {
  console.log(`🔍 Testing custom URL: ${customUrl}`);
}

tester.runFullTest(customUrl)
  .then((report) => {
    process.exit(report.foundService && report.summary.failed === 0 ? 0 : 1);
  })
  .catch((error) => {
    console.error('❌ Test suite error:', error);
    process.exit(1);
  }); 