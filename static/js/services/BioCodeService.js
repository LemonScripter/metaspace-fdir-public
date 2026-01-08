/**
 * BioCodeService - Bio-code fájlok API szolgáltatás
 * Moduláris UI architektúra - Service modul
 */
import apiClient from '../core/APIClient.js';

class BioCodeService {
    /**
     * Legutóbbi bio-code fájlok lekérése
     * @param {number} missionDay - Mission day (opcionális)
     * @returns {Promise} Fájl elérési utak és adatok
     */
    async getLatestFiles(missionDay = null) {
        const params = missionDay ? { mission_day: missionDay } : {};
        return await apiClient.get('/api/biocode/files/latest', params);
    }
    
    /**
     * Bio-code fájl betöltése
     * @param {string} filePath - Fájl elérési út
     * @returns {Promise} Fájl tartalma
     */
    async loadFile(filePath) {
        return await apiClient.get('/api/biocode/files/load', { path: filePath });
    }
    
    /**
     * Minden 3 szintű bio-code fájl betöltése
     * @param {number} missionDay - Mission day (opcionális)
     * @returns {Promise} { level1, level2, level3 } adatok
     */
    async loadAllLevels(missionDay = null) {
        try {
            const files = await this.getLatestFiles(missionDay);
            console.log('[BioCodeService] getLatestFiles response:', files);
            
            // API válasz struktúrájának kezelése
            const file_paths = files.file_paths || (files.status === 'success' ? files : null);
            
            if (!file_paths || (!file_paths.level1 && !file_paths.level2 && !file_paths.level3)) {
                console.warn('[BioCodeService] No file paths found');
                return { level1: null, level2: null, level3: null };
            }
            
            const { level1, level2, level3 } = file_paths;
            console.log('[BioCodeService] Loading files:', { level1, level2, level3 });
            
            const [level1Data, level2Data, level3Data] = await Promise.all([
                level1 ? this.loadFile(level1).catch((e) => {
                    console.error('[BioCodeService] Failed to load level1:', e);
                    return null;
                }) : Promise.resolve(null),
                level2 ? this.loadFile(level2).catch((e) => {
                    console.error('[BioCodeService] Failed to load level2:', e);
                    return null;
                }) : Promise.resolve(null),
                level3 ? this.loadFile(level3).catch((e) => {
                    console.error('[BioCodeService] Failed to load level3:', e);
                    return null;
                }) : Promise.resolve(null)
            ]);
            
            console.log('[BioCodeService] Loaded data:', {
                level1: level1Data ? 'OK' : 'NULL',
                level2: level2Data ? 'OK' : 'NULL',
                level3: level3Data ? 'OK' : 'NULL'
            });
            
            return {
                level1: level1Data?.data || level1Data || null,
                level2: level2Data?.data || level2Data || null,
                level3: level3Data?.data || level3Data || null,
                file_paths: file_paths,
                validation: files.validation || (files.status === 'success' ? files.validation : null)
            };
        } catch (error) {
            console.error('[BioCodeService] loadAllLevels error:', error);
            return { level1: null, level2: null, level3: null };
        }
    }
}

// Singleton instance exportálása
const bioCodeService = new BioCodeService();

export default bioCodeService;

