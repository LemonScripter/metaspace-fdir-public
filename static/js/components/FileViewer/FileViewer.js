/**
 * FileViewer - Bio-code és EKF fájlok megjelenítése
 * Moduláris UI architektúra - Component
 */
import ComponentBase from '../../core/ComponentBase.js';

class FileViewer extends ComponentBase {
    constructor(container, config = {}) {
        super(container, config);
        this.fileType = config.fileType || 'biocode'; // 'biocode' vagy 'ekf'
        this.currentLevel = null;
    }
    
    async render(data = null) {
        // Ha nincs adat, placeholder üzenet
        if (!data || (!data.level1 && !data.level2 && !data.level3)) {
            this.container.innerHTML = `
            <div class="file-viewer">
                <div class="file-viewer-header">
                    <h3>${this.fileType.toUpperCase()} Files</h3>
                    <div class="file-viewer-tabs">
                        <button class="tab-button" data-level="1">Level 1</button>
                        <button class="tab-button" data-level="2">Level 2</button>
                        <button class="tab-button active" data-level="3">Level 3</button>
                    </div>
                </div>
                <div class="file-viewer-content">
                    <div class="file-viewer-empty" style="padding: 20px; text-align: center; color: #0ff;">
                        <p>Loading ${this.fileType} files...</p>
                        <p style="font-size: 11px; color: #666;">Waiting for data...</p>
                    </div>
                </div>
            </div>
        `;
            // Tab listener-ek hozzáadása
            this.attachEventListeners();
            return;
        }
        
        const { level1, level2, level3, file_paths = {}, validation = {} } = data;
        
        this.container.innerHTML = `
            <div class="file-viewer">
                <div class="file-viewer-header">
                    <h3>${this.fileType.toUpperCase()} Files</h3>
                    <div class="file-viewer-tabs">
                        <button class="tab-button ${this.currentLevel === 1 ? 'active' : ''}" data-level="1">Level 1</button>
                        <button class="tab-button ${this.currentLevel === 2 ? 'active' : ''}" data-level="2">Level 2</button>
                        <button class="tab-button ${this.currentLevel === 3 ? 'active' : ''}" data-level="3">Level 3</button>
                    </div>
                </div>
                <div class="file-viewer-content">
                    <div class="file-viewer-level" id="file-level-1" style="display: ${this.currentLevel === 1 ? 'block' : 'none'}">
                        ${this._renderLevel(1, level1, file_paths.level1)}
                    </div>
                    <div class="file-viewer-level" id="file-level-2" style="display: ${this.currentLevel === 2 ? 'block' : 'none'}">
                        ${this._renderLevel(2, level2, file_paths.level2)}
                    </div>
                    <div class="file-viewer-level" id="file-level-3" style="display: ${this.currentLevel === 3 ? 'block' : 'none'}">
                        ${this._renderLevel(3, level3, file_paths.level3)}
                    </div>
                </div>
                ${validation.passed !== undefined ? this._renderValidation(validation) : ''}
            </div>
        `;
        
        // Alapértelmezett: Level 3 megjelenítése
        if (!this.currentLevel) {
            this.showLevel(3);
        }
    }
    
    /**
     * Szint renderelése
     * @private
     */
    _renderLevel(level, data, filePath) {
        if (!data) {
            return `<div class="file-viewer-empty">No Level ${level} data available</div>`;
        }
        
        if (this.fileType === 'biocode') {
            return this._renderBioCodeLevel(level, data, filePath);
        } else {
            return this._renderEKFLevel(level, data, filePath);
        }
    }
    
