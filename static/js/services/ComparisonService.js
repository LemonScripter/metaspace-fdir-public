/**
 * ComparisonService - EKF vs MetaSpace összehasonlítás API szolgáltatás
 * Moduláris UI architektúra - Service modul
 */
import apiClient from '../core/APIClient.js';

class ComparisonService {
    /**
     * Összehasonlítási metrikák lekérése
     * @param {number} missionDay - Mission day (opcionális)
     * @returns {Promise} Összehasonlítási adatok
     */
    async getMetrics(missionDay = null) {
        const params = missionDay ? { mission_day: missionDay } : {};
        return await apiClient.get('/api/comparison/metrics', params);
    }
    
    /**
     * Real-time összehasonlítás indítása
     * @param {Object} config - Konfiguráció (mission_day, update_interval, stb.)
     * @returns {Promise} Stream ID vagy connection info
     */
    async startRealTimeComparison(config = {}) {
        return await apiClient.post('/api/comparison/start', config);
    }
    
    /**
     * Real-time összehasonlítás leállítása
     * @param {string} streamId - Stream ID
     * @returns {Promise} Leállítás megerősítése
     */
    async stopRealTimeComparison(streamId) {
        return await apiClient.post('/api/comparison/stop', { stream_id: streamId });
    }
}

// Singleton instance exportálása
const comparisonService = new ComparisonService();

export default comparisonService;


