/**
 * ComparisonPanel - EKF vs MetaSpace összehasonlítás komponens
 * Moduláris UI architektúra - Component
 */
import ComponentBase from '../../core/ComponentBase.js';

class ComparisonPanel extends ComponentBase {
    async render(data = null) {
        // Ha nincs adat, placeholder adatok használata
        if (!data || (!data.ekf && !data.metaspace)) {
            data = {
                ekf: {
                    feasibility: 0,
                    decision: 'LOADING...',
                    confidence: 0,
                    anomaly_detected: false,
                    scenes_today: 0,
                    data_loss_today: 0
                },
                metaspace: {
                    feasibility: 0,
                    action: 'LOADING...',
                    safety_margin: 0,
                    biocode_level3: 'N/A'
                }
            };
        }
        
        const { ekf = {}, metaspace = {} } = data;
        
        this.container.innerHTML = `
            <div class="comparison-panel">
                <div class="comparison-header">
                    <h3>EKF vs MetaSpace Comparison</h3>
                    <div class="comparison-timestamp" id="comparison-timestamp"></div>
                </div>
                <div class="comparison-content">
                    <div class="comparison-column ekf-column">
                        <div class="column-header">
                            <h4>EKF</h4>
                            <div class="column-status" id="ekf-status"></div>
                        </div>
                        <div class="comparison-metrics">
                            <div class="metric">
                                <label>Feasibility:</label>
                                <div class="metric-value" id="ekf-feasibility">${ekf.feasibility !== undefined ? ekf.feasibility.toFixed(1) : 'N/A'}%</div>
                            </div>
                            <div class="metric">
                                <label>Decision:</label>
                                <div class="metric-value" id="ekf-decision">${ekf.decision || 'N/A'}</div>
                            </div>
                            <div class="metric">
                                <label>Confidence:</label>
                                <div class="metric-value" id="ekf-confidence">${ekf.confidence !== undefined ? ekf.confidence.toFixed(1) : 'N/A'}%</div>
                            </div>
                            <div class="metric">
                                <label>Anomaly:</label>
                                <div class="metric-value" id="ekf-anomaly">${ekf.anomaly_detected ? 'DETECTED' : 'NONE'}</div>
                            </div>
                            <div class="metric">
                                <label>Scenes Today:</label>
                                <div class="metric-value" id="ekf-scenes">${ekf.scenes_today !== undefined ? ekf.scenes_today : 'N/A'}</div>
                            </div>
                            <div class="metric">
                                <label>Data Loss:</label>
                                <div class="metric-value" id="ekf-data-loss">${ekf.data_loss_today !== undefined ? ekf.data_loss_today : 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                    <div class="comparison-column metaspace-column">
                        <div class="column-header">
                            <h4>MetaSpace</h4>
                            <div class="column-status" id="metaspace-status"></div>
                        </div>
                        <div class="comparison-metrics">
                            <div class="metric">
                                <label>Feasibility:</label>
                                <div class="metric-value" id="metaspace-feasibility">${metaspace.feasibility !== undefined ? metaspace.feasibility.toFixed(1) : 'N/A'}%</div>
                            </div>
                            <div class="metric">
                                <label>Decision:</label>
                                <div class="metric-value" id="metaspace-decision">${metaspace.action || 'N/A'}</div>
                            </div>
                            <div class="metric">
                                <label>Safety Margin:</label>
                                <div class="metric-value" id="metaspace-safety">${metaspace.safety_margin !== undefined ? metaspace.safety_margin : 'N/A'}</div>
                            </div>
                            <div class="metric">
                                <label>Bio-code L3:</label>
                                <div class="metric-value bio-code" id="metaspace-biocode">${metaspace.biocode_level3 || 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="comparison-difference" id="comparison-difference">
                    <div class="difference-label">Difference:</div>
                    <div class="difference-value" id="difference-value">-</div>
                </div>
            </div>
        `;
        
        // Státusz frissítése (azonnal, mert a DOM már frissült)
        this._updateStatus('ekf', ekf);
        this._updateStatus('metaspace', metaspace);
        this._updateDifference(ekf, metaspace);
        this._updateTimestamp();
        
        // ÖSSZES mező frissítése
        this._updateMetrics('ekf', ekf);
        this._updateMetrics('metaspace', metaspace);
    }
    
