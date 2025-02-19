// Global chart instances
let energyChart;
let carbonChart;

// Configuration and utilities
const CONFIG = {
    API_ENDPOINTS: {
        ENERGY_USAGE: '/api/energy-usage',
        CARBON_FOOTPRINT: '/api/carbon-footprint',
        TIPS: '/api/tips',
        LEADERBOARD: '/api/leaderboard'
    },
    CHART_COLORS: {
        PRIMARY: '#4CAF50',
        SECONDARY: '#2196F3',
        DANGER: '#f44336',
        WARNING: '#ff9800'
    }
};

// Initialize everything when the document loads
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupEventListeners();
    initializeRealTimeUpdates();
});

// Chart initialization
function initializeCharts() {
    initializeEnergyChart();
    initializeCarbonChart();
}

function initializeEnergyChart() {
    const ctx = document.getElementById('energyChart').getContext('2d');
    const energyData = JSON.parse(document.getElementById('energyChart').dataset.usage || '[]');

    energyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: energyData.map(d => formatDate(d.date)),
            datasets: [{
                label: 'Energy Usage (kWh)',
                data: energyData.map(d => d.usage_amount),
                borderColor: CONFIG.CHART_COLORS.PRIMARY,
                backgroundColor: `${CONFIG.CHART_COLORS.PRIMARY}20`,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Energy Usage (kWh)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

function initializeCarbonChart() {
    const ctx = document.getElementById('carbonChart').getContext('2d');
    const carbonData = JSON.parse(document.getElementById('carbonChart').dataset.footprint || '[]');

    carbonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: carbonData.map(d => formatDate(d.date)),
            datasets: [{
                label: 'Carbon Footprint (kg CO₂)',
                data: carbonData.map(d => d.emissions),
                backgroundColor: CONFIG.CHART_COLORS.SECONDARY,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'CO₂ Emissions (kg)'
                    }
                }
            }
        }
    });
}

// Event Listeners
function setupEventListeners() {
    // Energy usage logging
    const logUsageBtn = document.getElementById('logUsageBtn');
    if (logUsageBtn) {
        logUsageBtn.addEventListener('click', logNewUsage);
    }

    // Carbon footprint calculation
    const calculateFootprintBtn = document.getElementById('calculateFootprintBtn');
    if (calculateFootprintBtn) {
        calculateFootprintBtn.addEventListener('click', calculateFootprint);
    }

    // Tips interaction
    setupTipInteractions();

    // Form submissions
    setupFormHandlers();
}

// Energy Usage Functions
async function logNewUsage() {
    const usageForm = document.getElementById('usageForm');
    const usageInput = usageForm.querySelector('input[name="usage"]');
    const usage = parseFloat(usageInput.value);

    if (isNaN(usage) || usage < 0) {
        showNotification('Please enter a valid energy usage value', 'error');
        return;
    }

    try {
        const response = await fetch(CONFIG.API_ENDPOINTS.ENERGY_USAGE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ usage })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Energy usage logged successfully!', 'success');
            updateEnergyChart(data.usage_data);
            updateEcoPoints(data.eco_points);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        showNotification(`Failed to log energy usage: ${error.message}`, 'error');
    }
}

// Carbon Footprint Functions
async function calculateFootprint() {
    const footprintForm = document.getElementById('footprintForm');
    const formData = new FormData(footprintForm);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch(CONFIG.API_ENDPOINTS.CARBON_FOOTPRINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            updateCarbonChart(result.footprint_data);
            showNotification('Carbon footprint calculated successfully!', 'success');
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        showNotification(`Failed to calculate carbon footprint: ${error.message}`, 'error');
    }
}

// Tips and Community Functions
function setupTipInteractions() {
    document.querySelectorAll('.tip-like-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const tipId = e.currentTarget.dataset.tipId;
            await toggleTipLike(tipId);
        });
    });

    const tipForm = document.getElementById('tipForm');
    if (tipForm) {
        tipForm.addEventListener('submit', submitNewTip);
    }
}

async function toggleTipLike(tipId) {
    try {
        const response = await fetch(`${CONFIG.API_ENDPOINTS.TIPS}/${tipId}/like`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            updateTipLikes(tipId, data.likes);
            showNotification('Tip like updated!', 'success');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        showNotification(`Failed to update like: ${error.message}`, 'error');
    }
}

async function submitNewTip(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const tipContent = formData.get('tip');

    try {
        const response = await fetch(CONFIG.API_ENDPOINTS.TIPS, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tip: tipContent })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Tip submitted successfully!', 'success');
            updateTipsList(data.tips);
            e.target.reset();
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        showNotification(`Failed to submit tip: ${error.message}`, 'error');
    }
}

// UI Update Functions
function updateEnergyChart(newData) {
    if (energyChart) {
        energyChart.data.labels = newData.map(d => formatDate(d.date));
        energyChart.data.datasets[0].data = newData.map(d => d.usage_amount);
        energyChart.update();
    }
}

function updateCarbonChart(newData) {
    if (carbonChart) {
        carbonChart.data.labels = newData.map(d => formatDate(d.date));
        carbonChart.data.datasets[0].data = newData.map(d => d.emissions);
        carbonChart.update();
    }
}

function updateTipLikes(tipId, likes) {
    const likeCounter = document.querySelector(`[data-tip-id="${tipId}"] .likes-count`);
    if (likeCounter) {
        likeCounter.textContent = likes;
    }
}

function updateTipsList(tips) {
    const tipsContainer = document.querySelector('.tips-container');
    if (tipsContainer) {
        tipsContainer.innerHTML = tips.map(tip => `
            <div class="tip-card">
                <p>${tip.content}</p>
                <div class="tip-meta">
                    <span>By ${tip.username}</span>
                    <span class="likes-count">${tip.likes} likes</span>
                    <button class="tip-like-btn" data-tip-id="${tip.id}">
                        Like
                    </button>
                </div>
            </div>
        `).join('');
        setupTipInteractions();
    }
}

function updateEcoPoints(points) {
    const pointsDisplay = document.querySelector('.eco-points');
    if (pointsDisplay) {
        pointsDisplay.textContent = `${points} Points`;
    }
}

// Utility Functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Real-time updates
function initializeRealTimeUpdates() {
    // Update leaderboard every 5 minutes
    setInterval(async () => {
        try {
            const response = await fetch(CONFIG.API_ENDPOINTS.LEADERBOARD);
            const data = await response.json();
            if (response.ok) {
                updateLeaderboard(data);
            }
        } catch (error) {
            console.error('Failed to update leaderboard:', error);
        }
    }, 300000); // 5 minutes
}

function updateLeaderboard(leaderboardData) {
    const leaderboardContainer = document.querySelector('.leaderboard');
    if (leaderboardContainer) {
        leaderboardContainer.innerHTML = leaderboardData.map((user, index) => `
            <div class="leaderboard-item">
                <span class="rank">${index + 1}</span>
                <span class="username">${user.username}</span>
                <span class="points">${user.eco_points} pts</span>
            </div>
        `).join('');
    }
}

// Form handling
function setupFormHandlers() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            
            try {
                const response = await fetch(form.action, {
                    method: form.method,
                    body: form.method.toLowerCase() === 'get' ? null : formData
                });

                const data = await response.json();

                if (response.ok) {
                    showNotification('Form submitted successfully!', 'success');
                    if (form.dataset.reload === 'true') {
                        location.reload();
                    }
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                showNotification(`Form submission failed: ${error.message}`, 'error');
            }
        });
    });
}