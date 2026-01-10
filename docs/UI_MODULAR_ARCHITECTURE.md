# Moduláris UI Architektúra Terv
## MetaSpace Satellite Simulation - Komponens-alapú Frontend

**Cél:** Moduláris, bővíthető, karbantartható UI architektúra  
**Dátum:** 2025-12-28  
**Státusz:** Tervezés

---

## 1. ÁLTALÁNOS ELVEK

### 1.1 Moduláris Elvek
- **Komponens-alapú:** Minden UI elem önálló, újrafelhasználható komponens
- **Loose Coupling:** Komponensek minimális függőséggel kommunikálnak (Event Bus)
- **Single Responsibility:** Minden modul egy dolgot csinál jól
- **Dependency Injection:** Függőségek injektálása, nem hardcode-olva
- **Plugin Architecture:** Új funkciók plugin-ként adhatók hozzá

### 1.2 Kommunikációs Minta
```
┌─────────────┐
│   Event     │
│    Bus      │ ← Központi eseménykezelés
└─────────────┘
       ↑ ↓
   ┌───┴─┴───┐
   │         │
┌──▼──┐  ┌──▼──┐
│Comp1│  │Comp2│ ← Komponensek
└─────┘  └─────┘
```

---

## 2. FÁJLSTRUKTÚRA

```
static/
├── js/
│   ├── core/                    # Alapvető rendszer modulok
│   │   ├── EventBus.js          # Központi eseménykezelés
│   │   ├── StateManager.js      # Állapotkezelés
│   │   ├── APIClient.js         # API kommunikáció wrapper
│   │   └── ComponentBase.js    # Alap komponens osztály
│   │
│   ├── components/              # UI Komponensek
│   │   ├── OrbitVisualization/  # Orbit vizualizáció modul
│   │   │   ├── OrbitVisualization.js
│   │   │   ├── OrbitPath.js
│   │   │   ├── TaskTimeline.js
│   │   │   └── OrbitParameters.js
│   │   │
│   │   ├── SatelliteControl/    # Műhold irányítás modul
│   │   │   ├── SatelliteControl.js
│   │   │   ├── ComparisonPanel.js
│   │   │   ├── FileViewer.js
│   │   │   └── MetricsDisplay.js
│   │   │
│   │   ├── BioCodeViewer/       # Bio-code megjelenítés
│   │   │   ├── BioCodeViewer.js
│   │   │   ├── Level1Viewer.js
│   │   │   ├── Level2Viewer.js
│   │   │   └── Level3Viewer.js
│   │   │
│   │   ├── EKFViewer/          # EKF megjelenítés
│   │   │   ├── EKFViewer.js
│   │   │   ├── SensorViewer.js
│   │   │   ├── SubsystemViewer.js
│   │   │   └── MissionViewer.js
│   │   │
│   │   └── NavigationPlan/     # Navigációs terv kezelés
│   │       ├── NavigationPlan.js
│   │       ├── TaskList.js
│   │       └── PlanLoader.js
│   │
│   ├── services/                # Szolgáltatások
│   │   ├── NavigationService.js # Navigációs terv API
│   │   ├── BioCodeService.js    # Bio-code fájlok API
│   │   ├── EKFService.js        # EKF fájlok API
│   │   └── ComparisonService.js # Összehasonlítás API
│   │
│   ├── utils/                   # Segédfüggvények
│   │   ├── dateUtils.js
│   │   ├── mathUtils.js
│   │   ├── colorUtils.js
│   │   └── formatUtils.js
│   │
│   ├── plugins/                 # Plugin rendszer (bővíthetőség)
│   │   ├── PluginManager.js
│   │   └── example-plugin.js
│   │
│   └── pages/                   # Oldal-specifikus inicializálás
│       ├── navigation-plan-page.js
│       ├── v3-sandbox-page.js
│       └── index-page.js
│
├── css/
│   ├── core/                    # Alapvető stílusok
│   │   ├── variables.css        # CSS változók
│   │   ├── base.css            # Reset, alap stílusok
│   │   └── layout.css           # Layout stílusok
│   │
│   ├── components/              # Komponens-specifikus stílusok
│   │   ├── orbit-visualization.css
│   │   ├── satellite-control.css
│   │   ├── biocode-viewer.css
│   │   └── ekf-viewer.css
│   │
│   └── themes/                  # Témák (opcionális)
│       ├── dark.css
│       └── light.css
│
└── templates/
    └── navigation-plan.html     # Új oldal template
```

