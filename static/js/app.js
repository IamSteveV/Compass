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

    // Fade out current section
    [validateSection, patternsSection, notificationsSection].forEach(s => {
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
        } else if (section === 'notifications') {
            notificationsSection.style.display = 'block';
            setTimeout(() => { notificationsSection.style.opacity = '1'; }, 10);
            loadNotificationSettings();
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Architecture Validation System loaded');
});
