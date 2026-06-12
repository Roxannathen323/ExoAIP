import os
import json
import threading
import logging
import io
from flask import Flask, render_template, request, jsonify, send_file
from exo_fetcher import ExoFetcher
from aero_physics import AeroPhysics
from extraterrestrica_bio import AstroBiologyEngine
from vac_generator import VACGenerator
from radio_comms import RadioCommsEngine
from exo_weather import ExoWeatherEngine
from pulseway_nav import PulseWayNav
from space_weather import SpaceWeatherEngine
from exo_loadsheet import ExoLoadsheet
from sar_operations import SAROperations
from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive

# Nastavení logování
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

app = Flask(__name__)

# Cesta k mezipaměti planet
CACHE_FILE = 'planets_cache.json'
planets_list = []

def load_planets_cache():
    """
    Načte seznam planet z JSON souboru nebo jej stáhne z NASA, pokud neexistuje.
    """
    global planets_list
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                planets_list = json.load(f)
            logging.info(f"Načteno {len(planets_list)} planet z lokální mezipaměti.")
        except Exception as e:
            logging.error(f"Chyba při čtení mezipaměti: {e}")
            fetch_and_cache_planets()
    else:
        fetch_and_cache_planets()

def fetch_and_cache_planets():
    """
    Stáhne seznam všech jmen planet z NASA Exoplanet Archive a uloží do JSON.
    """
    global planets_list
    logging.info("Stahuji seznam planet z NASA (toto může trvat několik sekund)...")
    try:
        # Dotaz pouze na jména planet pro rychlost
        res = NasaExoplanetArchive.query_criteria(table="pscomppars", select="pl_name")
        planets_list = sorted([str(name) for name in res['pl_name']])
        
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(planets_list, f, ensure_ascii=False)
        
        logging.info(f"Seznam planet ({len(planets_list)}) byl úspěšně stažen a uložen.")
    except Exception as e:
        logging.error(f"Chyba při stahování seznamu planet: {e}")

