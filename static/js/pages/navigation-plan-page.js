/**
 * Navigation Plan Page - Fő inicializálás és koordináció
 * Moduláris UI architektúra - Page modul
 */
import ComparisonPanel from '../components/ComparisonPanel/ComparisonPanel.js';
import FileViewer from '../components/FileViewer/FileViewer.js';
import navigationService from '../services/NavigationService.js';
import bioCodeService from '../services/BioCodeService.js';
import ekfService from '../services/EKFService.js';
import comparisonService from '../services/ComparisonService.js';
import eventBus from '../core/EventBus.js';
import stateManager from '../core/StateManager.js';

class NavigationPlanPage {
    constructor() {
        this.comparisonPanel = null;
        this.bioCodeViewer = null;
        this.ekfViewer = null;
        this.updateInterval = null;
        this.isRunning = false;
        this.missionDay = 0;
    }
    
    async init() {
        console.log('[NavigationPlanPage] Initializing...');
        
        try {
            // Komponensek inicializálása
            await this.initComponents();
            
            // Orbit vizualizáció inicializálása
            this.initOrbitVisualization();
            
            // Task timeline inicializálása
            this.initTaskTimeline();
            
            // Navigációs terv betöltése (vagy placeholder)
            await this.loadNavigationPlan();
            
            // Event listener-ek
            this.attachEventListeners();
            
            // Idő frissítés
            this.startTimeUpdate();
            
            // AZONNALI placeholder adatok betöltése (hogy látszódjon valami)
            console.log('[NavigationPlanPage] Loading initial placeholder data...');
            await this.loadPlaceholderData();
            
            // Első adatfrissítés (valódi adatokkal, ha elérhető)
            setTimeout(async () => {
                try {
                    await this.update();
                } catch (error) {
                    console.warn('[NavigationPlanPage] Update failed, keeping placeholders:', error);
                }
            }, 1000);
            
            console.log('[NavigationPlanPage] Initialized successfully');
        } catch (error) {
            console.error('[NavigationPlanPage] Initialization error:', error);
            // Mégis betöltjük a placeholder adatokat
            await this.loadPlaceholderData();
        }
    }
    
    async initComponents() {
        console.log('[NavigationPlanPage] Initializing components...');
        
        // Comparison Panel
        const comparisonContainer = document.getElementById('comparison-panel-container');
        if (comparisonContainer) {
            console.log('[NavigationPlanPage] Initializing ComparisonPanel...');
            this.comparisonPanel = new ComparisonPanel(comparisonContainer, { eventBus, stateManager });
            await this.comparisonPanel.init();
            console.log('[NavigationPlanPage] ComparisonPanel initialized');
        } else {
            console.warn('[NavigationPlanPage] ComparisonPanel container not found!');
        }
        
        // Bio-code Viewer
        const bioCodeContainer = document.getElementById('biocode-viewer-container');
        if (bioCodeContainer) {
            console.log('[NavigationPlanPage] Initializing BioCodeViewer...');
            this.bioCodeViewer = new FileViewer(bioCodeContainer, { 
                fileType: 'biocode',
                eventBus,
                stateManager
            });
            await this.bioCodeViewer.init();
            console.log('[NavigationPlanPage] BioCodeViewer initialized');
        } else {
            console.warn('[NavigationPlanPage] BioCodeViewer container not found!');
        }
        
        // EKF Viewer
        const ekfContainer = document.getElementById('ekf-viewer-container');
        if (ekfContainer) {
            console.log('[NavigationPlanPage] Initializing EKFViewer...');
            this.ekfViewer = new FileViewer(ekfContainer, { 
                fileType: 'ekf',
                eventBus,
                stateManager
            });
            await this.ekfViewer.init();
            console.log('[NavigationPlanPage] EKFViewer initialized');
        } else {
            console.warn('[NavigationPlanPage] EKFViewer container not found!');
        }
    }
    
