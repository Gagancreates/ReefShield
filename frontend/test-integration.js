/**
 * Simple test script to verify backend integration
 * Run with: node test-integration.js
 */

const API_BASE_URL = 'http://localhost:8000/api';

async function testBackendIntegration() {
    console.log('🧪 Testing Frontend-Backend Integration...\n');

    // Test 1: Check if backend is running
    console.log('1️⃣ Testing backend connectivity...');
    try {
        const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('   ✅ Backend is running:', data.service);
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.log('   ❌ Backend not accessible:', error.message);
        console.log('   💡 Make sure to run: cd backend && python run.py');
        return false;
    }

    // Test 2: Test temperature analysis endpoint
    console.log('\n2️⃣ Testing temperature analysis endpoint...');
    try {
        const response = await fetch(`${API_BASE_URL}/temperature/analysis`);
        if (response.ok) {
            const data = await response.json();
            console.log('   ✅ Analysis endpoint working');
            console.log(`   📊 Found ${Object.keys(data.locations).length} locations`);
            console.log(`   📅 Generated at: ${data.generated_at}`);
            
            // Show sample location data
            const firstLocation = Object.values(data.locations)[0];
            if (firstLocation) {
                console.log(`   📍 Sample location: ${firstLocation.location_name}`);
                console.log(`   🌡️ Past data points: ${firstLocation.past_data.length}`);
                console.log(`   🔮 Future predictions: ${firstLocation.future_data.length}`);
            }
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.log('   ❌ Analysis endpoint failed:', error.message);
        return false;
    }

    // Test 3: Test current data endpoint
    console.log('\n3️⃣ Testing current data endpoint...');
    try {
        const response = await fetch(`${API_BASE_URL}/temperature/current`);
        if (response.ok) {
            const data = await response.json();
            console.log('   ✅ Current data endpoint working');
            console.log(`   📊 Found ${Object.keys(data.locations).length} locations`);
            
            // Show current temperatures
            Object.values(data.locations).forEach(location => {
                console.log(`   🌡️ ${location.location_id}: ${location.current_temp}°C (DHW: ${location.dhw}, Risk: ${location.risk_level})`);
            });
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.log('   ❌ Current data endpoint failed:', error.message);
        return false;
    }

    // Test 4: Test locations endpoint
    console.log('\n4️⃣ Testing locations endpoint...');
    try {
        const response = await fetch(`${API_BASE_URL}/temperature/locations`);
        if (response.ok) {
            const data = await response.json();
            console.log('   ✅ Locations endpoint working');
            console.log(`   📍 Configured locations: ${data.locations.length}`);
            
            data.locations.forEach(location => {
                console.log(`   • ${location.name} (${location.id}): ${location.coordinates.lat}°N, ${location.coordinates.lon}°E`);
            });
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.log('   ❌ Locations endpoint failed:', error.message);
        return false;
    }

    console.log('\n🎉 All integration tests passed!');
    console.log('\n📋 Next steps:');
    console.log('   1. Start the frontend: npm run dev');
    console.log('   2. Visit: http://localhost:3000/dashboard');
    console.log('   3. Verify real data is displayed in the dashboard');
    
    return true;
}

// Run the test
testBackendIntegration().catch(error => {
    console.error('❌ Test failed:', error);
    process.exit(1);
});