# Spustíme načítání/stahování v samostatném vlákně, aby server hned naskočil
threading.Thread(target=load_planets_cache, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify([])
    
    # Filtrování seznamu (max 10 výsledků)
    results = [p for p in planets_list if query in p.lower()][:10]
    return jsonify(results)

@app.route('/generate')
def generate():
    planet_name = request.args.get('planet')
    if not planet_name:
        return "Chybí název planety", 400
    
    fetcher = ExoFetcher()
    physics_engine = AeroPhysics()
    
    planet_data = fetcher.fetch_planet_data(planet_name)
    if not planet_data:
        return f"Data pro planetu '{planet_name}' nebyla nalezena.", 404
    
    physics_results = physics_engine.process_planet_physics(planet_data)
    
    # --- Astrobiology Module ---
    bio_engine = AstroBiologyEngine()
    # Sanitize inputs to float (handles astropy quantities/masked arrays)
    temp_val = float(physics_results['atmosphere']['temp_k'])
    radius_val = float(planet_data['radius'].value) if hasattr(planet_data['radius'], 'value') else float(planet_data['radius'])

    bio_hazard = bio_engine.analyze_bio_hazard(
        temp_val,
        radius_val,
        physics_results['atmosphere']['type']
    )
    
    # --- Map Generator ---
    # Create unique path for the map to avoid concurrency issues
    map_filename = f"vac_{planet_name.replace(' ', '_')}.png"
    map_path = os.path.join('static', 'maps', map_filename)
    VACGenerator.generate_map(planet_name, physics_results['archetype'], map_path)
    heightmap = VACGenerator.generate_heightmap(planet_name, physics_results['archetype'])
    
    # --- Weather & VOLMET ---
    weather_engine = ExoWeatherEngine()
    weather_data = weather_engine.generate_weather(
        physics_results['atmosphere']['temp_k'],
        physics_results['atmosphere']['pressure_hpa'],
        physics_results['atmosphere']['type'],
        physics_results['archetype']
    )
    volmet_text = weather_engine.generate_volmet(planet_name, weather_data)
    metar, taf = weather_engine.generate_metar_taf(weather_data, physics_results['archetype'])

    # --- Re-entry Profile ---
    reentry = physics_engine.calculate_reentry_profile(
        physics_results['atmosphere']['density_kgm3'],
        physics_results['gravity_g'],
        planet_data['radius']
    )
    blackout_sec = physics_engine.calculate_blackout_period(
        physics_results['v_escape_ms'],
        physics_results['gravity_g']
    )
    
    # --- Space Weather ---
    space_weather_engine = SpaceWeatherEngine()
    space_weather = space_weather_engine.analyze_space_weather(planet_data['st_teff'])
    
    # --- PulseWay RNAV ---
    nav_engine = PulseWayNav()
    nav_log = nav_engine.generate_navlog(planet_name, space_weather['status'])
    
    # --- Load & Balance ---
    loadsheet_engine = ExoLoadsheet()
    loadsheet = loadsheet_engine.calculate_loadsheet(physics_results['gravity_g'])
    
    # --- SAR Operations ---
    sar_engine = SAROperations()
    sar_plan = sar_engine.calculate_sar_plan(
        physics_results['atmosphere']['pressure_hpa'],
        physics_results['atmosphere']['temp_k'],
        bio_hazard['level']
    )

    # --- Decontamination Protocol ---
    sterilization_checklist = bio_engine.generate_sterilization_checklist(bio_hazard['level'])
    
    # --- Comms Shadow Detection ---
    is_locked = physics_engine.is_tidally_locked(planet_data)

    # Update Transcript with blackout
    comms_engine = RadioCommsEngine()
    transcript = comms_engine.generate_transcript(
        planet_name,
        physics_results['gravity_g'],
        physics_results['atmosphere']['temp_k'],
        bio_hazard['level'],
        blackout_sec
    )

    return render_template('aip_template.html', 
                           planet=planet_data, 
                           physics=physics_results,
                           bio=bio_hazard,
                           map_url=f"/static/maps/{map_filename}",
                           transcript=transcript,
                           volmet=volmet_text,
                           metar=metar,
                           taf=taf,
                           reentry=reentry,
                           space_weather=space_weather,
                           nav=nav_log,
                           loadsheet=loadsheet,
                           sar=sar_plan,
                           blackout_sec=blackout_sec,
                           sterilization=sterilization_checklist,
                           is_locked=is_locked,
                           heightmap=heightmap)

@app.route('/api/fpl/validate', methods=['POST'])
def validate_fpl():
    data = request.json
    mass = float(data.get('mass', 0))
    dv = float(data.get('dv', 0))
    planet_name = data.get('planet')
    deploy_relay = data.get('relay') == True
    
    fetcher = ExoFetcher()
    planet_data = fetcher.fetch_planet_data(planet_name)
    if not planet_data:
        return jsonify({"status": "REJ", "reason": "PLANETARY DATA LINK LOST"}), 404
        
    physics_engine = AeroPhysics()
    physics = physics_engine.process_planet_physics(planet_data)
    
    # Check Tidally Locked status
    is_locked = physics_engine.is_tidally_locked(planet_data)
    
    # If locked, relay is mandatory
    if is_locked and not deploy_relay:
        return jsonify({
            "status": "REJ",
            "reason": "COMMS SHADOW DETECTED: TIDALLY LOCKED SYSTEM. DEPLOY RELAY SATELLITE MANDATORY."
        })
    
    # If relay deployed, add 500kg to mass
    total_mass = mass + (500 if deploy_relay else 0)
    
    # Escape velocity in m/s
    v_esc_ms = physics['v_escape_ms']
    
    # Local Landing Weight check (using loadsheet logic)
    g_val = physics['gravity_g'] * 9.80665
    local_weight_kn = (total_mass * g_val) / 1000.0
    
    if local_weight_kn > 150.0:
        return jsonify({
            "status": "REJ",
            "reason": f"STRUCTURAL FAILURE IMMINENT: MAX ALLOWABLE LANDING WEIGHT EXCEEDED. CALC: {round(local_weight_kn, 1)} KN / LIMIT: 150.0 KN"
        })

    # Simple validation logic
    if dv < v_esc_ms:
        return jsonify({
            "status": "REJ",
            "reason": f"INSUFFICIENT DELTA-V FOR ASCENT. REQUIRED: {v_esc_ms} M/S. PROVIDED: {dv} M/S."
        })
    elif dv < v_esc_ms * 1.5:
        return jsonify({
            "status": "ACK",
            "reason": "CLEARED WITH MARGINAL FUEL RESERVES. CAUTION ADVISED."
        })
    else:
        return jsonify({
            "status": "ACK",
            "reason": "FPL CLEARED. NOMINAL MISSION PARAMETERS DETECTED."
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
