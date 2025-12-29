const BASE_URL = 'http://localhost:5000';

async function testEndpoint(name, url, options = {}) {
    console.log(`\nTesting ${name}...`);
    try {
        const response = await fetch(`${BASE_URL}${url}`, options);
        if (response.ok) {
            const data = await response.json();
            console.log(`✅ ${name} Success!`);
            // Summarize data shape
            if (Array.isArray(data)) {
                console.log(`   Items: ${data.length}`);
            } else if (typeof data === 'object') {
                console.log(`   Keys: ${Object.keys(data).join(', ')}`);
                if (data.personas) console.log(`   Personas Found: ${data.personas.map(p => p.name).join(', ')}`);
                if (data.wisdom) console.log(`   Wisdom Count: ${data.wisdom.length}`);
            }
        } else {
            console.error(`❌ ${name} Failed with status: ${response.status}`);
        }
    } catch (error) {
        console.error(`❌ ${name} Error:`, error.message);
    }
}

async function runTests() {
    console.log("=== YANTRAX FRONTEND API INTEGRATION TEST ===");

    // 1. AI Firm Status (The Heart)
    await testEndpoint('Firm Status', '/api/ai-firm/status');

    // 2. Persona Registry (Dynamic Cards)
    await testEndpoint('Personas List', '/api/personas');

    // 3. Knowledge Base (Legendary Wisdom)
    await testEndpoint('Knowledge Query', '/api/knowledge/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: 'philosophy', max_results: 1 })
    });

    // 4. Voting History (Top Signals)
    await testEndpoint('Voting History', '/api/ai-firm/voting-history?limit=5');

    // 5. Data Verification Stats (Institutional Grade)
    await testEndpoint('Verification Stats', '/api/data/verification-stats');

    console.log("\n=== TEST SUITE COMPLETE ===");
}

runTests();
