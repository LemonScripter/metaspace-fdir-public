# Tudományos Analízis: MetaSpace Szimulációs Validáció Kiegészítésére Vonatkozó Javaslatok

A mellékelt validációs dokumentáció (Safety Case, System Spec, FMEA, Validation Report) **előre mutat**, de a szimuláció **vitathatatlan** tudományos érvényességének megállapítására több kritikus dokumentációs és metodológiai kiegészítés szükséges. Az alábbiakban tudományos szempont szerinti strukturált javaslatok következnek.

***

### **I. FUNDAMENTÁLIS VALIDÁCIÓS HIÁNYOSSÁGOK**

#### **A. Code Verification Hiánya** [1][2][3]
**Probléma:** A Validációs Jelentésben (04_Validation_Report) "Unit Tests (Physics)" 3/3 tesztet számol fel, azonban nincsenek konkrét **Code Verification** (kódellenőrzés) eredmények dokumentálva.

**Szükséges kiegészítések:**
1. **Method of Manufactured Solutions (MMS)** alkalmazása [2][3][1]
   - A MetaSpace numerikus szolver (Python 3.10 alapú) verifikálásához szimulációs feladatokat kell konstruálni, amelyeknek ismert analitikus megoldásai vannak
   - Például: 1D hővezetés, konzervatív mechanikai rendszerek
   - Konvergencia analízis: \( \text{error} = O(h^p) \) ahol \( h \) a numerikus lépésköz, \( p \) a sorrend
   - Gridkonvergencia Index (GCI) számítás: \( \text{GCI} = \frac{1.25 \cdot \epsilon_{32}}{r^p - 1} \) ahol \( \epsilon_{32} \) relatív hiba, \( r \) refinement ratio [2]

2. **Numerikus stabilitás és pontosság analízis**
   - Time-stepping scheme verifikálása (RK4 vs Euler implicit/explicit stabilitás)
   - Round-off error accumulation, especially for long simulations (szatellit több napos missziók)
   - Single vs double precision impact on FDIR detection accuracy

#### **B. Modell Validáció Valós Adatokkal Szemben** [4][5]
**Probléma:** A dokumentáció nem tartalmaz összehasonlítást valós szatellit telemetria adatok vagy kalibrált fizikai tesztek ellen.

**Szükséges kiegészítések:**
1. **Validációs referencia adatok**
   - Valós CubeSat missziók telemetriai adatai (nyilvánosan elérhető):
     - IXION, UPMSat-2, Prinsipe, PEGASUS stb. mission databases
     - Vagy szimulált de fizikailag validált reference benchmark teszt-esetek
   
2. **Validációs metrikák** [5][6][4]
   - Mean Absolute Error (MAE), Root Mean Square Error (RMSE) explicit meghatározása
   - Percent Error: \( \text{PE} = 100 \cdot \frac{|\text{Simulated} - \text{Actual}|}{\text{Actual}}| \) < meghatározott threshold (pl. 5-10%)
   - Pearson correlation coefficient: \( r \geq 0.95 \) vagy hasonló

3. **Validation Experiment Design**
   - Boundary condition dokumentálása (initial conditions, external forces)
   - Measurement uncertainty quantification az összehasonlításban

#### **C. Bizonytalansági Kvantifikáció (UQ) Hiánya** [7][5]
**Probléma:** Nincsenek explicit **uncertainty propagation** vagy **sensitivity analysis** eredmények.

**Szükséges kiegészítések:**
1. **Input Uncertainty Quantification**
   - Solar irradiance variabilitás: \( \pm 5-7\% \) sztellar fluxus ciklus alatt
   - Orbital debris density uncertainty: \( \pm 30-50\% \) MASTER/ORDEM modell közötti eltérés
   - Sensor noise models (GPS spoofing severity, gyro bias distribution)

2. **Sensitivity Analysis**
   - Sobol Global Sensitivity Indices \( S_i \) (first-order, total-order) az FDIR threshold-hoz
   - Morris OAT (One-At-a-Time) screening az paraméter-fontosság azonosítására
   - Tornadó diagramok: melyik paraméter szórása okoz legnagyobb detektálási idő eltérést?

