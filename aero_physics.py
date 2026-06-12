import numpy as np

class AeroPhysics:
    """
    Fyzikální engine pro výpočet leteckých a atmosférických parametrů exoplanet.
    """
    
    # Konstanty
    G = 6.67430e-11  # Gravitační konstanta [m^3 kg^-1 s^-2]
    M_EARTH = 5.972e24  # Hmotnost Země [kg]
    R_EARTH = 6.371e6   # Poloměr Země [m]
    G_EARTH = 9.80665   # Standardní tíhové zrychlení Země [m/s^2]
    R_GAS = 8.314       # Univerzální plynová konstanta [J/(mol*K)]

    @staticmethod
    def calculate_gravity(mass_earth, radius_earth):
        """
        Vypočítá povrchovou gravitaci v m/s^2 a v jednotkách G.
        """
        # Sanitizace vstupů (astropy Quantity nebo MaskedArray)
        m_val = float(mass_earth.value) if hasattr(mass_earth, 'value') else float(mass_earth)
        r_val = float(radius_earth.value) if hasattr(radius_earth, 'value') else float(radius_earth)

        m = m_val * AeroPhysics.M_EARTH
        r = r_val * AeroPhysics.R_EARTH
        
        g = (AeroPhysics.G * m) / (r**2)
        g_unit = g / AeroPhysics.G_EARTH
        
        return round(float(g), 2), round(float(g_unit), 2)

    def estimate_atmosphere(self, data):
        """
        Odhadne parametry atmosféry na základě teploty a typu planety.
        Očištěno o astropy jednotky (Quantity).
        """
        import math

        # --- 1. Zpracování teploty ---
        temp_raw = data.get('temp_eq')
        if temp_raw is None:
            temp = 288.0
        else:
            # Převod na float (řeší astropy Quantity i MaskedArray)
            try:
                temp = float(temp_raw.value) if hasattr(temp_raw, 'value') else float(temp_raw)
            except (TypeError, ValueError):
                temp = 288.0
                
            if math.isnan(temp):
                temp = 288.0
                
        # --- 2. Zpracování poloměru ---
        radius_raw = data.get('radius', 1.0)
        try:
            radius = float(radius_raw.value) if hasattr(radius_raw, 'value') else float(radius_raw)
        except (TypeError, ValueError):
            radius = 1.0
            
        if math.isnan(radius):
            radius = 1.0
            
        # --- 3. Logika pro typ atmosféry ---
        if 200 <= temp <= 320 and radius < 2.0:
            atm_type = "Dusíková (N2) - Terestrická"
            molar_mass = 0.02897  # kg/mol (vzduch)
            gamma = 1.4
            base_pressure = 1013.25 # hPa
        elif radius >= 2.0:
            atm_type = "Vodíkovo-heliová (H/He) - Plynný obr"
            molar_mass = 0.002    # kg/mol
            gamma = 1.4
            base_pressure = 100000.0 # hPa
        else:
            # ZÁCHRANNÁ SÍŤ (pro příliš horké nebo ledové kamenné planety)
            atm_type = "Oxid uhličitý (CO2) - Extrémní / Neznámá"
            molar_mass = 0.04401  # kg/mol (CO2)
            gamma = 1.28
            base_pressure = 500.0 # hPa (střední odhad)
            
        # Výpočet rychlosti zvuku: c = sqrt(gamma * R * T / M)
        sound_speed = np.sqrt((gamma * AeroPhysics.R_GAS * temp) / molar_mass)
        
        return {
            'type': atm_type,
            'temp_k': round(float(temp), 1),
            'temp_c': round(float(temp) - 273.15, 1),
            'molar_mass': molar_mass,
            'pressure_hpa': base_pressure,
            'sound_speed_ms': round(float(sound_speed), 2),
            'sound_speed_kmh': round(float(sound_speed) * 3.6, 2)
        }

    def process_planet_physics(self, data):
        """
        Zpracuje všechna fyzikální data pro AIP.
        """
        # Sanitizace vstupů pro celou metodu
        mass_val = float(data['mass'].value) if hasattr(data['mass'], 'value') else float(data['mass'])
        radius_val = float(data['radius'].value) if hasattr(data['radius'], 'value') else float(data['radius'])

        g_ms2, g_unit = self.calculate_gravity(mass_val, radius_val)
        atm = self.estimate_atmosphere(data)
        
        # Výpočet únikové rychlosti (pro zajímavost v sekci AD)
        m = mass_val * AeroPhysics.M_EARTH
        r = radius_val * AeroPhysics.R_EARTH
        v_escape = np.sqrt(2 * AeroPhysics.G * m / r)
        
        physics_results = {
            'gravity_ms2': g_ms2,
            'gravity_g': g_unit,
            'atmosphere': atm,
            'v_escape_kmh': round(float(v_escape) * 3.6, 2),
            'v_escape_ms': round(float(v_escape), 2)
        }
        
        return physics_results
