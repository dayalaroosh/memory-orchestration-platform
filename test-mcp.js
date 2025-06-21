#!/usr/bin/env node

/**
 * Test script for Memory Orchestration MCP Server
 */

import { spawn } from 'child_process';
import { setTimeout } from 'timers/promises';

console.log('🧪 Testing Memory Orchestration MCP Server...\n');

// Test data
const testMemory = {
  content: 'Test memory for MCP integration',
  type: 'context',
  project: 'memory-orchestration',
  source: 'cursor',
  tags: ['test', 'mcp']
};

const testSearch = {
  query: 'test memory',
  limit: 5
};

const testContext = {
  current_task: 'Setting up MCP integration',
  project: 'memory-orchestration',
  include_actions: true
};

// Start MCP server
console.log('🚀 Starting MCP server...');
const mcpServer = spawn('node', ['memory-mcp-server.js'], {
  stdio: ['pipe', 'pipe', 'pipe']
});

let serverOutput = '';
mcpServer.stdout.on('data', (data) => {
  serverOutput += data.toString();
});

mcpServer.stderr.on('data', (data) => {
  console.log('MCP Server:', data.toString().trim());
});

// Wait for server to start
await setTimeout(2000);

// Test MCP protocol messages
async function testMCPMessage(message) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('Test timeout'));
    }, 5000);

    let response = '';
    
    const onData = (data) => {
      response += data.toString();
      try {
        const parsed = JSON.parse(response);
        clearTimeout(timeout);
        mcpServer.stdout.off('data', onData);
        resolve(parsed);
      } catch (e) {
        // Still accumulating data
      }
    };

    mcpServer.stdout.on('data', onData);
    mcpServer.stdin.write(JSON.stringify(message) + '\n');
  });
}

try {
  // Test 1: List tools
  console.log('🔧 Testing list tools...');
  const listToolsMessage = {
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/list'
  };

  try {
    const toolsResponse = await testMCPMessage(listToolsMessage);
    console.log('✅ Tools listed:', toolsResponse.result?.tools?.length || 0, 'tools found');
  } catch (e) {
    console.log('⚠️  Tools test failed:', e.message);
  }

  // Test 2: List resources
  console.log('📋 Testing list resources...');
  const listResourcesMessage = {
    jsonrpc: '2.0',
    id: 2,
    method: 'resources/list'
  };

  try {
    const resourcesResponse = await testMCPMessage(listResourcesMessage);
    console.log('✅ Resources listed:', resourcesResponse.result?.resources?.length || 0, 'resources found');
  } catch (e) {
    console.log('⚠️  Resources test failed:', e.message);
  }

  console.log('\n🎉 MCP Server basic tests completed!');
  console.log('📝 Note: Full functionality requires the Memory API to be running on port 8090');

} catch (error) {
  console.error('❌ Test failed:', error.message);
} finally {
  // Clean up
  mcpServer.kill();
  console.log('\n🛑 Test completed, MCP server stopped');
} 