3. **Output Uncertainty Intervals**
   - Monte Carlo szimuláció: 1000+ futás stochasztikus inputokkal
   - Confidence intervals (95%) a detektálási időre: TTD = 87 ± 8 ms

#### **D. FDIR-Specifikus Metrikai és Teljesítmény Karakterizáció** [8][9][10][11]
**Probléma:** Az FMEA (03_FMEA) csak "Detection (D)" érték 1 vs 9/10 összehasonlítást mutat, de hiányzik a részletes FDIR metrikai.

**Szükséges kiegészítések:**
1. **Detektálási Teljesítmény Metrikái**
   - **Time to Detect (TTD):** Eloszlás függvénye a hiba magnitúdójának függvényében
   - **False Alarm Rate (FAR) vs Missed Detection Rate (MDR):** ROC görbék (Receiver Operating Characteristic)
   - **Isolation Accuracy:** %-os arány, hányszor azonosítja helyesen a *konkrét* hibás komponenst (nem csak a szubszisztémát)

2. **Recovery Robustness**
   - Recovery Time: Mennyi idő alatt áll vissza a rendszer a Safe Mode-ba vagy Névleges állapotba?
   - Stability Margins during Recovery: Overshoot, settling time a szabályozási körben a recovery alatt

### **II. DOKUMENTÁCIÓS SZERKEZET ÉS TRACEABILITY JAVÍTÁSOK** [12][13]

**Probléma:** A dokumentumok (Safety Case -> System Spec -> FMEA) közötti kapcsolat logikai, de nem formálisan nyomon követhető (traceable).

**Javaslatok:**
1. **Requirements Traceability Matrix (RTM) létrehozása**
   - Minden System Spec követelményhez (pl. "REQ-FDIR-001") rendelni kell:
     - Kapcsolódó Hazard-ot a Safety Case-ből (pl. "H-01")
     - Kapcsolódó Failure Mode-ot az FMEA-ból (pl. "FM-GPS-02")
     - Kapcsolódó Teszt Esetet a Validációs Jelentésből (pl. "TEST-03")
   - Ez biztosítja a **"V-modell"** szerinti teljes lefedettséget.

2. **Formalizált Notation (Jelölésrendszer)**
   - Használjon strukturált nyelvezetet a követelményekhez (pl. EARS - Easy Approach to Requirements Syntax): "When [trigger], the [system] shall [response]."

### **III. REFERENCIÁK ÉS IRODALOMJEGYZÉK (Science Baseline)**

A tudományos megalapozottság érdekében az alábbi típusú forrásokat kell explicit módon hivatkozni a fenti hiányosságok pótlásakor:

1.  **Code Verification:**
    - Roache, P. J. (1998). *Verification and Validation in Computational Science and Engineering*. Hermosa.
    - Oberkampf, W. L., & Roy, C. J. (2010). *Verification and Validation in Scientific Computing*. Cambridge University Press.
2.  **Model Validation:**
    - AIAA (1998). *Guide for the Verification and Validation of Computational Fluid Dynamics Simulations* (AIAA G-077-1998).
    - Sargent, R. G. (2013). "Verification and validation of simulation models". *Journal of Simulation*.
3.  **Uncertainty Quantification:**
    - Smith, R. C. (2013). *Uncertainty Quantification: Theory, Implementation, and Applications*. SIAM.
4.  **FDIR Metrics:**
    - Isermann, R. (2006). *Fault-Diagnosis Systems: An Introduction from Fault Detection to Fault Tolerance*. Springer.
    - Patton, R. J., Frank, P. M., & Clark, R. N. (2000). *Issues of Fault Diagnosis for Dynamic Systems*. Springer.

### **ÖSSZEGZÉS**

A jelenlegi dokumentációs csomag egy **erős mérnöki (engineering) alap**, de hiányzik belőle a **szigorú tudományos (scientific) validációs réteg**. A fenti I. (A-D) pontokban részletezett kvantitatív analízisek és a II. pont szerinti traceability megteremtése emelné a projektet "demonstráció" szintről "tudományosan validált szimulációs keretrendszer" szintre.
