/**
 * NavigationService - Navigációs terv API szolgáltatás
 * Moduláris UI architektúra - Service modul
 */
import apiClient from '../core/APIClient.js';

class NavigationService {
    /**
     * Navigációs terv betöltése
     * @param {string} planId - Terv ID (opcionális, default: 'default')
     * @returns {Promise} Navigációs terv adatok
     */
    async loadPlan(planId = 'default') {
        return await apiClient.get(`/api/navigation/plan/${planId}`);
    }
    
    /**
     * Jelenlegi orbit lekérése
     * @param {string} time - UTC időpont (HH:MM:SS formátum, opcionális)
     * @returns {Promise} Jelenlegi orbit adatok
     */
    async getCurrentOrbit(time = null) {
        const params = time ? { time } : {};
        return await apiClient.get('/api/navigation/current-orbit', params);
    }
    
    /**
     * Közelgő task-ok lekérése
     * @param {number} lookahead - Hány perc előre nézzünk (alapértelmezett: 60)
     * @returns {Promise} Közelgő task-ok listája
     */
    async getUpcomingTasks(lookahead = 60) {
        return await apiClient.get('/api/navigation/upcoming-tasks', { lookahead });
    }
    
    /**
     * Adott időpontban végrehajtandó task
     * @param {string} time - UTC időpont (HH:MM:SS formátum)
     * @returns {Promise} Task adatok vagy null
     */
    async getTaskAtTime(time) {
        return await apiClient.get('/api/navigation/task-at-time', { time });
    }
    
    /**
     * Orbit paraméterek lekérése
     * @returns {Promise} Orbit paraméterek (altitude, period, inclination, stb.)
     */
    async getOrbitParameters() {
        return await apiClient.get('/api/navigation/orbit-parameters');
    }
}

// Singleton instance exportálása
const navigationService = new NavigationService();

export default navigationService;