    /**
     * Bio-code szint renderelése
     * @private
     */
    _renderBioCodeLevel(level, data, filePath) {
        if (level === 1) {
            const biocodes = data.biocodes || {};
            return `
                <div class="file-viewer-info">
                    <div class="file-path">File: ${filePath || 'N/A'}</div>
                    <div class="file-count">Nodes: ${data.count || 0}</div>
                    <div class="file-description" style="font-size: 11px; color: rgba(0, 243, 255, 0.6); margin-top: 5px;">
                        Node-level health status (64-bit bio-codes per component)
                    </div>
                </div>
                <div class="file-viewer-data">
                    ${Object.entries(biocodes).map(([nodeId, biocode]) => `
                        <div class="biocode-entry">
                            <div class="biocode-node">
                                <strong>${nodeId}</strong>
                                <span style="font-size: 10px; color: rgba(0, 243, 255, 0.5); display: block; margin-top: 2px;">Component</span>
                            </div>
                            <div class="biocode-value">
                                <code>${biocode}</code>
                                <span style="font-size: 10px; color: rgba(0, 243, 255, 0.5); display: block; margin-top: 2px;">64-bit bio-code</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else if (level === 2) {
            const biocodes = data.biocodes || {};
            return `
                <div class="file-viewer-info">
                    <div class="file-path">File: ${filePath || 'N/A'}</div>
                    <div class="file-count">Modules: ${data.count || 0}</div>
                    <div class="file-description" style="font-size: 11px; color: rgba(0, 243, 255, 0.6); margin-top: 5px;">
                        Module-level aggregation (32-bit bio-codes per subsystem)
                    </div>
                </div>
                <div class="file-viewer-data">
                    ${Object.entries(biocodes).map(([moduleName, biocode]) => `
                        <div class="biocode-entry">
                            <div class="biocode-module">
                                <strong>${moduleName}</strong>
                                <span style="font-size: 10px; color: rgba(0, 243, 255, 0.5); display: block; margin-top: 2px;">Subsystem</span>
                            </div>
                            <div class="biocode-value">
                                <code>${biocode}</code>
                                <span style="font-size: 10px; color: rgba(0, 243, 255, 0.5); display: block; margin-top: 2px;">32-bit bio-code</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else if (level === 3) {
            return `
                <div class="file-viewer-info">
                    <div class="file-path">File: ${filePath || 'N/A'}</div>
                    <div class="file-mission-day">Mission Day: ${data.mission_day || 'N/A'}</div>
                </div>
                <div class="file-viewer-data">
                    <div class="biocode-entry">
                        <div class="biocode-label">Bio-code:</div>
                        <div class="biocode-value large">${data.biocode || 'N/A'}</div>
                    </div>
                    <div class="biocode-entry">
                        <div class="biocode-label">Feasibility:</div>
                        <div class="biocode-value">${data.feasibility !== undefined ? data.feasibility.toFixed(1) : 'N/A'}%</div>
                    </div>
                    <div class="biocode-entry">
                        <div class="biocode-label">Action:</div>
                        <div class="biocode-value">${data.action || 'N/A'}</div>
                    </div>
                    <div class="biocode-entry">
                        <div class="biocode-label">Safety Margin:</div>
                        <div class="biocode-value">${data.safety_margin !== undefined ? data.safety_margin : 'N/A'}</div>
                    </div>
                </div>
            `;
        }
        return '';
    }
    
    /**
     * EKF szint renderelése
     * @private
     */
    _renderEKFLevel(level, data, filePath) {
        if (level === 1) {
            const sensors = data.sensors || {};
            return `
                <div class="file-viewer-info">
                    <div class="file-path">File: ${filePath || 'N/A'}</div>
                    <div class="file-count">Sensors: ${data.count || 0}</div>
                </div>
                <div class="file-viewer-data">
                    ${Object.entries(sensors).map(([sensorId, sensorData]) => `
                        <div class="ekf-entry">
                            <div class="ekf-sensor">${sensorId}</div>
                            <div class="ekf-details">
                                <div>Measurement: ${sensorData.measurement?.toFixed(3) || 'N/A'}</div>
                                <div>State Estimate: ${sensorData.state_estimate?.toFixed(3) || 'N/A'}</div>
                                <div>Covariance: ${sensorData.covariance?.toFixed(3) || 'N/A'}</div>
                                <div>Confidence: ${sensorData.confidence?.toFixed(1) || 'N/A'}%</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else if (level === 2) {
            const subsystems = data.subsystems || {};
            return `
                <div class="file-viewer-info">
                    <div class="file-path">File: ${filePath || 'N/A'}</div>
                    <div class="file-count">Subsystems: ${data.count || 0}</div>
                    <div class="file-description" style="font-size: 11px; color: rgba(0, 243, 255, 0.6); margin-top: 5px;">
                        Subsystem-level EKF data (navigation, power, payload, comm subsystem health, aggregated state vectors, covariance traces)
                    </div>
                </div>
                <div class="file-viewer-data">
                    ${Object.entries(subsystems).map(([subsystemName, subsystemData]) => `
                        <div class="ekf-entry">
                            <div class="ekf-subsystem">
                                <strong>${subsystemName}</strong>
                                <span style="font-size: 10px; color: rgba(0, 243, 255, 0.5); display: block; margin-top: 2px;">Subsystem</span>
                            </div>
                            <div class="ekf-details">
                                <div>
                                    <strong>Health:</strong> ${subsystemData.health?.toFixed(1) || 'N/A'}%
                                    <span style="font-size: 10px; color: rgba(0, 243, 255, 0.5); display: block; margin-top: 2px;">Subsystem health percentage</span>
                                </div>
                                <div>
                                    <strong>Covariance Trace:</strong> ${subsystemData.covariance_trace?.toFixed(3) || 'N/A'}
                                    <span style="font-size: 10px; color: rgba(0, 243, 255, 0.5); display: block; margin-top: 2px;">Aggregated uncertainty measure</span>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else if (level === 3) {
            return `
                <div class="file-viewer-info">
                    <div class="file-path">File: ${filePath || 'N/A'}</div>
                    <div class="file-mission-day">Mission Day: ${data.mission_day || 'N/A'}</div>
                </div>
                <div class="file-viewer-data">
                    <div class="ekf-entry">
                        <div class="ekf-label">Feasibility:</div>
                        <div class="ekf-value">${data.feasibility !== undefined ? data.feasibility.toFixed(1) : 'N/A'}%</div>
                    </div>
                    <div class="ekf-entry">
                        <div class="ekf-label">Anomaly Detected:</div>
                        <div class="ekf-value">${data.anomaly_detected ? 'YES' : 'NO'}</div>
                    </div>
                    <div class="ekf-entry">
                        <div class="ekf-label">Detection Latency:</div>
                        <div class="ekf-value">${data.detection_latency !== undefined ? data.detection_latency : 'N/A'} min</div>
                    </div>
                    <div class="ekf-entry">
                        <div class="ekf-label">Confidence:</div>
                        <div class="ekf-value">${data.confidence !== undefined ? data.confidence.toFixed(1) : 'N/A'}%</div>
                    </div>
                    <div class="ekf-entry">
                        <div class="ekf-label">Decision:</div>
                        <div class="ekf-value">${data.decision || 'N/A'}</div>
                    </div>
                    <div class="ekf-entry">
                        <div class="ekf-label">Scenes Today:</div>
                        <div class="ekf-value">${data.scenes_today !== undefined ? data.scenes_today : 'N/A'}</div>
                    </div>
                    <div class="ekf-entry">
                        <div class="ekf-label">Data Loss:</div>
                        <div class="ekf-value">${data.data_loss_today !== undefined ? data.data_loss_today : 'N/A'}</div>
                    </div>
                </div>
            `;
        }
        return '';
    }
    
    /**
     * Validáció renderelése
     * @private
     */
    _renderValidation(validation) {
        const status = validation.passed ? 'PASSED' : 'FAILED';
        const statusClass = validation.passed ? 'validation-passed' : 'validation-failed';
        
        return `
            <div class="file-viewer-validation ${statusClass}">
                <div class="validation-status">Validation: ${status}</div>
                ${validation.encrypted_validation ? `
                    <div class="validation-details">
                        Encrypted Validation: ${validation.encrypted_validation.passed ? 'PASSED' : 'FAILED'}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    attachEventListeners() {
        // Tab gombok - DELEGATION használata (mert a gombok dinamikusan jönnek létre)
        if (this.container) {
            this.container.addEventListener('click', (e) => {
                if (e.target.classList.contains('tab-button')) {
                    const level = parseInt(e.target.dataset.level);
                    if (level) {
                        console.log(`[FileViewer] Tab clicked: Level ${level}`);
                        this.showLevel(level);
                    }
                }
            });
        }
        
        // Real-time frissítés
        this.onEvent('files:updated', (data) => {
            this.update(data);
        });
    }
    
    /**
     * Szint megjelenítése
     * @param {number} level - Szint (1, 2, vagy 3)
     */
    showLevel(level) {
        this.currentLevel = level;
        
        if (!this.container) {
            console.warn('[FileViewer] Container not found for showLevel');
            return;
        }
        
        // Tab gombok frissítése
        const tabButtons = this.container.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            if (parseInt(button.dataset.level) === level) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        // Szint tartalmak megjelenítése/elrejtése
        for (let i = 1; i <= 3; i++) {
            const levelEl = this.container.querySelector(`#file-level-${i}`);
            if (levelEl) {
                levelEl.style.display = i === level ? 'block' : 'none';
            } else {
                console.warn(`[FileViewer] Level ${i} element not found`);
            }
        }
        
        console.log(`[FileViewer] Switched to Level ${level}`);
    }
}

export default FileViewer;

