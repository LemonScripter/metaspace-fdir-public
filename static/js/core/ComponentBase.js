/**
 * ComponentBase - Alap komponens osztály
 * Moduláris UI architektúra - Core modul
 * 
 * Minden komponens ebből származik.
 * 
 * Használat:
 *   import ComponentBase from './core/ComponentBase.js';
 *   class MyComponent extends ComponentBase {
 *       async render() { ... }
 *       attachEventListeners() { ... }
 *   }
 */
import eventBus from './EventBus.js';
import stateManager from './StateManager.js';

class ComponentBase {
    constructor(container, config = {}) {
        if (!container) {
            throw new Error('[ComponentBase] Container element is required');
        }
        
        this.container = container;
        this.config = {
            eventBus: eventBus,
            stateManager: stateManager,
            ...config
        };
        
        this.isInitialized = false;
        this.isDestroyed = false;
        this.eventListeners = []; // EventBus listener-ek nyilvántartása
        this.stateSubscriptions = []; // StateManager subscription-ök nyilvántartása
        
        // Debug név (ha van)
        this.name = this.constructor.name;
    }
    
    /**
     * Komponens inicializálás
     * @returns {Promise} Inicializálás befejezése
     */
    async init() {
        if (this.isInitialized) {
            console.warn(`[ComponentBase] Component ${this.name} already initialized`);
            return;
        }
        
        if (this.isDestroyed) {
            console.warn(`[ComponentBase] Component ${this.name} is destroyed, cannot initialize`);
            return;
        }
        
        try {
            // Renderelés
            await this.render();
            
            // Event listener-ek csatolása
            this.attachEventListeners();
            
            // State subscription-ök csatolása
            this.attachStateSubscriptions();
            
            this.isInitialized = true;
            
            // Esemény küldése
            this.config.eventBus.emit('component:initialized', { 
                component: this,
                name: this.name
            });
            
        } catch (error) {
            console.error(`[ComponentBase] Error initializing component ${this.name}:`, error);
            throw error;
        }
    }
    
    /**
     * Komponens renderelés (override-olni kell)
     * @param {*} data - Renderelési adatok (opcionális)
     * @returns {Promise} Renderelés befejezése
     */
    async render(data = null) {
        // Alapértelmezett: üres implementáció
        // Override-olni kell a leszármazott osztályban
        console.warn(`[ComponentBase] render() not implemented in ${this.name}`);
    }
    
    /**
     * Event listener-ek csatolása (override-olni kell)
     * Használja a this.onEvent() helper metódust
     */
    attachEventListeners() {
        // Alapértelmezett: üres implementáció
        // Override-olni kell a leszármazott osztályban
    }
    
    /**
     * State subscription-ök csatolása (override-olni kell)
     * Használja a this.onStateChange() helper metódust
     */
    attachStateSubscriptions() {
        // Alapértelmezett: üres implementáció
        // Override-olni kell a leszármazott osztályban
    }
    
    /**
     * Komponens frissítés
     * @param {*} data - Frissítési adatok
     * @returns {Promise} Frissítés befejezése
     */
    async update(data = null) {
        if (this.isDestroyed) {
            console.warn(`[ComponentBase] Component ${this.name} is destroyed, cannot update`);
            return;
        }
        
        if (!this.isInitialized) {
            console.warn(`[ComponentBase] Component ${this.name} not initialized, calling init() first`);
            await this.init();
            return;
        }
        
        try {
            await this.render(data);
        } catch (error) {
            console.error(`[ComponentBase] Error updating component ${this.name}:`, error);
            throw error;
        }
    }
    
    /**
     * Komponens megsemmisítése (cleanup)
     */
    destroy() {
        if (this.isDestroyed) {
            return;
        }
        
        // Event listener-ek leiratkozása
        this.eventListeners.forEach(({ event, callback }) => {
            this.config.eventBus.off(event, callback);
        });
        this.eventListeners = [];
        
        // State subscription-ök leiratkozása
        this.stateSubscriptions.forEach(unsubscribe => {
            if (typeof unsubscribe === 'function') {
                unsubscribe();
            }
        });
        this.stateSubscriptions = [];
        
        // Container ürítése
        if (this.container) {
            this.container.innerHTML = '';
        }
        
        this.isDestroyed = true;
        this.isInitialized = false;
        
        // Esemény küldése
        this.config.eventBus.emit('component:destroyed', { 
            component: this,
            name: this.name
        });
    }
    
    /**
     * Helper: Event listener hozzáadása (automatikus cleanup)
     * @param {string} event - Esemény neve
     * @param {Function} callback - Callback függvény
     */
    onEvent(event, callback) {
        this.config.eventBus.on(event, callback);
        this.eventListeners.push({ event, callback });
    }
    
    /**
     * Helper: State változás figyelése (automatikus cleanup)
     * @param {string} key - State kulcs
     * @param {Function} callback - Callback függvény (newValue, oldValue)
     */
    onStateChange(key, callback) {
        const unsubscribe = this.config.stateManager.subscribe(key, callback);
        this.stateSubscriptions.push(unsubscribe);
    }
    
    /**
     * Helper: State beállítása
     * @param {string} key - State kulcs
     * @param {*} value - Érték
     */
    setState(key, value) {
        this.config.stateManager.setState(key, value);
    }
    
    /**
     * Helper: State lekérése
     * @param {string} key - State kulcs
     * @param {*} defaultValue - Alapértelmezett érték
     * @returns {*} State értéke
     */
    getState(key, defaultValue = undefined) {
        return this.config.stateManager.getState(key, defaultValue);
    }
    
    /**
     * Helper: Esemény küldése
     * @param {string} event - Esemény neve
     * @param {*} data - Adatok
     */
    emit(event, data = null) {
        this.config.eventBus.emit(event, data);
    }
    
    /**
     * Helper: HTML elem létrehozása
     * @param {string} tag - HTML tag
     * @param {Object} attributes - Attribútumok
     * @param {string|HTMLElement} content - Tartalom
     * @returns {HTMLElement} Létrehozott elem
     */
    createElement(tag, attributes = {}, content = '') {
        const element = document.createElement(tag);
        
        // Attribútumok beállítása
        for (const key in attributes) {
            if (key === 'className') {
                element.className = attributes[key];
            } else if (key === 'style' && typeof attributes[key] === 'object') {
                Object.assign(element.style, attributes[key]);
            } else {
                element.setAttribute(key, attributes[key]);
            }
        }
        
        // Tartalom beállítása
        if (typeof content === 'string') {
            element.innerHTML = content;
        } else if (content instanceof HTMLElement) {
            element.appendChild(content);
        }
        
        return element;
    }
    
    /**
     * Helper: Query selector (komponens container-en belül)
     * @param {string} selector - CSS selector
     * @returns {HTMLElement|null} Elem vagy null
     */
    querySelector(selector) {
        return this.container.querySelector(selector);
    }
    
    /**
     * Helper: Query selector all (komponens container-en belül)
     * @param {string} selector - CSS selector
     * @returns {NodeList} Elemek
     */
    querySelectorAll(selector) {
        return this.container.querySelectorAll(selector);
    }
}

// Exportálás (ES6 modul és CommonJS kompatibilitás)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ComponentBase;
}

// Globális elérés (ha szükséges, de nem ajánlott)
if (typeof window !== 'undefined') {
    window.ComponentBase = ComponentBase;
}

export default ComponentBase;