---

## 3. CORE MODULOK

### 3.1 EventBus.js
**Felelősség:** Központi eseménykezelés, pub/sub minta

```javascript
class EventBus {
    constructor() {
        this.listeners = {};
    }
    
    // Esemény feliratkozás
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    // Esemény leiratkozás
    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }
    
    // Esemény küldés
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }
}

// Singleton instance
const eventBus = new EventBus();
export default eventBus;
```

### 3.2 StateManager.js
**Felelősség:** Globális állapotkezelés

```javascript
class StateManager {
    constructor() {
        this.state = {};
        this.listeners = {};
    }
    
    // Állapot beállítása
    setState(key, value) {
        const oldValue = this.state[key];
        this.state[key] = value;
        
        // Értesítés változásról
        if (this.listeners[key]) {
            this.listeners[key].forEach(callback => callback(value, oldValue));
        }
        
        // Globális változás esemény
        eventBus.emit('state:changed', { key, value, oldValue });
    }
    
    // Állapot lekérése
    getState(key) {
        return this.state[key];
    }
    
    // Állapot változás figyelése
    subscribe(key, callback) {
        if (!this.listeners[key]) {
            this.listeners[key] = [];
        }
        this.listeners[key].push(callback);
    }
}

const stateManager = new StateManager();
export default stateManager;
```

### 3.3 ComponentBase.js
**Felelősség:** Alap komponens osztály, minden komponens ebből származik

```javascript
class ComponentBase {
    constructor(container, config = {}) {
        this.container = container;
        this.config = config;
        this.isInitialized = false;
        this.isDestroyed = false;
        
        // Event bus és state manager injektálása
        this.eventBus = config.eventBus || eventBus;
        this.stateManager = config.stateManager || stateManager;
    }
    
    // Komponens inicializálás
    async init() {
        if (this.isInitialized) return;
        
        await this.render();
        this.attachEventListeners();
        this.isInitialized = true;
        
        this.eventBus.emit('component:initialized', { component: this });
    }
    
    // Komponens renderelés (override-olni kell)
    async render() {
        throw new Error('render() method must be implemented');
    }
    
    // Event listener-ek csatolása (override-olni kell)
    attachEventListeners() {
        // Alapértelmezett: üres
    }
    
    // Komponens frissítés
    async update(data) {
        if (this.isDestroyed) return;
        await this.render(data);
    }
    
    // Komponens megsemmisítése
    destroy() {
        this.isDestroyed = true;
        this.eventBus.emit('component:destroyed', { component: this });
    }
}

export default ComponentBase;
```

### 3.4 APIClient.js
**Felelősség:** API kommunikáció wrapper, error handling

```javascript
class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`[APIClient] Error fetching ${endpoint}:`, error);
            eventBus.emit('api:error', { endpoint, error });
            throw error;
        }
    }
    
    get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }
    
    post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

const apiClient = new APIClient();
export default apiClient;
```

---

## 4. KOMPONENS PÉLDÁK

### 4.1 OrbitVisualization Komponens

```javascript
import ComponentBase from '../core/ComponentBase.js';
import OrbitPath from './OrbitPath.js';
import TaskTimeline from './TaskTimeline.js';
import OrbitParameters from './OrbitParameters.js';

class OrbitVisualization extends ComponentBase {
    constructor(container, config) {
        super(container, config);
        
        // Sub-komponensek
        this.orbitPath = null;
        this.taskTimeline = null;
        this.orbitParameters = null;
    }
    
    async render(data) {
        this.container.innerHTML = `
            <div class="orbit-visualization">
                <div id="orbit-path-container"></div>
                <div id="task-timeline-container"></div>
                <div id="orbit-parameters-container"></div>
            </div>
        `;
        
        // Sub-komponensek inicializálása
        this.orbitPath = new OrbitPath(
            this.container.querySelector('#orbit-path-container'),
            { eventBus: this.eventBus }
        );
        
        this.taskTimeline = new TaskTimeline(
            this.container.querySelector('#task-timeline-container'),
            { eventBus: this.eventBus }
        );
        
        this.orbitParameters = new OrbitParameters(
            this.container.querySelector('#orbit-parameters-container'),
            { eventBus: this.eventBus }
        );
        
        await Promise.all([
            this.orbitPath.init(),
            this.taskTimeline.init(),
            this.orbitParameters.init()
        ]);
        
        // Adatok frissítése
        if (data) {
            this.update(data);
        }
    }
    
    async update(data) {
        await Promise.all([
            this.orbitPath.update(data.orbit),
            this.taskTimeline.update(data.tasks),
            this.orbitParameters.update(data.parameters)
        ]);
    }
    
    attachEventListeners() {
        // Orbit kiválasztás esemény
        this.eventBus.on('orbit:selected', (orbitData) => {
            this.stateManager.setState('selectedOrbit', orbitData);
        });
    }
}

export default OrbitVisualization;
```

