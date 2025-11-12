// Architecture Validation Frontend JavaScript

const API_BASE = '/api';

// Toast notification system
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

// Progress bar utility
const ProgressBar = {
    bar: null,

    create() {
        if (!this.bar) {
            this.bar = document.createElement('div');
            this.bar.id = 'upload-progress';
            this.bar.className = 'progress position-fixed top-0 start-0 w-100';
            this.bar.style.cssText = 'height: 4px; z-index: 9999; border-radius: 0;';
            this.bar.innerHTML = `
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-primary"
                     role="progressbar" style="width: 0%"></div>
            `;
            document.body.appendChild(this.bar);
        }
    },

    show(percent = 0) {
        this.create();
        this.bar.style.display = 'block';
        this.bar.querySelector('.progress-bar').style.width = percent + '%';
    },

    update(percent) {
        if (this.bar) {
            this.bar.querySelector('.progress-bar').style.width = percent + '%';
        }
    },

    hide() {
        if (this.bar) {
            this.update(100);
            setTimeout(() => {
                this.bar.style.display = 'none';
            }, 500);
        }
    }
};

// Show/hide sections with animation
function showSection(section) {
    const validateSection = document.getElementById('validate-section');
    const patternsSection = document.getElementById('patterns-section');

    // Fade out current section
    [validateSection, patternsSection].forEach(s => {
        if (s.style.display !== 'none') {
            s.style.opacity = '0';
            setTimeout(() => {
                s.style.display = 'none';
            }, 300);
        }
    });

    // Fade in new section
    setTimeout(() => {
        if (section === 'validate') {
            validateSection.style.display = 'block';
            setTimeout(() => { validateSection.style.opacity = '1'; }, 10);
        } else if (section === 'patterns') {
            patternsSection.style.display = 'block';
            setTimeout(() => { patternsSection.style.opacity = '1'; }, 10);
            loadPatterns();
        }
    }, 300);
}

// Show loading spinner with backdrop
function showLoading(text = 'Loading...') {
    hideLoading(); // Remove any existing spinner

    const spinner = document.createElement('div');
    spinner.id = 'loading-spinner';
    spinner.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9998;
        animation: fadeIn 0.3s ease;
    `;
    spinner.innerHTML = `
        <div class="text-center text-white">
            <div class="spinner-border mb-3" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div>${text}</div>
        </div>
    `;
    document.body.appendChild(spinner);
}

function hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => spinner.remove(), 300);
    }
}

// Validate Terraform plan
async function validateTerraform() {
    const fileInput = document.getElementById('terraformFile');
    const file = fileInput.files[0];

    if (!file) {
        Toast.warning('Please select a Terraform plan JSON file');
        return;
    }

    // Show progress bar
    ProgressBar.show(10);
    showLoading('Uploading and validating...');

    const formData = new FormData();
    formData.append('file', file);

    try {
        ProgressBar.update(30);

        const response = await fetch(`${API_BASE}/validate/terraform`, {
            method: 'POST',
            body: formData
        });

        ProgressBar.update(70);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Validation failed: ${response.statusText}`);
        }

        const report = await response.json();
        ProgressBar.update(90);

        displayValidationReport(report);

        // Show success toast based on compliance
        const complianceScore = (report.summary.compliance_score * 100).toFixed(0);
        if (complianceScore >= 95) {
            Toast.success(`Excellent! Validation passed with ${complianceScore}% compliance`);
            triggerConfetti();
        } else if (complianceScore >= 85) {
            Toast.success(`Validation completed with ${complianceScore}% compliance`);
        } else if (complianceScore >= 70) {
            Toast.warning(`Validation completed with ${complianceScore}% compliance. Review needed.`);
        } else {
            Toast.error(`Validation found critical issues. Compliance: ${complianceScore}%`);
        }

        // Save to history
        saveValidationToHistory(report);

    } catch (error) {
        Toast.error(`Error: ${error.message}`);
        console.error('Validation error:', error);
    } finally {
        hideLoading();
        ProgressBar.hide();
    }
}