    /**
     * Metrikák frissítése
     * @private
     */
    _updateMetrics(type, data) {
        if (!data) return;
        
        // EKF metrikák
        if (type === 'ekf') {
            const feasibilityEl = document.getElementById('ekf-feasibility');
            const decisionEl = document.getElementById('ekf-decision');
            const confidenceEl = document.getElementById('ekf-confidence');
            const anomalyEl = document.getElementById('ekf-anomaly');
            const scenesEl = document.getElementById('ekf-scenes');
            const dataLossEl = document.getElementById('ekf-data-loss');
            
            if (feasibilityEl) feasibilityEl.textContent = data.feasibility !== undefined ? `${data.feasibility.toFixed(1)}%` : 'N/A';
            if (decisionEl) decisionEl.textContent = data.decision || 'N/A';
            if (confidenceEl) confidenceEl.textContent = data.confidence !== undefined ? `${data.confidence.toFixed(1)}%` : 'N/A';
            if (anomalyEl) anomalyEl.textContent = data.anomaly_detected ? 'DETECTED' : 'NONE';
            if (scenesEl) scenesEl.textContent = data.scenes_today !== undefined ? data.scenes_today : 'N/A';
            if (dataLossEl) dataLossEl.textContent = data.data_loss_today !== undefined ? data.data_loss_today : 'N/A';
        }
        
        // MetaSpace metrikák
        if (type === 'metaspace') {
            const feasibilityEl = document.getElementById('metaspace-feasibility');
            const decisionEl = document.getElementById('metaspace-decision');
            const safetyEl = document.getElementById('metaspace-safety');
            const biocodeEl = document.getElementById('metaspace-biocode');
            
            if (feasibilityEl) feasibilityEl.textContent = data.feasibility !== undefined ? `${data.feasibility.toFixed(1)}%` : 'N/A';
            if (decisionEl) decisionEl.textContent = data.action || 'N/A';
            if (safetyEl) safetyEl.textContent = data.safety_margin !== undefined ? data.safety_margin : 'N/A';
            if (biocodeEl) biocodeEl.textContent = data.biocode_level3 || 'N/A';
        }
    }
    
    /**
     * Update metódus - meglévő render frissítése
     */
    async update(data) {
        if (!data || (!data.ekf && !data.metaspace)) {
            console.warn('[ComparisonPanel] No data provided for update');
            return;
        }
        
        const { ekf = {}, metaspace = {} } = data;
        
        console.log('[ComparisonPanel] Updating with data:', { ekf, metaspace });
        
        // Csak a mezőket frissítjük, nem újrarendereljük az egészet
        // Késleltetés, hogy a DOM biztosan frissüljön
        setTimeout(() => {
            this._updateStatus('ekf', ekf);
            this._updateStatus('metaspace', metaspace);
            this._updateMetrics('ekf', ekf);
            this._updateMetrics('metaspace', metaspace);
            this._updateDifference(ekf, metaspace);
            this._updateTimestamp();
            console.log('[ComparisonPanel] Update completed');
        }, 50);
    }
    
    attachEventListeners() {
        // Real-time frissítés esemény figyelése
        this.onEvent('comparison:updated', (data) => {
            this.update(data);
        });
    }
    
    /**
     * Státusz frissítése
     * @private
     */
    _updateStatus(type, data) {
        const statusEl = document.getElementById(`${type}-status`);
        if (!statusEl) {
            console.warn(`[ComparisonPanel] Status element not found: ${type}-status`);
            return;
        }
        
        if (!data) {
            console.warn(`[ComparisonPanel] No data for ${type}`);
            statusEl.textContent = 'NO DATA';
            statusEl.className = 'column-status status-warning';
            return;
        }
        
        // Feasibility vagy confidence használata
        const feasibility = data.feasibility !== undefined ? data.feasibility : 
                           (data.confidence !== undefined ? data.confidence : 100);
        
        let status = 'NOMINAL';
        let statusClass = 'status-nominal';
        
        // Státusz meghatározása
        if (data.anomaly_detected === true || feasibility < 40) {
            status = 'CRITICAL';
            statusClass = 'status-critical';
        } else if (feasibility < 70) {
            status = 'WARNING';
            statusClass = 'status-warning';
        }
        
        statusEl.textContent = status;
        statusEl.className = `column-status ${statusClass}`;
        console.log(`[ComparisonPanel] ${type} status: ${status} (feasibility: ${feasibility})`);
    }
    
