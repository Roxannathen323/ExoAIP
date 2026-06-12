import random

class PulseWayNav:
    """
    Galactic navigation engine using Pulsar triangulation.
    """

    def generate_navlog(self, planet_name, system_status="NORMAL"):
        """
        Generates 3 fiktivní pulsary and a flight track.
        """
        pulsars = [
            {"id": "PSR J0437-4715", "freq": "173.6 HZ", "snr": round(random.uniform(12, 45), 1)},
            {"id": "PSR B1919+21", "freq": "0.74 HZ", "snr": round(random.uniform(8, 30), 1)},
            {"id": "PSR J0737-3039", "freq": "44.0 HZ", "snr": round(random.uniform(5, 25), 1)}
        ]
        
        status = "FIX VALID"
        if system_status == "DEGRADED":
            status = "NAV DEGRADED"
            for p in pulsars:
                p["snr"] = round(p["snr"] * 0.1, 1)

        # Fictional flight path to a surface point
        track = random.randint(0, 359)
        heading = (track + random.randint(-10, 10)) % 360
        distance = round(random.uniform(100, 5000), 1)

        return {
            "pulsars": pulsars,
            "status": status,
            "log": {
                "destination": f"SECTOR-{random.randint(100, 999)}",
                "track": f"{track:03d}°",
                "heading": f"{heading:03d}°",
                "dist": f"{distance} NM"
            }
        }
