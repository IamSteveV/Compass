// Architecture Validation Frontend JavaScript

const API_BASE = '/api';

// Show/hide sections
function showSection(section) {
    document.getElementById('validate-section').style.display = section === 'validate' ? 'block' : 'none';
    document.getElementById('patterns-section').style.display = section === 'patterns' ? 'block' : 'none';

    if (section === 'patterns') {
        loadPatterns();
    }
}

// Show loading spinner
function showLoading() {
    const spinner = document.createElement('div');
    spinner.id = 'loading-spinner';
    spinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.body.appendChild(spinner);
}

function hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Validate Terraform plan
async function validateTerraform() {
    const fileInput = document.getElementById('terraformFile');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a Terraform plan JSON file');
        return;
    }

    showLoading();

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/validate/terraform`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Validation failed: ${response.statusText}`);
        }

        const report = await response.json();
        displayValidationReport(report);
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Validate CMDB application
async function validateCMDB() {
    const appId = document.getElementById('cmdbAppId').value.trim();

    if (!appId) {
        alert('Please enter an application name or sys_id');
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/validate/cmdb`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ app_id: appId })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || response.statusText);
        }

        const report = await response.json();
        displayValidationReport(report);
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Display validation report
function displayValidationReport(report) {
    const resultsDiv = document.getElementById('validation-results');
    const contentDiv = document.getElementById('results-content');

    let html = '';

    // Pattern match
    if (report.pattern_match) {
        const score = (report.pattern_match.similarity_score * 100).toFixed(1);
        const scoreClass = score >= 95 ? 'score-high' : score >= 85 ? 'score-medium' : 'score-low';

        html += `
            <div class="row mb-3">
                <div class="col-md-6">
                    <h6>Pattern Match</h6>
                    <p class="mb-1"><strong>${report.pattern_match.pattern_name}</strong></p>
                    <p class="compliance-score ${scoreClass}">${score}%</p>
                </div>
                <div class="col-md-6">
                    <h6>Approval Track</h6>
                    <p class="fs-5">
                        ${getApprovalTrackBadge(report.approval_track)}
                    </p>
                </div>
            </div>
            <hr>
        `;
    }

    // Summary
    const summary = report.summary;
    html += `
        <div class="row mb-3">
            <div class="col-3">
                <div class="result-badge result-passed">
                    <div>✓ Passed</div>
                    <div class="fs-4">${summary.passed}</div>
                </div>
            </div>
            <div class="col-3">
                <div class="result-badge result-warning">
                    <div>⚠ Warnings</div>
                    <div class="fs-4">${summary.warnings}</div>
                </div>
            </div>
            <div class="col-3">
                <div class="result-badge result-failed">
                    <div>✗ Violations</div>
                    <div class="fs-4">${summary.failed}</div>
                </div>
            </div>
            <div class="col-3">
                <div class="result-badge">
                    <div>Compliance</div>
                    <div class="fs-4">${(summary.compliance_score * 100).toFixed(0)}%</div>
                </div>
            </div>
        </div>
        <hr>
    `;

    // Critical issues
    const criticalResults = report.results.filter(r => r.status === 'failed' && r.severity === 'critical');
    if (criticalResults.length > 0) {
        html += '<h6 class="text-danger">Critical Issues</h6>';
        criticalResults.forEach(result => {
            html += `
                <div class="violation-item violation-critical">
                    <strong>${result.rule_name}</strong> (${result.rule_id})
                    <p class="mb-0">${result.message}</p>
                </div>
            `;
        });
    }

    // High priority issues
    const highResults = report.results.filter(r => r.status === 'failed' && r.severity === 'high');
    if (highResults.length > 0) {
        html += '<h6 class="text-warning mt-3">High Priority Issues</h6>';
        highResults.forEach(result => {
            html += `
                <div class="violation-item violation-high">
                    <strong>${result.rule_name}</strong> (${result.rule_id})
                    <p class="mb-0">${result.message}</p>
                </div>
            `;
        });
    }

    // Pattern deviations
    if (report.pattern_match && report.pattern_match.deviations.length > 0) {
        html += '<h6 class="mt-3">Pattern Deviations</h6>';
        html += '<ul>';
        report.pattern_match.deviations.slice(0, 5).forEach(deviation => {
            html += `<li>${deviation}</li>`;
        });
        if (report.pattern_match.deviations.length > 5) {
            html += `<li class="text-muted">... and ${report.pattern_match.deviations.length - 5} more</li>`;
        }
        html += '</ul>';
    }

    contentDiv.innerHTML = html;
    resultsDiv.style.display = 'block';

    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

function getApprovalTrackBadge(track) {
    const badges = {
        'fast_track': '<span class="badge bg-success fs-6">FAST TRACK ✓</span>',
        'standard_review': '<span class="badge bg-warning fs-6">STANDARD REVIEW</span>',
        'full_review': '<span class="badge bg-danger fs-6">FULL REVIEW</span>'
    };
    return badges[track] || track;
}

// Load patterns
async function loadPatterns() {
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/patterns/?status=approved`);
        const patterns = await response.json();

        const listDiv = document.getElementById('patterns-list');
        listDiv.innerHTML = '';

        patterns.forEach(pattern => {
            const card = document.createElement('div');
            card.className = 'col-md-4 mb-3';
            card.innerHTML = `
                <div class="card pattern-card" onclick="showPatternDetails('${pattern.metadata.id}')">
                    <div class="card-body">
                        <h5 class="card-title">${pattern.metadata.name}</h5>
                        <p class="card-text text-muted">${pattern.metadata.description.substring(0, 100)}...</p>
                        <div>
                            <span class="badge bg-primary">${pattern.metadata.id}</span>
                            <span class="badge bg-success">v${pattern.metadata.version}</span>
                        </div>
                    </div>
                </div>
            `;
            listDiv.appendChild(card);
        });
    } catch (error) {
        alert(`Error loading patterns: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Show pattern details
async function showPatternDetails(patternId) {
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/patterns/${patternId}`);
        const pattern = await response.json();

        document.getElementById('patternModalTitle').textContent = pattern.metadata.name;

        let html = `
            <div class="mb-3">
                <strong>ID:</strong> ${pattern.metadata.id} |
                <strong>Version:</strong> ${pattern.metadata.version} |
                <strong>Status:</strong> <span class="badge bg-success">${pattern.metadata.status}</span>
            </div>
            <div class="mb-3">
                <h6>Description</h6>
                <p>${pattern.metadata.description}</p>
            </div>
            <div class="mb-3">
                <h6>Components</h6>
                <ul>
                    ${pattern.architecture.components.map(c => `<li><strong>${c.name}</strong> (${c.type})</li>`).join('')}
                </ul>
            </div>
            <div class="mb-3">
                <h6>Terraform Module</h6>
                <code>${pattern.implementation.terraform_module}</code>
            </div>
        `;

        document.getElementById('patternModalBody').innerHTML = html;

        const modal = new bootstrap.Modal(document.getElementById('patternModal'));
        modal.show();
    } catch (error) {
        alert(`Error loading pattern details: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Architecture Validation System loaded');
});
