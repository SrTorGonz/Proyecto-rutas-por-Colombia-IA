import pandas as pd
import json

# Leer el archivo Excel correctamente
df = pd.read_excel('departamentos_colombia.xlsx', 
                  sheet_name='Lista Departamentos',
                  header=2)  # Saltamos las 2 primeras filas de encabezado

# Obtener los nombres reales de las capitales (de la fila 3 del Excel)
nombres_capitales = [
    'Leticia', 'Medellín', 'Arauca', 'Barranquilla', 'Cartagena de Indias',
    'Tunja', 'Manizales', 'Florencia', 'Yopal', 'Popayán', 'Valledupar',
    'Quibdó', 'Montería', 'Bogotá', 'Inírida', 'San José del Guaviare',
    'Neiva', 'Riohacha', 'Santa Marta', 'Villavicencio', 'Pasto',
    'San José de Cúcuta', 'Mocoa', 'Armenia', 'Pereira', 'San Andrés',
    'Bucaramanga', 'Sincelejo', 'Ibagué', 'Cali', 'Mitú', 'Puerto Carreño'
]

# Crear estructura de datos corregida
conexiones_colombia = {
    'capitales': nombres_capitales,
    'conexiones': {}
}

# Mapeo de índices de columnas a nombres de capitales
columna_a_capital = {i+4: nombre for i, nombre in enumerate(nombres_capitales)}

# Procesar cada fila correctamente
for _, row in df.iterrows():
    if pd.notna(row.iloc[2]):  # Verificar que la fila tenga datos de departamento
        capital = row.iloc[3]  # Columna 'Capital'
        conexiones_colombia['conexiones'][capital] = {}
        
        for col_idx, ciudad_conexion in columna_a_capital.items():
            distancia = row.iloc[col_idx]
            if pd.notna(distancia) and distancia != 0 and ciudad_conexion != capital:
                conexiones_colombia['conexiones'][capital][ciudad_conexion] = distancia

# Guardar en JSON con formato correcto
with open('conexiones_colombia_final.json', 'w', encoding='utf-8') as f:
    json.dump(conexiones_colombia, f, indent=2, ensure_ascii=False)

print("Archivo JSON generado correctamente: 'conexiones_colombia_final.json'")