### 4.2 ComparisonPanel Komponens

```javascript
import ComponentBase from '../core/ComponentBase.js';

class ComparisonPanel extends ComponentBase {
    async render(data) {
        const { ekf, metaspace } = data || {};
        
        this.container.innerHTML = `
            <div class="comparison-panel">
                <div class="comparison-header">
                    <h3>EKF vs MetaSpace Comparison</h3>
                </div>
                <div class="comparison-content">
                    <div class="ekf-column">
                        <h4>EKF</h4>
                        <div class="feasibility">${ekf?.feasibility || 0}%</div>
                        <div class="decision">${ekf?.decision || 'N/A'}</div>
                    </div>
                    <div class="metaspace-column">
                        <h4>MetaSpace</h4>
                        <div class="feasibility">${metaspace?.feasibility || 0}%</div>
                        <div class="decision">${metaspace?.decision || 'N/A'}</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    attachEventListeners() {
        // Real-time frissítés
        this.eventBus.on('comparison:updated', (data) => {
            this.update(data);
        });
    }
}

export default ComparisonPanel;
```

---

## 5. SZOLGÁLTATÁSOK

### 5.1 NavigationService.js

```javascript
import apiClient from '../core/APIClient.js';

class NavigationService {
    async loadPlan(planId) {
        return await apiClient.get(`/api/navigation/plan/${planId}`);
    }
    
    async getCurrentOrbit(time) {
        return await apiClient.get('/api/navigation/current-orbit', { time });
    }
    
    async getUpcomingTasks(lookahead = 60) {
        return await apiClient.get('/api/navigation/upcoming-tasks', { lookahead });
    }
}

const navigationService = new NavigationService();
export default navigationService;
```

### 5.2 BioCodeService.js

```javascript
import apiClient from '../core/APIClient.js';

class BioCodeService {
    async getLatestFiles(missionDay = null) {
        const params = missionDay ? { mission_day: missionDay } : {};
        return await apiClient.get('/api/biocode/files/latest', params);
    }
    
    async loadFile(filePath) {
        return await apiClient.get('/api/biocode/files/load', { path: filePath });
    }
}

const bioCodeService = new BioCodeService();
export default bioCodeService;
```

---

## 6. OLDAL INICIALIZÁLÁS

### 6.1 navigation-plan-page.js

```javascript
import OrbitVisualization from '../components/OrbitVisualization/OrbitVisualization.js';
import SatelliteControl from '../components/SatelliteControl/SatelliteControl.js';
import navigationService from '../services/NavigationService.js';
import bioCodeService from '../services/BioCodeService.js';
import ekfService from '../services/EKFService.js';
import eventBus from '../core/EventBus.js';
import stateManager from '../core/StateManager.js';

class NavigationPlanPage {
    constructor() {
        this.orbitVisualization = null;
        this.satelliteControl = null;
        this.updateInterval = null;
    }
    
    async init() {
        // Komponensek inicializálása
        this.orbitVisualization = new OrbitVisualization(
            document.querySelector('#orbit-visualization-container'),
            { eventBus, stateManager }
        );
        
        this.satelliteControl = new SatelliteControl(
            document.querySelector('#satellite-control-container'),
            { eventBus, stateManager }
        );
        
        await Promise.all([
            this.orbitVisualization.init(),
            this.satelliteControl.init()
        ]);
        
        // Navigációs terv betöltése
        await this.loadNavigationPlan();
        
        // Real-time frissítés indítása
        this.startAutoUpdate();
        
        // Event listener-ek
        this.attachEventListeners();
    }
    
