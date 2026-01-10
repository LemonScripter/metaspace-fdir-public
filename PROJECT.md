# MetaSpace Satellite Simulation

## Project Overview
**MetaSpace** is a sophisticated satellite mission assurance simulator designed to demonstrate and compare a novel **Deterministic FDIR (Fault Detection, Isolation, and Recovery)** system against the traditional **Extended Kalman Filter (EKF)** approach.

The project models a **Landsat-9** satellite and runs comparative scenarios where faults (e.g., sensor failures, power loss) are injected to observe how each system responds. MetaSpace utilizes a proprietary "Bio-Code" logic to strictly enforce physical invariants, ensuring immediate fault isolation and hardware safety, whereas EKF often attempts to smooth errors, potentially leading to mission failure.

### Key Components
1.  **V2 Main Simulation (`/`)**:
    *   Direct A/B comparison of EKF vs. MetaSpace.
    *   Fault injection scenarios (GPS Spoofing, Battery Thermal Runaway, etc.).
    *   Real-time telemetry and health matrix visualization.
2.  **V3 Neural Sandbox (`/v3-sandbox`)**:
    *   A "Holographic" neural network representation of the satellite.
    *   Controlled by 3-Level Bio-Codes.
    *   Features autonomous "self-healing" and mathematical validation of all operations.
3.  **Navigation Plan Simulation (`/navigation-plan`)**:
    *   Split-screen UI tracking orbit positions and mission tasks.
    *   Generates and visualizes the binary Bio-Code and EKF execution files.

## Technical Architecture
*   **Backend:** Python (Flask)
    *   **Physics Engine:** `backend/modules/landsat9.py` (High-fidelity physical model)
    *   **Logic Cores:**
        *   `metaspace.py`: New deterministic FDIR.
        *   `ekf_model.py`: Legacy probabilistic estimator.
        *   `v3_neural_core.py`: Self-healing neural network logic.
    *   **File Managers:** Handles binary `.bio` and `.ekf` file generation and storage.
*   **Frontend:** HTML5, CSS3, JavaScript
    *   **Visualizations:** D3.js for orbit tracks, neural networks, and charts.
    *   **Architecture:** Modular JS architecture (`ComponentBase`, `EventBus`, `StateManager`) for the Navigation Plan UI.

## Building and Running

### Prerequisites
*   Python 3.10+
*   `pip` (Python package installer)

### Setup
1.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Execution
1.  **Start the Server:**
    ```bash
    python app.py
    ```
2.  **Access the Dashboard:**
    Open a browser and navigate to `http://localhost:5000`.

## Directory Structure
*   `app.py`: Main Flask application entry point.
*   `backend/`: Contains all server-side logic and data storage.
    *   `modules/`: Python source code for physics, logic, and file management.
    *   `biocodes/`: Generated deterministic state files (`.bio`).
    *   `ekf_execution/`: Generated probabilistic state files (`.ekf`).
*   `templates/`: HTML templates for the three simulation modes.
*   `static/`:
    *   `js/`: Frontend logic (modularized in `core/`, `services/`, `components/`).
    *   `css/`: Stylesheets.
*   `docs/`: Extensive project documentation and specifications.

## Development Conventions
*   **Simulation Isolation:** The three simulation modes (`V2`, `V3`, `NavPlan`) use isolated global variables (prefixed with `_navigation_plan_`, etc.) in `app.py` to prevent state cross-contamination.
*   **File Formats:** The system generates custom binary files for "Bio-Code" (deterministic state) and EKF data, featuring magic numbers, metadata, and timestamps.
*   **Validation:** The V3 engine includes a rigorous mathematical validation layer (`v3_validation_engine.py`) that produces unforgeable JSON reports in `validation_reports/`.

## Current Status (as of Jan 2026)
*   **Stable:** All three simulation modes are functional.
*   **Focus:** The project is currently refining the Navigation Plan UI and ensuring strict mathematical proof of safety in the V3 engine.
*   **See `STATUS.md`** for a detailed changelog and feature list.
