/**
 * EventBus - Központi eseménykezelés (Pub/Sub minta)
 * Moduláris UI architektúra - Core modul
 * 
 * Használat:
 *   import eventBus from './core/EventBus.js';
 *   eventBus.on('event:name', (data) => { ... });
 *   eventBus.emit('event:name', data);
 */
class EventBus {
    constructor() {
        this.listeners = {};
        this.eventHistory = []; // Opcionális: eseménytörténet (debug céljából)
        this.maxHistorySize = 100;
    }
    
    /**
     * Esemény feliratkozás
     * @param {string} event - Esemény neve
     * @param {Function} callback - Callback függvény
     * @returns {Function} Unsubscribe függvény
     */
    on(event, callback) {
        if (typeof callback !== 'function') {
            console.warn(`[EventBus] Invalid callback for event "${event}"`);
            return () => {};
        }
        
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        
        this.listeners[event].push(callback);
        
        // Unsubscribe függvény visszaadása
        return () => {
            this.off(event, callback);
        };
    }
    
    /**
     * Esemény leiratkozás
     * @param {string} event - Esemény neve
     * @param {Function} callback - Callback függvény (opcionális, ha nincs, akkor minden listener leiratkozik)
     */
    off(event, callback) {
        if (!this.listeners[event]) {
            return;
        }
        
        if (callback) {
            // Konkrét callback eltávolítása
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
            
            // Ha nincs több listener, töröljük az eseményt
            if (this.listeners[event].length === 0) {
                delete this.listeners[event];
            }
        } else {
            // Minden listener eltávolítása
            delete this.listeners[event];
        }
    }
    
    /**
     * Esemény küldés (emit)
     * @param {string} event - Esemény neve
     * @param {*} data - Adatok (bármilyen típus)
     */
    emit(event, data = null) {
        // Eseménytörténet (debug)
        this._addToHistory(event, data);
        
        // Listener-ek meghívása
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`[EventBus] Error in callback for event "${event}":`, error);
                }
            });
        }
        
        // Wildcard listener-ek (pl. "*" vagy "event:*")
        const wildcardPattern = '*';
        if (this.listeners[wildcardPattern]) {
            this.listeners[wildcardPattern].forEach(callback => {
                try {
                    callback({ event, data });
                } catch (error) {
                    console.error(`[EventBus] Error in wildcard callback:`, error);
                }
            });
        }
    }
    
    /**
     * Eseménytörténet hozzáadása (debug)
     * @private
     */
    _addToHistory(event, data) {
        this.eventHistory.push({
            event,
            data,
            timestamp: Date.now()
        });
        
        // Történet méret korlátozása
        if (this.eventHistory.length > this.maxHistorySize) {
            this.eventHistory.shift();
        }
    }
    
    /**
     * Eseménytörténet lekérése (debug)
     * @returns {Array} Eseménytörténet
     */
    getHistory() {
        return [...this.eventHistory];
    }
    
    /**
     * Eseménytörténet törlése
     */
    clearHistory() {
        this.eventHistory = [];
    }
    
    /**
     * Összes listener törlése (cleanup)
     */
    clear() {
        this.listeners = {};
        this.clearHistory();
    }
    
    /**
     * Aktív listener-ek száma (debug)
     * @returns {Object} Esemény neve -> listener szám
     */
    getListenerCounts() {
        const counts = {};
        for (const event in this.listeners) {
            counts[event] = this.listeners[event].length;
        }
        return counts;
    }
}

// Singleton instance exportálása
const eventBus = new EventBus();

// Exportálás (ES6 modul és CommonJS kompatibilitás)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = eventBus;
}

// Globális elérés (ha szükséges, de nem ajánlott)
if (typeof window !== 'undefined') {
    window.EventBus = EventBus;
    window.eventBus = eventBus;
}

export default eventBus;

