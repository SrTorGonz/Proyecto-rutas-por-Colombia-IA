import tkinter as tk
from tkinter import ttk
import json
import math
from queue import PriorityQueue
import folium
from folium.plugins import MousePosition
from PIL import Image, ImageTk, ImageEnhance
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# Coordenadas de las capitales
coordenadas = {
    'Leticia': (-4.2129211, -69.9425963),
    'Medellín': (6.269732449999999, -75.60255965090315),
    'Arauca': (6.6666755, -71.0000086),
    'Barranquilla': (11.0101922, -74.8231794084391),
    'Cartagena de Indias': (10.4265566, -75.5441671),
    'Tunja': (5.5324313, -73.3616014),
    'Manizales': (5.0743694, -75.50811667440546),
    'Florencia': (1.6158666, -75.6143045),
    'Yopal': (5.3356662, -72.3936931),
    'Popayán': (2.4422295, -76.6072368),
    'Valledupar': (10.34311145, -73.37579338828454),
    'Quibdó': (5.6923407, -76.6583801),
    'Montería': (8.6046053, -75.97832027208273),
    'Bogotá': (4.6533816, -74.0836333),
    'Inírida': (3.8650368, -67.9259848),
    'San José del Guaviare': (2.5716141, -72.6426515),
    'Neiva': (2.9257038, -75.2893937),
    'Riohacha': (11.236191300000002, -72.88204560476245),
    'Santa Marta': (11.2320944, -74.1950916),
    'Villavicencio': (4.1347644, -73.6201517),
    'Pasto': (1.2140275, -77.2785096),
    'San José de Cúcuta': (8.07761875, -72.46890019811272),
    'Mocoa': (1.1466295, -76.6482327),
    'Armenia': (4.491976149999999, -75.74135085294314),
    'Pereira': (4.7854606, -75.7883220137654),
    'San Andrés': (12.537597850000001, -81.72041550499901),
    'Bucaramanga': (7.16698415, -73.1047294009737),
    'Sincelejo': (9.2973386, -75.3926601),
    'Ibagué': (4.4386033, -75.2108857),
    'Cali': (3.4519988, -76.5325259),
    'Mitú': (1.2538499, -70.2345576),
    'Puerto Carreño': (6.1909225, -67.4841891)
}