// Validate CMDB application
async function validateCMDB() {
    const appId = document.getElementById('cmdbAppId').value.trim();

    if (!appId) {
        Toast.warning('Please enter an application name or sys_id');
        return;
    }

    ProgressBar.show(10);
    showLoading('Querying CMDB and validating...');

    try {
        ProgressBar.update(30);

        const response = await fetch(`${API_BASE}/validate/cmdb`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ app_id: appId })
        });

        ProgressBar.update(70);

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || response.statusText);
        }

        const report = await response.json();
        ProgressBar.update(90);

        displayValidationReport(report);

        // Show success toast
        const complianceScore = (report.summary.compliance_score * 100).toFixed(0);
        if (complianceScore >= 95) {
            Toast.success(`Excellent! Validation passed with ${complianceScore}% compliance`);
            triggerConfetti();
        } else if (complianceScore >= 85) {
            Toast.success(`Validation completed with ${complianceScore}% compliance`);
        } else {
            Toast.warning(`Validation completed. Compliance: ${complianceScore}%`);
        }

        // Save to history
        saveValidationToHistory(report);

    } catch (error) {
        Toast.error(`Error: ${error.message}`);
        console.error('Validation error:', error);
    } finally {
        hideLoading();
        ProgressBar.hide();
    }
}

// Save validation to history
async function saveValidationToHistory(report) {
    try {
        await fetch(`${API_BASE}/history/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(report)
        });
    } catch (error) {
        console.error('Failed to save validation history:', error);
        // Don't show error to user, this is optional
    }
}

// Confetti animation for excellent results
function triggerConfetti() {
    // Simple confetti effect using CSS
    const colors = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#0dcaf0'];
    const confettiCount = 50;

    for (let i = 0; i < confettiCount; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                top: -10px;
                left: ${Math.random() * 100}%;
                opacity: 1;
                transform: rotate(${Math.random() * 360}deg);
                animation: confettiFall ${2 + Math.random() * 2}s ease-out forwards;
                z-index: 10000;
                pointer-events: none;
            `;
            document.body.appendChild(confetti);

            setTimeout(() => confetti.remove(), 4000);
        }, i * 30);
    }
}

// Add confetti animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes confettiFall {
        to {
            top: 100vh;
            opacity: 0;
            transform: translateY(100vh) rotate(${Math.random() * 360}deg);
        }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(style);

