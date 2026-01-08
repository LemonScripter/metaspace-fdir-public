/**
 * StateManager - Globális állapotkezelés
 * Moduláris UI architektúra - Core modul
 * 
 * Használat:
 *   import stateManager from './core/StateManager.js';
 *   stateManager.setState('key', value);
 *   const value = stateManager.getState('key');
 *   stateManager.subscribe('key', (newValue, oldValue) => { ... });
 */
import eventBus from './EventBus.js';

class StateManager {
    constructor() {
        this.state = {};
        this.listeners = {};
        this.stateHistory = {}; // Opcionális: állapottörténet (debug)
        this.maxHistorySize = 50;
    }
    
    /**
     * Állapot beállítása
     * @param {string} key - Állapot kulcs
     * @param {*} value - Érték (bármilyen típus)
     * @param {Object} options - Opciók (silent: true = nem küld eseményt)
     */
    setState(key, value, options = {}) {
        if (typeof key !== 'string') {
            console.warn('[StateManager] Key must be a string');
            return;
        }
        
        const oldValue = this.state[key];
        const hasChanged = oldValue !== value;
        
        // Állapot beállítása
        this.state[key] = value;
        
        // Állapottörténet (debug)
        this._addToHistory(key, value, oldValue);
        
        // Ha változott, értesítjük a listener-eket
        if (hasChanged && !options.silent) {
            // Konkrét kulcs listener-ek
            if (this.listeners[key]) {
                this.listeners[key].forEach(callback => {
                    try {
                        callback(value, oldValue);
                    } catch (error) {
                        console.error(`[StateManager] Error in callback for key "${key}":`, error);
                    }
                });
            }
            
            // Globális változás esemény (EventBus-on keresztül)
            eventBus.emit('state:changed', { 
                key, 
                value, 
                oldValue,
                timestamp: Date.now()
            });
            
            // Konkrét kulcs esemény (pl. 'state:changed:keyName')
            eventBus.emit(`state:changed:${key}`, { 
                value, 
                oldValue,
                timestamp: Date.now()
            });
        }
    }
    
    /**
     * Állapot lekérése
     * @param {string} key - Állapot kulcs
     * @param {*} defaultValue - Alapértelmezett érték (ha nincs)
     * @returns {*} Állapot értéke
     */
    getState(key, defaultValue = undefined) {
        if (key in this.state) {
            return this.state[key];
        }
        return defaultValue;
    }
    
    /**
     * Több állapot beállítása egyszerre
     * @param {Object} stateUpdates - { key: value } objektum
     * @param {Object} options - Opciók
     */
    setMultipleStates(stateUpdates, options = {}) {
        const changes = {};
        
        for (const key in stateUpdates) {
            const oldValue = this.state[key];
            const newValue = stateUpdates[key];
            
            if (oldValue !== newValue) {
                this.state[key] = newValue;
                this._addToHistory(key, newValue, oldValue);
                changes[key] = { value: newValue, oldValue };
            }
        }
        
        // Események küldése (ha van változás)
        if (Object.keys(changes).length > 0 && !options.silent) {
            // Minden változott kulcs listener-je
            for (const key in changes) {
                if (this.listeners[key]) {
                    this.listeners[key].forEach(callback => {
                        try {
                            callback(changes[key].value, changes[key].oldValue);
                        } catch (error) {
                            console.error(`[StateManager] Error in callback for key "${key}":`, error);
                        }
                    });
                }
            }
            
            // Globális esemény
            eventBus.emit('state:changed:multiple', { 
                changes,
                timestamp: Date.now()
            });
        }
    }
    
    /**
     * Állapot változás figyelése
     * @param {string} key - Állapot kulcs
     * @param {Function} callback - Callback függvény (newValue, oldValue) => {}
     * @returns {Function} Unsubscribe függvény
     */
    subscribe(key, callback) {
        if (typeof callback !== 'function') {
            console.warn(`[StateManager] Invalid callback for key "${key}"`);
            return () => {};
        }
        
        if (!this.listeners[key]) {
            this.listeners[key] = [];
        }
        
        this.listeners[key].push(callback);
        
        // Unsubscribe függvény visszaadása
        return () => {
            this.unsubscribe(key, callback);
        };
    }
    
    /**
     * Állapot változás leiratkozása
     * @param {string} key - Állapot kulcs
     * @param {Function} callback - Callback függvény (opcionális)
     */
    unsubscribe(key, callback) {
        if (!this.listeners[key]) {
            return;
        }
        
        if (callback) {
            // Konkrét callback eltávolítása
            this.listeners[key] = this.listeners[key].filter(cb => cb !== callback);
            
            // Ha nincs több listener, töröljük
            if (this.listeners[key].length === 0) {
                delete this.listeners[key];
            }
        } else {
            // Minden listener eltávolítása
            delete this.listeners[key];
        }
    }
    
    /**
     * Állapot törlése
     * @param {string} key - Állapot kulcs
     */
    deleteState(key) {
        const oldValue = this.state[key];
        delete this.state[key];
        
        // Listener-ek törlése
        if (this.listeners[key]) {
            delete this.listeners[key];
        }
        
        // Esemény küldése
        eventBus.emit('state:deleted', { key, oldValue });
    }
    
    /**
     * Összes állapot lekérése (read-only másolat)
     * @returns {Object} Állapot objektum
     */
    getAllState() {
        return { ...this.state };
    }
    
    /**
     * Állapottörténet hozzáadása (debug)
     * @private
     */
    _addToHistory(key, value, oldValue) {
        if (!this.stateHistory[key]) {
            this.stateHistory[key] = [];
        }
        
        this.stateHistory[key].push({
            value,
            oldValue,
            timestamp: Date.now()
        });
        
        // Történet méret korlátozása
        if (this.stateHistory[key].length > this.maxHistorySize) {
            this.stateHistory[key].shift();
        }
    }
    
    /**
     * Állapottörténet lekérése (debug)
     * @param {string} key - Állapot kulcs (opcionális, ha nincs, akkor minden)
     * @returns {Array|Object} Állapottörténet
     */
    getHistory(key = null) {
        if (key) {
            return this.stateHistory[key] ? [...this.stateHistory[key]] : [];
        }
        
        // Minden kulcs története (másolat)
        const history = {};
        for (const k in this.stateHistory) {
            history[k] = [...this.stateHistory[k]];
        }
        return history;
    }
    
    /**
     * Állapottörténet törlése
     * @param {string} key - Állapot kulcs (opcionális, ha nincs, akkor minden)
     */
    clearHistory(key = null) {
        if (key) {
            delete this.stateHistory[key];
        } else {
            this.stateHistory = {};
        }
    }
    
    /**
     * Összes állapot és listener törlése (cleanup)
     */
    clear() {
        this.state = {};
        this.listeners = {};
        this.clearHistory();
    }
    
    /**
     * Aktív listener-ek száma (debug)
     * @returns {Object} Kulcs -> listener szám
     */
    getListenerCounts() {
        const counts = {};
        for (const key in this.listeners) {
            counts[key] = this.listeners[key].length;
        }
        return counts;
    }
}

// Singleton instance exportálása
const stateManager = new StateManager();

// Exportálás (ES6 modul és CommonJS kompatibilitás)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = stateManager;
}

// Globális elérés (ha szükséges, de nem ajánlott)
if (typeof window !== 'undefined') {
    window.StateManager = StateManager;
    window.stateManager = stateManager;
}

export default stateManager;


