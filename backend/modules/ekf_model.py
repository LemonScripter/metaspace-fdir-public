import numpy as np
import random

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
        
        REÁLIS VISELKEDÉS:
        - Solar panel hiba → akku lassan lemerül → GPS timeout (< 10%) → EKF lassan reagál
        - Battery failure → akku azonnal lemerül → GPS timeout → EKF lassan reagál
        - GPS antenna hiba → rossz GPS adat → EKF lassan reagál (heurisztikus próbálkozás)
        - IMU drift → fokozatos navigációs hiba → EKF lassan reagál
        """
        
        # 1. Szenzor adatok lekérése
        gps = self.model.get_gps_measurement()
        
        # 2. Hiba logika (Szimulált EKF viselkedés)
        # REÁLIS: Ha az akku < 10%, a GPS jel eltűnik (nincs elég energia)
        # Az EKF ezt észleli, de lassan reagál (valószínűségszámítás, átlagolás)
        if gps is None:
            # GPS Timeout - Ezt észreveszi, de lassan
            # Reálisan: 1-2 nap alatt észleli a GPS timeout-ot
            # Heurisztikusan próbálja visszaállítani a kapcsolatot
            self.confidence -= 2.0  # Lassan csökken (átlagolva)
        else:
            # GPS van. Ha az akksi halott, az EKF ezt NEM látja a GPS jelben!
            # Ezért a confidence marad 100%, amíg a feszültség el nem tűnik teljesen.
            
            # Csak a GPS hibát venné észre, de azt is lassan (átlagolva)
            # GPS antenna hiba esetén: rossz adatot kap, heurisztikusan próbálja visszaterelni
            # Lassan csökken a bizalom (valószínűségszámítás, tehetetlenség)
            if self.model.gps_error > 50.0:
                # Lassan csökken a bizalom (szimulálva a tehetetlenséget és heurisztikus próbálkozást)
                # Minél nagyobb a GPS hiba, annál gyorsabban csökken
                # De még mindig lassan (EKF jellemző: heurisztikus, valószínűségszámítás)
                # Az EKF heurisztikusan próbálja visszaterelni a műholdat, de lassan
                error_factor = min(2.0, (self.model.gps_error - 50.0) / 25.0)
                self.confidence -= (1.5 + error_factor)  # Lassabban csökken
            else:
                # Nincs hiba, vagy kicsi hiba -> növeljük a bizalmat
                # De csak lassan (max 100%)
                self.confidence = min(100.0, self.confidence + 1.0)
        
        # Határolás
        self.confidence = max(0.0, min(100.0, self.confidence))
        
        # 3. Döntés
        # Az EKF csak akkor jelez hibát, ha nagyon biztos benne (60% alatt)
        if self.confidence < 60.0:
            self.anomaly_detected = True
            # Dinamikus detection latency számítás a hiba típusa alapján
            # Tudományos alap: EKF valószínűségszámítási módszere miatt lassan reagál
            self.detection_latency = self._calculate_detection_latency()
        else:
            self.anomaly_detected = False
            
        # 4. Adatgyűjtés (A végzetes hiba: Ha nincs hiba jelezve, gyűjtünk!)
        # Ha az akksi 18%, de az EKF 100%-ot mond, akkor gyűjtünk -> Selejt/Veszély
        # GPS antenna hiba esetén: Az EKF rossz adatot kap, de lassan reagál
        # Közben tovább gyűjt adatot (fölösleges/költséges fotók) -> data_loss nő
        if not self.anomaly_detected:
            # Ha nincs hiba jelezve, de van GPS hiba, akkor rossz adatot gyűjtünk
            if self.model.gps_error > 50.0:
                # GPS hiba van, de az EKF még nem észlelte -> rossz adatot gyűjtünk
                # A data_loss növekszik, mert rossz minőségű adat készül
                self.scenes_today = 700  # Tovább gyűjt (rossz adat)
                # A data_loss arányos a GPS hibával (minél nagyobb a hiba, annál rosszabb az adat)
                data_quality = max(0.0, 1.0 - (self.model.gps_error / 100.0))
                self.data_loss_today = int(700 * (1.0 - data_quality))  # Fölösleges/költséges fotók
            else:
                self.scenes_today = 700
                self.data_loss_today = 0 # Látszólag minden oké (ez a veszély)
        else:
            self.scenes_today = 0
            self.data_loss_today = 700
    
    def _calculate_detection_latency(self):
        """
        Dinamikus detection latency számítás a hiba típusa alapján.
        Tudományos alap: EKF valószínűségszámítási módszere miatt lassan reagál.
        
        Returns:
            int: Detection latency percben
        """
        gps = self.model.get_gps_measurement()
        
        # GPS timeout (akku < 10%): 1-2 nap (1440-2880 perc)
        # Az EKF lassan észleli, mert csak a GPS jel hiányát látja
        if gps is None:
            # 1-2 nap közötti véletlenszerű érték
            return random.randint(1440, 2880)  # 1-2 nap
        
        # GPS error (GPS antenna hiba vagy spoofing): 0.5-2 nap (720-2880 perc)
        # Az EKF heurisztikusan próbálja korrigálni, de lassan reagál
        if self.model.gps_error > 50.0:
            # Minél nagyobb a hiba, annál gyorsabban észleli (de még mindig lassan)
            if self.model.gps_error > 80.0:
                # Nagy hiba: 0.5-1 nap
                return random.randint(720, 1440)
            else:
                # Közepes hiba: 1-2 nap
                return random.randint(1440, 2880)
        
        # IMU drift: 2-5 nap (2880-7200 perc)
        # Fokozatos hiba, az EKF lassan észleli
        if hasattr(self.model, 'imu_accumulated_error') and self.model.imu_accumulated_error > 0.2:
            # Minél nagyobb a drift, annál gyorsabban észleli
            if self.model.imu_accumulated_error > 0.5:
                # Nagy drift: 2-3 nap
                return random.randint(2880, 4320)
            else:
                # Közepes drift: 3-5 nap
                return random.randint(4320, 7200)
        
        # Alapértelmezett: 2-3 nap (ha nem tudjuk meghatározni a hiba típusát)
        return random.randint(2880, 4320)