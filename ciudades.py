import tkinter as tk
from tkinter import ttk
import json
import math
from queue import PriorityQueue
import folium
from folium.plugins import MousePosition
from PIL import Image, ImageTk
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        
        # Configurar Selenium
        self.setup_selenium()
        
        # Crear contenedor para el mapa
        self.browser_frame = ttk.Frame(self)
        self.browser_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mapa inicial
        self.mapa = None
        self.zoom_level = 6
        self.map_center = [4.5709, -74.2973]
        self.create_map()
    
    def setup_selenium(self):
        """Configurar Selenium para capturar el mapa"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=700,700")
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def create_map(self):
        """Crear un nuevo mapa con la configuración actual"""
        self.mapa = folium.Map(
            location=self.map_center,
            zoom_start=self.zoom_level,
            tiles='OpenStreetMap',
            control_scale=True,
            width='100%',
            height='100%'
        )
        
        # Añadir controles de posición del mouse
        MousePosition().add_to(self.mapa)
        self.update_map()
    
    def update_map(self):
        """Actualizar la visualización del mapa"""
        temp_html = os.path.abspath('temp_map.html')
        self.mapa.save(temp_html)
        
        self.driver.get(f"file:///{temp_html}")
        time.sleep(1.5)
        
        temp_png = os.path.abspath('temp_map.png')
        self.driver.save_screenshot(temp_png)
        
        # Mostrar la imagen en el frame
        for widget in self.browser_frame.winfo_children():
            widget.destroy()
        
        img = Image.open(temp_png)
        img = img.resize((700, 700), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        
        label = tk.Label(self.browser_frame, image=img_tk)
        label.image = img_tk
        label.pack(fill=tk.BOTH, expand=True)
        
        try:
            os.remove(temp_html)
            os.remove(temp_png)
        except:
            pass
    
    def reset_view(self):
        """Resetear la vista al zoom y posición inicial"""
        self.zoom_level = 6
        self.map_center = [4.5709, -74.2973]
        self.create_map()

class MapaColombiaConBusqueda:
    def __init__(self, root):
        self.root = root
        self.root.title("Rutas por Colombia con Algoritmos de Búsqueda")
        self.root.geometry("1100x800")
        
        # Cargar datos del JSON
        with open('conexiones.json', 'r', encoding='utf-8') as f:
            self.datos = json.load(f)
        
        # Ordenar las ciudades alfabéticamente
        self.ciudades_ordenadas = sorted(self.datos['capitales'])
        
        # Frame principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para el mapa interactivo
        self.map_frame = MapaInteractivo(self.main_frame)
        self.map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame para controles (derecha)
        self.control_frame = ttk.Frame(self.main_frame, width=300)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Selectores de ciudades (ordenados alfabéticamente)
        ttk.Label(self.control_frame, text="Ciudad Inicial:", font=('Arial', 10, 'bold')).pack(pady=(20,5))
        self.ciudad_inicial = ttk.Combobox(self.control_frame, values=self.ciudades_ordenadas, state='readonly')
        self.ciudad_inicial.pack(fill=tk.X, padx=10)
        
        ttk.Label(self.control_frame, text="Ciudad Destino:", font=('Arial', 10, 'bold')).pack(pady=(20,5))
        self.ciudad_destino = ttk.Combobox(self.control_frame, values=self.ciudades_ordenadas, state='readonly')
        self.ciudad_destino.pack(fill=tk.X, padx=10)
        
        # Botones de búsqueda
        ttk.Button(self.control_frame, text="Búsqueda Voraz", command=self.busqueda_voraz).pack(pady=(30,10), fill=tk.X, padx=10)
        ttk.Button(self.control_frame, text="Búsqueda A*", command=self.busqueda_a_estrella).pack(pady=10, fill=tk.X, padx=10)
        ttk.Button(self.control_frame, text="Limpiar Ruta", command=self.limpiar_ruta).pack(pady=10, fill=tk.X, padx=10)
        
        # Área de información
        self.info_label = ttk.Label(self.control_frame, text="Seleccione ciudades y algoritmo", wraplength=280)
        self.info_label.pack(pady=(30,10), fill=tk.X, padx=10)
        
        # Variables para el seguimiento de elementos
        self.ruta_actual = None
        self.elementos_ruta = []
        
        # Mostrar el mapa inicial con conexiones
        self.mostrar_mapa_inicial()
    
    def limpiar_ruta_actual(self):
        """Elimina completamente la ruta actual del mapa"""
        for elemento in self.elementos_ruta:
            if elemento in self.map_frame.mapa._children:
                del self.map_frame.mapa._children[elemento]
        self.elementos_ruta = []
        self.ruta_actual = None
    
    def mostrar_mapa_inicial(self):
        """Muestra el mapa completo con todas las conexiones base"""
        self.limpiar_ruta_actual()
        
        # Limpiar elementos existentes
        for item in list(self.map_frame.mapa._children.keys()):
            if item.startswith('poly_line') or item.startswith('circle_marker'):
                del self.map_frame.mapa._children[item]
        
        # Restablecer vista
        self.map_frame.reset_view()
        
        # Añadir conexiones base (color gris medio, grosor fino)
        for ciudad, conexiones in self.datos['conexiones'].items():
            if ciudad in coordenadas:
                for destino, distancia in conexiones.items():
                    if destino in coordenadas:
                        folium.PolyLine(
                            locations=[coordenadas[ciudad], coordenadas[destino]],
                            color='#997a16', 
                            weight=3,        # Grosor fino
                            opacity=0.8,
                            tooltip=f"{ciudad} - {destino}: {distancia} km"
                        ).add_to(self.map_frame.mapa)
        
        # Añadir marcadores base (rojos)
        for ciudad, (lat, lon) in coordenadas.items():
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                popup=ciudad,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=1
            ).add_to(self.map_frame.mapa)
        
        # Ajustar vista para mostrar todo Colombia
        lats = [coord[0] for coord in coordenadas.values()]
        lons = [coord[1] for coord in coordenadas.values()]
        self.map_frame.mapa.fit_bounds([(min(lats)-1, min(lons)-1), (max(lats)+1, max(lons)+1)])
        self.map_frame.update_map()
    
    def distancia_entre_ciudades(self, ciudad1, ciudad2):
        """Calcular distancia entre dos ciudades (si están conectadas)"""
        if ciudad1 in self.datos['conexiones'] and ciudad2 in self.datos['conexiones'][ciudad1]:
            return self.datos['conexiones'][ciudad1][ciudad2]
        elif ciudad2 in self.datos['conexiones'] and ciudad1 in self.datos['conexiones'][ciudad2]:
            return self.datos['conexiones'][ciudad2][ciudad1]
        return None
    
    def distancia_heuristic(self, ciudad1, ciudad2):
        """Distancia en línea recta entre ciudades usando coordenadas"""
        lat1, lon1 = coordenadas[ciudad1]
        lat2, lon2 = coordenadas[ciudad2]
        return math.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 100  # Factor de escala
    
    def busqueda_voraz(self):
        """Implementación de búsqueda voraz (primero el mejor)"""
        inicio = self.ciudad_inicial.get()
        destino = self.ciudad_destino.get()
        
        if not inicio or not destino:
            self.info_label.config(text="Seleccione ambas ciudades")
            return
        
        cola_prioridad = PriorityQueue()
        cola_prioridad.put((0, inicio, [inicio], 0))  # (heurística, ciudad, ruta, distancia_acumulada)
        visitados = set()
        
        while not cola_prioridad.empty():
            _, ciudad_actual, ruta, distancia_acum = cola_prioridad.get()
            
            if ciudad_actual == destino:
                self.ruta_actual = ruta
                self.mostrar_ruta(ruta)
                self.info_label.config(text=f"Ruta encontrada (Voraz):\n{' → '.join(ruta)}\nDistancia total: {distancia_acum:.1f} km")
                return
            
            if ciudad_actual not in visitados:
                visitados.add(ciudad_actual)
                
                if ciudad_actual in self.datos['conexiones']:
                    for vecino, distancia in self.datos['conexiones'][ciudad_actual].items():
                        if vecino not in visitados:
                            heuristica = self.distancia_heuristic(vecino, destino)
                            nueva_ruta = ruta.copy()
                            nueva_ruta.append(vecino)
                            nueva_distancia = distancia_acum + distancia
                            cola_prioridad.put((heuristica, vecino, nueva_ruta, nueva_distancia))
        
        self.info_label.config(text="No se encontró ruta")
    
    def busqueda_a_estrella(self):
        """Implementación de búsqueda A*"""
        inicio = self.ciudad_inicial.get()
        destino = self.ciudad_destino.get()
        
        if not inicio or not destino:
            self.info_label.config(text="Seleccione ambas ciudades")
            return
        
        cola_prioridad = PriorityQueue()
        cola_prioridad.put((0, inicio, [inicio], 0))  # (f, ciudad, ruta, g)
        visitados = set()
        
        while not cola_prioridad.empty():
            _, ciudad_actual, ruta, costo_real = cola_prioridad.get()
            
            if ciudad_actual == destino:
                self.ruta_actual = ruta
                self.mostrar_ruta(ruta)
                self.info_label.config(text=f"Ruta encontrada (A*):\n{' → '.join(ruta)}\nDistancia total: {costo_real:.1f} km")
                return
            
            if ciudad_actual not in visitados:
                visitados.add(ciudad_actual)
                
                if ciudad_actual in self.datos['conexiones']:
                    for vecino, distancia in self.datos['conexiones'][ciudad_actual].items():
                        if vecino not in visitados:
                            nuevo_costo_real = costo_real + distancia
                            heuristica = self.distancia_heuristic(vecino, destino)
                            prioridad = nuevo_costo_real + heuristica
                            nueva_ruta = ruta.copy()
                            nueva_ruta.append(vecino)
                            cola_prioridad.put((prioridad, vecino, nueva_ruta, nuevo_costo_real))
        
        self.info_label.config(text="No se encontró ruta")
    
    def mostrar_ruta(self, ruta):
        """Muestra una ruta específica en el mapa"""
        if not ruta or len(ruta) < 2:
            return
        
        # Limpiar ruta anterior completamente
        self.limpiar_ruta_actual()
        
        puntos_ruta = [coordenadas[ciudad] for ciudad in ruta if ciudad in coordenadas]
        if len(puntos_ruta) > 1:
            # Línea de ruta (azul oscuro, más gruesa)
            ruta_line = folium.PolyLine(
                locations=[[lat, lon] for lat, lon in puntos_ruta],
                color='#121966',  # Azul más oscuro
                weight=4,         # Grosor aumentado
                opacity=0.9,
                tooltip="Ruta encontrada"
            )
            ruta_line.add_to(self.map_frame.mapa)
            self.elementos_ruta.append(ruta_line.get_name())
            
            # Marcadores verdes para ciudades en la ruta
            for ciudad in ruta:
                if ciudad in coordenadas:
                    lat, lon = coordenadas[ciudad]
                    marker = folium.CircleMarker(
                        location=[lat, lon],
                        radius=6,
                        popup=ciudad,
                        color='green',
                        fill=True,
                        fill_color='green',
                        fill_opacity=0.9
                    )
                    marker.add_to(self.map_frame.mapa)
                    self.elementos_ruta.append(marker.get_name())
        
        # Ajustar vista para mostrar la ruta
        lats = [coord[0] for coord in puntos_ruta]
        lons = [coord[1] for coord in puntos_ruta]
        self.map_frame.mapa.fit_bounds([(min(lats)-0.5, min(lons)-0.5), (max(lats)+0.5, max(lons)+0.5)])
        self.map_frame.update_map()
    
    def limpiar_ruta(self):
        """Vuelve a mostrar el mapa completo con todas las conexiones"""
        self.mostrar_mapa_inicial()
        self.info_label.config(text="Ruta limpiada - Vista completa de Colombia")

if __name__ == "__main__":
    root = tk.Tk()
    app = MapaColombiaConBusqueda(root)
    root.mainloop()