class MapaInteractivo(tk.Frame):
    def __init__(self, parent, datos_conexiones, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.datos = datos_conexiones
        self.setup_selenium()
        self.setup_ui()
        self.setup_mapa_base()
        
    def setup_selenium(self):
        """Configuración optimizada para máxima calidad visual"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=850,850")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--force-device-scale-factor=1.5")
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def setup_ui(self):
        """Configuración de la interfaz gráfica"""
        self.browser_frame = ttk.Frame(self)
        self.browser_frame.pack(fill=tk.BOTH, expand=True)
        self.label = tk.Label(self.browser_frame)
        self.label.pack(fill=tk.BOTH, expand=True)
    
    def setup_mapa_base(self):
        """Crea el mapa base con zoom y área ajustados para Colombia completa"""
        self.mapa = folium.Map(
            location=[4.0, -74.0],
            zoom_start=5.8,
            tiles='OpenStreetMap',
            control_scale=True,
            width='850px',
            height='850px',
            prefer_canvas=True,
            zoom_control=False
        )
        
        # CSS para eliminar scrollbars y mejorar renderizado
        self.mapa.get_root().html.add_child(folium.Element("""
            <style>
                body { margin: 0; padding: 0; overflow: hidden; }
                html { overflow: hidden; }
                .leaflet-container { 
                    overflow: hidden !important; 
                    background-color: white !important;
                }
            </style>
        """))
        
        MousePosition().add_to(self.mapa)
        self._add_base_elements()
        self._capture_and_show_map()
    
    def _add_base_elements(self):
        """Añade elementos al mapa con colores vibrantes y máxima opacidad"""
        # Conexiones base
        for ciudad, conexiones in self.datos['conexiones'].items():
            if ciudad in coordenadas:
                for destino, distancia in conexiones.items():
                    if destino in coordenadas:
                        folium.PolyLine(
                            locations=[coordenadas[ciudad], coordenadas[destino]],
                            color='#E67E22',
                            weight=4.5,
                            opacity=1.0,
                            line_cap='round',
                            tooltip=f"{ciudad} - {destino}: {distancia} km"
                        ).add_to(self.mapa)
        
        # Marcadores base
        for ciudad, (lat, lon) in coordenadas.items():
            folium.CircleMarker(
                location=[lat, lon],
                radius=7.5,
                popup=ciudad,
                color='#E74C3C',
                fill=True,
                fill_color='#E74C3C',
                fill_opacity=1.0,
                stroke=True,
                weight=1.5
            ).add_to(self.mapa)
        
        # Ajustar vista específicamente para Colombia
        self._ajustar_vista_colombia()
    
    def _ajustar_vista_colombia(self):
        """Ajuste preciso para mostrar toda Colombia sin cortes"""
        bounds = [
            [-4.3, -79.2],  # Punto más al suroeste (Leticia)
            [12.6, -66.8]   # Punto más al noreste (Punta Gallinas)
        ]
        self.mapa.fit_bounds(bounds, padding=(20, 20))
    
    def _capture_and_show_map(self):
        """Captura el mapa con alta calidad y ajustes precisos"""
        temp_html = 'temp_map.html'
        self.mapa.save(temp_html)
        
        with open(temp_html, 'a') as f:
            f.write("""
            <style>
                body { background-color: white !important; }
                .leaflet-container { background: white !important; }
            </style>
            <script>
                setTimeout(function() {
                    window.scrollTo(0, 0);
                }, 1000);
            </script>
            """)
        
        self.driver.get(f"file:///{os.path.abspath(temp_html)}")
        WebDriverWait(self.driver, 5).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(1.5)
        
        temp_png = 'temp_map.png'
        self.driver.save_screenshot(temp_png)
        
        img = Image.open(temp_png)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
        img = img.resize((800, 800), Image.LANCZOS)
        
        img_tk = ImageTk.PhotoImage(img)
        
        self.label.config(image=img_tk)
        self.label.image = img_tk
        
        os.remove(temp_html)
        os.remove(temp_png)
    
    def mostrar_ruta(self, ruta):
        """Muestra la ruta completa sin cortes con zoom ajustado"""
        if not ruta or len(ruta) < 2:
            return
            
        # Crear mapa temporal
        temp_map = folium.Map(
            location=[5.0, -74.0],
            zoom_start=5.5,
            tiles='OpenStreetMap',
            width='850px',
            height='850px',
            prefer_canvas=True,
            min_zoom=4,
            max_zoom=12,
            max_bounds=True,
            bounds=[[-4.5, -82.0], [13.0, -66.0]]
        )
        
        # CSS para mejor visualización
        temp_map.get_root().html.add_child(folium.Element("""
            <style>
                .leaflet-container { 
                    background: white !important;
                    overflow: hidden !important;
                }
            </style>
        """))
        
        # Añadir elementos base con opacidad reducida
        self._add_base_elements_to_map(temp_map)
        
        # Obtener coordenadas de la ruta
        puntos_ruta = [coordenadas[ciudad] for ciudad in ruta if ciudad in coordenadas]
        
        # Añadir ruta resaltada
        folium.PolyLine(
            locations=puntos_ruta,
            color='#2980B9',
            weight=6.5,
            opacity=1.0,
            line_cap='round',
            tooltip="Ruta encontrada"
        ).add_to(temp_map)
        
        # Añadir marcadores especiales para la ruta
        for ciudad in ruta:
            if ciudad in coordenadas:
                folium.CircleMarker(
                    location=coordenadas[ciudad],
                    radius=9,
                    popup=ciudad,
                    color='#27AE60',
                    fill=True,
                    fill_color='#27AE60',
                    fill_opacity=1.0,
                    stroke=True,
                    weight=2
                ).add_to(temp_map)
        
        # Calcular los límites óptimos para la ruta
        self._ajustar_vista_ruta(temp_map, puntos_ruta)
        
        # Capturar y mostrar el mapa
        self._capture_and_show_temp_map(temp_map)
    
    def _ajustar_vista_ruta(self, mapa, puntos_ruta):
        """Ajuste de vista mejorado que garantiza que la ruta nunca se corte"""
        if not puntos_ruta or len(puntos_ruta) < 2:
            return

        # Calcular los límites geográficos de la ruta
        lats = [p[0] for p in puntos_ruta]
        lons = [p[1] for p in puntos_ruta]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Calcular la extensión de la ruta
        lat_span = max_lat - min_lat
        lon_span = max_lon - min_lon
        
        # Asegurar un mínimo de extensión para evitar zoom excesivo
        min_span = 3.0  # Aumentado a 3 grados
        lat_span = max(lat_span, min_span)
        lon_span = max(lon_span, min_span)
        
        # Padding dinámico basado en la extensión de la ruta
        padding_factor = 0.35  # Aumentado a 35% de padding
        
        # Aplicar padding
        south = min_lat - (lat_span * padding_factor)
        north = max_lat + (lat_span * padding_factor)
        west = min_lon - (lon_span * padding_factor)
        east = max_lon + (lon_span * padding_factor)
        
        # Asegurar que no nos salgamos de los límites de Colombia
        south = max(south, -4.5)
        north = min(north, 13.0)
        west = max(west, -82.0)
        east = min(east, -66.0)
        
        # Ajustar relación de aspecto para que se adapte mejor a la ventana
        window_aspect = 1.0
        route_aspect = lon_span / lat_span
        
        if route_aspect > window_aspect:
            # Ruta más ancha que alta
            desired_lon_span = lon_span
            desired_lat_span = desired_lon_span / window_aspect
            delta_lat = (desired_lat_span - lat_span) / 2
            south = max(south - delta_lat, -4.5)
            north = min(north + delta_lat, 13.0)
        else:
            # Ruta más alta que ancha
            desired_lat_span = lat_span
            desired_lon_span = desired_lat_span * window_aspect
            delta_lon = (desired_lon_span - lon_span) / 2
            west = max(west - delta_lon, -82.0)
            east = min(east + delta_lon, -66.0)
        
        # Aplicar los nuevos límites con padding adicional
        mapa.fit_bounds([[south, west], [north, east]], padding=(30, 30))
    
    def _add_base_elements_to_map(self, map_obj):
        """Añade elementos base con opacidad reducida"""
        for ciudad, conexiones in self.datos['conexiones'].items():
            if ciudad in coordenadas:
                for destino, distancia in conexiones.items():
                    if destino in coordenadas:
                        folium.PolyLine(
                            locations=[coordenadas[ciudad], coordenadas[destino]],
                            color='#E67E22',
                            weight=3.5,
                            opacity=0.7
                        ).add_to(map_obj)
        
        for ciudad, (lat, lon) in coordenadas.items():
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                popup=ciudad,
                color='#E74C3C',
                fill=True,
                fill_opacity=0.7
            ).add_to(map_obj)
    
    def _capture_and_show_temp_map(self, temp_map):
        """Captura el mapa temporal con alta calidad"""
        temp_html = 'temp_ruta.html'
        temp_map.save(temp_html)
        
        with open(temp_html, 'a') as f:
            f.write("""
            <style>
                body { background: white !important; }
            </style>
            <script>
                setTimeout(function() {
                    window.scrollTo(0, 0);
                }, 1500);
            </script>
            """)
        
        self.driver.get(f"file:///{os.path.abspath(temp_html)}")
        WebDriverWait(self.driver, 5).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(2)
        
        temp_png = 'temp_ruta.png'
        self.driver.save_screenshot(temp_png)
        
        img = Image.open(temp_png)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
        img = img.resize((800, 800), Image.LANCZOS)
        
        img_tk = ImageTk.PhotoImage(img)
        
        self.label.config(image=img_tk)
        self.label.image = img_tk
        
        os.remove(temp_html)
        os.remove(temp_png)
    
    def reiniciar_vista(self):
        """Restablece la vista inicial enfocada en Colombia"""
        self.setup_mapa_base()

class MapaColombiaConBusqueda:
    def __init__(self, root):
        self.root = root
        self.root.title("Rutas por Colombia - Versión Definitiva HD")
        self.root.geometry("1250x900")
        
        with open('conexiones.json', 'r', encoding='utf-8') as f:
            self.datos = json.load(f)
        
        self.ciudades_ordenadas = sorted(self.datos['capitales'])
        self.heuristic_cache = {}
        
        self._setup_ui()
        self._precompute_grafo()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario con texto negro en botones"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Frame del mapa
        map_frame = ttk.LabelFrame(self.main_frame, text="Mapa de Colombia", padding=10)
        map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.map_frame = MapaInteractivo(map_frame, self.datos)
        self.map_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel de control
        control_frame = ttk.LabelFrame(self.main_frame, text="Controles", width=350, padding=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Selectores de ciudades
        cities_frame = ttk.Frame(control_frame)
        cities_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(cities_frame, text="Ciudad Origen:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.ciudad_inicial = ttk.Combobox(cities_frame, values=self.ciudades_ordenadas, state='readonly')
        self.ciudad_inicial.pack(fill=tk.X, pady=5)
        
        ttk.Label(cities_frame, text="Ciudad Destino:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.ciudad_destino = ttk.Combobox(cities_frame, values=self.ciudades_ordenadas, state='readonly')
        self.ciudad_destino.pack(fill=tk.X, pady=5)
        
        # Botones de búsqueda con texto negro
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=15)
        
        style = ttk.Style()
        style.configure('Black.TButton', foreground='black', font=('Arial', 10, 'bold'))
        
        ttk.Button(btn_frame, text="Búsqueda Voraz", 
                  command=self.busqueda_voraz, style='Black.TButton').pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Búsqueda A*", 
                  command=self.busqueda_a_estrella, style='Black.TButton').pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Reiniciar Mapa", 
                  command=self.reiniciar_vista, style='Black.TButton').pack(fill=tk.X, pady=5)
        
        # Panel de información
        info_frame = ttk.LabelFrame(control_frame, text="Resultados", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_label = ttk.Label(info_frame, text="Seleccione ciudades y algoritmo", 
                                  wraplength=300, justify=tk.LEFT, font=('Arial', 10))
        self.info_label.pack(fill=tk.BOTH, expand=True)
    
    def _precompute_grafo(self):
        """Precomputa el grafo para búsquedas rápidas"""
        self.grafo = {}
        for ciudad, conexiones in self.datos['conexiones'].items():
            self.grafo[ciudad] = list(conexiones.items())
    
    def distancia_heuristic(self, ciudad1, ciudad2):
        """Distancia heurística con caché"""
        cache_key = (ciudad1, ciudad2)
        if cache_key not in self.heuristic_cache:
            lat1, lon1 = coordenadas[ciudad1]
            lat2, lon2 = coordenadas[ciudad2]
            self.heuristic_cache[cache_key] = math.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 100
        return self.heuristic_cache[cache_key]
    
    def busqueda_voraz(self):
        """Búsqueda voraz optimizada"""
        inicio = self.ciudad_inicial.get()
        destino = self.ciudad_destino.get()
        
        if not inicio or not destino:
            self.info_label.config(text="Seleccione ambas ciudades")
            return
        
        start_time = time.time()
        
        cola = PriorityQueue()
        cola.put((0, inicio, [inicio], 0))
        visitados = set()
        
        while not cola.empty():
            _, actual, ruta, distancia = cola.get()
            
            if actual == destino:
                self._mostrar_resultado(ruta, distancia, "Voraz", start_time)
                return
            
            if actual not in visitados:
                visitados.add(actual)
                
                for vecino, dist in self.grafo.get(actual, []):
                    if vecino not in visitados:
                        heuristica = self.distancia_heuristic(vecino, destino)
                        cola.put((heuristica, vecino, ruta + [vecino], distancia + dist))
        
        self.info_label.config(text="No se encontró ruta")
    
    def busqueda_a_estrella(self):
        """Búsqueda A* optimizada"""
        inicio = self.ciudad_inicial.get()
        destino = self.ciudad_destino.get()
        
        if not inicio or not destino:
            self.info_label.config(text="Seleccione ambas ciudades")
            return
        
        start_time = time.time()
        
        cola = PriorityQueue()
        cola.put((0, inicio, [inicio], 0))
        visitados = set()
        
        while not cola.empty():
            _, actual, ruta, costo_real = cola.get()
            
            if actual == destino:
                self._mostrar_resultado(ruta, costo_real, "A*", start_time)
                return
            
            if actual not in visitados:
                visitados.add(actual)
                
                for vecino, dist in self.grafo.get(actual, []):
                    if vecino not in visitados:
                        nuevo_costo = costo_real + dist
                        heuristica = self.distancia_heuristic(vecino, destino)
                        cola.put((
                            nuevo_costo + heuristica,
                            vecino,
                            ruta + [vecino],
                            nuevo_costo
                        ))
        
        self.info_label.config(text="No se encontró ruta")
    
    def _mostrar_resultado(self, ruta, distancia, algoritmo, start_time):
        """Muestra los resultados con formato mejorado"""
        elapsed = time.time() - start_time
        self.map_frame.mostrar_ruta(ruta)
        
        info_text = (
            f"⚡ Ruta encontrada ({algoritmo})\n"
            f"📍 {' → '.join(ruta)}\n"
            f"📏 Distancia: {distancia:.1f} km\n"
        )
        self.info_label.config(text=info_text, font=('Arial', 10))
    
    def reiniciar_vista(self):
        """Reinicia la vista inicial"""
        self.map_frame.reiniciar_vista()
        self.info_label.config(text="Mapa reiniciado. Seleccione ciudades y algoritmo.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MapaColombiaConBusqueda(root)
    root.mainloop()