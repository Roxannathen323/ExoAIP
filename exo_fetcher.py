from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive
import logging

# Nastavení logování
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class ExoFetcher:
    """
    Třída pro stahování dat o exoplanetách z NASA Exoplanet Archive.
    """

    def __init__(self):
        self.table = "pscomppars"

    def fetch_planet_data(self, planet_name):
        """
        Stáhne data pro konkrétní planetu.
        
        Args:
            planet_name (str): Název exoplanety (např. 'TRAPPIST-1 e').
            
        Returns:
            dict: Slovník s daty o planetě nebo None, pokud planeta nebyla nalezena.
        """
        logging.info(f"Vyhledávám data pro planetu: {planet_name}...")
        
        try:
            # Dotaz na NASA Exoplanet Archive
            # Používáme tabulku 'pscomppars' (Planetary Systems Composite Parameters)
            res = NasaExoplanetArchive.query_criteria(
                table=self.table,
                where=f"pl_name = '{planet_name}'"
            )
            
            if len(res) == 0:
                logging.warning(f"Planeta '{planet_name}' nebyla v archivu nalezena.")
                return None
            
            # Převedeme první řádek výsledku na slovník
            data = {
                'name': res['pl_name'][0],
                'hostname': res['hostname'][0],
                'mass': res['pl_bmasse'][0],      # Hmotnost v jednotkách Země
                'radius': res['pl_rade'][0],    # Poloměr v jednotkách Země
                'temp_eq': res['pl_eqt'][0],      # Rovnovážná teplota [K]
                'st_teff': res['st_teff'][0],     # Efektivní teplota hvězdy [K]
                'semi_major_axis': res['pl_orbsmax'][0], # Velká poloosa [AU]
                'disc_year': res['disc_year'][0]  # Rok objevu
            }
            
            # Kontrola kritických dat
            critical_fields = ['mass', 'radius']
            missing = [f for f in critical_fields if data[f] is None or str(data[f]) == '--' or str(data[f]) == 'nan']
            
            if missing:
                logging.error(f"Pro planetu '{planet_name}' chybí kritická data: {', '.join(missing)}")
                return None
                
            return data

        except Exception as e:
            logging.error(f"Chyba při komunikaci s NASA Archive: {e}")
            return None

if __name__ == "__main__":
    # Testovací kód
    fetcher = ExoFetcher()
    test_planet = "TRAPPIST-1 e"
    data = fetcher.fetch_planet_data(test_planet)
    if data:
        print(f"Data pro {test_planet}: {data}")
