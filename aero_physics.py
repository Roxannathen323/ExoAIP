import numpy as np
from datetime import datetime

class AeroPhysics:
    """
    Physics engine for calculating aeronautical and atmospheric parameters of exoplanets.
    """
    
    # Constants
    G = 6.67430e-11  # Gravitational constant [m^3 kg^-1 s^-2]
    M_EARTH = 5.972e24  # Earth mass [kg]
    R_EARTH = 6.371e6   # Earth radius [m]
    G_EARTH = 9.80665   # Standard gravity [m/s^2]
    R_GAS = 8.314       # Universal gas constant [J/(mol*K)]

    # Exo-Drone MK-I Reference Parameters
    DRONE_MASS = 250.0  # kg
    DRONE_WING_AREA = 5.0  # m^2
    DRONE_CL_MAX = 1.5

    @staticmethod
    def calculate_gravity(mass_earth, radius_earth):
        """
        Calculates surface gravity in m/s^2 and G units.
        """
        # Input sanitization
        m_val = float(mass_earth.value) if hasattr(mass_earth, 'value') else float(mass_earth)
        r_val = float(radius_earth.value) if hasattr(radius_earth, 'value') else float(radius_earth)

        m = m_val * AeroPhysics.M_EARTH
        r = r_val * AeroPhysics.R_EARTH
        
        g = (AeroPhysics.G * m) / (r**2)
        g_unit = g / AeroPhysics.G_EARTH
        
        return round(float(g), 2), round(float(g_unit), 2)

    def estimate_atmosphere(self, data):
        """
        Estimates atmospheric parameters based on temperature and planet type.
        """
        import math

        # --- 1. Temperature processing ---
        temp_raw = data.get('temp_eq')
        if temp_raw is None:
            temp = 288.0
        else:
            try:
                temp = float(temp_raw.value) if hasattr(temp_raw, 'value') else float(temp_raw)
            except (TypeError, ValueError):
                temp = 288.0
                
            if math.isnan(temp):
                temp = 288.0
                
        # --- 2. Radius processing ---
        radius_raw = data.get('radius', 1.0)
        try:
            radius = float(radius_raw.value) if hasattr(radius_raw, 'value') else float(radius_raw)
        except (TypeError, ValueError):
            radius = 1.0
            
        if math.isnan(radius):
            radius = 1.0
            
        # --- 3. Atmosphere type logic ---
        if 200 <= temp <= 320 and radius < 2.0:
            atm_type = "Nitrogen-Oxygen (N2/O2) - Terrestrial"
            molar_mass = 0.02897  # kg/mol
            gamma = 1.4
            base_pressure = 1013.25 # hPa
        elif radius >= 2.0:
            atm_type = "Hydrogen-Helium (H/He) - Gas Giant"
            molar_mass = 0.002    # kg/mol
            gamma = 1.4
            base_pressure = 100000.0 # hPa
        else:
            atm_type = "Carbon Dioxide (CO2) - Extreme/Unknown"
            molar_mass = 0.04401  # kg/mol
            gamma = 1.28
            base_pressure = 500.0 # hPa
            
        # Speed of sound: c = sqrt(gamma * R * T / M)
        sound_speed = np.sqrt((gamma * AeroPhysics.R_GAS * temp) / molar_mass)
        
        # Gas Density: rho = P / (R_spec * T)
        # R_spec = R_GAS / molar_mass
        r_spec = AeroPhysics.R_GAS / molar_mass
        # Pressure in hPa to Pa (x100)
        density = (base_pressure * 100) / (r_spec * temp)

        return {
            'type': atm_type,
            'temp_k': round(float(temp), 1),
            'temp_c': round(float(temp) - 273.15, 1),
            'molar_mass': molar_mass,
            'pressure_hpa': base_pressure,
            'density_kgm3': round(float(density), 4),
            'sound_speed_ms': round(float(sound_speed), 2),
            'sound_speed_kmh': round(float(sound_speed) * 3.6, 2),
            'sound_speed_kt': round(float(sound_speed) * 1.94384, 1)
        }

    def determine_archetype(self, temp, radius):
        """
        Determines planet archetype for visualization.
        """
        if radius >= 2.0:
            if temp > 800:
                return "hot-jupiter"
            elif temp < 250:
                return "ice-giant"
            else:
                return "gas-giant"
        else:
            if temp > 1000:
                return "lava-world"
            elif temp > 320:
                return "desert-rock"
            elif 200 <= temp <= 320:
                if radius < 1.5:
                    return "earth-like"
                else:
                    return "super-earth"
            else:
                return "frozen-rock"

    def generate_notam(self, planet_name, gravity_g, temp_k, atm_type):
        """
        Generates a procedural ICAO NOTAM for the planet.
        """
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        notam_id = f"A{timestamp[:4]}/26"
        
        warnings = []
        if gravity_g > 1.5:
            warnings.append("DANGER AREA. HIGH G-LOAD EXPECTED DURING DESCENT. STRUCTURAL LIMITATIONS APPLY.")
        if temp_k < 200:
            warnings.append("SEVERE ICING CONDITIONS AND CRYOGENIC TEMPERATURES DETECTED.")
        if temp_k > 350:
            warnings.append("EXTREME THERMAL RADIATION. HEAT SHIELD DEGRADATION PROBABLE.")
        if "H/He" in atm_type:
            warnings.append("ATMOSPHERIC COMPOSITION HAZARDOUS FOR AIR-BREATHING PROPULSION.")
            
        if not warnings:
            warnings.append("NO SIGNIFICANT OPERATIONAL HAZARDS DETECTED.")

        notam_text = f"{notam_id} NOTAMN\nQ) XAIP/QXXXX/I/NBO/A/000/999/\nA) {planet_name.upper()}\nB) {timestamp}\nE) "
        notam_text += " ".join(warnings)
        
        return notam_text

    def calculate_signal_delay(self, distance_pc):
        """
        Calculates signal delay (one-way) based on distance in parsecs.
        Returns delay in hours and a formatted string.
        """
        if distance_pc is None or str(distance_pc) == '--':
            return 0, "UNKNOWN"
        
        # 1 pc = 3.26156 light years
        # Handle astropy Quantity or MaskedArray
        dist_val = float(distance_pc.value) if hasattr(distance_pc, 'value') else float(distance_pc)
        light_years = dist_val * 3.26156
        
        # Delay in hours (1 year = 365.25 * 24 hours)
        delay_hours = light_years * 365.25 * 24
        
        if delay_hours < 24:
            formatted = f"{round(delay_hours, 1)} HOURS"
        else:
            days = delay_hours / 24
            if days < 365:
                formatted = f"{round(days, 1)} DAYS"
            else:
                formatted = f"{round(light_years, 1)} YEARS"
                
        return delay_hours, formatted

    def process_planet_physics(self, data):
        """
        Processes all physical data for AIP.
        """
        # Input sanitization
        mass_val = float(data['mass'].value) if hasattr(data['mass'], 'value') else float(data['mass'])
        radius_val = float(data['radius'].value) if hasattr(data['radius'], 'value') else float(data['radius'])

        g_ms2, g_unit = self.calculate_gravity(mass_val, radius_val)
        atm = self.estimate_atmosphere(data)
        
        # Archetype determination
        archetype = self.determine_archetype(atm['temp_k'], radius_val)
        
        # NOTAM generation
        notam = self.generate_notam(data['name'], g_unit, atm['temp_k'], atm['type'])
        
        # Signal Delay
        delay_h, delay_fmt = self.calculate_signal_delay(data.get('distance'))

        # Escape velocity
        m = mass_val * AeroPhysics.M_EARTH
        r = radius_val * AeroPhysics.R_EARTH
        v_escape = np.sqrt(2 * AeroPhysics.G * m / r)
        
        # Stall Speed (Vs) calculation
        # Vs = sqrt((2 * m * g) / (rho * S * Cl_max))
        rho = atm['density_kgm3']
        g = g_ms2
        m_drone = AeroPhysics.DRONE_MASS
        s_drone = AeroPhysics.DRONE_WING_AREA
        cl_max = AeroPhysics.DRONE_CL_MAX

        if rho > 0.0001:  # Threshold for "flight possible"
            vs_ms = np.sqrt((2 * m_drone * g) / (rho * s_drone * cl_max))
            vs_kt = round(vs_ms * 1.94384, 1)
        else:
            vs_kt = "UNABLE TO SUSTAIN FLIGHT"

        physics_results = {
            'gravity_ms2': g_ms2,
            'gravity_g': g_unit,
            'atmosphere': atm,
            'archetype': archetype,
            'notam': notam,
            'signal_delay': delay_fmt,
            'stall_speed_kt': vs_kt,
            'v_escape_kmh': round(float(v_escape) * 3.6, 2),
            'v_escape_ms': round(float(v_escape), 2),
            'v_escape_kt': round(float(v_escape) * 1.94384, 1)
        }
        
        return physics_results

    def calculate_reentry_profile(self, density_kgm3, gravity_g, radius_earth):
        """
        Calculates safe entry angle and thermal load estimates.
        """
        # Base angle for Earth-like is ~5.0 to 7.0 degrees
        # Thick atmosphere (e.g. Venus/Giant) requires shallower approach
        # Thin atmosphere (e.g. Mars) requires steeper approach
        
        rel_density = density_kgm3 / 1.225 # Relative to Earth surface
        
        if rel_density > 10:
            angle_min, angle_max = 2.5, 3.8
            hazard = "EXTREME THERMAL LOAD. SHALLOW DESCENT MANDATORY."
        elif rel_density > 1.5:
            angle_min, angle_max = 4.0, 5.5
            hazard = "HIGH DYNAMIC PRESSURE. STRUCTURAL MONITORING REQUIRED."
        elif rel_density < 0.1:
            angle_min, angle_max = 8.5, 12.0
            hazard = "THIN ATMOSPHERE. STEEP ANGLE REQUIRED TO PREVENT BOUNCE."
        else:
            angle_min, angle_max = 5.8, 7.2
            hazard = "STANDARD ENTRY CORRIDOR."

        if gravity_g > 2.0:
            hazard += " DANGER: HIGH G-STRESS EXPECTED."

        return {
            "angle_range": f"{angle_min}° - {angle_max}°",
            "thermal_load": "CRITICAL" if rel_density > 5 else "HIGH" if rel_density > 1 else "NOMINAL",
            "hazard_warning": hazard
        }

    def calculate_blackout_period(self, v_escape_ms, gravity_g):
        """
        Calculates Plasma Blackout duration during entry.
        Higher speed and gravity increase duration.
        """
        # Base blackout for Earth is ~120-240 seconds
        base_blackout = (v_escape_ms / 11186.0) * 180.0
        # Gravity factor (higher G -> more intense compression)
        g_factor = 1.0 + (gravity_g - 1.0) * 0.2
        return round(base_blackout * g_factor, 1)

    def is_tidally_locked(self, data):
        """
        Infers if the planet is tidally locked based on distance and star type.
        (NASA data often missing this flag, so we use proximity as proxy).
        """
        dist_au = data.get('semi_major_axis')
        if dist_au is None: return False
        
        # Simple proxy: if < 0.1 AU and star is red dwarf or similar, high probability
        spec = data.get('st_spectype', '')
        if float(dist_au) < 0.1 and ('M' in str(spec) or 'K' in str(spec)):
            return True
        return False