    async loadNavigationPlan() {
        try {
            const plan = await navigationService.loadPlan('default');
            stateManager.setState('navigationPlan', plan);
            eventBus.emit('navigation:plan:loaded', plan);
        } catch (error) {
            console.error('[NavigationPlanPage] Failed to load plan:', error);
        }
    }
    
    startAutoUpdate() {
        this.updateInterval = setInterval(async () => {
            await this.update();
        }, 1000); // 1 másodpercenként
    }
    
    async update() {
        // Adatok frissítése
        const [orbit, tasks, biocodeFiles, ekfFiles] = await Promise.all([
            navigationService.getCurrentOrbit(),
            navigationService.getUpcomingTasks(),
            bioCodeService.getLatestFiles(),
            ekfService.getLatestFiles()
        ]);
        
        // Komponensek frissítése
        await Promise.all([
            this.orbitVisualization.update({ orbit, tasks }),
            this.satelliteControl.update({ biocodeFiles, ekfFiles })
        ]);
    }
    
    attachEventListeners() {
        // Szimuláció indítás/leállítás
        eventBus.on('simulation:start', () => {
            this.startAutoUpdate();
        });
        
        eventBus.on('simulation:stop', () => {
            if (this.updateInterval) {
                clearInterval(this.updateInterval);
            }
        });
    }
    
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        if (this.orbitVisualization) {
            this.orbitVisualization.destroy();
        }
        
        if (this.satelliteControl) {
            this.satelliteControl.destroy();
        }
    }
}

// Oldal inicializálása
document.addEventListener('DOMContentLoaded', async () => {
    const page = new NavigationPlanPage();
    await page.init();
    window.navigationPlanPage = page; // Debug céljából
});
```

---

## 7. PLUGIN RENDSZER

### 7.1 PluginManager.js

```javascript
class PluginManager {
    constructor() {
        this.plugins = [];
    }
    
    register(plugin) {
        if (plugin.init && typeof plugin.init === 'function') {
            this.plugins.push(plugin);
            plugin.init(eventBus, stateManager);
        }
    }
    
    unregister(plugin) {
        const index = this.plugins.indexOf(plugin);
        if (index > -1) {
            if (plugin.destroy && typeof plugin.destroy === 'function') {
                plugin.destroy();
            }
            this.plugins.splice(index, 1);
        }
    }
}

const pluginManager = new PluginManager();
export default pluginManager;
```

### 7.2 Példa Plugin

```javascript
// plugins/custom-metrics-plugin.js
class CustomMetricsPlugin {
    init(eventBus, stateManager) {
        this.eventBus = eventBus;
        this.stateManager = stateManager;
        
        // Esemény figyelése
        this.eventBus.on('comparison:updated', (data) => {
            this.handleComparisonUpdate(data);
        });
    }
    
    handleComparisonUpdate(data) {
        // Egyedi logika
        console.log('[CustomMetricsPlugin] Comparison updated:', data);
    }
    
    destroy() {
        this.eventBus.off('comparison:updated', this.handleComparisonUpdate);
    }
}

export default CustomMetricsPlugin;
```

---

## 8. ELŐNYÖK

### 8.1 Bővíthetőség
- Új komponens: csak új fájl, ComponentBase-ből származtatás
- Új szolgáltatás: új service fájl, APIClient használata
- Új plugin: plugin regisztrálás

### 8.2 Karbantarthatóság
- Komponensek izolálva, könnyen tesztelhetők
- Függőségek explicit módon injektálva
- Event-driven kommunikáció, laza csatolás

### 8.3 Újrafelhasználhatóság
- Komponensek más oldalakon is használhatók
- Szolgáltatások központilag kezelve
- Utils modulok újrafelhasználhatóak

---

## 9. KÖVETKEZŐ LÉPÉSEK

1. **Core modulok implementálása** (EventBus, StateManager, ComponentBase, APIClient)
2. **Első komponens implementálása** (például ComparisonPanel)
3. **Szolgáltatások implementálása** (NavigationService, BioCodeService)
4. **Oldal inicializálás** (navigation-plan-page.js)
5. **Backend API endpoint-ok** (Flask route-ok)
6. **Tesztelés és finomhangolás**

---

**Státusz:** Terv kész, implementációra vár


