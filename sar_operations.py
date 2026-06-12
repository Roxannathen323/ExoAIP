import math

class SAROperations:
    """
    Search and Rescue engine for extreme planetary environments.
    """

    def calculate_sar_plan(self, pressure_hpa, temp_k, bio_hazard_level):
        """
        Calculates Time of Useful Consciousness (TUC) and rescue patterns.
        """
        # Base TUC (minutes)
        tuc = 60.0
        
        # Pressure factor (low pressure or extreme high pressure reduces TUC)
        if pressure_hpa < 500:
            tuc *= (pressure_hpa / 500)
        elif pressure_hpa > 50000:
            tuc *= 0.1 # Crushing pressure
            
        # Temperature factor
        if temp_k < 100 or temp_k > 500:
            tuc *= 0.2
        elif temp_k < 200 or temp_k > 400:
            tuc *= 0.5
            
        # Biohazard factor
        if "LEVEL 5" in bio_hazard_level:
            tuc *= 0.1
        elif "LEVEL 4" in bio_hazard_level:
            tuc *= 0.4

        # Search patterns
        pattern = "EXPANDING SQUARE"
        if pressure_hpa < 100: # Near vacuum or extreme thin
            pattern = "CREEPING LINE"

        return {
            "tuc_min": round(tuc, 1),
            "pattern": pattern,
            "grid_id": f"XAIP-SAR-{math.ceil(pressure_hpa/100)}",
            "advisory": f"INITIATE IMMEDIATE RESCUE PROTOCOL. LAST KNOWN POSITION RECORDED. TUC ESTIMATED AT {round(tuc, 1)} MINUTES."
        }
