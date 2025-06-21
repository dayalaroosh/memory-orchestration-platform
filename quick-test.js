// Quick Test for Render Service
// Usage: node quick-test.js https://your-service.onrender.com

import axios from 'axios';

const serviceUrl = process.argv[2];
const apiKey = 'memory-gpt-2025-key';

if (!serviceUrl) {
  console.log('❌ Please provide your Render service URL:');
  console.log('   node quick-test.js https://your-service.onrender.com');
  process.exit(1);
}

console.log(`🔍 Testing Render service: ${serviceUrl}`);

async function testService() {
  try {
    // Test health endpoint
    console.log('\n📋 Testing health endpoint...');
    const healthResponse = await axios.get(`${serviceUrl}/health`, {
      headers: { 'Authorization': `Bearer ${apiKey}` },
      timeout: 15000
    });
    
    console.log('✅ Health check passed!');
    console.log('📊 Service info:', JSON.stringify(healthResponse.data, null, 2));
    
    // Test memory storage
    console.log('\n📋 Testing memory storage...');
    const memoryResponse = await axios.post(`${serviceUrl}/gpt/memories`, {
      memory: 'Test memory from quick test',
      metadata: { source: 'quick-test', timestamp: new Date().toISOString() }
    }, {
      headers: { 
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      timeout: 15000
    });
    
    console.log('✅ Memory storage works!');
    console.log('📝 Response:', JSON.stringify(memoryResponse.data, null, 2));
    
    // Test memory search
    console.log('\n📋 Testing memory search...');
    const searchResponse = await axios.post(`${serviceUrl}/gpt/search`, {
      query: 'test',
      limit: 5
    }, {
      headers: { 
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      timeout: 15000
    });
    
    console.log('✅ Memory search works!');
    console.log('🔍 Search results:', JSON.stringify(searchResponse.data, null, 2));
    
    console.log('\n🎉 All tests passed! Your Render service is working correctly.');
    console.log('\n📋 Next steps:');
    console.log(`1. Create .env file with: MEMORY_API_URL=${serviceUrl}`);
    console.log('2. Update mcp-config.json with this URL');
    console.log('3. Test MCP server with: node memory-mcp-server.js');
    
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
    if (error.response) {
      console.log(`   Status: ${error.response.status}`);
      console.log(`   Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Check if the URL is correct');
    console.log('2. Verify the service is deployed and running on Render');
    console.log('3. Check if the API key is correct');
    process.exit(1);
  }
}

testService(); 