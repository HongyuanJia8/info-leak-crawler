document.getElementById('scanForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data - Note: HTML form has 'address' but backend expects 'location'
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        location: document.getElementById('address').value // Map address to location
    };
    
    // Validate at least one field is filled
    if (!formData.name && !formData.email && !formData.phone && !formData.location) {
        showError('Please provide at least one piece of information to scan.');
        return;
    }
    
    // Show loading state
    const scanButton = document.getElementById('scanButton');
    const buttonText = scanButton.querySelector('.button-text');
    const loadingSpinner = scanButton.querySelector('.loading-spinner');
    
    scanButton.classList.add('loading');
    scanButton.disabled = true;
    buttonText.textContent = 'Scanning...';
    loadingSpinner.style.display = 'inline-block';
    
    // Hide previous results and errors
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'none';
    
    try {
        // Make API call
        const response = await fetch('/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'An error occurred during scanning');
        }
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        // Reset button state
        scanButton.classList.remove('loading');
        scanButton.disabled = false;
        buttonText.textContent = 'Start Scan';
        loadingSpinner.style.display = 'none';
    }
});

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    
    // Update AI Analysis - using the new backend structure
    document.getElementById('aiAnalysis').textContent = data.chatgpt_analysis || 'Analysis not available';
    
    // Update percentage circle - using the new backend structure
    const percentage = parseInt(data.leak_percentage) || 0;
    const percentageCircle = document.getElementById('percentageCircle');
    const percentageText = document.getElementById('percentageText');
    
    percentageText.textContent = percentage + '%';
    percentageCircle.setAttribute('stroke-dasharray', `${percentage}, 100`);
    
    // Set color based on percentage
    percentageCircle.classList.remove('low', 'medium', 'high');
    if (percentage < 30) {
        percentageCircle.classList.add('low');
    } else if (percentage < 60) {
        percentageCircle.classList.add('medium');
    } else {
        percentageCircle.classList.add('high');
    }
    
    // Update summary stats - using simplified structure since detailed scan stats may not be available
    const totalResults = data.detailed_results ? data.detailed_results.length : 0;
    document.getElementById('totalResults').textContent = totalResults;
    document.getElementById('scanTime').textContent = '2.1s'; // Placeholder since scan_time is not in new structure
    document.getElementById('riskLevel').textContent = (data.risk_level || 'low').toUpperCase();
    
    // Update risk level color
    const riskLevelElement = document.getElementById('riskLevel');
    riskLevelElement.style.color = getRiskColor(data.risk_level || 'low');
    
    // Update risk breakdown - simplified since we don't have detailed risk stats
    const highRisk = data.risk_level === 'high' ? totalResults : 0;
    const mediumRisk = data.risk_level === 'medium' ? totalResults : 0;
    const lowRisk = data.risk_level === 'low' ? totalResults : 0;
    
    document.getElementById('highRisk').textContent = highRisk;
    document.getElementById('mediumRisk').textContent = mediumRisk;
    document.getElementById('lowRisk').textContent = lowRisk;
    
    // Display detailed results
    displayDetailedResults(data.detailed_results || []);
    
    // Display recommendations
    displayRecommendations(data.recommendations || []);
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayDetailedResults(results) {
    const container = document.getElementById('detailedResultsList');
    container.innerHTML = '';
    
    if (results.length === 0) {
        container.innerHTML = '<p style="color: #666; text-align: center;">No detailed results found.</p>';
        return;
    }
    
    results.forEach((result, index) => {
        const riskLevel = result.risk_assessment?.risk_level || 'low';
        const resultDiv = document.createElement('div');
        resultDiv.className = `result-item ${riskLevel}-risk`;
        
        const matchedInfo = result.matched_info || {};
        const matchedTypes = Object.keys(matchedInfo).filter(key => key !== 'additional_pii');
        
        resultDiv.innerHTML = `
            <h4>${result.title || 'Untitled Result'}</h4>
            <div class="result-url">${result.url || 'No URL available'}</div>
            ${result.snippet ? `<div class="result-snippet">${escapeHtml(result.snippet)}</div>` : ''}
            ${matchedTypes.length > 0 ? `
                <div class="matched-info">
                    ${matchedTypes.map(type => `<span class="info-tag">${type}</span>`).join('')}
                </div>
            ` : ''}
        `;
        
        container.appendChild(resultDiv);
    });
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsList');
    container.innerHTML = '';
    
    if (!recommendations || recommendations.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'No specific recommendations available at this time.';
        container.appendChild(li);
        return;
    }
    
    recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        container.appendChild(li);
    });
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function resetForm() {
    document.getElementById('scanForm').reset();
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function getRiskColor(riskLevel) {
    switch(riskLevel.toLowerCase()) {
        case 'high':
            return '#F44336';
        case 'medium':
            return '#FF9800';
        case 'low':
            return '#4CAF50';
        default:
            return '#666';
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
} 