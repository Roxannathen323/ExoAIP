import argparse
import sys
import os
from jinja2 import Environment, FileSystemLoader
from exo_fetcher import ExoFetcher
from aero_physics import AeroPhysics
import logging

def main():
    # Nastavení argumentů příkazové řádky
    parser = argparse.ArgumentParser(description='ExoAIP - Generátor leteckých příruček pro exoplanety.')
    parser.add_argument('planet', type=str, help='Název exoplanety (např. "TRAPPIST-1 e")')
    parser.add_argument('--output', type=str, help='Název výstupního souboru (volitelné)')
    
    args = parser.parse_args()
    planet_name = args.planet
    
    # 1. Stažení dat
    fetcher = ExoFetcher()
    planet_data = fetcher.fetch_planet_data(planet_name)
    
    if not planet_data:
        logging.error(f"Nepodařilo se získat data pro planetu '{planet_name}'. Ukončuji.")
        sys.exit(1)
        
    # 2. Fyzikální výpočty
    physics_engine = AeroPhysics()
    physics_results = physics_engine.process_planet_physics(planet_data)
    
    # 3. Generování HTML (Jinja2)
    try:
        # Nastavení prostředí Jinja2
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('aip_template.html')
        
        # Renderování šablony
        output_html = template.render(
            planet=planet_data,
            physics=physics_results
        )
        
        # 4. Uložení souboru
        if args.output:
            filename = args.output
        else:
            # Vytvoření bezpečného názvu souboru
            safe_name = planet_name.replace(" ", "_").replace("-", "_")
            filename = f"{safe_name}_AIP.html"
            
        with open(filename, "w", encoding="utf-8") as f:
            f.write(output_html)
            
        print(f"\nÚspěch! Letecká příručka byla vygenerována: {filename}")
        print(f"Planeta: {planet_data['name']}")
        print(f"Gravitace: {physics_results['gravity_g']} G")
        print(f"Atmosféra: {physics_results['atmosphere']['type']}")
        
    except Exception as e:
        logging.error(f"Chyba při generování šablony: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