// Display validation report with animations
function displayValidationReport(report) {
    const resultsDiv = document.getElementById('validation-results');
    const contentDiv = document.getElementById('results-content');

    let html = '';

    // Add copy and download buttons at top
    html += `
        <div class="d-flex justify-content-end mb-3 gap-2">
            <button class="btn btn-sm btn-outline-secondary" onclick="copyReportToClipboard()">
                <i class="bi bi-clipboard"></i> Copy Report
            </button>
            <button class="btn btn-sm btn-outline-primary" onclick="downloadReport()">
                <i class="bi bi-download"></i> Download JSON
            </button>
        </div>
    `;

    // Pattern match
    if (report.pattern_match) {
        const score = (report.pattern_match.similarity_score * 100).toFixed(1);
        const scoreClass = score >= 95 ? 'score-high' : score >= 85 ? 'score-medium' : 'score-low';

        html += `
            <div class="row mb-3 animate-fade-in">
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

    // Summary with animated badges
    const summary = report.summary;
    html += `
        <div class="row mb-3">
            <div class="col-3">
                <div class="result-badge result-passed animate-fade-in" style="animation-delay: 0.1s">
                    <div>✓ Passed</div>
                    <div class="fs-4">${summary.passed}</div>
                </div>
            </div>
            <div class="col-3">
                <div class="result-badge result-warning animate-fade-in" style="animation-delay: 0.2s">
                    <div>⚠ Warnings</div>
                    <div class="fs-4">${summary.warnings}</div>
                </div>
            </div>
            <div class="col-3">
                <div class="result-badge result-failed animate-fade-in" style="animation-delay: 0.3s">
                    <div>✗ Violations</div>
                    <div class="fs-4">${summary.failed}</div>
                </div>
            </div>
            <div class="col-3">
                <div class="result-badge animate-fade-in" style="animation-delay: 0.4s">
                    <div>Compliance</div>
                    <div class="fs-4">${(summary.compliance_score * 100).toFixed(0)}%</div>
                </div>
            </div>
        </div>
        <hr>
    `;

    // Critical issues with expandable details
    const criticalResults = report.results.filter(r => r.status === 'failed' && r.severity === 'critical');
    if (criticalResults.length > 0) {
        html += '<h6 class="text-danger animate-fade-in">🔴 Critical Issues</h6>';
        criticalResults.forEach((result, idx) => {
            html += `
                <div class="violation-item violation-critical animate-slide-in" style="animation-delay: ${0.1 * idx}s">
                    <strong>${result.rule_name}</strong> <span class="badge bg-danger">${result.rule_id}</span>
                    <p class="mb-0">${result.message}</p>
                    ${result.resource_name ? `<small class="text-muted">Resource: ${result.resource_name}</small>` : ''}
                </div>
            `;
        });
    }

    // High priority issues
    const highResults = report.results.filter(r => r.status === 'failed' && r.severity === 'high');
    if (highResults.length > 0) {
        html += '<h6 class="text-warning mt-3 animate-fade-in">⚠️ High Priority Issues</h6>';
        highResults.forEach((result, idx) => {
            html += `
                <div class="violation-item violation-high animate-slide-in" style="animation-delay: ${0.1 * idx}s">
                    <strong>${result.rule_name}</strong> <span class="badge bg-warning">${result.rule_id}</span>
                    <p class="mb-0">${result.message}</p>
                    ${result.resource_name ? `<small class="text-muted">Resource: ${result.resource_name}</small>` : ''}
                </div>
            `;
        });
    }

    // Pattern deviations
    if (report.pattern_match && report.pattern_match.deviations.length > 0) {
        html += '<h6 class="mt-3 animate-fade-in">📋 Pattern Deviations</h6>';
        html += '<ul class="animate-fade-in">';
        report.pattern_match.deviations.slice(0, 5).forEach(deviation => {
            html += `<li>${deviation}</li>`;
        });
        if (report.pattern_match.deviations.length > 5) {
            html += `<li class="text-muted">... and ${report.pattern_match.deviations.length - 5} more</li>`;
        }
        html += '</ul>';
    }

    contentDiv.innerHTML = html;

    // Store report for copy/download
    window.currentReport = report;

    // Fade in results
    resultsDiv.style.display = 'none';
    resultsDiv.style.opacity = '0';
    resultsDiv.style.display = 'block';

    setTimeout(() => {
        resultsDiv.style.transition = 'opacity 0.5s ease-in';
        resultsDiv.style.opacity = '1';
    }, 50);

    // Smooth scroll to results
    setTimeout(() => {
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 300);
}

// Copy report to clipboard
function copyReportToClipboard() {
    if (!window.currentReport) {
        Toast.error('No report available to copy');
        return;
    }

    const reportText = generateReportText(window.currentReport);

    navigator.clipboard.writeText(reportText).then(() => {
        Toast.success('Report copied to clipboard!');
    }).catch(err => {
        Toast.error('Failed to copy report');
        console.error('Copy failed:', err);
    });
}

// Download report as JSON
function downloadReport() {
    if (!window.currentReport) {
        Toast.error('No report available to download');
        return;
    }

    const dataStr = JSON.stringify(window.currentReport, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `validation-report-${window.currentReport.id}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    Toast.success('Report downloaded successfully');
}

// Generate text version of report
function generateReportText(report) {
    let text = '=== ARCHITECTURE VALIDATION REPORT ===\n\n';
    text += `Report ID: ${report.id}\n`;
    text += `Timestamp: ${new Date(report.timestamp).toLocaleString()}\n`;
    text += `Source: ${report.source_type}\n\n`;

    if (report.pattern_match) {
        text += `Pattern Match: ${report.pattern_match.pattern_name}\n`;
        text += `Similarity Score: ${(report.pattern_match.similarity_score * 100).toFixed(1)}%\n`;
        text += `Approval Track: ${report.approval_track}\n\n`;
    }

    const summary = report.summary;
    text += `SUMMARY:\n`;
    text += `  Passed: ${summary.passed}\n`;
    text += `  Warnings: ${summary.warnings}\n`;
    text += `  Violations: ${summary.failed}\n`;
    text += `  Compliance Score: ${(summary.compliance_score * 100).toFixed(0)}%\n\n`;

    const criticalResults = report.results.filter(r => r.status === 'failed' && r.severity === 'critical');
    if (criticalResults.length > 0) {
        text += `CRITICAL ISSUES (${criticalResults.length}):\n`;
        criticalResults.forEach(r => {
            text += `  - ${r.rule_id}: ${r.rule_name}\n`;
            text += `    ${r.message}\n`;
        });
        text += '\n';
    }

    const highResults = report.results.filter(r => r.status === 'failed' && r.severity === 'high');
    if (highResults.length > 0) {
        text += `HIGH PRIORITY ISSUES (${highResults.length}):\n`;
        highResults.forEach(r => {
            text += `  - ${r.rule_id}: ${r.rule_name}\n`;
            text += `    ${r.message}\n`;
        });
        text += '\n';
    }

    return text;
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
