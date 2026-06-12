import random

class AstroBiologyEngine:
    """
    Advanced Engine for generating probabilistic biosphere reports based on planetary data.
    """

    def analyze_bio_hazard(self, temp_k, radius, atm_type):
        """
        Main analysis entry point. Returns hazard level and a detailed biosphere report.
        """
        is_rocky = radius < 2.0
        is_giant = radius >= 2.0
        
        # 1. Determine Hazard Level
        hazard_level = "LEVEL 2: LOW PROBABILITY"
        quarantine = "STANDARD DECONTAMINATION"
        life_support = "BASIC LIFE SUPPORT (BLS)"

        if is_giant:
            hazard_level = "LEVEL 1: BIO-STERILE (GAS GIANT)"
            quarantine = "NO PLANETARY SURFACE. RADIATION SHIELDING PRIMARY."
            life_support = "CLOSED-LOOP O2. HIGH-PRESSURE SUIT."
        elif 250 <= temp_k <= 350 and is_rocky:
            hazard_level = "LEVEL 4: BIOTIC SIGNATURES DETECTED"
            quarantine = "STRICT QUARANTINE. NO EXTERNAL EXHAUST AUTHORIZED."
            life_support = "CLASS 4 BIO-ISOLATION. CLOSED-LOOP RE-BREATHERS."
        elif temp_k > 400 and is_rocky:
            hazard_level = "LEVEL 5: EXTREME TOXICITY / ACIDIC"
            quarantine = "TOTAL ISOLATION. CORROSIVE ATMOSPHERE HAZARD."
            life_support = "HAZMAT CLASS A. REINFORCED CHASSIS INTEGRITY."
        elif temp_k < 200:
            hazard_level = "LEVEL 3: CRYOGENIC STASIS POTENTIAL"
            quarantine = "LOW ACTIVITY. PREVENT THERMAL CONTAMINATION."
            life_support = "TPS GRADE 5. EXTERNAL HEATING SYSTEMS."

        # 2. Generate Detailed Biosphere Report
        report = self._generate_biosphere_report(temp_k, radius, atm_type, is_rocky, is_giant)

        return {
            "level": hazard_level,
            "quarantine": quarantine,
            "life_support": life_support,
            "biosphere_report": report
        }

    def _generate_biosphere_report(self, temp, radius, atm, is_rocky, is_giant):
        """
        Generates a scientific report of hypothetical life forms.
        """
        if is_giant:
            return (
                "DATA ANALYSIS INDICATES HYPOTHETICAL 'AEROPLANKTON' ECOSYSTEM. "
                "ORGANISMS LIKELY UTILIZE AMMONIA-BASED BIOCHEMISTRY WITHIN UPPER CLOUD LAYERS. "
                "BUOYANCY-DRIVEN LIFE FORMS DETECTED. NO TERRESTRIAL ANALOGS EXIST. "
                "CAUTION: HIGH PROBABILITY OF SYMBIOTIC MICRO-ORGANISMS IN ATMOSPHERIC STREAMS."
            )
        
        if temp > 450:
            return (
                "LITOTROPHIC FAUNA IDENTIFIED. LIFE FORMS LIKELY UTILIZE SILICATE-BASED METABOLISM "
                "FOR RADIATION RESISTANCE. FLORA CONSISTS OF SEMI-CRYSTALLINE STRUCTURES "
                "THRIVING ON GEOTHERMAL VENTS. BIOLOGICAL SIGNATURES INDICATE HIGH CONCENTRATION "
                "OF METAL-OXIDIZING BACTERIA WITHIN SURFACE REGOLITH."
            )
        
        if 250 <= temp <= 350:
            star_type_hint = "RED DWARF SYSTEM DETECTED" # Hypothetical check
            return (
                f"COMPLEX CARBON-BASED ECOSYSTEM DETECTED IN HABITABLE ZONE. "
                "PHOTOSYNTHETIC FLORA EXHIBITS DARK VIOLET/BLACK PIGMENTATION DUE TO STAR SPECTRUM. "
                "SURFACE BIOME INDICATES DENSE LIQUID WATER RESERVOIRS. "
                "DIVERSE FAUNA DETECTED WITH ADVANCED NEURO-SENSORY CAPABILITIES. "
                "HIGH PROBABILITY OF COMPETITIVE SYMBIOSIS BETWEEN MACRO-ORGANISMS."
            )
            
        if temp < 200:
            return (
                "CRYOPHYLLIC BIO-SIGNATURES DETECTED. LIFE LIKELY OPERATES ON LIQUID METHANE/ETHANE "
                "SOLVENT SYSTEM. ORGANISMS EXHIBIT EXTREME METABOLIC SLOWDOWN. "
                "MICROBIAL MATS DETECTED BENEATH SUBSURFACE ICE LAYERS. "
                "HIGH PROBABILITY OF CHEMOAUTOTROPHIC PRIMARY PRODUCERS."
            )

        return "BIOLOGICAL ANALYSIS INCONCLUSIVE. SCANNING FOR NON-TRADITIONAL BIO-SIGNATURES..."

    def generate_sterilization_checklist(self, hazard_level):
        """
        Generates a rigorous scientific sterilization protocol for high-risk biomes.
        """
        if "LEVEL 1" in hazard_level or "LEVEL 2" in hazard_level:
            return []

        protocol = [
            {"id": "THM-01", "task": "INITIATING THERMAL BAKE-OUT AT 500C", "desc": "Total molecular degradation of organic remnants."},
            {"id": "UVC-02", "task": "UV-C IRRADIATION OF CARGO BAY", "desc": "Destroying secondary DNA/RNA structures using 254nm spectrum."},
            {"id": "ACD-03", "task": "ACID BATH FOR EXTERNAL HULL", "desc": "Neutralizing silicate-based lithotrophic spores."},
            {"id": "GAS-04", "task": "ETHYLENE OXIDE DEEP-PURGE", "desc": "Gaseous sterilization of internal avionics and life-support ducts."},
            {"id": "ISO-05", "task": "PLAZMA-SHIELD BIO-CONTAINMENT", "desc": "Active ionization of all atmospheric exhaust ports."}
        ]
        
        if "LEVEL 5" in hazard_level:
            protocol.append({"id": "CRIT-06", "task": "KINETIC IMPACTOR DEPLOYMENT", "desc": "Pre-departure neutralization of landing zone (Scorched Earth Protocol)."})

        return protocol
