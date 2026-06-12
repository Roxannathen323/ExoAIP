class ExoLoadsheet:
    """
    ICAO-style Load & Balance Manifest adjusted for local planetary gravity.
    """

    MAX_STRUCTURAL_LIMIT_KN = 150.0  # kN (kilonewtons)

    def calculate_loadsheet(self, gravity_g, dow=5000, fuel=2000, payload=1500):
        """
        Calculates total weight and checks structural limits.
        """
        total_mass = dow + fuel + payload
        
        # Local Weight (Newtons) = Mass (kg) * g (m/s2)
        # g_m_s2 = gravity_g * 9.80665
        g_val = gravity_g * 9.80665
        total_weight_n = total_mass * g_val
        total_weight_kn = total_weight_n / 1000.0

        limit_exceeded = total_weight_kn > self.MAX_STRUCTURAL_LIMIT_KN
        
        status = "LOAD CLEARED"
        if limit_exceeded:
            status = "STRUCTURAL FAILURE IMMINENT: MAX ALLOWABLE LANDING WEIGHT EXCEEDED"

        return {
            "dow": dow,
            "fuel": fuel,
            "payload": payload,
            "total_mass": total_mass,
            "local_weight_kn": round(total_weight_kn, 2),
            "limit_kn": self.MAX_STRUCTURAL_LIMIT_KN,
            "status": status,
            "limit_exceeded": limit_exceeded
        }
