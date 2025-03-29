import tkinter as tk
from tkinter import ttk
import json
import math
from queue import PriorityQueue

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

class MapaColombiaConBusqueda:
    def __init__(self, root):
        self.root = root
        self.root.title("Rutas por Colombia con Algoritmos de Búsqueda")
        self.root.geometry("1100x800")
        
        # Cargar datos del JSON
        with open('conexiones.json', 'r', encoding='utf-8') as f:
            self.datos = json.load(f)
        
        # Frame principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para el mapa
        self.map_frame = ttk.Frame(self.main_frame)
        self.map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas para el mapa
        self.canvas = tk.Canvas(self.map_frame, width=700, height=700, bg='white')
        self.canvas.pack(pady=10)
        
        # Frame para controles (derecha)
        self.control_frame = ttk.Frame(self.main_frame, width=300)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Selectores de ciudades
        ttk.Label(self.control_frame, text="Ciudad Inicial:", font=('Arial', 10, 'bold')).pack(pady=(20,5))
        self.ciudad_inicial = ttk.Combobox(self.control_frame, values=self.datos['capitales'], state='readonly')
        self.ciudad_inicial.pack(fill=tk.X, padx=10)
        
        ttk.Label(self.control_frame, text="Ciudad Destino:", font=('Arial', 10, 'bold')).pack(pady=(20,5))
        self.ciudad_destino = ttk.Combobox(self.control_frame, values=self.datos['capitales'], state='readonly')
        self.ciudad_destino.pack(fill=tk.X, padx=10)
        
        # Botones de búsqueda
        ttk.Button(self.control_frame, text="Búsqueda Voraz", command=self.busqueda_voraz).pack(pady=(30,10), fill=tk.X, padx=10)
        ttk.Button(self.control_frame, text="Búsqueda A*", command=self.busqueda_a_estrella).pack(pady=10, fill=tk.X, padx=10)
        ttk.Button(self.control_frame, text="Limpiar Ruta", command=self.limpiar_ruta).pack(pady=10, fill=tk.X, padx=10)
        
        # Área de información
        self.info_label = ttk.Label(self.control_frame, text="Seleccione ciudades y algoritmo", wraplength=280)
        self.info_label.pack(pady=(30,10), fill=tk.X, padx=10)
        
        # Variables para el zoom y desplazamiento
        self.zoom = 1.3
        self.offset_x = 0
        self.offset_y = 50
        
        # Dibujar el mapa
        self.dibujar_mapa()
        
        # Manejar eventos del ratón
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        
    def convertir_coordenadas(self, lat, lon):
        """Convertir coordenadas geográficas a coordenadas de pantalla"""
        x = (lon + 78) * 15 * self.zoom + self.offset_x
        y = (15 - lat) * 15 * self.zoom + self.offset_y
        return x, y
    
    def dibujar_mapa(self):
        """Dibujar el mapa con capitales y conexiones"""
        self.canvas.delete("all")
        
        # Dibujar conexiones
        for ciudad, conexiones in self.datos['conexiones'].items():
            if ciudad in coordenadas:
                x1, y1 = self.convertir_coordenadas(*coordenadas[ciudad])
                for destino in conexiones:
                    if destino in coordenadas:
                        x2, y2 = self.convertir_coordenadas(*coordenadas[destino])
                        self.canvas.create_line(x1, y1, x2, y2, fill="#aaa", width=1)
        
        # Dibujar puntos de las capitales
        self.ciudad_tags = {}
        for ciudad, (lat, lon) in coordenadas.items():
            x, y = self.convertir_coordenadas(lat, lon)
            punto = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="#e74c3c", outline="#c0392b", width=1)
            self.ciudad_tags[punto] = ciudad
            self.canvas.tag_bind(punto, "<Enter>", lambda e, c=ciudad: self.mostrar_info_ciudad(c))
            self.canvas.tag_bind(punto, "<Leave>", lambda e: self.ocultar_info_ciudad())
    
    def mostrar_info_ciudad(self, ciudad):
        """Mostrar información de la ciudad al pasar el ratón"""
        info = f"{ciudad}"
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{self.root.winfo_pointerx()+15}+{self.root.winfo_pointery()+15}")
        tk.Label(self.tooltip, text=info, bg="#ffffe0", relief="solid", borderwidth=1).pack()
    
    def ocultar_info_ciudad(self):
        """Ocultar el tooltip de información"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
    
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
        cola_prioridad.put((0, inicio, [inicio]))
        visitados = set()
        
        while not cola_prioridad.empty():
            _, ciudad_actual, ruta = cola_prioridad.get()
            
            if ciudad_actual == destino:
                self.mostrar_ruta(ruta)
                self.info_label.config(text=f"Ruta encontrada (Voraz):\n{' → '.join(ruta)}")
                return
            
            if ciudad_actual not in visitados:
                visitados.add(ciudad_actual)
                
                if ciudad_actual in self.datos['conexiones']:
                    for vecino in self.datos['conexiones'][ciudad_actual]:
                        if vecino not in visitados:
                            heuristica = self.distancia_heuristic(vecino, destino)
                            nueva_ruta = ruta.copy()
                            nueva_ruta.append(vecino)
                            cola_prioridad.put((heuristica, vecino, nueva_ruta))
        
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
        """Resaltar la ruta encontrada en el mapa"""
        self.limpiar_ruta()
        
        for i in range(len(ruta)-1):
            ciudad1 = ruta[i]
            ciudad2 = ruta[i+1]
            
            if ciudad1 in coordenadas and ciudad2 in coordenadas:
                x1, y1 = self.convertir_coordenadas(*coordenadas[ciudad1])
                x2, y2 = self.convertir_coordenadas(*coordenadas[ciudad2])
                
                # Dibujar línea de conexión resaltada
                self.canvas.create_line(x1, y1, x2, y2, fill="#3498db", width=3)
                
                # Resaltar ciudades de la ruta
                self.canvas.create_oval(x1-7, y1-7, x1+7, y1+7, fill="#2ecc71", outline="#27ae60", width=2)
                self.canvas.create_oval(x2-7, y2-7, x2+7, y2+7, fill="#2ecc71", outline="#27ae60", width=2)
    
    def limpiar_ruta(self):
        """Limpiar la ruta resaltada"""
        self.dibujar_mapa()
    
    def start_drag(self, event):
        """Iniciar arrastre del mapa"""
        self.last_x = event.x
        self.last_y = event.y
    
    def drag(self, event):
        """Arrastrar el mapa"""
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.offset_x += dx
        self.offset_y += dy
        self.last_x = event.x
        self.last_y = event.y
        self.dibujar_mapa()

if __name__ == "__main__":
    root = tk.Tk()
    app = MapaColombiaConBusqueda(root)
    root.mainloop()