    /**
     * Különbség számítása és megjelenítése
     * @private
     */
    _updateDifference(ekf, metaspace) {
        const diffEl = document.getElementById('difference-value');
        if (!diffEl) {
            console.warn('[ComparisonPanel] Difference element not found');
            return;
        }
        
        const ekfFeas = ekf.feasibility || 0;
        const msFeas = metaspace.feasibility || 0;
        const difference = msFeas - ekfFeas;
        
        diffEl.textContent = `${difference > 0 ? '+' : ''}${difference.toFixed(1)}%`;
        diffEl.className = `difference-value ${difference > 0 ? 'positive' : difference < 0 ? 'negative' : 'neutral'}`;
    }
    
    /**
     * Metrikák frissítése
     * @private
     */
    _updateMetrics(type, data) {
        if (!data) {
            console.warn(`[ComparisonPanel] No data for ${type} metrics`);
            return;
        }
        
        console.log(`[ComparisonPanel] Updating ${type} metrics:`, data);
        
        // EKF metrikák
        if (type === 'ekf') {
            const feasibilityEl = document.getElementById('ekf-feasibility');
            const decisionEl = document.getElementById('ekf-decision');
            const confidenceEl = document.getElementById('ekf-confidence');
            const anomalyEl = document.getElementById('ekf-anomaly');
            const scenesEl = document.getElementById('ekf-scenes');
            const dataLossEl = document.getElementById('ekf-data-loss');
            
            if (feasibilityEl) {
                const feas = data.feasibility !== undefined ? data.feasibility : (data.confidence !== undefined ? data.confidence : null);
                feasibilityEl.textContent = feas !== null ? `${feas.toFixed(1)}%` : 'N/A';
                console.log(`[ComparisonPanel] EKF feasibility: ${feas}`);
            }
            if (decisionEl) {
                decisionEl.textContent = data.decision || 'N/A';
                console.log(`[ComparisonPanel] EKF decision: ${data.decision || 'N/A'}`);
            }
            if (confidenceEl) {
                confidenceEl.textContent = data.confidence !== undefined ? `${data.confidence.toFixed(1)}%` : 'N/A';
            }
            if (anomalyEl) {
                anomalyEl.textContent = data.anomaly_detected ? 'DETECTED' : 'NONE';
            }
            if (scenesEl) {
                scenesEl.textContent = data.scenes_today !== undefined ? data.scenes_today : 'N/A';
            }
            if (dataLossEl) {
                dataLossEl.textContent = data.data_loss_today !== undefined ? data.data_loss_today : 'N/A';
            }
        }
        
        // MetaSpace metrikák
        if (type === 'metaspace') {
            const feasibilityEl = document.getElementById('metaspace-feasibility');
            const decisionEl = document.getElementById('metaspace-decision');
            const safetyEl = document.getElementById('metaspace-safety');
            const biocodeEl = document.getElementById('metaspace-biocode');
            
            if (feasibilityEl) {
                feasibilityEl.textContent = data.feasibility !== undefined ? `${data.feasibility.toFixed(1)}%` : 'N/A';
                console.log(`[ComparisonPanel] MetaSpace feasibility: ${data.feasibility}`);
            }
            if (decisionEl) {
                decisionEl.textContent = data.action || 'N/A';
                console.log(`[ComparisonPanel] MetaSpace action: ${data.action || 'N/A'}`);
            }
            if (safetyEl) {
                safetyEl.textContent = data.safety_margin !== undefined ? `${data.safety_margin}%` : 'N/A';
            }
            if (biocodeEl) {
                biocodeEl.textContent = data.biocode_level3 || 'N/A';
            }
        }
    }
    
    /**
     * Timestamp frissítése
     * @private
     */
    _updateTimestamp() {
        const timestampEl = document.getElementById('comparison-timestamp');
        if (timestampEl) {
            timestampEl.textContent = new Date().toLocaleTimeString();
        }
    }
}

export default ComparisonPanel;

