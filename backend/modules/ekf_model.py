import numpy as np

class EKFSimulator:
    """
    Hagyományos Extended Kalman Filter (a 'régi' technológia).
    """
    def __init__(self, landsat_model):
        self.model = landsat_model
        
        # Állapotbecslés (dummy)
        self.state = np.zeros(15)
        self.covariance = np.eye(15) * 10.0
        
        self.confidence = 100.0
        self.anomaly_detected = False
        self.detection_latency = 0
        
        # Metrikák
        self.scenes_today = 0
        self.data_loss_today = 0

    def update(self):
        """
        EKF frissítési ciklus.
        A probléma: Az EKF a *szenzorokra* figyel, nem az akkumulátorra.
        Ha az akku lemerül, az EKF gyakran még "jónak" látja a navigációt,
        ezért engedi tovább a működést -> Dead Bus.
        """
        
        # 1. Szenzor adatok lekérése
        gps = self.model.get_gps_measurement()
        
        # 2. Hiba logika (Szimulált EKF viselkedés)
        if gps is None:
            # GPS Timeout - Ezt észreveszi
            self.confidence -= 5.0
        else:
            # GPS van. Ha az akksi halott, az EKF ezt NEM látja a GPS jelben!
            # Ezért a confidence marad 100%, amíg a feszültség el nem tűnik teljesen.
            
            # Csak a GPS hibát venné észre, de azt is lassan (átlagolva)
            if self.model.gps_error > 50.0:
                # Lassan csökken a bizalom (szimulálva a tehetetlenséget)
                self.confidence -= 2.0
            else:
                self.confidence += 1.0
        
        # Határolás
        self.confidence = max(0.0, min(100.0, self.confidence))
        
        # 3. Döntés
        # Az EKF csak akkor jelez hibát, ha nagyon biztos benne (60% alatt)
        if self.confidence < 60.0:
            self.anomaly_detected = True
            self.detection_latency = 50000 # Nagyon lassú (napok)
        else:
            self.anomaly_detected = False
            
        # 4. Adatgyűjtés (A végzetes hiba: Ha nincs hiba jelezve, gyűjtünk!)
        # Ha az akksi 18%, de az EKF 100%-ot mond, akkor gyűjtünk -> Selejt/Veszély
        if not self.anomaly_detected:
            self.scenes_today = 700
            self.data_loss_today = 0 # Látszólag minden oké (ez a veszély)
        else:
            self.scenes_today = 0
            self.data_loss_today = 700