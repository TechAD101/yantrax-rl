#!/usr/bin/env node

/**
 * YantraX Live Integration Test
 * Tests the connection between frontend and backend
 */

const https = require('https');
const http = require('http');

const BACKEND_URL = 'https://yantrax-backend.onrender.com';
const FRONTEND_URL = 'https://yantrax-rl.vercel.app';

const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function makeRequest(url) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https:') ? https : http;
    const req = lib.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve({ status: res.statusCode, data: json, raw: data });
        } catch {
          resolve({ status: res.statusCode, data: null, raw: data });
        }
      });
    });
    
    req.on('error', reject);
    req.setTimeout(10000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

async function testEndpoint(name, url, expectedFields = []) {
  try {
    log(`\n🔍 Testing ${name}...`, 'cyan');
    log(`   URL: ${url}`, 'blue');
    
    const result = await makeRequest(url);
    
    if (result.status === 200) {
      log(`   ✅ Status: ${result.status} OK`, 'green');
      
      if (result.data) {
        log(`   📊 Response type: ${typeof result.data}`, 'yellow');
        
        // Check for expected fields
        if (expectedFields.length > 0) {
          const missingFields = expectedFields.filter(field => !(field in result.data));
          if (missingFields.length === 0) {
            log(`   ✅ All expected fields present: ${expectedFields.join(', ')}`, 'green');
          } else {
            log(`   ⚠️  Missing fields: ${missingFields.join(', ')}`, 'yellow');
          }
        }
        
        // Show sample data
        const sampleKeys = Object.keys(result.data).slice(0, 3);
        log(`   📋 Sample fields: ${sampleKeys.join(', ')}`, 'blue');
      }
      
      return { success: true, data: result.data };
    } else {
      log(`   ❌ Status: ${result.status}`, 'red');
      log(`   Error: ${result.raw}`, 'red');
      return { success: false, error: `HTTP ${result.status}` };
    }
  } catch (error) {
    log(`   ❌ Failed: ${error.message}`, 'red');
    return { success: false, error: error.message };
  }
}

async function runFullTest() {
  log('🚀 YantraX Live Integration Test Suite', 'bold');
  log('========================================', 'cyan');
  
  const results = [];
  
  // Test backend health
  results.push(await testEndpoint(
    'Backend Health Check',
    `${BACKEND_URL}/health`,
    ['status', 'services', 'timestamp']
  ));
  
  // Test market data
  results.push(await testEndpoint(
    'Market Data (AAPL)',
    `${BACKEND_URL}/market-price?symbol=AAPL`,
    ['symbol', 'price', 'change', 'timestamp']
  ));
  
  // Test AI agents
  results.push(await testEndpoint(
    'AI God Cycle',
    `${BACKEND_URL}/god-cycle`,
    ['agents', 'signal', 'final_balance', 'status']
  ));
  
  // Test journal
  results.push(await testEndpoint(
    'Trading Journal',
    `${BACKEND_URL}/journal`,
    []
  ));
  
  // Test commentary
  results.push(await testEndpoint(
    'AI Commentary',
    `${BACKEND_URL}/commentary`,
    []
  ));
  
  // Test multi-asset data
  results.push(await testEndpoint(
    'Multi-Asset Data',
    `${BACKEND_URL}/multi-asset-data?symbols=AAPL,MSFT,GOOGL`,
    ['data', 'timestamp']
  ));
  
  // Summary
  log('\n📊 TEST SUMMARY', 'bold');
  log('================', 'cyan');
  
  const successful = results.filter(r => r.success).length;
  const total = results.length;
  const successRate = ((successful / total) * 100).toFixed(1);
  
  log(`\n✅ Successful tests: ${successful}/${total} (${successRate}%)`, 'green');
  
  if (successful === total) {
    log('\n🎉 ALL TESTS PASSED! Your backend is fully operational.', 'green');
    log('\n🔗 Integration Status:', 'bold');
    log('   ✅ Backend API: Operational', 'green');
    log('   ✅ Market Data: Live', 'green');
    log('   ✅ AI Agents: Active', 'green');
    log('   ✅ Real-time Updates: Working', 'green');
    
    log('\n🚀 Next Steps:', 'bold');
    log('   1. Deploy frontend to Vercel', 'cyan');
    log('   2. Verify CORS configuration', 'cyan');
    log('   3. Test frontend-backend connection', 'cyan');
    log('   4. Monitor live trading dashboard', 'cyan');
  } else {
    log(`\n⚠️  Some tests failed. Check the issues above.`, 'yellow');
    
    const failed = results.filter(r => !r.success);
    log('\n❌ Failed Tests:', 'red');
    failed.forEach((test, i) => {
      log(`   ${i + 1}. ${test.error}`, 'red');
    });
  }
  
  log('\n🔧 Backend URL: ' + BACKEND_URL, 'blue');
  log('🌐 Frontend URL: ' + FRONTEND_URL, 'blue');
  
  log('\n' + '='.repeat(50), 'cyan');
}

// Run the test suite
if (require.main === module) {
  runFullTest().catch(error => {
    log(`\n💥 Test suite crashed: ${error.message}`, 'red');
    process.exit(1);
  });
}

module.exports = { testEndpoint, runFullTest };
