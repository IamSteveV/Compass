// Dashboard JavaScript

const API_BASE = '/api';

let patternChart = null;
let violationsChart = null;

// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    loadRecentValidations();
});

async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE}/analytics/dashboard/summary`);
        const data = await response.json();

        // Update summary cards
        updateSummaryCards(data.compliance);

        // Update charts
        updatePatternChart(data.popular_patterns);
        updateViolationsChart(data.top_violations);

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Show sample data for demo
        showSampleData();
    }
}

function updateSummaryCards(compliance) {
    document.getElementById('total-validations').textContent =
        compliance.total_validations || '0';

    const avgCompliance = (compliance.avg_compliance_score * 100).toFixed(0);
    const complianceEl = document.getElementById('avg-compliance');
    complianceEl.textContent = avgCompliance + '%';
    complianceEl.className = avgCompliance >= 90 ? 'score-high' :
                            avgCompliance >= 70 ? 'score-medium' : 'score-low';

    document.getElementById('total-violations').textContent =
        compliance.total_violations || '0';

    const passRate = (compliance.pass_rate * 100).toFixed(0);
    document.getElementById('pass-rate').textContent = passRate + '%';
}

function updatePatternChart(patterns) {
    const ctx = document.getElementById('patternChart').getContext('2d');

    if (patternChart) {
        patternChart.destroy();
    }

    const labels = patterns.map(p => p.pattern_name || p.pattern_id);
    const data = patterns.map(p => p.usage_count);

    patternChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Usage Count',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function updateViolationsChart(violations) {
    const ctx = document.getElementById('violationsChart').getContext('2d');

    if (violationsChart) {
        violationsChart.destroy();
    }

    const labels = violations.map(v => v.rule_id);
    const data = violations.map(v => v.violation_count);

    const colors = violations.map(v => {
        switch(v.severity) {
            case 'critical': return 'rgba(220, 53, 69, 0.5)';
            case 'high': return 'rgba(255, 193, 7, 0.5)';
            case 'medium': return 'rgba(13, 202, 240, 0.5)';
            default: return 'rgba(108, 117, 125, 0.5)';
        }
    });

    violationsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Violation Count',
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.5', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

async function loadRecentValidations() {
    try {
        const response = await fetch(`${API_BASE}/analytics/validations/recent?limit=10`);
        const validations = await response.json();

        const tbody = document.getElementById('recent-validations');
        tbody.innerHTML = '';

        if (validations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No validations found</td></tr>';
            return;
        }

        validations.forEach(v => {
            const row = document.createElement('tr');

            const timestamp = new Date(v.timestamp).toLocaleString();
            const compliance = (v.compliance_score * 100).toFixed(0);
            const statusBadge = getStatusBadge(v.overall_status);

            row.innerHTML = `
                <td>${timestamp}</td>
                <td>${v.application_name || '-'}</td>
                <td><span class="badge bg-secondary">${v.environment || '-'}</span></td>
                <td>${v.pattern_name || '-'}</td>
                <td>${compliance}%</td>
                <td>${statusBadge}</td>
            `;
            tbody.appendChild(row);
        });

    } catch (error) {
        console.error('Error loading recent validations:', error);
        document.getElementById('recent-validations').innerHTML =
            '<tr><td colspan="6" class="text-center text-muted">No validation history available yet</td></tr>';
    }
}

function getStatusBadge(status) {
    const badges = {
        'passed': '<span class="badge bg-success">Passed</span>',
        'failed': '<span class="badge bg-danger">Failed</span>',
        'warning': '<span class="badge bg-warning">Warning</span>'
    };
    return badges[status] || status;
}

function showSampleData() {
    // Show sample data for demo when no real data exists
    updateSummaryCards({
        total_validations: 42,
        avg_compliance_score: 0.87,
        total_violations: 15,
        pass_rate: 0.83
    });

    updatePatternChart([
        {pattern_id: 'PAT-001', pattern_name: '3-Tier Web', usage_count: 15},
        {pattern_id: 'PAT-002', pattern_name: 'Microservices', usage_count: 8},
        {pattern_id: 'COMP-001', pattern_name: 'HA Database', usage_count: 12}
    ]);

    updateViolationsChart([
        {rule_id: 'SEC-001', violation_count: 5, severity: 'critical'},
        {rule_id: 'META-001', violation_count: 8, severity: 'high'},
        {rule_id: 'RES-001', violation_count: 3, severity: 'medium'}
    ]);
}
