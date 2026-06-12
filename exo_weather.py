import random
from datetime import datetime

class ExoWeatherEngine:
    """
    Engine for generating procedural planetary weather and ICAO VOLMET broadcasts.
    """

    def generate_weather(self, temp_k, pressure_hpa, atm_type, archetype):
        """
        Simulates planetary weather conditions based on physical parameters.
        """
        # 1. Wind Logic
        # Hot Jupiters and Tidally Locked planets have extreme winds
        if archetype in ['hot-jupiter', 'lava-world']:
            wind_speed = random.randint(200, 800)
        elif archetype in ['gas-giant', 'ice-giant']:
            wind_speed = random.randint(100, 400)
        else:
            wind_speed = random.randint(5, 45)
        
        wind_dir = random.randint(0, 359)

        # 2. Visibility and Phenomena
        phenomena = "NIL"
        visibility = "9999" # In meters

        if "CO2" in atm_type or archetype == 'desert-rock':
            phenomena = "WIDESPREAD DUSTSTORM"
            visibility = str(random.randint(500, 2000))
        elif archetype == 'frozen-rock' or (temp_k < 200 and "H/He" not in atm_type):
            phenomena = "METHANE SNOW"
            visibility = str(random.randint(1000, 5000))
        elif archetype == 'hot-jupiter' or archetype == 'gas-giant':
            phenomena = "AMMONIA CLOUDS"
            visibility = "2000"
        elif "Terrestrial" in atm_type and 273 < temp_k < 310:
            phenomena = "LIGHT RAIN"
            visibility = "8000"
        
        return {
            "wind_dir": f"{wind_dir:03d}",
            "wind_speed": wind_speed,
            "visibility": visibility,
            "phenomena": phenomena,
            "temp_c": int(temp_k - 273.15),
            "dew_point": int(temp_k - 273.15 - random.randint(2, 10)),
            "qnh": int(pressure_hpa)
        }

    def generate_volmet(self, planet_name, weather):
        """
        Formats weather data into a standardized ICAO VOLMET broadcast string.
        """
        zulu_time = datetime.utcnow().strftime("%H%M") + "Z"
        
        broadcast = [
            "ORBITAL METEOROLOGICAL CENTER",
            f"VOLMET FOR {planet_name.upper()}",
            f"OBSERVATION AT {zulu_time}",
            f"WIND {weather['wind_dir']} DEGREES {weather['wind_speed']} KNOTS",
            f"VISIBILITY {weather['visibility']} METERS",
            f"PRESENT WEATHER {weather['phenomena']}",
            f"TEMPERATURE {weather['temp_c']} DEWPOINT {weather['dew_point']}",
            f"QNH {weather['qnh']} HECTOPASCALS",
            "NOSIG",
            "OUT"
        ]
        
        return " ... ".join(broadcast)

    def generate_metar_taf(self, weather, archetype):
        """
        Generates raw, encoded ICAO METAR and TAF strings for exotic conditions.
        """
        zulu_time = datetime.utcnow().strftime("%d%H%M") + "Z"
        icao = "OEXO" # Outer-space Exo-port
        
        # 1. Wind encoding
        wind = f"{weather['wind_dir']}{weather['wind_speed']:02d}KT"
        
        # 2. Visibility
        vis = weather['visibility'] if int(weather['visibility']) < 9999 else "9999"
        
        # 3. Phenomena mapping to ICAO codes
        phenom_code = "NSW" # No Significant Weather
        if "DUSTSTORM" in weather['phenomena']: phenom_code = "DS"
        elif "METHANE SNOW" in weather['phenomena']: phenom_code = "SN CH4"
        elif "AMMONIA" in weather['phenomena']: phenom_code = "FG NH3"
        elif "RAIN" in weather['phenomena']: phenom_code = "RA"
        
        if archetype == 'lava-world': phenom_code = "VA" # Volcanic Ash
        
        # 4. Temperature encoding (M for minus)
        t = weather['temp_c']
        dp = weather['dew_point']
        t_str = f"{'M' if t < 0 else ''}{abs(t):02d}"
        dp_str = f"{'M' if dp < 0 else ''}{abs(dp):02d}"
        
        # 5. Pressure
        qnh = f"Q{weather['qnh']:04d}"
        
        metar = f"METAR {icao} {zulu_time} {wind} {vis} {phenom_code} {t_str}/{dp_str} {qnh} NOSIG"
        
        # Simple TAF
        taf = f"TAF {icao} {zulu_time} {zulu_time[:-1]}/{int(zulu_time[:2])+1:02d}1200 {wind} {vis} {phenom_code} PROB30 TEMPO {vis} {phenom_code}"
        
        return metar, taf