    initOrbitVisualization() {
        const svg = d3.select('#orbit-visualization');
        const container = document.getElementById('orbit-visualization');
        
        if (!container) return;
        
        const width = container.clientWidth;
        const height = container.clientHeight || 400;
        
        svg.attr('width', width).attr('height', height);
        
        // Alapvető orbit path (egyszerűsített)
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) * 0.4;
        
        // Föld (középpont)
        svg.append('circle')
            .attr('cx', centerX)
            .attr('cy', centerY)
            .attr('r', 20)
            .attr('fill', '#0f0')
            .attr('opacity', 0.8);
        
        // Orbit path (ellipszis - manuális path)
        const ellipsePath = d3.line()
            .x(d => centerX + radius * Math.cos(d))
            .y(d => centerY + radius * 0.7 * Math.sin(d))
            .curve(d3.curveLinearClosed);
        
        const points = d3.range(0, Math.PI * 2, 0.1);
        
        svg.append('path')
            .datum(points)
            .attr('d', ellipsePath)
            .attr('fill', 'none')
            .attr('stroke', 'rgba(0, 243, 255, 0.5)')
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', '5,5');
        
        // Műhold pozíció (animált)
        this.satelliteCircle = svg.append('circle')
            .attr('cx', centerX + radius)
            .attr('cy', centerY)
            .attr('r', 8)
            .attr('fill', '#0ff')
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);
        
        // Orbit animáció
        this.animateOrbit();
    }
    
    animateOrbit() {
        if (!this.satelliteCircle) return;
        
        const svg = d3.select('#orbit-visualization');
        const container = document.getElementById('orbit-visualization');
        if (!container) return;
        
        const width = container.clientWidth;
        const height = container.clientHeight || 400;
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) * 0.4;
        
        let angle = 0;
        
        const animate = () => {
            if (!this.isRunning) return;
            
            angle += 0.01;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * 0.7 * Math.sin(angle);
            
            this.satelliteCircle
                .transition()
                .duration(100)
                .attr('cx', x)
                .attr('cy', y);
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    initTaskTimeline() {
        const timeline = d3.select('#task-timeline');
        const container = document.getElementById('task-timeline');
        
        if (!container) {
            console.warn('[NavigationPlanPage] Task timeline container not found');
            return;
        }
        
        const width = container.clientWidth || 600;
        const height = container.clientHeight || 200;
        
        // SVG törlés, ha már létezik
        timeline.selectAll('*').remove();
        
        timeline.attr('width', width).attr('height', height);
        
        // Timeline track
        timeline.append('line')
            .attr('x1', 20)
            .attr('y1', height / 2)
            .attr('x2', width - 20)
            .attr('y2', height / 2)
            .attr('stroke', 'rgba(0, 243, 255, 0.3)')
            .attr('stroke-width', 2)
            .attr('class', 'timeline-track');
        
        // Task-ok (placeholder - később frissül)
        this.timelineGroup = timeline.append('g').attr('class', 'timeline-tasks');
        
        // Placeholder task-ok betöltése
        this.updateTaskTimeline([]);
    }
    
    updateTaskTimeline(tasks) {
        if (!this.timelineGroup) return;
        
        const container = document.getElementById('task-timeline');
        if (!container) return;
        
        const width = container.clientWidth || 600;
        const height = container.clientHeight || 200;
        
        // Régi task-ok törlése
        this.timelineGroup.selectAll('.task-marker').remove();
        this.timelineGroup.selectAll('.task-label').remove();
        
        if (!tasks || tasks.length === 0) {
            // Placeholder task
            const placeholderX = width / 2;
            this.timelineGroup.append('circle')
                .attr('cx', placeholderX)
                .attr('cy', height / 2)
                .attr('r', 6)
                .attr('fill', 'rgba(0, 243, 255, 0.5)')
                .attr('class', 'task-marker');
            
            this.timelineGroup.append('text')
                .attr('x', placeholderX)
                .attr('y', height / 2 - 15)
                .attr('text-anchor', 'middle')
                .attr('fill', 'rgba(0, 243, 255, 0.8)')
                .attr('font-size', '12px')
                .attr('class', 'task-label')
                .text('No tasks');
            return;
        }
        
        // Valódi task-ok renderelése
        const orbitDuration = 99; // perc
        tasks.forEach((task, index) => {
            const window = task.window || {};
            const startTime = this._parseTime(window.start || '00:00:00');
            const endTime = this._parseTime(window.end || '01:00:00');
            const startPercent = (startTime / orbitDuration) * 100;
            const x = 20 + ((width - 40) * startPercent / 100);
            
            // Task marker
            this.timelineGroup.append('circle')
                .attr('cx', x)
                .attr('cy', height / 2)
                .attr('r', 8)
                .attr('fill', task.type === 'imaging' ? '#0ff' : '#ff6b35')
                .attr('class', 'task-marker')
                .attr('data-task-id', task.task_id);
            
            // Task label
            this.timelineGroup.append('text')
                .attr('x', x)
                .attr('y', height / 2 - 15)
                .attr('text-anchor', 'middle')
                .attr('fill', 'rgba(0, 243, 255, 0.9)')
                .attr('font-size', '11px')
                .attr('class', 'task-label')
                .text(task.task_id || `Task ${index + 1}`);
        });
    }
    
    _parseTime(timeStr) {
        // "HH:MM:SS" vagy "HH:MM" formátum
        const parts = timeStr.split(':');
        if (parts.length >= 2) {
            return parseInt(parts[0]) * 60 + parseInt(parts[1]);
        }
        return 0;
    }
    
    async loadNavigationPlan() {
        try {
            console.log('[NavigationPlanPage] Loading navigation plan...');
            const plan = await navigationService.loadPlan('default');
            console.log('[NavigationPlanPage] Plan loaded:', plan);
            
            if (plan && plan.plan) {
                stateManager.setState('navigationPlan', plan.plan);
                
                // Orbit paraméterek frissítése
                const params = await navigationService.getOrbitParameters();
                console.log('[NavigationPlanPage] Orbit parameters:', params);
                
                if (params && params.parameters) {
                    const altEl = document.getElementById('altitude');
                    const periodEl = document.getElementById('period');
                    const inclEl = document.getElementById('inclination');
                    
                    if (altEl) altEl.textContent = `${params.parameters.orbital_altitude_km} km`;
                    if (periodEl) periodEl.textContent = `${params.parameters.orbital_period_minutes} min`;
                    if (inclEl) inclEl.textContent = `${params.parameters.inclination_degrees}°`;
                }
                
                eventBus.emit('navigation:plan:loaded', plan.plan);
            }
        } catch (error) {
            console.error('[NavigationPlanPage] Failed to load plan:', error);
            // Fallback: placeholder adatok (nem await, mert lehet, hogy még nincsenek komponensek)
            // A loadPlaceholderData() majd meghívódik az init() végén
        }
    }
    
    async loadPlaceholderData() {
        console.log('[NavigationPlanPage] Loading placeholder data...');
        
        // Orbit paraméterek (placeholder)
        const altEl = document.getElementById('altitude');
        const periodEl = document.getElementById('period');
        const inclEl = document.getElementById('inclination');
        const orbitEl = document.getElementById('current-orbit');
        
        if (altEl) altEl.textContent = '705 km';
        if (periodEl) periodEl.textContent = '99 min';
        if (inclEl) inclEl.textContent = '98.2°';
        if (orbitEl) orbitEl.textContent = '1';
        
        // Placeholder adatok a komponensekhez
        const placeholderComparison = {
            ekf: {
                feasibility: 75.5,
                decision: 'CONTINUE_WITH_MONITORING',
                confidence: 80.0,
                anomaly_detected: false,
                scenes_today: 650,
                data_loss_today: 50
            },
            metaspace: {
                feasibility: 92.3,
                action: 'CONTINUE_NOMINAL',
                safety_margin: 15,
                biocode_level3: '0x8F2C_A4E7_B1D9_5C6A'
            }
        };
        
        const placeholderBioCode = {
            level1: {
                count: 8,
                biocodes: {
                    'OLI2': '0x0001_8F2C_A4E7_B1D9',
                    'TIRS2': '0x0002_9E3D_B5F8_C2EA',
                    'ST_A': '0x0003_A4E7_C3F9_D1EB',
                    'ST_B': '0x0004_B5F8_D4EA_E2FC',
                    'EPS': '0x0005_C6E9_E5FB_F3GD',
                    'OBC': '0x0006_D7FA_F6GC_G4HE',
                    'X_BAND': '0x0007_E8GB_G7HD_H5IF',
                    'S_BAND': '0x0008_F9HC_H8IE_I6JG'
                }
            },
            level2: {
                count: 4,
                biocodes: {
                    'payload': '0xA7_F4_B2_E8',
                    'power': '0xB8_E5_C3_F9',
                    'navigation': '0xC9_F6_D4_EA',
                    'comm': '0xDA_G7_E5_FB'
                }
            },
            level3: {
                mission_day: 150,
                biocode: '0x8F2C_A4E7_B1D9_5C6A',
                feasibility: 92.3,
                action: 'CONTINUE_NOMINAL',
                safety_margin: 15
            },
            file_paths: {
                level1: 'backend/biocodes/level1_0150_20251228.bio',
                level2: 'backend/biocodes/level2_0150_20251228.bio',
                level3: 'backend/biocodes/level3_0150_20251228.bio'
            },
            validation: {
                passed: true,
                encrypted_validation: {
                    passed: true,
                    details: 'All validators passed'
                }
            }
        };
        
        const placeholderEKF = {
            level1: {
                count: 4,
                sensors: {
                    'GPS': {
                        measurement: 705.0,
                        state_estimate: 704.8,
                        covariance: 0.5,
                        confidence: 95.0
                    },
                    'IMU': {
                        measurement: 0.0,
                        state_estimate: 0.1,
                        covariance: 0.2,
                        confidence: 85.0
                    },
                    'STAR_TRACKER_A': {
                        measurement: 0.0,
                        state_estimate: 0.05,
                        covariance: 0.1,
                        confidence: 90.0
                    },
                    'STAR_TRACKER_B': {
                        measurement: 0.0,
                        state_estimate: 0.05,
                        covariance: 0.1,
                        confidence: 90.0
                    }
                }
            },
            level2: {
                count: 4,
                subsystems: {
                    'navigation': {
                        health: 85.0,
                        covariance_trace: 12.5
                    },
                    'power': {
                        health: 90.0,
                        covariance_trace: 8.2
                    },
                    'payload': {
                        health: 88.0,
                        covariance_trace: 10.1
                    },
                    'comm': {
                        health: 92.0,
                        covariance_trace: 6.5
                    }
                }
            },
            level3: {
                mission_day: 150,
                feasibility: 75.5,
                anomaly_detected: false,
                detection_latency: 0,
                confidence: 80.0,
                decision: 'CONTINUE_WITH_MONITORING',
                scenes_today: 650,
                data_loss_today: 50
            },
            file_paths: {
                level1: 'backend/ekf_execution/level1_0150_20251228.ekf',
                level2: 'backend/ekf_execution/level2_0150_20251228.ekf',
                level3: 'backend/ekf_execution/level3_0150_20251228.ekf'
            }
        };
        
            // Komponensek frissítése placeholder adatokkal (azonnal)
            console.log('[NavigationPlanPage] Updating components with placeholder data...');
            
            // Promise.all használata, hogy párhuzamosan frissítsük
            const updatePromises = [];
            
            if (this.comparisonPanel) {
                updatePromises.push(
                    this.comparisonPanel.update(placeholderComparison)
                        .then(() => console.log('[NavigationPlanPage] ComparisonPanel updated'))
                        .catch(error => console.error('[NavigationPlanPage] ComparisonPanel update error:', error))
                );
            }
            
            if (this.bioCodeViewer) {
                updatePromises.push(
                    this.bioCodeViewer.update(placeholderBioCode)
                        .then(() => console.log('[NavigationPlanPage] BioCodeViewer updated'))
                        .catch(error => console.error('[NavigationPlanPage] BioCodeViewer update error:', error))
                );
            }
            
            if (this.ekfViewer) {
                updatePromises.push(
                    this.ekfViewer.update(placeholderEKF)
                        .then(() => console.log('[NavigationPlanPage] EKFViewer updated'))
                        .catch(error => console.error('[NavigationPlanPage] EKFViewer update error:', error))
                );
            }
            
            await Promise.all(updatePromises);
            console.log('[NavigationPlanPage] Placeholder data loaded');
    }
    
    attachEventListeners() {
        // Start/Stop gombok
        const startBtn = document.getElementById('start-simulation');
        const stopBtn = document.getElementById('stop-simulation');
        const resetBtn = document.getElementById('reset-simulation');
        
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startSimulation());
        }
        
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopSimulation());
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetSimulation());
        }
        
        // EventBus események
        eventBus.on('simulation:start', () => this.startSimulation());
        eventBus.on('simulation:stop', () => this.stopSimulation());
    }
    
    startSimulation() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        document.getElementById('simulation-status').textContent = 'RUNNING';
        document.getElementById('start-simulation').style.display = 'none';
        document.getElementById('stop-simulation').style.display = 'inline-block';
        
        // Orbit animáció indítása
        this.animateOrbit();
        
        // Real-time frissítés indítása
        this.startAutoUpdate();
        
        eventBus.emit('simulation:started');
    }
    
    stopSimulation() {
        if (!this.isRunning) return;
        
        this.isRunning = false;
        document.getElementById('simulation-status').textContent = 'STOPPED';
        document.getElementById('start-simulation').style.display = 'inline-block';
        document.getElementById('stop-simulation').style.display = 'none';
        
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        eventBus.emit('simulation:stopped');
    }
    
    resetSimulation() {
        this.stopSimulation();
        this.missionDay = 0;
        document.getElementById('mission-day').textContent = '0';
        stateManager.setState('missionDay', 0);
        eventBus.emit('simulation:reset');
    }
    
    startAutoUpdate() {
        this.updateInterval = setInterval(async () => {
            await this.update();
        }, 2000); // 2 másodpercenként
    }
    
    async update() {
        try {
            console.log('[NavigationPlanPage] Updating data...');
            
            // Navigációs adatok (hiba esetén placeholder)
            let orbit, tasks, params;
            try {
                [orbit, tasks, params] = await Promise.all([
                    navigationService.getCurrentOrbit(),
                    navigationService.getUpcomingTasks(60),
                    navigationService.getOrbitParameters()
                ]);
            } catch (error) {
                console.warn('[NavigationPlanPage] Navigation API error, using placeholders:', error);
                orbit = { orbit: { orbit_number: 1 } };
                tasks = { tasks: [] };
                params = { parameters: { orbital_altitude_km: 705, orbital_period_minutes: 99, inclination_degrees: 98.2 } };
            }
            
            // Orbit paraméterek frissítése (MINDIG frissítjük, még ha ugyanazok az értékek)
            if (params && params.parameters) {
                const altEl = document.getElementById('altitude');
                const periodEl = document.getElementById('period');
                const inclEl = document.getElementById('inclination');
                const orbitEl = document.getElementById('current-orbit');
                
                const altitude = params.parameters.orbital_altitude_km || 705;
                const period = params.parameters.orbital_period_minutes || 99;
                const inclination = params.parameters.inclination_degrees || 98.2;
                const orbitNum = orbit?.orbit?.orbit_number || orbit?.orbit_number || '1';
                
                if (altEl) {
                    altEl.textContent = `${altitude} km`;
                    console.log(`[NavigationPlanPage] Altitude updated: ${altitude} km`);
                }
                if (periodEl) {
                    periodEl.textContent = `${period} min`;
                    console.log(`[NavigationPlanPage] Period updated: ${period} min`);
                }
                if (inclEl) {
                    inclEl.textContent = `${inclination}°`;
                    console.log(`[NavigationPlanPage] Inclination updated: ${inclination}°`);
                }
                if (orbitEl) {
                    orbitEl.textContent = orbitNum;
                    console.log(`[NavigationPlanPage] Orbit number updated: ${orbitNum}`);
                }
            } else {
                console.warn('[NavigationPlanPage] No orbit parameters available');
            }
            
            // Task timeline frissítése
            if (tasks && tasks.tasks && Array.isArray(tasks.tasks)) {
                this.updateTaskTimeline(tasks.tasks);
            } else if (orbit && orbit.orbit && orbit.orbit.tasks) {
                this.updateTaskTimeline(orbit.orbit.tasks);
            }
            
            // Bio-code és EKF fájlok (hiba esetén placeholder)
            let biocodeFiles, ekfFiles, comparison;
            try {
                [biocodeFiles, ekfFiles, comparison] = await Promise.all([
                    bioCodeService.loadAllLevels(this.missionDay).catch(() => null),
                    ekfService.loadAllLevels(this.missionDay).catch(() => null),
                    comparisonService.getMetrics(this.missionDay).catch(() => null)
                ]);
            } catch (error) {
                console.warn('[NavigationPlanPage] Files API error:', error);
                biocodeFiles = null;
                ekfFiles = null;
                comparison = null;
            }
            
            // API válasz struktúrájának kezelése
            if (comparison && comparison.status === 'success') {
                // Ha az API válasz { status: "success", ekf: {...}, metaspace: {...} } formátumú
                comparison = {
                    ekf: comparison.ekf || {},
                    metaspace: comparison.metaspace || {}
                };
            }
            
            // Ha nincsenek adatok, placeholder használata
            if (!comparison || !comparison.ekf || !comparison.metaspace || 
                Object.keys(comparison.ekf).length === 0 || Object.keys(comparison.metaspace).length === 0) {
                console.log('[NavigationPlanPage] Using placeholder comparison data');
                comparison = {
                    ekf: {
                        feasibility: 75.5,
                        decision: 'CONTINUE_WITH_MONITORING',
                        confidence: 80.0,
                        anomaly_detected: false,
                        scenes_today: 650,
                        data_loss_today: 50
                    },
                    metaspace: {
                        feasibility: 92.3,
                        action: 'CONTINUE_NOMINAL',
                        safety_margin: 15,
                        biocode_level3: '0x8F2C_A4E7_B1D9_5C6A'
                    }
                };
            } else {
                console.log('[NavigationPlanPage] Using real comparison data:', comparison);
                // Biztosítjuk, hogy minden mező létezik
                if (!comparison.ekf.feasibility && comparison.ekf.feasibility !== 0) {
                    comparison.ekf.feasibility = comparison.ekf.confidence || 75.5;
                }
                if (!comparison.metaspace.feasibility && comparison.metaspace.feasibility !== 0) {
                    comparison.metaspace.feasibility = 92.3;
                }
            }
            
            // Bio-code fájlok ellenőrzése (részletes logolás)
            console.log('[NavigationPlanPage] Bio-code files check:', {
                hasFiles: !!biocodeFiles,
                hasLevel1: !!(biocodeFiles?.level1),
                hasLevel2: !!(biocodeFiles?.level2),
                hasLevel3: !!(biocodeFiles?.level3),
                level1Keys: biocodeFiles?.level1 ? Object.keys(biocodeFiles.level1) : [],
                level2Keys: biocodeFiles?.level2 ? Object.keys(biocodeFiles.level2) : [],
                level3Keys: biocodeFiles?.level3 ? Object.keys(biocodeFiles.level3) : []
            });
            
            // Ha nincsenek bio-code fájlok, placeholder használata
            if (!biocodeFiles || (!biocodeFiles.level1 && !biocodeFiles.level2 && !biocodeFiles.level3)) {
                console.log('[NavigationPlanPage] Using placeholder bio-code data (no real data available)');
                biocodeFiles = {
                    level1: {
                        count: 8,
                        biocodes: {
                            'OLI2': '0x0001_8F2C_A4E7_B1D9',
                            'TIRS2': '0x0002_9E3D_B5F8_C2EA',
                            'ST_A': '0x0003_A4E7_C3F9_D1EB',
                            'ST_B': '0x0004_B5F8_D4EA_E2FC',
                            'EPS': '0x0005_C6E9_E5FB_F3GD',
                            'OBC': '0x0006_D7FA_F6GC_G4HE',
                            'X_BAND': '0x0007_E8GB_G7HD_H5IF',
                            'S_BAND': '0x0008_F9HC_H8IE_I6JG'
                        }
                    },
                    level2: {
                        count: 4,
                        biocodes: {
                            'payload': '0xA7_F4_B2_E8',
                            'power': '0xB8_E5_C3_F9',
                            'navigation': '0xC9_F6_D4_EA',
                            'comm': '0xDA_G7_E5_FB'
                        }
                    },
                    level3: {
                        mission_day: this.missionDay,
                        biocode: '0x8F2C_A4E7_B1D9_5C6A',
                        feasibility: 92.3,
                        action: 'CONTINUE_NOMINAL',
                        safety_margin: 15
                    },
                    file_paths: {
                        level1: 'backend/biocodes/level1_placeholder.bio',
                        level2: 'backend/biocodes/level2_placeholder.bio',
                        level3: 'backend/biocodes/level3_placeholder.bio'
                    }
                };
            } else {
                console.log('[NavigationPlanPage] Using real bio-code data:', biocodeFiles);
            }
            
            // Ha nincsenek EKF fájlok, placeholder használata
            if (!ekfFiles || (!ekfFiles.level1 && !ekfFiles.level2 && !ekfFiles.level3)) {
                console.log('[NavigationPlanPage] Using placeholder EKF data');
                ekfFiles = {
                    level1: {
                        count: 4,
                        sensors: {
                            'GPS': {
                                measurement: 705.0,
                                state_estimate: 704.8,
                                covariance: 0.5,
                                confidence: 95.0
                            },
                            'IMU': {
                                measurement: 0.0,
                                state_estimate: 0.1,
                                covariance: 0.2,
                                confidence: 85.0
                            },
                            'STAR_TRACKER_A': {
                                measurement: 0.0,
                                state_estimate: 0.05,
                                covariance: 0.1,
                                confidence: 90.0
                            },
                            'STAR_TRACKER_B': {
                                measurement: 0.0,
                                state_estimate: 0.05,
                                covariance: 0.1,
                                confidence: 90.0
                            }
                        }
                    },
                    level2: {
                        count: 4,
                        subsystems: {
                            'navigation': {
                                health: 85.0,
                                covariance_trace: 12.5
                            },
                            'power': {
                                health: 90.0,
                                covariance_trace: 8.2
                            },
                            'payload': {
                                health: 88.0,
                                covariance_trace: 10.1
                            },
                            'comm': {
                                health: 92.0,
                                covariance_trace: 6.5
                            }
                        }
                    },
                    level3: {
                        mission_day: this.missionDay,
                        feasibility: 75.5,
                        anomaly_detected: false,
                        detection_latency: 0,
                        confidence: 80.0,
                        decision: 'CONTINUE_WITH_MONITORING',
                        scenes_today: 650,
                        data_loss_today: 50
                    },
                    file_paths: {
                        level1: 'backend/ekf_execution/level1_placeholder.ekf',
                        level2: 'backend/ekf_execution/level2_placeholder.ekf',
                        level3: 'backend/ekf_execution/level3_placeholder.ekf'
                    }
                };
            } else {
                console.log('[NavigationPlanPage] Using real EKF data:', ekfFiles);
            }
            
            // Komponensek frissítése (MINDIG frissítjük, még placeholder adatokkal is)
            console.log('[NavigationPlanPage] Updating components...');
            console.log('[NavigationPlanPage] Comparison data:', comparison);
            console.log('[NavigationPlanPage] BioCode files:', biocodeFiles ? 'Available' : 'Missing');
            console.log('[NavigationPlanPage] EKF files:', ekfFiles ? 'Available' : 'Missing');
            
            if (this.comparisonPanel) {
                console.log('[NavigationPlanPage] Updating ComparisonPanel...');
                await this.comparisonPanel.update(comparison);
                console.log('[NavigationPlanPage] ComparisonPanel updated');
            } else {
                console.warn('[NavigationPlanPage] ComparisonPanel not initialized!');
            }
            
            if (this.bioCodeViewer) {
                console.log('[NavigationPlanPage] Updating BioCodeViewer...');
                await this.bioCodeViewer.update(biocodeFiles);
                console.log('[NavigationPlanPage] BioCodeViewer updated');
            } else {
                console.warn('[NavigationPlanPage] BioCodeViewer not initialized!');
            }
            
            if (this.ekfViewer) {
                console.log('[NavigationPlanPage] Updating EKFViewer...');
                await this.ekfViewer.update(ekfFiles);
                console.log('[NavigationPlanPage] EKFViewer updated');
            } else {
                console.warn('[NavigationPlanPage] EKFViewer not initialized!');
            }
            
            console.log('[NavigationPlanPage] All components updated');
            
            // Mission day növelése (ha szimuláció fut)
            // MEGJEGYZÉS: A mission_day csak akkor változik, ha fut a szimuláció!
            // A szimuláció indításához meg kell nyomni a "Start" gombot!
            if (this.isRunning) {
                // Mission day növelése (minden 10. frissítésnél, hogy ne változzon túl gyorsan)
                if (!this.updateCount) this.updateCount = 0;
                this.updateCount++;
                
                // Minden 5. frissítésnél (10 másodpercenként) növeljük a mission day-t
                if (this.updateCount % 5 === 0) {
                    const oldMissionDay = this.missionDay;
                    this.missionDay++;
                    const missionDayEl = document.getElementById('mission-day');
                    if (missionDayEl) {
                        missionDayEl.textContent = this.missionDay;
                    }
                    stateManager.setState('missionDay', this.missionDay);
                    console.log(`[NavigationPlanPage] Mission day increased to: ${this.missionDay}`);
                    
                    // ÚJ FÁJLOK GENERÁLÁSA a backend-en
                    try {
                        console.log(`[NavigationPlanPage] Generating new files for mission day ${this.missionDay}...`);
                        const response = await fetch('/api/simulation/generate-files', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ mission_day: this.missionDay })
                        });
                        
                        if (response.ok) {
                            const result = await response.json();
                            console.log(`[NavigationPlanPage] Files generated:`, result);
                            // Azonnal frissítjük az adatokat
                            await this.update();
                        } else {
                            console.warn(`[NavigationPlanPage] Failed to generate files: ${response.statusText}`);
                        }
                    } catch (error) {
                        console.error(`[NavigationPlanPage] Error generating files:`, error);
                    }
                }
            } else {
                // Ha nem fut a szimuláció, tájékoztatjuk a felhasználót
                if (this.updateCount === 0 || this.updateCount % 10 === 0) {
                    console.log('[NavigationPlanPage] Simulation is not running. Click "Start" to begin simulation.');
                }
            }
            
        } catch (error) {
            console.error('[NavigationPlanPage] Update error:', error);
        }
    }
    
    startTimeUpdate() {
        setInterval(() => {
            const now = new Date();
            document.getElementById('current-time').textContent = now.toLocaleTimeString();
        }, 1000);
    }
    
    destroy() {
        this.stopSimulation();
        
        if (this.comparisonPanel) {
            this.comparisonPanel.destroy();
        }
        
        if (this.bioCodeViewer) {
            this.bioCodeViewer.destroy();
        }
        
        if (this.ekfViewer) {
            this.ekfViewer.destroy();
        }
    }
}

// Oldal inicializálása
document.addEventListener('DOMContentLoaded', async () => {
    const page = new NavigationPlanPage();
    await page.init();
    window.navigationPlanPage = page; // Debug céljából
});

