/**
 * APIClient - API kommunikáció wrapper
 * Moduláris UI architektúra - Core modul
 * 
 * Használat:
 *   import apiClient from './core/APIClient.js';
 *   const data = await apiClient.get('/api/endpoint');
 *   const result = await apiClient.post('/api/endpoint', { data });
 */
import eventBus from './EventBus.js';

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
        this.timeout = 30000; // 30 másodperc timeout
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 másodperc
    }
    
    /**
     * Alapvető request metódus
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch opciók
     * @returns {Promise} Response JSON
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        // Konfiguráció összeállítása
        const config = {
            headers: {
                ...this.defaultHeaders,
                ...options.headers
            },
            ...options
        };
        
        // Timeout hozzáadása (ha támogatott)
        if (this.timeout > 0) {
            config.signal = AbortSignal.timeout(this.timeout);
        }
        
        let lastError = null;
        
        // Retry logika
        for (let attempt = 0; attempt < this.retryAttempts; attempt++) {
            try {
                // Esemény: request kezdés
                eventBus.emit('api:request:start', { endpoint, attempt: attempt + 1 });
                
                const response = await fetch(url, config);
                
                // HTTP status ellenőrzés
                if (!response.ok) {
                    const errorText = await response.text().catch(() => 'Unknown error');
                    throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorText}`);
                }
                
                // JSON parsing
                const data = await response.json();
                
                // Esemény: request sikeres
                eventBus.emit('api:request:success', { endpoint, data });
                
                return data;
                
            } catch (error) {
                lastError = error;
                
                // Abort signal (timeout vagy manual abort) - ne próbáljuk újra
                if (error.name === 'AbortError' || error.name === 'TimeoutError') {
                    eventBus.emit('api:request:timeout', { endpoint, error });
                    throw error;
                }
                
                // Utolsó próbálkozás - dobjuk a hibát
                if (attempt === this.retryAttempts - 1) {
                    eventBus.emit('api:request:error', { endpoint, error, attempts: attempt + 1 });
                    throw error;
                }
                
                // Várakozás a következő próbálkozás előtt
                await this._delay(this.retryDelay * (attempt + 1));
            }
        }
        
        // Ha ide jutunk, valami nem stimmel
        throw lastError || new Error('Unknown API error');
    }
    
    /**
     * GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} params - Query paraméterek
     * @param {Object} options - További opciók
     * @returns {Promise} Response JSON
     */
    async get(endpoint, params = {}, options = {}) {
        // Query string összeállítása
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        return this.request(url, {
            method: 'GET',
            ...options
        });
    }
    
    /**
     * POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @param {Object} options - További opciók
     * @returns {Promise} Response JSON
     */
    async post(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options
        });
    }
    
    /**
     * PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @param {Object} options - További opciók
     * @returns {Promise} Response JSON
     */
    async put(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options
        });
    }
    
    /**
     * DELETE request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - További opciók
     * @returns {Promise} Response JSON
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            method: 'DELETE',
            ...options
        });
    }
    
    /**
     * Várakozás (delay)
     * @private
     */
    _delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Base URL beállítása
     * @param {string} baseURL - Base URL
     */
    setBaseURL(baseURL) {
        this.baseURL = baseURL;
    }
    
    /**
     * Default header hozzáadása
     * @param {string} key - Header kulcs
     * @param {string} value - Header érték
     */
    setHeader(key, value) {
        this.defaultHeaders[key] = value;
    }
    
    /**
     * Default header eltávolítása
     * @param {string} key - Header kulcs
     */
    removeHeader(key) {
        delete this.defaultHeaders[key];
    }
    
    /**
     * Timeout beállítása
     * @param {number} timeout - Timeout milliszekundumban
     */
    setTimeout(timeout) {
        this.timeout = timeout;
    }
    
    /**
     * Retry beállítások
     * @param {number} attempts - Próbálkozások száma
     * @param {number} delay - Várakozás milliszekundumban
     */
    setRetry(attempts, delay) {
        this.retryAttempts = attempts;
        this.retryDelay = delay;
    }
}

// Singleton instance exportálása
const apiClient = new APIClient();

// Exportálás (ES6 modul és CommonJS kompatibilitás)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = apiClient;
}

// Globális elérés (ha szükséges, de nem ajánlott)
if (typeof window !== 'undefined') {
    window.APIClient = APIClient;
    window.apiClient = apiClient;
}

export default apiClient;

