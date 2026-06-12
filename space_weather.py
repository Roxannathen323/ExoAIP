import random

class SpaceWeatherEngine:
    """
    Engine for detecting solar flares and stellar radiation hazards.
    """

    def analyze_space_weather(self, st_teff):
        """
        Calculates stellar risk based on star temperature (M-dwarfs are more active).
        """
        risk_level = "LOW"
        advisory = "STALLAR RADIATION NOMINAL. NO CME DETECTED."
        status = "NORMAL"

        # Handle astropy MaskedQuantity truthiness issue
        st_teff_val = None
        if st_teff is not None:
            try:
                st_teff_val = float(st_teff.value) if hasattr(st_teff, 'value') else float(st_teff)
            except (TypeError, ValueError):
                st_teff_val = None

        # Red dwarfs (Teff < 4000K) have high flare activity
        if st_teff_val is not None and st_teff_val < 4000:
            if random.random() > 0.4: # 60% chance of flare for M-dwarfs
                risk_level = "CRITICAL"
                advisory = "SPACE WEATHER ADVISORY: CLASS X SOLAR FLARE DETECTED. CME IMPACT IMMINENT."
                status = "DEGRADED"
        elif random.random() > 0.9: # 10% chance for other stars
            risk_level = "MODERATE"
            advisory = "SOLAR WIND INTENSIFYING. MINOR RADIO INTERFERENCE EXPECTED."

        return {
            "risk": risk_level,
            "advisory": advisory,
            "status": status
        }
