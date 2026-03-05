// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State management
let currentContract = '';
let currentClauses = [];
let currentModel = 'mistral';

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    checkModelStatus();
});

async function initializeApp() {
    // Get DOM elements
    const form = document.getElementById('contract-form');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');
    const validateBtn = document.getElementById('validate-btn');
    const modelSelect = document.getElementById('model-select');

    // Event listeners
    form.addEventListener('submit', handleFormSubmit);
    copyBtn.addEventListener('click', copyContract);
    downloadBtn.addEventListener('click', downloadContract);
    validateBtn.addEventListener('click', validateContract);
    modelSelect.addEventListener('change', switchModel);

    // Load available models
    await loadAvailableModels();
}

async function checkModelStatus() {
    const statusBadge = document.getElementById('model-status');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy' && data.model_loaded) {
            statusBadge.innerHTML = '<i class="fas fa-circle" style="color: #22c55e"></i> Local AI Agent Ready';
            statusBadge.className = 'status-badge online';
            showToast('Connected to local LLM agent', 'success');
        } else {
            statusBadge.innerHTML = '<i class="fas fa-circle" style="color: #ef4444"></i> Model Not Loaded - Check Ollama';
            statusBadge.className = 'status-badge offline';
            showToast('Model not loaded. Make sure Ollama is running.', 'error');
        }
    } catch (error) {
        statusBadge.innerHTML = '<i class="fas fa-circle" style="color: #ef4444"></i> Backend Not Connected';
        statusBadge.className = 'status-badge offline';
        showToast('Cannot connect to backend. Make sure the server is running.', 'error');
        console.error('Health check failed:', error);
    }
}

async function loadAvailableModels() {
    try {
        const response = await fetch(`${API_BASE_URL}/models`);
        const data = await response.json();
        
        const modelSelect = document.getElementById('model-select');
        const models = data.models || [];
        
        // Clear existing options
        modelSelect.innerHTML = '';
        
        // Add available models
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model.charAt(0).toUpperCase() + model.slice(1);
            modelSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load models:', error);
    }
}

async function switchModel(event) {
    const modelName = event.target.value;
    const generateBtn = document.getElementById('generate-btn');
    
    try {
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Switching Model...';
        
        const response = await fetch(`${API_BASE_URL}/switch-model/${modelName}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentModel = modelName;
            showToast(`Switched to ${modelName} model`, 'success');
        } else {
            showToast(`Failed to switch model: ${data.detail}`, 'error');
        }
    } catch (error) {
        showToast('Error switching model', 'error');
        console.error('Switch model error:', error);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Contract';
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Get form values
    const contractData = {
        contractType: document.getElementById('contract-type').value,
        parties: {
            party1: document.getElementById('party1').value,
            party2: document.getElementById('party2').value,
            party1_details: parseDetails(document.getElementById('party1-details').value),
            party2_details: parseDetails(document.getElementById('party2-details').value)
        },
        terms: document.getElementById('terms').value,
        duration: document.getElementById('duration').value,
        penalty: document.getElementById('penalty').value,
        language: document.getElementById('language').value,
        jurisdiction: document.getElementById('jurisdiction').value,
        additional_clauses: document.getElementById('additional-clauses').value
    };
    
    // Validate required fields
    if (!contractData.contractType || !contractData.parties.party1 || !contractData.parties.party2 || !contractData.terms) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    // Generate contract
    await generateContract(contractData);
}

function parseDetails(detailsText) {
    if (!detailsText) return {};
    
    const details = {};
    const lines = detailsText.split('\n');
    
    lines.forEach(line => {
        const [key, value] = line.split(':').map(s => s.trim());
        if (key && value) {
            details[key] = value;
        }
    });
    
    return details;
}

async function generateContract(contractData) {
    // Show loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('empty-state').classList.add('hidden');
    document.getElementById('contract-display').classList.add('hidden');
    document.getElementById('generate-btn').disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate-contract`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(contractData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayContract(data);
            enableOutputButtons(true);
            showToast('Contract generated successfully!', 'success');
        } else {
            throw new Error('Generation failed');
        }
    } catch (error) {
        console.error('Generation error:', error);
        showToast('Failed to generate contract. Check backend connection.', 'error');
        document.getElementById('empty-state').classList.remove('hidden');
    } finally {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('generate-btn').disabled = false;
    }
}

function displayContract(data) {
    // Store current contract
    currentContract = data.contract;
    currentClauses = data.clauses || [];
    
    // Display contract
    const contractContent = document.getElementById('contract-content');
    contractContent.textContent = data.contract;
    
    // Display clauses
    const clausesList = document.getElementById('clauses-list');
    clausesList.innerHTML = '';
    data.clauses.forEach(clause => {
        const li = document.createElement('li');
        li.textContent = clause;
        clausesList.appendChild(li);
    });
    
    // Display summary
    document.getElementById('summary-text').textContent = data.summary;
    
    // Display warnings if any
    if (data.warnings && data.warnings.length > 0) {
        const warningsSection = document.getElementById('warnings-section');
        const warningsList = document.getElementById('warnings-list');
        
        warningsList.innerHTML = '';
        data.warnings.forEach(warning => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${warning}`;
            warningsList.appendChild(li);
        });
        
        warningsSection.classList.remove('hidden');
    } else {
        document.getElementById('warnings-section').classList.add('hidden');
    }
    
    // Show contract display
    document.getElementById('contract-display').classList.remove('hidden');
    document.getElementById('empty-state').classList.add('hidden');
}

function enableOutputButtons(enabled) {
    const buttons = ['copy-btn', 'download-btn', 'validate-btn'];
    buttons.forEach(id => {
        document.getElementById(id).disabled = !enabled;
    });
}

async function copyContract() {
    try {
        await navigator.clipboard.writeText(currentContract);
        showToast('Contract copied to clipboard!', 'success');
    } catch (error) {
        showToast('Failed to copy contract', 'error');
    }
}

function downloadContract() {
    const blob = new Blob([currentContract], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `contract_${new Date().toISOString().slice(0,10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showToast('Contract downloaded!', 'success');
}

async function validateContract() {
    if (!currentContract) return;
    
    showToast('Validating contract...', 'warning');
    
    try {
        const response = await fetch(`${API_BASE_URL}/validate-contract`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ contract_text: currentContract })
        });
        
        const data = await response.json();
        
        // Display validation results in a modal or alert
        alert(`Validation Report:\n\n${data.report}`);
    } catch (error) {
        showToast('Validation failed', 'error');
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Periodic status check
setInterval(checkModelStatus, 30000); // Check every 30 seconds