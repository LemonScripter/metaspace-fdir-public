/**
 * EKFService - EKF fájlok API szolgáltatás
 * Moduláris UI architektúra - Service modul
 */
import apiClient from '../core/APIClient.js';

class EKFService {
    /**
     * Legutóbbi EKF fájlok lekérése
     * @param {number} missionDay - Mission day (opcionális)
     * @returns {Promise} Fájl elérési utak és adatok
     */
    async getLatestFiles(missionDay = null) {
        const params = missionDay ? { mission_day: missionDay } : {};
        return await apiClient.get('/api/ekf/files/latest', params);
    }
    
    /**
     * EKF fájl betöltése
     * @param {string} filePath - Fájl elérési út
     * @returns {Promise} Fájl tartalma
     */
    async loadFile(filePath) {
        return await apiClient.get('/api/ekf/files/load', { path: filePath });
    }
    
    /**
     * Minden 3 szintű EKF fájl betöltése
     * @param {number} missionDay - Mission day (opcionális)
     * @returns {Promise} { level1, level2, level3 } adatok
     */
    async loadAllLevels(missionDay = null) {
        try {
            const files = await this.getLatestFiles(missionDay);
            console.log('[EKFService] getLatestFiles response:', files);
            
            // API válasz struktúrájának kezelése
            const file_paths = files.file_paths || (files.status === 'success' ? files : null);
            
            if (!file_paths || (!file_paths.level1 && !file_paths.level2 && !file_paths.level3)) {
                console.warn('[EKFService] No file paths found');
                return { level1: null, level2: null, level3: null };
            }
            
            const { level1, level2, level3 } = file_paths;
            console.log('[EKFService] Loading files:', { level1, level2, level3 });
            
            const [level1Data, level2Data, level3Data] = await Promise.all([
                level1 ? this.loadFile(level1).catch((e) => {
                    console.error('[EKFService] Failed to load level1:', e);
                    return null;
                }) : Promise.resolve(null),
                level2 ? this.loadFile(level2).catch((e) => {
                    console.error('[EKFService] Failed to load level2:', e);
                    return null;
                }) : Promise.resolve(null),
                level3 ? this.loadFile(level3).catch((e) => {
                    console.error('[EKFService] Failed to load level3:', e);
                    return null;
                }) : Promise.resolve(null)
            ]);
            
            console.log('[EKFService] Loaded data:', {
                level1: level1Data ? 'OK' : 'NULL',
                level2: level2Data ? 'OK' : 'NULL',
                level3: level3Data ? 'OK' : 'NULL'
            });
            
            return {
                level1: level1Data?.data || level1Data || null,
                level2: level2Data?.data || level2Data || null,
                level3: level3Data?.data || level3Data || null,
                file_paths: file_paths
            };
        } catch (error) {
            console.error('[EKFService] loadAllLevels error:', error);
            return { level1: null, level2: null, level3: null };
        }
    }
}

// Singleton instance exportálása
const ekfService = new EKFService();

export default ekfService;

