// Dashboard JavaScript

const API_BASE = '/api';

let patternChart = null;
let violationsChart = null;
let complianceTrendChart = null;
let autoRefreshInterval = null;

// Toast notification system (same as app.js)
const Toast = {
    container: null,

    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container position-fixed top-0 end-0 p-3';
            this.container.style.zIndex = '9999';
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', duration = 5000) {
        this.init();

        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        this.container.appendChild(toastEl);
        const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: duration });
        toast.show();

        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    },

    success(message) { this.show(message, 'success'); },
    error(message) { this.show(message, 'danger', 8000); },
    warning(message) { this.show(message, 'warning'); },
    info(message) { this.show(message, 'info'); }
};

// Auto-refresh controls
function toggleAutoRefresh() {
    const checkbox = document.getElementById('autoRefresh');
    if (checkbox && checkbox.checked) {
        startAutoRefresh();
        Toast.success('Auto-refresh enabled (30 seconds)');
    } else {
        stopAutoRefresh();
        Toast.info('Auto-refresh disabled');
    }
}

function startAutoRefresh() {
    if (autoRefreshInterval) return;
    autoRefreshInterval = setInterval(() => {
        loadDashboardData();
        loadRecentValidations();
    }, 30000); // Refresh every 30 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Manual refresh
function refreshDashboard() {
    Toast.info('Refreshing dashboard...');
    loadDashboardData();
    loadRecentValidations();
}

// Export dashboard data
function exportDashboardData() {
    if (!window.dashboardData) {
        Toast.error('No data available to export');
        return;
    }

    const dataStr = JSON.stringify(window.dashboardData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `dashboard-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    Toast.success('Dashboard data exported successfully');
}

// Check system health
async function checkSystemHealth() {
    try {
        const response = await fetch('/health');
        const health = await response.json();

        const statusDiv = document.getElementById('systemStatus');
        const statusMessage = document.getElementById('statusMessage');
        const statusSpinner = document.getElementById('statusSpinner');

        if (!statusDiv || !statusMessage) return;

        // Remove existing classes
        statusDiv.className = 'alert d-flex align-items-center';

        if (health.status === 'healthy') {
            statusDiv.classList.add('alert-success');
            statusMessage.innerHTML = `<strong>System Healthy</strong> - ${health.components.validation_engine.rules_count} rules, ${health.components.pattern_library.patterns_count} patterns loaded`;
            statusSpinner.style.display = 'none';
        } else if (health.status === 'degraded') {
            statusDiv.classList.add('alert-warning');
            statusMessage.innerHTML = '<strong>System Degraded</strong> - Some components may not be fully functional';
            statusSpinner.style.display = 'none';
        } else {
            statusDiv.classList.add('alert-danger');
            statusMessage.innerHTML = '<strong>System Unhealthy</strong> - Please check logs';
            statusSpinner.style.display = 'none';
        }

        statusDiv.style.display = 'flex';

        // Auto-hide after 10 seconds if healthy
        if (health.status === 'healthy') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 10000);
        }

    } catch (error) {
        console.error('Failed to check system health:', error);
        const statusDiv = document.getElementById('systemStatus');
        const statusMessage = document.getElementById('statusMessage');

        if (statusDiv && statusMessage) {
            statusDiv.className = 'alert alert-danger d-flex align-items-center';
            statusMessage.innerHTML = '<strong>Cannot reach API</strong> - System may be offline';
            statusDiv.style.display = 'flex';
        }
    }
}

// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check system health first
    checkSystemHealth();

    loadDashboardData();
    loadRecentValidations();

    // Add refresh button if not exists
    addDashboardControls();
});

// Add dashboard control buttons
function addDashboardControls() {
    const header = document.querySelector('.container h1') || document.querySelector('h1');
    if (!header) return;

    const controlsDiv = document.createElement('div');
    controlsDiv.className = 'd-flex justify-content-between align-items-center mb-4';
    controlsDiv.innerHTML = `
        <h1 class="mb-0">Analytics Dashboard</h1>
        <div class="d-flex gap-2 align-items-center">
            <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" id="autoRefresh" onchange="toggleAutoRefresh()">
                <label class="form-check-label" for="autoRefresh">Auto-refresh</label>
            </div>
            <button class="btn btn-sm btn-outline-primary" onclick="refreshDashboard()">
                <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
            <button class="btn btn-sm btn-outline-secondary" onclick="exportDashboardData()">
                <i class="bi bi-download"></i> Export
            </button>
        </div>
    `;

    // Replace the h1 with our controls
    if (header.tagName === 'H1') {
        header.replaceWith(controlsDiv);
    } else {
        header.parentNode.insertBefore(controlsDiv, header);
        header.remove();
    }
}

async function loadDashboardData() {
    try {
        // Show loading skeleton
        showLoadingSkeleton();

        const response = await fetch(`${API_BASE}/analytics/dashboard/summary`);

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        const data = await response.json();

        // Store data globally for export
        window.dashboardData = data;

        // Update summary cards with animation
        updateSummaryCards(data.compliance);

        // Update charts
        updatePatternChart(data.popular_patterns);
        updateViolationsChart(data.top_violations);

        // Hide loading skeleton
        hideLoadingSkeleton();

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        Toast.warning('Using sample data - connect to API for live data');
        // Show sample data for demo
        showSampleData();
        hideLoadingSkeleton();
    }
}

// Loading skeleton
function showLoadingSkeleton() {
    const cards = document.querySelectorAll('.col-md-3 h2, .col-md-3 h6');
    cards.forEach(card => {
        if (!card.dataset.originalContent) {
            card.dataset.originalContent = card.textContent;
            card.innerHTML = '<span class="placeholder col-8 bg-secondary"></span>';
        }
    });
}

function hideLoadingSkeleton() {
    const cards = document.querySelectorAll('.col-md-3 h2, .col-md-3 h6');
    cards.forEach(card => {
        if (card.dataset.originalContent) {
            // Restore will happen via updateSummaryCards
            delete card.dataset.originalContent;
        }
    });
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

    // Generate gradient colors
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(54, 162, 235, 0.8)');
    gradient.addColorStop(1, 'rgba(54, 162, 235, 0.2)');

    patternChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Usage Count',
                data: data,
                backgroundColor: gradient,
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                borderRadius: 8,
                hoverBackgroundColor: 'rgba(54, 162, 235, 0.9)',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return `Used ${context.parsed.y} time${context.parsed.y !== 1 ? 's' : ''}`;
                        },
                        afterLabel: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed.y / total) * 100).toFixed(1);
                            return `${percentage}% of total usage`;
                        }
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
            case 'critical': return 'rgba(220, 53, 69, 0.7)';
            case 'high': return 'rgba(255, 193, 7, 0.7)';
            case 'medium': return 'rgba(13, 202, 240, 0.7)';
            default: return 'rgba(108, 117, 125, 0.7)';
        }
    });

    const borderColors = violations.map(v => {
        switch(v.severity) {
            case 'critical': return 'rgba(220, 53, 69, 1)';
            case 'high': return 'rgba(255, 193, 7, 1)';
            case 'medium': return 'rgba(13, 202, 240, 1)';
            default: return 'rgba(108, 117, 125, 1)';
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
                borderColor: borderColors,
                borderWidth: 2,
                borderRadius: 8,
                hoverBackgroundColor: colors.map(c => c.replace('0.7', '0.9')),
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart',
                delay: (context) => {
                    return context.dataIndex * 100;
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const violation = violations[context.dataIndex];
                            return `${context.parsed.y} violation${context.parsed.y !== 1 ? 's' : ''}`;
                        },
                        afterLabel: function(context) {
                            const violation = violations[context.dataIndex];
                            return [
                                `Severity: ${violation.severity.toUpperCase()}`,
                                `Rule: ${violation.rule_name || violation.rule_id}`
                            ];
                        }
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
