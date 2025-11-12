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
    const notificationsSection = document.getElementById('notifications-section');
    const terraformCloudSection = document.getElementById('terraform-cloud-section');
    const analyticsSection = document.getElementById('analytics-section');
    const resourceGraphSection = document.getElementById('resource-graph-section');
    const settingsSection = document.getElementById('settings-section');

    // Fade out current section
    [validateSection, patternsSection, notificationsSection, terraformCloudSection, analyticsSection, resourceGraphSection, settingsSection].forEach(s => {
        if (s && s.style.display !== 'none') {
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
        } else if (section === 'notifications') {
            notificationsSection.style.display = 'block';
            setTimeout(() => { notificationsSection.style.opacity = '1'; }, 10);
            loadNotificationSettings();
        } else if (section === 'terraform-cloud') {
            terraformCloudSection.style.display = 'block';
            setTimeout(() => { terraformCloudSection.style.opacity = '1'; }, 10);
        } else if (section === 'analytics') {
            analyticsSection.style.display = 'block';
            setTimeout(() => { analyticsSection.style.opacity = '1'; }, 10);
        } else if (section === 'resource-graph') {
            resourceGraphSection.style.display = 'block';
            setTimeout(() => { resourceGraphSection.style.opacity = '1'; }, 10);
            populateHistoryValidationSelect();
        } else if (section === 'settings') {
            settingsSection.style.display = 'block';
            setTimeout(() => { settingsSection.style.opacity = '1'; }, 10);
            loadValidationRules();
            loadSystemSettings();
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
            <button class="btn btn-sm btn-outline-danger" onclick="downloadPDFReport()">
                <i class="bi bi-file-pdf"></i> Download PDF
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

    // Enable manual notification button
    const sendNotificationBtn = document.getElementById('sendNotificationBtn');
    if (sendNotificationBtn) {
        sendNotificationBtn.disabled = false;
    }

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

// Download report as PDF
async function downloadPDFReport() {
    if (!window.currentReport) {
        Toast.error('No report available to download');
        return;
    }

    try {
        Toast.info('Generating PDF report...');

        const response = await fetch(`${API_BASE}/reports/generate-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(window.currentReport)
        });

        if (!response.ok) {
            throw new Error(`PDF generation failed: ${response.statusText}`);
        }

        // Get PDF blob
        const blob = await response.blob();

        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `validation-report-${window.currentReport.id}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        Toast.success('PDF report downloaded successfully');

    } catch (error) {
        Toast.error(`Failed to generate PDF: ${error.message}`);
        console.error('PDF generation error:', error);
    }
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

// ==========================================
// Pattern Management Functions
// ==========================================

// Global state for pattern management
let currentPatterns = [];
let currentEditingPattern = null;
let patternComponents = { required: [], optional: [] };
let patternRelationships = [];

// Load patterns
async function loadPatterns() {
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/patterns/`);
        const patterns = await response.json();
        currentPatterns = patterns;

        const listDiv = document.getElementById('patterns-list');
        listDiv.innerHTML = '';

        if (patterns.length === 0) {
            listDiv.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info">
                        No patterns found. Click "Create New Pattern" to add your first pattern.
                    </div>
                </div>
            `;
            hideLoading();
            return;
        }

        patterns.forEach(pattern => {
            const card = document.createElement('div');
            card.className = 'col-md-4 mb-3 pattern-item';
            card.setAttribute('data-pattern-name', pattern.metadata.name.toLowerCase());
            card.setAttribute('data-pattern-category', pattern.metadata.category || '');
            card.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${pattern.metadata.name}</h5>
                        <p class="card-text text-muted">${pattern.metadata.description.substring(0, 100)}...</p>
                        <div class="mb-2">
                            <span class="badge bg-primary">${pattern.metadata.id}</span>
                            <span class="badge bg-success">v${pattern.metadata.version}</span>
                            ${pattern.metadata.category ? `<span class="badge bg-info">${pattern.metadata.category}</span>` : ''}
                        </div>
                        <div class="btn-group w-100" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="showPatternDetails('${pattern.metadata.id}')">
                                <i class="bi bi-eye"></i> View
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="editPattern('${pattern.metadata.id}')">
                                <i class="bi bi-pencil"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deletePattern('${pattern.metadata.id}')">
                                <i class="bi bi-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            `;
            listDiv.appendChild(card);
        });
    } catch (error) {
        Toast.error(`Error loading patterns: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Filter patterns
function filterPatterns() {
    const searchTerm = document.getElementById('pattern-search').value.toLowerCase();
    const categoryFilter = document.getElementById('pattern-category-filter').value;

    const items = document.querySelectorAll('.pattern-item');

    items.forEach(item => {
        const name = item.getAttribute('data-pattern-name');
        const category = item.getAttribute('data-pattern-category');

        const matchesSearch = !searchTerm || name.includes(searchTerm);
        const matchesCategory = !categoryFilter || category === categoryFilter;

        item.style.display = (matchesSearch && matchesCategory) ? '' : 'none';
    });
}

// Show pattern details
async function showPatternDetails(patternId) {
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/patterns/${patternId}`);
        const pattern = await response.json();

        currentEditingPattern = pattern;

        document.getElementById('patternModalTitle').textContent = pattern.metadata.name;

        let html = `
            <div class="mb-3">
                <strong>ID:</strong> ${pattern.metadata.id} |
                <strong>Version:</strong> ${pattern.metadata.version} |
                <strong>Status:</strong> <span class="badge bg-success">${pattern.metadata.status || 'Active'}</span>
            </div>
            <div class="mb-3">
                <h6>Description</h6>
                <p>${pattern.metadata.description}</p>
            </div>
            <div class="mb-3">
                <h6>Components</h6>
                <ul>
                    ${pattern.architecture.components.map(c => `
                        <li>
                            <strong>${c.name}</strong> (${c.type})
                            ${c.required ? '<span class="badge bg-danger">Required</span>' : '<span class="badge bg-secondary">Optional</span>'}
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;

        if (pattern.architecture.relationships && pattern.architecture.relationships.length > 0) {
            html += `
                <div class="mb-3">
                    <h6>Relationships</h6>
                    <ul>
                        ${pattern.architecture.relationships.map(r => `
                            <li><code>${r.from}</code> → <code>${r.to}</code> (${r.type})</li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }

        if (pattern.implementation && pattern.implementation.terraform_module) {
            html += `
                <div class="mb-3">
                    <h6>Terraform Module</h6>
                    <code>${pattern.implementation.terraform_module}</code>
                </div>
            `;
        }

        if (pattern.metadata.tags) {
            html += `
                <div class="mb-3">
                    <h6>Tags</h6>
                    ${pattern.metadata.tags.map(tag => `<span class="badge bg-secondary">${tag}</span>`).join(' ')}
                </div>
            `;
        }

        document.getElementById('patternModalBody').innerHTML = html;

        // Set button attributes for edit/delete
        document.getElementById('edit-pattern-btn').setAttribute('data-pattern-id', patternId);
        document.getElementById('delete-pattern-btn').setAttribute('data-pattern-id', patternId);

        const modal = new bootstrap.Modal(document.getElementById('patternModal'));
        modal.show();
    } catch (error) {
        Toast.error(`Error loading pattern details: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Show create pattern modal
function showCreatePatternModal() {
    currentEditingPattern = null;
    patternComponents = { required: [], optional: [] };
    patternRelationships = [];

    document.getElementById('patternEditModalTitle').textContent = 'Create New Pattern';
    document.getElementById('pattern-form').reset();
    document.getElementById('pattern-version').value = '1.0.0';

    // Clear dynamic lists
    document.getElementById('required-components-list').innerHTML = '';
    document.getElementById('optional-components-list').innerHTML = '';
    document.getElementById('relationships-list').innerHTML = '';
    document.getElementById('pattern-json-preview').style.display = 'none';

    const modal = new bootstrap.Modal(document.getElementById('patternEditModal'));
    modal.show();
}

// Edit pattern
async function editPattern(patternId) {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/patterns/${patternId}`);
        const pattern = await response.json();

        currentEditingPattern = pattern;

        // Populate form
        document.getElementById('patternEditModalTitle').textContent = 'Edit Pattern';
        document.getElementById('pattern-name').value = pattern.metadata.name;
        document.getElementById('pattern-version').value = pattern.metadata.version;
        document.getElementById('pattern-description').value = pattern.metadata.description;
        document.getElementById('pattern-category').value = pattern.metadata.category || 'web';
        document.getElementById('pattern-environment').value = pattern.metadata.environment || '';
        document.getElementById('pattern-author').value = pattern.metadata.author || '';
        document.getElementById('pattern-tags').value = pattern.metadata.tags ? pattern.metadata.tags.join(', ') : '';

        // Populate components
        patternComponents.required = pattern.architecture.components.filter(c => c.required) || [];
        patternComponents.optional = pattern.architecture.components.filter(c => !c.required) || [];
        renderComponentLists();

        // Populate relationships
        patternRelationships = pattern.architecture.relationships || [];
        renderRelationshipsList();

        const modal = new bootstrap.Modal(document.getElementById('patternEditModal'));
        modal.show();
    } catch (error) {
        Toast.error(`Error loading pattern for editing: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Edit pattern from view modal
function editPatternFromView() {
    const patternId = document.getElementById('edit-pattern-btn').getAttribute('data-pattern-id');
    bootstrap.Modal.getInstance(document.getElementById('patternModal')).hide();
    editPattern(patternId);
}

// Delete pattern
async function deletePattern(patternId) {
    if (!confirm('Are you sure you want to delete this pattern? This action cannot be undone.')) {
        return;
    }

    try {
        Toast.info('Deleting pattern...');
        showLoading();

        const response = await fetch(`${API_BASE}/patterns/${patternId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete pattern');
        }

        Toast.success('Pattern deleted successfully!');
        await loadPatterns();

    } catch (error) {
        Toast.error(`Failed to delete pattern: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Delete pattern from view modal
function deletePatternFromView() {
    const patternId = document.getElementById('delete-pattern-btn').getAttribute('data-pattern-id');
    bootstrap.Modal.getInstance(document.getElementById('patternModal')).hide();
    deletePattern(patternId);
}

// Add required component
function addRequiredComponent() {
    patternComponents.required.push({
        name: '',
        type: '',
        count: { min: 1, max: 1 }
    });
    renderComponentLists();
}

// Add optional component
function addOptionalComponent() {
    patternComponents.optional.push({
        name: '',
        type: '',
        count: { min: 0, max: null }
    });
    renderComponentLists();
}

// Remove component
function removeComponent(type, index) {
    if (type === 'required') {
        patternComponents.required.splice(index, 1);
    } else {
        patternComponents.optional.splice(index, 1);
    }
    renderComponentLists();
}

// Render component lists
function renderComponentLists() {
    // Render required components
    const requiredList = document.getElementById('required-components-list');
    requiredList.innerHTML = '';

    patternComponents.required.forEach((comp, idx) => {
        const div = document.createElement('div');
        div.className = 'card mb-2';
        div.innerHTML = `
            <div class="card-body">
                <div class="row">
                    <div class="col-md-5">
                        <input type="text" class="form-control" placeholder="Component name"
                               value="${comp.name}" onchange="updateComponent('required', ${idx}, 'name', this.value)">
                    </div>
                    <div class="col-md-5">
                        <input type="text" class="form-control" placeholder="Resource type (e.g., aws_instance)"
                               value="${comp.type}" onchange="updateComponent('required', ${idx}, 'type', this.value)">
                    </div>
                    <div class="col-md-2">
                        <button class="btn btn-danger btn-sm w-100" onclick="removeComponent('required', ${idx})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        requiredList.appendChild(div);
    });

    // Render optional components
    const optionalList = document.getElementById('optional-components-list');
    optionalList.innerHTML = '';

    patternComponents.optional.forEach((comp, idx) => {
        const div = document.createElement('div');
        div.className = 'card mb-2';
        div.innerHTML = `
            <div class="card-body">
                <div class="row">
                    <div class="col-md-5">
                        <input type="text" class="form-control" placeholder="Component name"
                               value="${comp.name}" onchange="updateComponent('optional', ${idx}, 'name', this.value)">
                    </div>
                    <div class="col-md-5">
                        <input type="text" class="form-control" placeholder="Resource type (e.g., aws_s3_bucket)"
                               value="${comp.type}" onchange="updateComponent('optional', ${idx}, 'type', this.value)">
                    </div>
                    <div class="col-md-2">
                        <button class="btn btn-danger btn-sm w-100" onclick="removeComponent('optional', ${idx})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        optionalList.appendChild(div);
    });
}

// Update component
function updateComponent(type, index, field, value) {
    if (type === 'required') {
        patternComponents.required[index][field] = value;
    } else {
        patternComponents.optional[index][field] = value;
    }
}

// Add relationship
function addRelationship() {
    patternRelationships.push({
        from: '',
        to: '',
        type: 'depends_on'
    });
    renderRelationshipsList();
}

// Remove relationship
function removeRelationship(index) {
    patternRelationships.splice(index, 1);
    renderRelationshipsList();
}

// Render relationships list
function renderRelationshipsList() {
    const list = document.getElementById('relationships-list');
    list.innerHTML = '';

    patternRelationships.forEach((rel, idx) => {
        const div = document.createElement('div');
        div.className = 'card mb-2';
        div.innerHTML = `
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4">
                        <input type="text" class="form-control" placeholder="From component"
                               value="${rel.from}" onchange="updateRelationship(${idx}, 'from', this.value)">
                    </div>
                    <div class="col-md-3">
                        <select class="form-select" onchange="updateRelationship(${idx}, 'type', this.value)">
                            <option value="depends_on" ${rel.type === 'depends_on' ? 'selected' : ''}>Depends On</option>
                            <option value="connects_to" ${rel.type === 'connects_to' ? 'selected' : ''}>Connects To</option>
                            <option value="contains" ${rel.type === 'contains' ? 'selected' : ''}>Contains</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <input type="text" class="form-control" placeholder="To component"
                               value="${rel.to}" onchange="updateRelationship(${idx}, 'to', this.value)">
                    </div>
                    <div class="col-md-1">
                        <button class="btn btn-danger btn-sm w-100" onclick="removeRelationship(${idx})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        list.appendChild(div);
    });
}

// Update relationship
function updateRelationship(index, field, value) {
    patternRelationships[index][field] = value;
}

// Preview pattern JSON
function previewPatternJSON() {
    const pattern = buildPatternFromForm();
    const preview = document.getElementById('pattern-json-preview');
    preview.textContent = JSON.stringify(pattern, null, 2);
    preview.style.display = 'block';
}

// Build pattern object from form
function buildPatternFromForm() {
    const allComponents = [
        ...patternComponents.required.map(c => ({ ...c, required: true })),
        ...patternComponents.optional.map(c => ({ ...c, required: false }))
    ];

    const tags = document.getElementById('pattern-tags').value
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0);

    return {
        metadata: {
            id: currentEditingPattern ? currentEditingPattern.metadata.id : '',
            name: document.getElementById('pattern-name').value,
            version: document.getElementById('pattern-version').value,
            description: document.getElementById('pattern-description').value,
            category: document.getElementById('pattern-category').value,
            environment: document.getElementById('pattern-environment').value || null,
            author: document.getElementById('pattern-author').value || 'Unknown',
            tags: tags,
            status: 'approved'
        },
        architecture: {
            components: allComponents,
            relationships: patternRelationships
        },
        implementation: {
            terraform_module: ''
        }
    };
}

// Test pattern
async function testPattern() {
    try {
        const pattern = buildPatternFromForm();

        if (!pattern.metadata.name) {
            Toast.warning('Please provide a pattern name');
            return;
        }

        Toast.info('Testing pattern...');
        showLoading();

        const response = await fetch(`${API_BASE}/patterns/test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pattern)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Pattern test failed');
        }

        const result = await response.json();

        // Show test results
        const resultsDiv = document.getElementById('pattern-test-results');
        resultsDiv.innerHTML = `
            <div class="alert alert-success">
                <h6><i class="bi bi-check-circle"></i> Pattern is valid!</h6>
                <p>The pattern structure is correct and can be saved.</p>
            </div>
            <h6>Pattern Summary:</h6>
            <ul>
                <li><strong>Components:</strong> ${pattern.architecture.components.length}</li>
                <li><strong>Relationships:</strong> ${pattern.architecture.relationships.length}</li>
                <li><strong>Required Resources:</strong> ${pattern.architecture.components.filter(c => c.required).length}</li>
            </ul>
        `;

        const testModal = new bootstrap.Modal(document.getElementById('patternTestModal'));
        testModal.show();

        Toast.success('Pattern validation passed!');

    } catch (error) {
        const resultsDiv = document.getElementById('pattern-test-results');
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                <h6><i class="bi bi-x-circle"></i> Pattern validation failed</h6>
                <p>${error.message}</p>
            </div>
        `;

        const testModal = new bootstrap.Modal(document.getElementById('patternTestModal'));
        testModal.show();

        Toast.error(`Pattern test failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Save pattern
async function savePattern() {
    try {
        const pattern = buildPatternFromForm();

        if (!pattern.metadata.name) {
            Toast.warning('Please provide a pattern name');
            return;
        }

        if (pattern.architecture.components.length === 0) {
            Toast.warning('Please add at least one component');
            return;
        }

        Toast.info('Saving pattern...');
        showLoading();

        let response;
        if (currentEditingPattern) {
            // Update existing pattern
            response = await fetch(`${API_BASE}/patterns/${currentEditingPattern.metadata.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(pattern)
            });
        } else {
            // Create new pattern
            response = await fetch(`${API_BASE}/patterns/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(pattern)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save pattern');
        }

        const savedPattern = await response.json();

        Toast.success(`Pattern ${currentEditingPattern ? 'updated' : 'created'} successfully!`);

        // Close modal and reload patterns
        bootstrap.Modal.getInstance(document.getElementById('patternEditModal')).hide();
        await loadPatterns();

    } catch (error) {
        Toast.error(`Failed to save pattern: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// ===== Notification Functions =====

// Load notification settings
async function loadNotificationSettings() {
    try {
        const response = await fetch(`${API_BASE}/notifications/settings`);
        const settings = await response.json();

        const statusBadge = settings.enabled
            ? '<span class="badge bg-success">Enabled</span>'
            : '<span class="badge bg-danger">Disabled</span>';

        const html = `
            <table class="table table-sm">
                <tr>
                    <th class="text-end" style="width: 40%;">Status:</th>
                    <td>${statusBadge}</td>
                </tr>
                <tr>
                    <th class="text-end">SMTP Host:</th>
                    <td><code>${settings.smtp_host}</code></td>
                </tr>
                <tr>
                    <th class="text-end">SMTP Port:</th>
                    <td><code>${settings.smtp_port}</code></td>
                </tr>
                <tr>
                    <th class="text-end">From Email:</th>
                    <td><code>${settings.from_email}</code></td>
                </tr>
                <tr>
                    <th class="text-end">From Name:</th>
                    <td>${settings.from_name}</td>
                </tr>
                <tr>
                    <th class="text-end">Notify on Failure:</th>
                    <td>${settings.notify_on_failure ? '✅ Yes' : '❌ No'}</td>
                </tr>
                <tr>
                    <th class="text-end">Notify on Critical:</th>
                    <td>${settings.notify_on_critical ? '✅ Yes' : '❌ No'}</td>
                </tr>
                <tr>
                    <th class="text-end">Notify on Success:</th>
                    <td>${settings.notify_on_success ? '✅ Yes' : '❌ No'}</td>
                </tr>
            </table>
        `;

        document.getElementById('notification-settings').innerHTML = html;
    } catch (error) {
        document.getElementById('notification-settings').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i> Failed to load notification settings: ${error.message}
            </div>
        `;
    }
}

// Send test email
async function sendTestEmail() {
    const recipient = document.getElementById('testEmailRecipient').value;
    const subject = document.getElementById('testEmailSubject').value;
    const body = document.getElementById('testEmailBody').value;

    if (!recipient) {
        Toast.error('Please enter a recipient email address');
        return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(recipient)) {
        Toast.error('Please enter a valid email address');
        return;
    }

    try {
        Toast.info('Sending test email...');

        const response = await fetch(`${API_BASE}/notifications/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipient: recipient,
                subject: subject || undefined,
                body: body || undefined
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send test email');
        }

        const result = await response.json();
        Toast.success(result.message || 'Test email sent successfully!');
    } catch (error) {
        Toast.error(`Failed to send test email: ${error.message}`);
    }
}

// Send manual notification
async function sendManualNotification() {
    const recipientsInput = document.getElementById('notificationRecipients').value;
    const includePDF = document.getElementById('includePDF').checked;

    if (!recipientsInput) {
        Toast.error('Please enter at least one recipient email address');
        return;
    }

    // Parse recipients (comma-separated)
    const recipients = recipientsInput.split(',').map(e => e.trim()).filter(e => e);

    if (recipients.length === 0) {
        Toast.error('Please enter valid email addresses');
        return;
    }

    // Validate each email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    for (const email of recipients) {
        if (!emailRegex.test(email)) {
            Toast.error(`Invalid email address: ${email}`);
            return;
        }
    }

    if (!window.currentReport) {
        Toast.error('No validation report available. Please complete a validation first.');
        return;
    }

    try {
        Toast.info('Sending notification...');

        const response = await fetch(`${API_BASE}/notifications/send-validation-report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                report: window.currentReport,
                recipients: recipients,
                include_pdf: includePDF
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send notification');
        }

        const result = await response.json();
        Toast.success(result.message || 'Notification sent successfully!');
    } catch (error) {
        Toast.error(`Failed to send notification: ${error.message}`);
    }
}

// ===== Terraform State File Functions =====

// Analyze Terraform state file
async function analyzeStateFile() {
    const fileInput = document.getElementById('terraformStateFile');
    const file = fileInput.files[0];

    if (!file) {
        Toast.error('Please select a state file');
        return;
    }

    try {
        Toast.info('Analyzing state file...');
        showLoading('Analyzing Terraform state...');

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/terraform/state/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const result = await response.json();

        displayStateAnalysis(result);
        Toast.success('State analysis complete!');

    } catch (error) {
        Toast.error(`Analysis failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Validate Terraform state file
async function validateStateFile() {
    const fileInput = document.getElementById('terraformStateFile');
    const file = fileInput.files[0];

    if (!file) {
        Toast.error('Please select a state file');
        return;
    }

    try {
        Toast.info('Validating state file...');
        showLoading('Running validation...');

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/terraform/state/validate`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Validation failed');
        }

        const report = await response.json();

        // Display validation report (reuse existing function)
        displayValidationReport(report);
        Toast.success('Validation complete!');

        // Scroll to results
        document.getElementById('validation-results').scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });

    } catch (error) {
        Toast.error(`Validation failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Display state analysis results
function displayStateAnalysis(analysis) {
    const resultsDiv = document.getElementById('state-analysis-results');
    const contentDiv = document.getElementById('state-analysis-content');

    const summary = analysis.analysis.summary;
    const stats = analysis.stats;
    const patterns = analysis.analysis.patterns_detected || [];
    const security = analysis.analysis.security_findings || [];
    const costDrivers = analysis.analysis.cost_drivers || {};

    let html = '<div class="row">';

    // Summary Cards
    html += `
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-primary text-white">
                <div class="card-body">
                    <h3 class="mb-0">${summary.total_resources}</h3>
                    <p class="mb-0">Total Resources</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-info text-white">
                <div class="card-body">
                    <h3 class="mb-0">${summary.resource_types}</h3>
                    <p class="mb-0">Resource Types</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-success text-white">
                <div class="card-body">
                    <h3 class="mb-0">${summary.modules}</h3>
                    <p class="mb-0">Modules</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-center bg-secondary text-white">
                <div class="card-body">
                    <h3 class="mb-0">${summary.providers}</h3>
                    <p class="mb-0">Providers</p>
                </div>
            </div>
        </div>
    </div>`;

    // Resource Categories
    html += '<div class="card mb-3"><div class="card-header bg-primary text-white"><h6 class="mb-0">Resource Categories</h6></div><div class="card-body">';
    html += '<div class="row">';

    for (const [category, count] of Object.entries(stats.by_category)) {
        html += `
            <div class="col-md-4 mb-2">
                <div class="d-flex justify-content-between align-items-center p-2 border rounded">
                    <span class="text-capitalize">${category}</span>
                    <span class="badge bg-primary">${count}</span>
                </div>
            </div>
        `;
    }
    html += '</div></div></div>';

    // Detected Patterns
    if (patterns.length > 0) {
        html += '<div class="card mb-3"><div class="card-header bg-success text-white"><h6 class="mb-0">Detected Patterns</h6></div><div class="card-body">';
        patterns.forEach(pattern => {
            const confidence = (pattern.confidence * 100).toFixed(0);
            html += `
                <div class="alert alert-success mb-2">
                    <strong>${pattern.name}</strong>
                    <span class="badge bg-success float-end">${confidence}% confidence</span>
                    <p class="mb-0 mt-2 small">${pattern.description}</p>
                </div>
            `;
        });
        html += '</div></div>';
    }

    // Security Findings
    if (security.length > 0) {
        html += '<div class="card mb-3"><div class="card-header bg-warning"><h6 class="mb-0">Security Findings</h6></div><div class="card-body">';
        html += '<table class="table table-sm"><thead><tr><th>Severity</th><th>Resource</th><th>Finding</th></tr></thead><tbody>';
        security.forEach(finding => {
            const severityClass = {
                'critical': 'danger',
                'high': 'warning',
                'medium': 'info',
                'low': 'secondary'
            }[finding.severity] || 'secondary';

            html += `
                <tr>
                    <td><span class="badge bg-${severityClass}">${finding.severity.toUpperCase()}</span></td>
                    <td><code>${finding.resource}</code></td>
                    <td>${finding.finding}</td>
                </tr>
            `;
        });
        html += '</tbody></table></div></div>';
    }

    // Cost Drivers
    if (costDrivers.summary) {
        html += '<div class="card mb-3"><div class="card-header bg-info text-white"><h6 class="mb-0">Cost Drivers</h6></div><div class="card-body">';
        html += '<div class="row">';
        html += `
            <div class="col-md-4 mb-2">
                <div class="p-3 border rounded text-center">
                    <h4 class="mb-0">${costDrivers.summary.compute_instances}</h4>
                    <small>Compute Instances</small>
                </div>
            </div>
            <div class="col-md-4 mb-2">
                <div class="p-3 border rounded text-center">
                    <h4 class="mb-0">${costDrivers.summary.databases}</h4>
                    <small>Databases</small>
                </div>
            </div>
            <div class="col-md-4 mb-2">
                <div class="p-3 border rounded text-center">
                    <h4 class="mb-0">${costDrivers.summary.storage_resources}</h4>
                    <small>Storage Resources</small>
                </div>
            </div>
        `;
        html += '</div></div></div>';
    }

    // Mermaid Diagram
    if (analysis.diagram && analysis.diagram.mermaid) {
        html += `
            <div class="card mb-3">
                <div class="card-header bg-secondary text-white">
                    <h6 class="mb-0">Resource Diagram</h6>
                </div>
                <div class="card-body">
                    <pre class="bg-light p-3 rounded"><code>${analysis.diagram.mermaid}</code></pre>
                    <p class="small text-muted mb-0">
                        Copy this Mermaid diagram to <a href="https://mermaid.live" target="_blank">mermaid.live</a> to visualize
                    </p>
                </div>
            </div>
        `;
    }

    contentDiv.innerHTML = html;
    resultsDiv.style.display = 'block';

    // Smooth scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ===== Terraform Cloud Functions =====

// Store Terraform Cloud config globally
let tfcConfig = {
    apiToken: '',
    organization: '',
    baseUrl: 'https://app.terraform.io/api/v2'
};

// Store workspaces globally
let tfcWorkspaces = [];

// Get Terraform Cloud configuration from form
function getTerraformCloudConfig() {
    return {
        api_token: document.getElementById('tfcApiToken').value,
        organization: document.getElementById('tfcOrganization').value,
        base_url: document.getElementById('tfcBaseUrl').value || 'https://app.terraform.io/api/v2'
    };
}

// Test Terraform Cloud connection
async function testTerraformCloudConnection() {
    const config = getTerraformCloudConfig();

    if (!config.api_token || !config.organization) {
        Toast.error('Please enter API token and organization name');
        return;
    }

    try {
        Toast.info('Testing connection...');

        const response = await fetch(`${API_BASE}/terraform/cloud/test?` + new URLSearchParams({
            api_token: config.api_token,
            organization: config.organization,
            base_url: config.base_url
        }));

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Connection test failed');
        }

        const result = await response.json();

        // Show success status
        const statusDiv = document.getElementById('tfc-connection-status');
        statusDiv.className = 'alert alert-success mb-4';
        statusDiv.innerHTML = `
            <h6><i class="bi bi-check-circle"></i> Connection Successful</h6>
            <p class="mb-0">Connected to organization: <strong>${result.organization}</strong></p>
            <p class="mb-0">Found ${result.workspace_count} workspace(s)</p>
        `;
        statusDiv.style.display = 'block';

        Toast.success('Connection successful!');

        // Store config
        tfcConfig = config;

    } catch (error) {
        // Show error status
        const statusDiv = document.getElementById('tfc-connection-status');
        statusDiv.className = 'alert alert-danger mb-4';
        statusDiv.innerHTML = `
            <h6><i class="bi bi-x-circle"></i> Connection Failed</h6>
            <p class="mb-0">${error.message}</p>
        `;
        statusDiv.style.display = 'block';

        Toast.error(`Connection failed: ${error.message}`);
    }
}

// Load Terraform Cloud workspaces
async function loadTerraformCloudWorkspaces() {
    const config = getTerraformCloudConfig();

    if (!config.api_token || !config.organization) {
        Toast.error('Please enter API token and organization name');
        return;
    }

    try {
        Toast.info('Loading workspaces...');
        showLoading('Loading workspaces from Terraform Cloud...');

        const response = await fetch(`${API_BASE}/terraform/cloud/workspaces`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to load workspaces');
        }

        const result = await response.json();
        tfcWorkspaces = result.workspaces;

        // Display workspaces
        displayTerraformCloudWorkspaces(tfcWorkspaces);
        Toast.success(`Loaded ${tfcWorkspaces.length} workspace(s)`);

        // Show workspaces container
        document.getElementById('tfc-workspaces-container').style.display = 'block';

        // Store config
        tfcConfig = config;

    } catch (error) {
        Toast.error(`Failed to load workspaces: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Display Terraform Cloud workspaces
function displayTerraformCloudWorkspaces(workspaces) {
    const listDiv = document.getElementById('workspaces-list');

    if (workspaces.length === 0) {
        listDiv.innerHTML = '<div class="alert alert-info">No workspaces found</div>';
        return;
    }

    let html = '';
    workspaces.forEach(workspace => {
        const resourceCount = workspace.resource_count || 0;
        const lastUpdated = workspace.updated_at ? new Date(workspace.updated_at).toLocaleDateString() : 'N/A';

        html += `
            <div class="list-group-item workspace-item" data-workspace-name="${workspace.name}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${workspace.name}</h6>
                        <small class="text-muted">
                            <i class="bi bi-box"></i> ${resourceCount} resources &nbsp;
                            <i class="bi bi-calendar"></i> Updated: ${lastUpdated}
                        </small>
                    </div>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewWorkspaceDetails('${workspace.name}')">
                            <i class="bi bi-eye"></i> Details
                        </button>
                        <button class="btn btn-sm btn-outline-info" onclick="analyzeWorkspace('${workspace.name}')">
                            <i class="bi bi-search"></i> Analyze
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="validateWorkspace('${workspace.name}')">
                            <i class="bi bi-check-circle"></i> Validate
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    listDiv.innerHTML = html;
}

// Filter workspaces by search
function filterWorkspaces() {
    const searchTerm = document.getElementById('workspaceSearch').value.toLowerCase();
    const workspaceItems = document.querySelectorAll('.workspace-item');

    workspaceItems.forEach(item => {
        const workspaceName = item.getAttribute('data-workspace-name').toLowerCase();
        if (workspaceName.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// View workspace details
async function viewWorkspaceDetails(workspaceName) {
    try {
        Toast.info('Loading workspace details...');
        showLoading('Loading workspace details...');

        const workspace = tfcWorkspaces.find(w => w.name === workspaceName);

        if (!workspace) {
            throw new Error('Workspace not found');
        }

        // Display details
        const detailsDiv = document.getElementById('workspace-details-content');
        let html = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Workspace Information</h6>
                    <table class="table table-sm">
                        <tr><th>Name:</th><td>${workspace.name}</td></tr>
                        <tr><th>ID:</th><td><code>${workspace.id}</code></td></tr>
                        <tr><th>Terraform Version:</th><td>${workspace.terraform_version || 'N/A'}</td></tr>
                        <tr><th>Execution Mode:</th><td>${workspace.execution_mode || 'remote'}</td></tr>
                        <tr><th>Auto Apply:</th><td>${workspace.auto_apply ? 'Yes' : 'No'}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Statistics</h6>
                    <table class="table table-sm">
                        <tr><th>Resource Count:</th><td>${workspace.resource_count || 0}</td></tr>
                        <tr><th>Working Directory:</th><td>${workspace.working_directory || '/'}</td></tr>
                        <tr><th>Created:</th><td>${new Date(workspace.created_at).toLocaleString()}</td></tr>
                        <tr><th>Last Updated:</th><td>${new Date(workspace.updated_at).toLocaleString()}</td></tr>
                    </table>
                </div>
            </div>
        `;

        detailsDiv.innerHTML = html;
        document.getElementById('tfc-workspace-details').style.display = 'block';

        // Scroll to details
        document.getElementById('tfc-workspace-details').scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });

    } catch (error) {
        Toast.error(`Failed to load details: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Close workspace details
function closeTerraformCloudWorkspaceDetails() {
    document.getElementById('tfc-workspace-details').style.display = 'none';
}

// Analyze workspace
async function analyzeWorkspace(workspaceName) {
    try {
        Toast.info('Analyzing workspace...');
        showLoading('Analyzing workspace from Terraform Cloud...');

        const response = await fetch(`${API_BASE}/terraform/cloud/workspace/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                workspace_name: workspaceName,
                config: tfcConfig
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const result = await response.json();

        // Display analysis results
        if (result.has_state && result.analysis) {
            displayWorkspaceAnalysis(result);
            Toast.success('Workspace analysis complete!');
        } else {
            Toast.warning('Workspace has no state to analyze');
        }

    } catch (error) {
        Toast.error(`Analysis failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Display workspace analysis
function displayWorkspaceAnalysis(result) {
    const contentDiv = document.getElementById('workspace-analysis-content');

    const analysis = result.analysis;
    const workspace = result.workspace;

    let html = `
        <h6>Workspace: ${workspace.name}</h6>
        <div class="row mb-3">
            <div class="col-md-3">
                <div class="card text-center bg-primary text-white">
                    <div class="card-body">
                        <h4 class="mb-0">${analysis.summary.total_resources}</h4>
                        <small>Total Resources</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center bg-info text-white">
                    <div class="card-body">
                        <h4 class="mb-0">${analysis.summary.resource_types}</h4>
                        <small>Resource Types</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center bg-success text-white">
                    <div class="card-body">
                        <h4 class="mb-0">${analysis.summary.modules}</h4>
                        <small>Modules</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center bg-secondary text-white">
                    <div class="card-body">
                        <h4 class="mb-0">${analysis.patterns_detected?.length || 0}</h4>
                        <small>Patterns Detected</small>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Security Findings
    if (analysis.security_findings && analysis.security_findings.length > 0) {
        html += `
            <div class="card mb-3">
                <div class="card-header bg-warning">
                    <h6 class="mb-0">Security Findings</h6>
                </div>
                <div class="card-body">
                    <ul class="mb-0">
        `;

        analysis.security_findings.slice(0, 5).forEach(finding => {
            html += `<li><span class="badge bg-${finding.severity === 'high' ? 'danger' : 'warning'}">${finding.severity}</span> ${finding.finding}</li>`;
        });

        html += `
                    </ul>
                </div>
            </div>
        `;
    }

    contentDiv.innerHTML = html;
    document.getElementById('tfc-workspace-analysis').style.display = 'block';

    // Scroll to results
    document.getElementById('tfc-workspace-analysis').scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
    });
}

// Validate workspace
async function validateWorkspace(workspaceName) {
    try {
        Toast.info('Validating workspace...');
        showLoading('Running validation against workspace...');

        const response = await fetch(`${API_BASE}/terraform/cloud/workspace/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                workspace_name: workspaceName,
                config: tfcConfig
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Validation failed');
        }

        const report = await response.json();

        // Display validation report (reuse existing function)
        displayValidationReport(report);
        Toast.success('Validation complete!');

        // Scroll to results
        document.getElementById('validation-results').scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });

    } catch (error) {
        Toast.error(`Validation failed: ${error.message}`);
    } finally{
        hideLoading();
    }
}

// ==========================================
// Analytics Dashboard Functions
// ==========================================

// Global state for analytics
let analyticsData = {
    summary: null,
    trends: null,
    patterns: null,
    rules: null,
    history: [],
    charts: {}
};

// Load system-wide analytics summary
async function loadSystemAnalytics() {
    try {
        Toast.info('Loading system analytics...');
        showLoading('Fetching analytics data...');

        const response = await fetch(`${API_BASE}/analytics/summary`);
        if (!response.ok) {
            throw new Error('Failed to load analytics');
        }

        const data = await response.json();
        analyticsData.summary = data;

        // Display overview cards
        displayAnalyticsOverview(data);

        // Load related data
        await Promise.all([
            loadPatternStatistics(),
            loadRulePerformance(),
            loadTopViolations(),
            loadValidationHistory()
        ]);

        Toast.success('Analytics loaded successfully!');

    } catch (error) {
        Toast.error(`Failed to load analytics: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Display analytics overview cards
function displayAnalyticsOverview(data) {
    const container = document.getElementById('analytics-stats-cards');
    const overviewDiv = document.getElementById('analytics-overview');

    overviewDiv.style.display = 'block';

    const cards = [
        {
            title: 'Total Validations',
            value: data.total_validations || 0,
            icon: 'clipboard-check',
            color: 'primary'
        },
        {
            title: 'Avg. Compliance',
            value: `${((data.average_compliance || 0) * 100).toFixed(1)}%`,
            icon: 'graph-up',
            color: 'success'
        },
        {
            title: 'Active Patterns',
            value: data.unique_patterns || 0,
            icon: 'diagram-3',
            color: 'info'
        },
        {
            title: 'Total Rules',
            value: data.total_rules || 0,
            icon: 'shield-check',
            color: 'warning'
        }
    ];

    let html = '';
    cards.forEach(card => {
        html += `
            <div class="col-md-3 mb-3">
                <div class="card text-center bg-${card.color} text-white">
                    <div class="card-body">
                        <i class="bi bi-${card.icon} fs-1"></i>
                        <h3 class="mt-2 mb-0">${card.value}</h3>
                        <p class="mb-0">${card.title}</p>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Load compliance trends
async function loadComplianceTrends() {
    try {
        Toast.info('Loading compliance trends...');
        showLoading('Fetching trend data...');

        const response = await fetch(`${API_BASE}/analytics/trends?days=30`);
        if (!response.ok) {
            throw new Error('Failed to load trends');
        }

        const data = await response.json();
        analyticsData.trends = data;

        displayComplianceTrends(data);
        Toast.success('Trends loaded successfully!');

    } catch (error) {
        Toast.error(`Failed to load trends: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Display compliance trends chart
function displayComplianceTrends(data) {
    const section = document.getElementById('compliance-trends-section');
    section.style.display = 'block';

    const ctx = document.getElementById('complianceTrendsChart');

    // Destroy existing chart if it exists
    if (analyticsData.charts.compliance) {
        analyticsData.charts.compliance.destroy();
    }

    analyticsData.charts.compliance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates || [],
            datasets: [{
                label: 'Compliance Score',
                data: data.scores || [],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Compliance: ${(context.parsed.y * 100).toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                }
            }
        }
    });
}

// Load pattern usage statistics
async function loadPatternStatistics() {
    try {
        const response = await fetch(`${API_BASE}/analytics/patterns`);
        if (!response.ok) {
            throw new Error('Failed to load pattern statistics');
        }

        const data = await response.json();
        analyticsData.patterns = data;

        displayPatternStatistics(data);

    } catch (error) {
        console.error('Failed to load pattern statistics:', error);
    }
}

// Display pattern statistics
function displayPatternStatistics(data) {
    const section = document.getElementById('pattern-stats-section');
    section.style.display = 'block';

    const ctx = document.getElementById('patternUsageChart');

    // Destroy existing chart if it exists
    if (analyticsData.charts.patterns) {
        analyticsData.charts.patterns.destroy();
    }

    const patterns = data.patterns || [];
    const labels = patterns.map(p => p.pattern_name);
    const counts = patterns.map(p => p.usage_count);
    const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
    ];

    analyticsData.charts.patterns = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });

    // Display pattern table
    const tableDiv = document.getElementById('pattern-usage-table');
    let tableHtml = '<table class="table table-sm"><thead><tr><th>Pattern</th><th>Count</th><th>%</th></tr></thead><tbody>';

    const total = counts.reduce((a, b) => a + b, 0);
    patterns.forEach(p => {
        const percentage = total > 0 ? ((p.usage_count / total) * 100).toFixed(1) : 0;
        tableHtml += `
            <tr>
                <td>${p.pattern_name}</td>
                <td>${p.usage_count}</td>
                <td>${percentage}%</td>
            </tr>
        `;
    });

    tableHtml += '</tbody></table>';
    tableDiv.innerHTML = tableHtml;
}

// Load rule performance metrics
async function loadRulePerformance() {
    try {
        const response = await fetch(`${API_BASE}/analytics/rules`);
        if (!response.ok) {
            throw new Error('Failed to load rule performance');
        }

        const data = await response.json();
        analyticsData.rules = data;

        displayRulePerformance(data);

    } catch (error) {
        console.error('Failed to load rule performance:', error);
    }
}

// Display rule performance metrics
function displayRulePerformance(data) {
    const section = document.getElementById('rule-performance-section');
    section.style.display = 'block';

    const tbody = document.querySelector('#rule-performance-table tbody');
    const rules = data.rules || [];

    let html = '';
    rules.forEach(rule => {
        const passRate = rule.total_executions > 0
            ? ((rule.pass_count / rule.total_executions) * 100).toFixed(1)
            : 0;

        const passRateClass = passRate >= 80 ? 'success' : passRate >= 50 ? 'warning' : 'danger';

        html += `
            <tr>
                <td><code>${rule.rule_id}</code></td>
                <td><span class="badge bg-secondary">${rule.category}</span></td>
                <td>${rule.total_executions}</td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar bg-${passRateClass}" role="progressbar"
                             style="width: ${passRate}%" aria-valuenow="${passRate}"
                             aria-valuemin="0" aria-valuemax="100">
                            ${passRate}%
                        </div>
                    </div>
                </td>
                <td>${rule.avg_execution_time_ms ? rule.avg_execution_time_ms.toFixed(2) : 'N/A'}</td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

// Load top violations
async function loadTopViolations() {
    try {
        const response = await fetch(`${API_BASE}/analytics/summary`);
        if (!response.ok) {
            return;
        }

        const data = await response.json();

        if (data.top_violations && data.top_violations.length > 0) {
            displayTopViolations(data.top_violations);
        }

    } catch (error) {
        console.error('Failed to load top violations:', error);
    }
}

// Display top violations chart
function displayTopViolations(violations) {
    const section = document.getElementById('top-violations-section');
    section.style.display = 'block';

    const ctx = document.getElementById('topViolationsChart');

    // Destroy existing chart if it exists
    if (analyticsData.charts.violations) {
        analyticsData.charts.violations.destroy();
    }

    const labels = violations.map(v => v.rule_id);
    const counts = violations.map(v => v.count);

    analyticsData.charts.violations = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Violation Count',
                data: counts,
                backgroundColor: 'rgba(255, 99, 132, 0.8)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Load validation history
async function loadValidationHistory() {
    try {
        const response = await fetch(`${API_BASE}/history?limit=50`);
        if (!response.ok) {
            throw new Error('Failed to load validation history');
        }

        const data = await response.json();
        analyticsData.history = data.validations || [];

        displayValidationHistory(analyticsData.history);
        populateComparisonDropdowns(analyticsData.history);

    } catch (error) {
        console.error('Failed to load validation history:', error);
    }
}

// Display validation history table
function displayValidationHistory(validations) {
    const section = document.getElementById('validation-history-section');
    section.style.display = 'block';

    const tbody = document.querySelector('#validation-history-table tbody');

    let html = '';
    validations.forEach(val => {
        const statusClass = val.status === 'passed' ? 'success' :
                           val.status === 'failed' ? 'danger' : 'warning';

        const compliance = val.compliance_score
            ? `${(val.compliance_score * 100).toFixed(1)}%`
            : 'N/A';

        const timestamp = new Date(val.timestamp).toLocaleString();

        html += `
            <tr>
                <td>${timestamp}</td>
                <td><code>${val.source_identifier || val.source_type}</code></td>
                <td>${val.pattern_name || 'Unknown'}</td>
                <td><span class="badge bg-${statusClass}">${val.status}</span></td>
                <td>${compliance}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="viewValidationDetails('${val.validation_id}')">
                        <i class="bi bi-eye"></i> View
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="downloadValidationReport('${val.validation_id}')">
                        <i class="bi bi-download"></i> PDF
                    </button>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

// Filter validation history
function filterValidationHistory() {
    const searchTerm = document.getElementById('history-search').value.toLowerCase();
    const rows = document.querySelectorAll('#validation-history-table tbody tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// View validation details
async function viewValidationDetails(validationId) {
    try {
        Toast.info('Loading validation details...');
        showLoading('Fetching validation report...');

        const response = await fetch(`${API_BASE}/history/${validationId}`);
        if (!response.ok) {
            throw new Error('Failed to load validation details');
        }

        const report = await response.json();
        displayValidationReport(report);

        // Scroll to results
        document.getElementById('validation-results').scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });

        Toast.success('Validation details loaded!');

    } catch (error) {
        Toast.error(`Failed to load details: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Download validation report as PDF
async function downloadValidationReport(validationId) {
    try {
        Toast.info('Generating PDF report...');

        const response = await fetch(`${API_BASE}/reports/${validationId}/pdf`);
        if (!response.ok) {
            throw new Error('Failed to generate PDF');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `validation-report-${validationId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        Toast.success('PDF downloaded successfully!');

    } catch (error) {
        Toast.error(`Failed to download PDF: ${error.message}`);
    }
}

// Populate comparison dropdowns
function populateComparisonDropdowns(validations) {
    const select1 = document.getElementById('compare-validation-1');
    const select2 = document.getElementById('compare-validation-2');

    let options = '<option value="">Select a validation...</option>';
    validations.forEach(val => {
        const timestamp = new Date(val.timestamp).toLocaleString();
        options += `<option value="${val.validation_id}">${timestamp} - ${val.source_identifier || val.source_type}</option>`;
    });

    select1.innerHTML = options;
    select2.innerHTML = options;
}

// Compare validations
async function compareValidations() {
    try {
        const val1 = document.getElementById('compare-validation-1').value;
        const val2 = document.getElementById('compare-validation-2').value;

        if (!val1 || !val2) {
            Toast.warning('Please select two validations to compare');
            return;
        }

        if (val1 === val2) {
            Toast.warning('Please select different validations');
            return;
        }

        Toast.info('Comparing validations...');
        showLoading('Generating comparison...');

        const response = await fetch(`${API_BASE}/analytics/compare?validation_ids=${val1},${val2}`);
        if (!response.ok) {
            throw new Error('Failed to compare validations');
        }

        const data = await response.json();
        displayComparisonResults(data);

        Toast.success('Comparison complete!');

    } catch (error) {
        Toast.error(`Comparison failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Display comparison results
function displayComparisonResults(data) {
    const container = document.getElementById('comparison-results');
    container.style.display = 'block';

    const val1 = data.validation_1;
    const val2 = data.validation_2;
    const diff = data.differences;

    let html = `
        <h5>Comparison Results</h5>
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        Validation 1
                    </div>
                    <div class="card-body">
                        <p><strong>Status:</strong> <span class="badge bg-${val1.status === 'passed' ? 'success' : 'danger'}">${val1.status}</span></p>
                        <p><strong>Compliance:</strong> ${(val1.compliance_score * 100).toFixed(1)}%</p>
                        <p><strong>Total Rules:</strong> ${val1.total_rules}</p>
                        <p><strong>Passed:</strong> ${val1.passed_rules}</p>
                        <p><strong>Failed:</strong> ${val1.failed_rules}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        Validation 2
                    </div>
                    <div class="card-body">
                        <p><strong>Status:</strong> <span class="badge bg-${val2.status === 'passed' ? 'success' : 'danger'}">${val2.status}</span></p>
                        <p><strong>Compliance:</strong> ${(val2.compliance_score * 100).toFixed(1)}%</p>
                        <p><strong>Total Rules:</strong> ${val2.total_rules}</p>
                        <p><strong>Passed:</strong> ${val2.passed_rules}</p>
                        <p><strong>Failed:</strong> ${val2.failed_rules}</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="card mt-3">
            <div class="card-header bg-secondary text-white">
                Key Differences
            </div>
            <div class="card-body">
                <p><strong>Compliance Change:</strong>
                    <span class="badge bg-${diff.compliance_change > 0 ? 'success' : 'danger'}">
                        ${diff.compliance_change > 0 ? '+' : ''}${(diff.compliance_change * 100).toFixed(1)}%
                    </span>
                </p>
                <p><strong>New Failures:</strong> ${diff.new_failures || 0}</p>
                <p><strong>New Passes:</strong> ${diff.new_passes || 0}</p>
            </div>
        </div>
    `;

    container.innerHTML = html;
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ==========================================
// Resource Graph Visualizer Functions
// ==========================================

// Global state for resource graph
let resourceGraphData = {
    network: null,
    nodes: null,
    edges: null,
    rawData: null,
    physicsEnabled: true
};

// Resource type to color mapping
const RESOURCE_TYPE_COLORS = {
    'compute': '#97C2FC',
    'database': '#FB7E81',
    'network': '#7BE141',
    'storage': '#FFA807',
    'security': '#C2FABC',
    'load_balancer': '#FFCA81',
    'default': '#CCCCCC'
};

// Populate validation history select for graph source
async function populateHistoryValidationSelect() {
    try {
        const response = await fetch(`${API_BASE}/history?limit=20`);
        if (!response.ok) {
            return;
        }

        const data = await response.json();
        const select = document.getElementById('history-validation-select');

        let options = '<option value="">Select a validation...</option>';
        (data.validations || []).forEach(val => {
            const timestamp = new Date(val.timestamp).toLocaleString();
            options += `<option value="${val.validation_id}">${timestamp} - ${val.source_identifier || val.source_type}</option>`;
        });

        select.innerHTML = options;

    } catch (error) {
        console.error('Failed to load validation history:', error);
    }
}

// Generate resource graph
async function generateResourceGraph() {
    try {
        Toast.info('Generating resource graph...');
        showLoading('Building dependency graph...');

        let graphData;
        const source = document.querySelector('input[name="graph-source"]:checked').id;

        if (source === 'graph-from-current') {
            // Use current validation report
            if (!window.currentReport) {
                throw new Error('No current validation available. Please run a validation first.');
            }
            graphData = {
                resources: window.currentReport.resources || [],
                topology: window.currentReport.topology || []
            };

        } else if (source === 'graph-from-history') {
            // Load from historical validation
            const validationId = document.getElementById('history-validation-select').value;
            if (!validationId) {
                throw new Error('Please select a validation from history');
            }

            const response = await fetch(`${API_BASE}/graph/${validationId}`);
            if (!response.ok) {
                throw new Error('Failed to load graph data');
            }

            graphData = await response.json();

        } else if (source === 'graph-from-custom') {
            // Parse custom JSON data
            const customData = document.getElementById('custom-graph-data').value;
            if (!customData.trim()) {
                throw new Error('Please provide custom graph data in JSON format');
            }

            try {
                graphData = JSON.parse(customData);
            } catch (e) {
                throw new Error('Invalid JSON format: ' + e.message);
            }
        }

        // Store raw data
        resourceGraphData.rawData = graphData;

        // Generate graph using API
        const response = await fetch(`${API_BASE}/graph/generate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(graphData)
        });

        if (!response.ok) {
            throw new Error('Failed to generate graph');
        }

        const result = await response.json();

        // Display interactive graph
        displayInteractiveGraph(result);

        Toast.success('Graph generated successfully!');

    } catch (error) {
        Toast.error(`Graph generation failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Display interactive graph using vis-network
function displayInteractiveGraph(graphData) {
    const container = document.getElementById('resource-graph-canvas');
    const vizContainer = document.getElementById('graph-visualization-container');

    vizContainer.style.display = 'block';

    // Prepare nodes
    const nodes = (graphData.nodes || []).map(node => {
        const category = categorizeResource(node.type);
        return {
            id: node.id,
            label: node.label || node.id,
            title: `${node.type}\n${node.id}`,
            color: RESOURCE_TYPE_COLORS[category] || RESOURCE_TYPE_COLORS['default'],
            shape: 'box',
            font: { size: 14 },
            data: node
        };
    });

    // Prepare edges
    const edges = (graphData.edges || []).map((edge, idx) => ({
        id: idx,
        from: edge.from,
        to: edge.to,
        label: edge.type || 'depends_on',
        arrows: 'to',
        smooth: { type: 'cubicBezier' }
    }));

    // Create vis-network dataset
    resourceGraphData.nodes = new vis.DataSet(nodes);
    resourceGraphData.edges = new vis.DataSet(edges);

    // Network options
    const options = {
        nodes: {
            borderWidth: 2,
            borderWidthSelected: 4,
            shadow: true
        },
        edges: {
            width: 2,
            shadow: true,
            color: {
                color: '#848484',
                highlight: '#2B7CE9',
                hover: '#2B7CE9'
            }
        },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -30000,
                centralGravity: 0.3,
                springLength: 200,
                springConstant: 0.04,
                damping: 0.09,
                avoidOverlap: 0.5
            },
            stabilization: {
                iterations: 200
            }
        },
        interaction: {
            hover: true,
            navigationButtons: true,
            keyboard: true
        }
    };

    // Destroy existing network
    if (resourceGraphData.network) {
        resourceGraphData.network.destroy();
    }

    // Create new network
    resourceGraphData.network = new vis.Network(container, {
        nodes: resourceGraphData.nodes,
        edges: resourceGraphData.edges
    }, options);

    // Event handlers
    resourceGraphData.network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            showNodeDetails(nodeId);
        }
    });

    resourceGraphData.network.on('stabilizationIterationsDone', function() {
        resourceGraphData.network.setOptions({ physics: false });
        resourceGraphData.physicsEnabled = false;
    });

    // Update statistics
    updateGraphStatistics(graphData);

    // Populate type filter
    populateTypeFilter(nodes);

    // Scroll to graph
    vizContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Categorize resource by type
function categorizeResource(resourceType) {
    const type = resourceType.toLowerCase();

    if (type.includes('instance') || type.includes('vm') || type.includes('container')) {
        return 'compute';
    } else if (type.includes('db') || type.includes('database') || type.includes('rds')) {
        return 'database';
    } else if (type.includes('vpc') || type.includes('subnet') || type.includes('route') || type.includes('gateway')) {
        return 'network';
    } else if (type.includes('bucket') || type.includes('storage') || type.includes('volume')) {
        return 'storage';
    } else if (type.includes('sg') || type.includes('security_group') || type.includes('acl')) {
        return 'security';
    } else if (type.includes('lb') || type.includes('load_balancer') || type.includes('alb') || type.includes('elb')) {
        return 'load_balancer';
    }

    return 'default';
}

// Update graph statistics
function updateGraphStatistics(graphData) {
    document.getElementById('graph-total-nodes').textContent = graphData.nodes?.length || 0;
    document.getElementById('graph-total-edges').textContent = graphData.edges?.length || 0;

    const uniqueTypes = new Set((graphData.nodes || []).map(n => categorizeResource(n.type)));
    document.getElementById('graph-resource-types').textContent = uniqueTypes.size;

    document.getElementById('graph-circular-deps').textContent = graphData.circular_dependencies || 0;
}

// Populate type filter dropdown
function populateTypeFilter(nodes) {
    const types = new Set();
    nodes.forEach(node => {
        const category = categorizeResource(node.data.type);
        types.add(category);
    });

    const select = document.getElementById('graph-filter-type');
    let options = '<option value="">All Resource Types</option>';

    Array.from(types).sort().forEach(type => {
        const displayName = type.charAt(0).toUpperCase() + type.slice(1);
        options += `<option value="${type}">${displayName}</option>`;
    });

    select.innerHTML = options;
}

// Show node details
function showNodeDetails(nodeId) {
    const node = resourceGraphData.nodes.get(nodeId);
    if (!node) return;

    const detailsDiv = document.getElementById('selected-node-details');
    const content = document.getElementById('node-details-content');

    // Get connected nodes
    const connectedEdges = resourceGraphData.network.getConnectedEdges(nodeId);
    const connectedNodes = resourceGraphData.network.getConnectedNodes(nodeId);

    const dependencies = connectedNodes.filter(id => {
        const edges = resourceGraphData.network.getConnectedEdges(id);
        return edges.some(edgeId => {
            const edge = resourceGraphData.edges.get(edgeId);
            return edge.from === nodeId && edge.to === id;
        });
    });

    const dependents = connectedNodes.filter(id => {
        const edges = resourceGraphData.network.getConnectedEdges(id);
        return edges.some(edgeId => {
            const edge = resourceGraphData.edges.get(edgeId);
            return edge.from === id && edge.to === nodeId;
        });
    });

    let html = `
        <h6>${node.data.type}</h6>
        <p><code>${node.id}</code></p>

        <div class="row">
            <div class="col-md-6">
                <h6>Dependencies (${dependencies.length})</h6>
                <ul class="list-unstyled">
    `;

    dependencies.forEach(depId => {
        const depNode = resourceGraphData.nodes.get(depId);
        html += `<li><code>${depNode.label}</code></li>`;
    });

    html += `
                </ul>
            </div>
            <div class="col-md-6">
                <h6>Dependents (${dependents.length})</h6>
                <ul class="list-unstyled">
    `;

    dependents.forEach(depId => {
        const depNode = resourceGraphData.nodes.get(depId);
        html += `<li><code>${depNode.label}</code></li>`;
    });

    html += `
                </ul>
            </div>
        </div>
    `;

    if (node.data.properties) {
        html += '<h6 class="mt-3">Properties</h6>';
        html += '<pre class="bg-light p-2">' + JSON.stringify(node.data.properties, null, 2) + '</pre>';
    }

    content.innerHTML = html;
    detailsDiv.style.display = 'block';

    // Highlight connected nodes
    resourceGraphData.network.selectNodes([nodeId, ...connectedNodes]);
}

// Close node details
function closeNodeDetails() {
    document.getElementById('selected-node-details').style.display = 'none';
    resourceGraphData.network.unselectAll();
}

// Search graph nodes
function searchGraphNodes() {
    const searchTerm = document.getElementById('graph-search').value.toLowerCase();

    if (!searchTerm) {
        // Reset all nodes
        resourceGraphData.nodes.forEach(node => {
            resourceGraphData.nodes.update({
                id: node.id,
                opacity: 1.0,
                hidden: false
            });
        });
        return;
    }

    // Filter nodes
    resourceGraphData.nodes.forEach(node => {
        const matches = node.label.toLowerCase().includes(searchTerm) ||
                       node.id.toLowerCase().includes(searchTerm) ||
                       node.data.type.toLowerCase().includes(searchTerm);

        resourceGraphData.nodes.update({
            id: node.id,
            opacity: matches ? 1.0 : 0.2
        });
    });

    // Select matching nodes
    const matchingNodes = resourceGraphData.nodes.get({
        filter: node => {
            return node.label.toLowerCase().includes(searchTerm) ||
                   node.id.toLowerCase().includes(searchTerm) ||
                   node.data.type.toLowerCase().includes(searchTerm);
        }
    }).map(n => n.id);

    if (matchingNodes.length > 0) {
        resourceGraphData.network.selectNodes(matchingNodes);
        resourceGraphData.network.focus(matchingNodes[0], {
            scale: 1.5,
            animation: true
        });
    }
}

// Filter graph by type
function filterGraphByType() {
    const selectedType = document.getElementById('graph-filter-type').value;

    if (!selectedType) {
        // Show all nodes
        resourceGraphData.nodes.forEach(node => {
            resourceGraphData.nodes.update({
                id: node.id,
                hidden: false
            });
        });
        return;
    }

    // Filter by type
    resourceGraphData.nodes.forEach(node => {
        const category = categorizeResource(node.data.type);
        resourceGraphData.nodes.update({
            id: node.id,
            hidden: category !== selectedType
        });
    });
}

// Fit graph to view
function fitGraphToView() {
    if (resourceGraphData.network) {
        resourceGraphData.network.fit({
            animation: {
                duration: 1000,
                easingFunction: 'easeInOutQuad'
            }
        });
    }
}

// Reset graph zoom
function resetGraphZoom() {
    if (resourceGraphData.network) {
        resourceGraphData.network.moveTo({
            scale: 1.0,
            animation: {
                duration: 500,
                easingFunction: 'easeInOutQuad'
            }
        });
    }
}

// Toggle graph physics
function toggleGraphPhysics() {
    if (resourceGraphData.network) {
        resourceGraphData.physicsEnabled = !resourceGraphData.physicsEnabled;
        resourceGraphData.network.setOptions({
            physics: {
                enabled: resourceGraphData.physicsEnabled
            }
        });

        Toast.info(`Physics ${resourceGraphData.physicsEnabled ? 'enabled' : 'disabled'}`);
    }
}

// Export graph as Mermaid
async function exportGraphAsMermaid() {
    try {
        if (!resourceGraphData.rawData) {
            throw new Error('No graph data available. Generate a graph first.');
        }

        Toast.info('Generating Mermaid diagram...');

        const response = await fetch(`${API_BASE}/graph/mermaid`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(resourceGraphData.rawData)
        });

        if (!response.ok) {
            throw new Error('Failed to generate Mermaid diagram');
        }

        const result = await response.json();

        // Display Mermaid code
        const container = document.getElementById('mermaid-diagram-container');
        const codeEl = document.getElementById('mermaid-code');

        codeEl.textContent = result.diagram;
        container.style.display = 'block';

        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        Toast.success('Mermaid diagram generated!');

    } catch (error) {
        Toast.error(`Mermaid export failed: ${error.message}`);
    }
}

// Export graph as DOT
async function exportGraphAsDOT() {
    try {
        if (!resourceGraphData.rawData) {
            throw new Error('No graph data available. Generate a graph first.');
        }

        Toast.info('Generating DOT file...');

        const response = await fetch(`${API_BASE}/graph/dot`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(resourceGraphData.rawData)
        });

        if (!response.ok) {
            throw new Error('Failed to generate DOT file');
        }

        const result = await response.json();

        // Download DOT file
        const blob = new Blob([result.dot], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resource-graph.dot';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        Toast.success('DOT file downloaded!');

    } catch (error) {
        Toast.error(`DOT export failed: ${error.message}`);
    }
}

// Copy Mermaid code to clipboard
function copyMermaidCode() {
    const codeEl = document.getElementById('mermaid-code');
    const text = codeEl.textContent;

    navigator.clipboard.writeText(text).then(() => {
        Toast.success('Mermaid code copied to clipboard!');
    }).catch(() => {
        Toast.error('Failed to copy to clipboard');
    });
}

// ==========================================
// Settings & Configuration Functions
// ==========================================

// Global state for settings
let systemSettings = {
    validation: {},
    report: {},
    storage: {},
    integrations: {},
    preferences: {}
};

// Load validation rules
async function loadValidationRules() {
    try {
        showLoading('Loading validation rules...');

        const response = await fetch(`${API_BASE}/rules/`);
        if (!response.ok) {
            throw new Error('Failed to load rules');
        }

        const rules = await response.json();

        const tbody = document.querySelector('#rules-table tbody');
        tbody.innerHTML = '';

        rules.forEach(rule => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><code>${rule.id}</code></td>
                <td>${rule.name || 'N/A'}</td>
                <td><span class="badge bg-secondary">${rule.category || 'N/A'}</span></td>
                <td><span class="badge bg-${rule.severity === 'critical' ? 'danger' : rule.severity === 'high' ? 'warning' : 'info'}">${rule.severity || 'N/A'}</span></td>
                <td>
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" ${rule.enabled !== false ? 'checked' : ''}
                               onchange="toggleRule('${rule.id}', this.checked)">
                    </div>
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="viewRuleDetails('${rule.id}')">
                        <i class="bi bi-eye"></i> View
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });

        Toast.success('Rules loaded');

    } catch (error) {
        Toast.error(`Failed to load rules: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Filter rules
function filterRules() {
    const searchTerm = document.getElementById('rules-search').value.toLowerCase();
    const rows = document.querySelectorAll('#rules-table tbody tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// Toggle rule enabled/disabled
async function toggleRule(ruleId, enabled) {
    try {
        const response = await fetch(`${API_BASE}/rules/${ruleId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled })
        });

        if (!response.ok) {
            throw new Error('Failed to toggle rule');
        }

        Toast.success(`Rule ${enabled ? 'enabled' : 'disabled'}`);

    } catch (error) {
        Toast.error(`Failed to toggle rule: ${error.message}`);
        // Revert checkbox
        loadValidationRules();
    }
}

// View rule details
async function viewRuleDetails(ruleId) {
    try {
        showLoading('Loading rule details...');

        const response = await fetch(`${API_BASE}/rules/${ruleId}`);
        if (!response.ok) {
            throw new Error('Failed to load rule details');
        }

        const rule = await response.json();

        const detailsDiv = document.getElementById('rule-details-content');
        detailsDiv.innerHTML = `
            <h6>${rule.name || rule.id}</h6>
            <div class="mb-3">
                <strong>ID:</strong> <code>${rule.id}</code><br>
                <strong>Category:</strong> <span class="badge bg-secondary">${rule.category || 'N/A'}</span><br>
                <strong>Severity:</strong> <span class="badge bg-${rule.severity === 'critical' ? 'danger' : rule.severity === 'high' ? 'warning' : 'info'}">${rule.severity || 'N/A'}</span><br>
                <strong>Status:</strong> ${rule.enabled !== false ? '<span class="badge bg-success">Enabled</span>' : '<span class="badge bg-secondary">Disabled</span>'}
            </div>
            <div class="mb-3">
                <strong>Description:</strong>
                <p>${rule.description || 'No description available'}</p>
            </div>
            ${rule.configuration ? `
                <div class="mb-3">
                    <strong>Configuration:</strong>
                    <pre class="bg-light p-2">${JSON.stringify(rule.configuration, null, 2)}</pre>
                </div>
            ` : ''}
        `;

        document.getElementById('rule-details-card').style.display = 'block';

    } catch (error) {
        Toast.error(`Failed to load rule details: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Load system settings
async function loadSystemSettings() {
    try {
        const response = await fetch(`${API_BASE}/settings/`);
        if (response.ok) {
            systemSettings = await response.json();
            populateSettingsForm();
        }
    } catch (error) {
        console.error('Failed to load system settings:', error);
    }
}

// Populate settings form
function populateSettingsForm() {
    if (systemSettings.validation) {
        if (systemSettings.validation.mode) {
            document.getElementById('default-validation-mode').value = systemSettings.validation.mode;
        }
        if (systemSettings.validation.complianceThreshold) {
            document.getElementById('compliance-threshold').value = systemSettings.validation.complianceThreshold;
        }
    }

    if (systemSettings.report) {
        if (systemSettings.report.format) {
            document.getElementById('default-report-format').value = systemSettings.report.format;
        }
        if (systemSettings.report.detailLevel) {
            document.getElementById('report-detail-level').value = systemSettings.report.detailLevel;
        }
    }
}

// Save validation settings
async function saveValidationSettings() {
    try {
        const settings = {
            mode: document.getElementById('default-validation-mode').value,
            complianceThreshold: parseInt(document.getElementById('compliance-threshold').value),
            autoApproveFastTrack: document.getElementById('auto-approve-fast-track').value === 'true',
            requirePatternMatch: document.getElementById('require-pattern-match').checked
        };

        Toast.info('Saving validation settings...');

        const response = await fetch(`${API_BASE}/settings/validation`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        if (!response.ok) {
            throw new Error('Failed to save settings');
        }

        systemSettings.validation = settings;
        Toast.success('Validation settings saved!');

    } catch (error) {
        Toast.error(`Failed to save settings: ${error.message}`);
    }
}

// Save report settings
async function saveReportSettings() {
    try {
        const settings = {
            format: document.getElementById('default-report-format').value,
            detailLevel: document.getElementById('report-detail-level').value,
            includePassedRules: document.getElementById('include-passed-rules').checked,
            includeTopologyDiagram: document.getElementById('include-topology-diagram').checked
        };

        Toast.info('Saving report settings...');

        const response = await fetch(`${API_BASE}/settings/report`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        if (!response.ok) {
            throw new Error('Failed to save settings');
        }

        systemSettings.report = settings;
        Toast.success('Report settings saved!');

    } catch (error) {
        Toast.error(`Failed to save settings: ${error.message}`);
    }
}

// Save storage settings
async function saveStorageSettings() {
    try {
        const settings = {
            retentionDays: parseInt(document.getElementById('history-retention-days').value),
            maxReportSize: parseInt(document.getElementById('max-report-size').value),
            backupFrequency: document.getElementById('backup-frequency').value
        };

        Toast.info('Saving storage settings...');

        const response = await fetch(`${API_BASE}/settings/storage`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        if (!response.ok) {
            throw new Error('Failed to save settings');
        }

        systemSettings.storage = settings;
        Toast.success('Storage settings saved!');

    } catch (error) {
        Toast.error(`Failed to save settings: ${error.message}`);
    }
}

// Cleanup old records
async function cleanupOldRecords() {
    if (!confirm('This will delete validation history older than the retention period. Continue?')) {
        return;
    }

    try {
        Toast.info('Cleaning up old records...');
        showLoading('Deleting old records...');

        const response = await fetch(`${API_BASE}/maintenance/cleanup`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Cleanup failed');
        }

        const result = await response.json();
        Toast.success(`Cleanup complete! Deleted ${result.deletedCount || 0} records.`);

    } catch (error) {
        Toast.error(`Cleanup failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Test CMDB connection
async function testCMDBConnection() {
    try {
        const config = {
            type: document.getElementById('cmdb-type').value,
            endpoint: document.getElementById('cmdb-endpoint').value,
            apiKey: document.getElementById('cmdb-api-key').value
        };

        if (!config.endpoint || !config.apiKey) {
            Toast.warning('Please provide endpoint and API key');
            return;
        }

        Toast.info('Testing CMDB connection...');
        showLoading('Connecting to CMDB...');

        const response = await fetch(`${API_BASE}/integrations/cmdb/test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            throw new Error('Connection test failed');
        }

        const result = await response.json();
        Toast.success(`Connection successful! Found ${result.recordCount || 0} records.`);

    } catch (error) {
        Toast.error(`Connection failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Save CMDB settings
async function saveCMDBSettings() {
    try {
        const config = {
            type: document.getElementById('cmdb-type').value,
            endpoint: document.getElementById('cmdb-endpoint').value,
            apiKey: document.getElementById('cmdb-api-key').value
        };

        Toast.info('Saving CMDB settings...');

        const response = await fetch(`${API_BASE}/integrations/cmdb`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            throw new Error('Failed to save settings');
        }

        systemSettings.integrations.cmdb = config;
        Toast.success('CMDB settings saved!');

    } catch (error) {
        Toast.error(`Failed to save settings: ${error.message}`);
    }
}

// Save Git settings
async function saveGitSettings() {
    try {
        const config = {
            repoUrl: document.getElementById('git-repo-url').value,
            branch: document.getElementById('git-branch').value,
            token: document.getElementById('git-token').value,
            autoSync: document.getElementById('git-auto-sync').checked
        };

        Toast.info('Saving Git settings...');

        const response = await fetch(`${API_BASE}/integrations/git`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            throw new Error('Failed to save settings');
        }

        systemSettings.integrations.git = config;
        Toast.success('Git settings saved!');

    } catch (error) {
        Toast.error(`Failed to save settings: ${error.message}`);
    }
}

// Save user preferences
async function saveUserPreferences() {
    try {
        const preferences = {
            theme: document.getElementById('ui-theme').value,
            itemsPerPage: parseInt(document.getElementById('items-per-page').value),
            dateFormat: document.getElementById('date-format').value,
            timezone: document.getElementById('timezone').value,
            showTooltips: document.getElementById('show-tooltips').checked,
            enableAnimations: document.getElementById('enable-animations').checked,
            autoRefresh: document.getElementById('auto-refresh').checked
        };

        // Save to localStorage
        localStorage.setItem('userPreferences', JSON.stringify(preferences));

        systemSettings.preferences = preferences;
        Toast.success('Preferences saved!');

        // Apply theme if changed
        applyTheme(preferences.theme);

    } catch (error) {
        Toast.error(`Failed to save preferences: ${error.message}`);
    }
}

// Reset preferences to defaults
function resetPreferences() {
    if (!confirm('Reset all preferences to defaults?')) {
        return;
    }

    localStorage.removeItem('userPreferences');

    document.getElementById('ui-theme').value = 'light';
    document.getElementById('items-per-page').value = '50';
    document.getElementById('date-format').value = 'MM/DD/YYYY';
    document.getElementById('timezone').value = 'UTC';
    document.getElementById('show-tooltips').checked = true;
    document.getElementById('enable-animations').checked = true;
    document.getElementById('auto-refresh').checked = false;

    Toast.success('Preferences reset to defaults');
}

// Apply theme
function applyTheme(theme) {
    // Theme application would be implemented based on CSS classes
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
}

// Export configuration
async function exportConfiguration() {
    try {
        Toast.info('Exporting configuration...');
        showLoading('Generating export...');

        const response = await fetch(`${API_BASE}/export/configuration`);
        if (!response.ok) {
            throw new Error('Export failed');
        }

        const config = await response.json();

        const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `architecture-validation-config-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        Toast.success('Configuration exported!');

    } catch (error) {
        Toast.error(`Export failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Import configuration
async function importConfiguration(file) {
    if (!file) return;

    if (!confirm('Importing will overwrite existing configuration. Continue?')) {
        return;
    }

    try {
        Toast.info('Importing configuration...');
        showLoading('Importing...');

        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                const config = JSON.parse(e.target.result);

                const response = await fetch(`${API_BASE}/import/configuration`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });

                if (!response.ok) {
                    throw new Error('Import failed');
                }

                Toast.success('Configuration imported! Reloading...');
                setTimeout(() => window.location.reload(), 2000);

            } catch (error) {
                Toast.error(`Import failed: ${error.message}`);
            } finally {
                hideLoading();
            }
        };

        reader.readAsText(file);

    } catch (error) {
        Toast.error(`Import failed: ${error.message}`);
        hideLoading();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Architecture Validation System loaded');

    // Load user preferences from localStorage
    const savedPreferences = localStorage.getItem('userPreferences');
    if (savedPreferences) {
        try {
            const preferences = JSON.parse(savedPreferences);
            systemSettings.preferences = preferences;
            applyTheme(preferences.theme);
        } catch (error) {
            console.error('Failed to load preferences:', error);
        }
    }
});
