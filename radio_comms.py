import random

class RadioCommsEngine:
    """
    Engine for generating ICAO-standard radio transcripts based on planetary conditions.
    """

    def generate_transcript(self, planet_name, gravity_g, temp_k, bio_hazard_level, blackout_sec):
        """
        Creates a dynamic dialogue between Orbital Control and Exo-1.
        """
        controller = "ORBITAL CONTROL"
        pilot = "EXO-1"
        
        # Standard establishment
        transcript = [
            f"{pilot}: {controller}, {pilot}, established on intercept course for {planet_name.upper()}.",
            f"{controller}: {pilot}, {controller}, Roger. Descend to FL150, QNH 1013."
        ]

        # FIR Handover
        transcript.append(f"{controller}: {pilot}, contact Deep Space Control on 121.5. G-day.")
        transcript.append(f"{pilot}: Switching to 121.5, {pilot} out.")
        
        # Blackout Warning
        transcript.append(f"SYSTEM: WARNING - IONIZATION DETECTED. ENTERING PLASMA BLACKOUT.")
        transcript.append(f"SYSTEM: ESTIMATED DURATION: {blackout_sec} SECONDS.")
        
        # Condition-based dialogue (post-blackout simulation)
        transcript.append(f"{pilot}: DEEP SPACE CONTROL, {pilot} established on descent. Radio check.")
        transcript.append(f"{controller}: {pilot}, DEEP SPACE, loud and clear. Continue approach.")

        if gravity_g > 1.5:
            transcript.append(f"{pilot}: Copy FL150. Warning: Detecting high G-load. Structural integrity at 82%.")
            transcript.append(f"{controller}: {pilot}, understood. Structural limit exceeded. Suggest steep entry profile.")
        
        if "LEVEL 4" in bio_hazard_level or "LEVEL 5" in bio_hazard_level:
            transcript.append(f"{controller}: {pilot}, maintain strict quarantine altitude. Do not descend below FL100 until bio-scan complete.")
            transcript.append(f"{pilot}: {pilot} copy. Clas-4 bio-isolation active. Closed-loop life support online.")

        if temp_k < 200:
            transcript.append(f"{pilot}: {controller}, encountering severe icing. Requesting higher speed for thermal friction.")
            transcript.append(f"{controller}: {pilot}, approved as requested. Maintain V-max until boundary layer stabilization.")
        elif temp_k > 350:
            transcript.append(f"{pilot}: {pilot} reporting extreme thermal radiation. Heat shield degradation at 15%.")
            transcript.append(f"{controller}: {pilot}, copy. Accelerated descent authorized. Aim for night-side touchdown.")

        # Standard closing
        transcript.append(f"{controller}: {pilot}, contact Approach on 121.5. Good luck.")
        transcript.append(f"{pilot}: Contacting Approach, 121.5. {pilot} out.")

        return transcript
