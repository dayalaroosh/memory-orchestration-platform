// Simple Integration Test for Memory Platform
import axios from 'axios';

const CONFIG = {
  MEMORY_API_URL: 'http://localhost:8090',
  MEMORY_API_KEY: 'memory-gpt-2025-key'
};

console.log('🚀 Starting Memory Platform Integration Test...');

// Test 1: Memory API Health Check
console.log('\n📋 Test 1: Memory API Health Check');
try {
  const response = await axios.get(`${CONFIG.MEMORY_API_URL}/health`, {
    headers: {
      'Authorization': `Bearer ${CONFIG.MEMORY_API_KEY}`
    }
  });
  
  console.log('✅ Memory API is accessible');
  console.log(`   Status: ${response.data.status}`);
  console.log(`   Services: ${JSON.stringify(response.data.services)}`);
} catch (error) {
  console.log('❌ Memory API health check failed:', error.message);
  process.exit(1);
}

console.log('\n🎉 Memory API test completed successfully!');
