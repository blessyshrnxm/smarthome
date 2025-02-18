// Select necessary DOM elements
const energyForm = document.getElementById('energyForm');
const totalConsumptionEl = document.getElementById('totalConsumption');
const energyChartEl = document.getElementById('energyChart').getContext('2d');

// Variables for tracking data
let totalConsumption = 0;
let appliances = [];
let consumptionData = [];
let applianceLabels = [];

// Create the chart
const energyChart = new Chart(energyChartEl, {
    type: 'bar',
    data: {
        labels: applianceLabels,
        datasets: [{
            label: 'Energy Consumption (kWh)',
            data: consumptionData,
            backgroundColor: 'rgba(52, 152, 219, 0.7)',
            borderColor: 'rgba(52, 152, 219, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Form submission handling
energyForm.addEventListener('submit', function(event) {
    event.preventDefault();

    // Get user input
    const appliance = document.getElementById('appliance').value;
    const hoursUsed = parseFloat(document.getElementById('hoursUsed').value);
    const powerRating = parseFloat(document.getElementById('powerRating').value);

    if (appliance && hoursUsed && powerRating) {
        // Calculate energy consumption
        const energyUsed = hoursUsed * powerRating;

        // Update total consumption
        totalConsumption += energyUsed;
        totalConsumptionEl.textContent = `Total Consumption: ${totalConsumption.toFixed(2)} kWh`;

        // Add appliance data to chart
        appliances.push(appliance);
        consumptionData.push(energyUsed);
        applianceLabels.push(appliance);

        // Update the chart
        energyChart.update();

        // Clear the form for new inputs
        energyForm.reset();
    } else {
        alert('Please fill in all the fields!');
    }
});
