import streamlit as st
import base64
from datetime import datetime
import re

# Configuración de la página
st.set_page_config(
    page_title="Taller SQL - Base de Datos I",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Datos SQL 
SCHEMA_SQL = """-- schema.sql - DDL mínimo para sistema universitario
-- Base de Datos I - Semana 3

CREATE TABLE alumno (
    alumno_id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    ciudad VARCHAR(60)
);

CREATE TABLE curso (
    curso_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    creditos INT CHECK (creditos BETWEEN 1 AND 6)
);

CREATE TABLE inscripcion (
    inscripcion_id SERIAL PRIMARY KEY,
    alumno_id INT NOT NULL REFERENCES alumno(alumno_id),
    curso_id INT NOT NULL REFERENCES curso(curso_id),
    fecha DATE NOT NULL DEFAULT CURRENT_DATE
);"""

SEED_SQL = """-- seed.sql - DML de ejemplo
-- Base de Datos I - Semana 3

INSERT INTO alumno (nombre, email, ciudad) VALUES
('Ana Gómez', 'ana.gomez@uni.edu', 'Medellín'),
('Luis Ríos', 'luis.rios@uni.edu', 'Bogotá'),
('Sara Díaz', 'sara.diaz@uni.edu', 'Cali');

INSERT INTO curso (nombre, creditos) VALUES
('Base de Datos I', 3),
('Programación I', 4);

INSERT INTO inscripcion (alumno_id, curso_id) VALUES 
(1, 1), (2, 1), (3, 2);"""

GUIA_PDF = """GUÍA DEL TALLER - SEMANA 3
Base de Datos I - SQL Básico

OBJETIVOS:
1. Crear tablas con DDL mínimo
2. Manipular datos con INSERT, UPDATE, DELETE
3. Consultar con SELECT y WHERE

EJERCICIOS INCLUIDOS:
- 5 ejercicios guiados paso a paso
- Práctica autónoma con retos
- Cheat-sheet de comandos SQL

RECURSOS:
- schema.sql: Estructura de tablas
- seed.sql: Datos de ejemplo
- PostgreSQL 17 recomendado

NOTAS:
- Complete los ejercicios en orden
- Use las pistas cuando sea necesario
- Active "Modo docente" para ver soluciones

Profesor: Dr. Juan Martínez
Universidad Nacional"""

# CSS 
def aplicar_estilos():
    st.markdown("""
    <style>
    /* Diseño limpio y académico */
    .main {
        background-color: #ffffff;
        padding: 1.5rem;
    }
    
    /* Header principal */
    .header-taller {
        background: linear-gradient(90deg, #3b5998 0%, #4a69bd 100%);
        color: white;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .header-taller h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 500;
    }
    
    .header-taller p {
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }
    
    /* Cards de contenido */
    .ejercicio-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .solucion-card {
        background: #e8f5e9;
        border: 1px solid #4caf50;
        border-radius: 6px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    /* Modo docente */
    .modo-docente-badge {
        background: #ff9800;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    /* Progreso */
    .progreso-container {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    /* FAQ */
    .faq-item {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Botones */
    .stButton > button {
        background-color: #3b5998;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #2d4373;
    }
    
    /* Código */
    .stCode {
        background-color: #f5f5f5 !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-taller h1 {
            font-size: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def inicializar_estado():
    if 'ejercicios_completados' not in st.session_state:
        st.session_state.ejercicios_completados = [False] * 5
    
    if 'ejercicios_autonomos' not in st.session_state:
        st.session_state.ejercicios_autonomos = [False] * 5
    
    if 'modo_docente' not in st.session_state:
        st.session_state.modo_docente = False
    
    if 'faq' not in st.session_state:
        st.session_state.faq = []
    
    if 'objetivos_completados' not in st.session_state:
        st.session_state.objetivos_completados = {
            'lei_objetivos': False,
            'complete_guiados': False,
            'hice_autonomos': False
        }
    
    if 'vista_actual' not in st.session_state:
        st.session_state.vista_actual = "Inicio"
    
    if 'soluciones_reveladas' not in st.session_state:
        st.session_state.soluciones_reveladas = [False] * 5


def validar_sintaxis_sql(codigo):
    """Validación básica de sintaxis SQL"""
    codigo = codigo.strip().upper()
    comandos_validos = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
    
    if not codigo:
        return False, "El código está vacío"
    
    primer_comando = codigo.split()[0] if codigo.split() else ""
    if primer_comando in comandos_validos:
        return True, f"Comando {primer_comando} detectado correctamente"
    else:
        return False, f"El código debe comenzar con un comando SQL válido"

def calcular_progreso():
    """Calcula el progreso total del taller"""
    total = len(st.session_state.ejercicios_completados) + \
            len(st.session_state.ejercicios_autonomos) + \
            len(st.session_state.objetivos_completados)
    
    completados = sum(st.session_state.ejercicios_completados) + \
                  sum(st.session_state.ejercicios_autonomos) + \
                  sum(st.session_state.objetivos_completados.values())
    
    return (completados / total * 100) if total > 0 else 0


def vista_inicio():
    st.markdown("""
    <div class="header-taller">
        <h1>Semana 3 – Taller Interactivo de SQL (DDL/DML/SELECT)</h1>
        <p>Base de Datos I | Universidad Digital</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### Objetivos de Aprendizaje
    
    En este taller interactivo aprenderás a trabajar con los comandos SQL fundamentales 
    para la definición y manipulación de datos en PostgreSQL 17. Al finalizar, serás 
    capaz de crear estructuras de datos básicas y realizar operaciones CRUD completas.
    """)
    
    st.markdown("### Logros Esperados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Crear Tablas (DDL)**
        - Definir estructuras básicas
        - Establecer restricciones
        - Modificar tablas existentes
        """)
    
    with col2:
        st.markdown("""
        **Manipular Datos (DML)**
        - INSERT de registros
        - UPDATE de información
        - DELETE selectivo
        """)
    
    with col3:
        st.markdown("""
        **Consultar (SELECT)**
        - Filtros con WHERE
        - Ordenamiento básico
        - Selección de columnas
        """)
    
    st.divider()
    
    st.markdown("### Indicador de Progreso")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.objetivos_completados['lei_objetivos'] = st.checkbox(
            "✓ Leí los objetivos",
            value=st.session_state.objetivos_completados['lei_objetivos']
        )
    
    with col2:
        st.session_state.objetivos_completados['complete_guiados'] = st.checkbox(
            "✓ Completé ejercicios guiados",
            value=st.session_state.objetivos_completados['complete_guiados']
        )
    
    with col3:
        st.session_state.objetivos_completados['hice_autonomos'] = st.checkbox(
            "✓ Hice práctica autónoma",
            value=st.session_state.objetivos_completados['hice_autonomos']
        )
    
    progreso = calcular_progreso()
    st.progress(progreso / 100)
    st.info(f"Progreso total del taller: {progreso:.1f}%")
    
    if st.session_state.modo_docente:
        st.markdown("""
        <div class="solucion-card">
        <strong>Modo Docente Activo:</strong> Las soluciones y notas para el profesor están visibles.
        </div>
        """, unsafe_allow_html=True)

def vista_contexto():
    st.markdown("## Contexto & Mini-Esquema")
    
    st.markdown("""
    ### Dominio: Sistema Universitario Simplificado
    
    Trabajaremos con un modelo básico de gestión académica que incluye:
    - **Alumnos**: Estudiantes registrados en la universidad
    - **Cursos**: Asignaturas disponibles con sus créditos
    - **Inscripciones**: Relación entre alumnos y cursos
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Estructura de Datos (DDL)")
        st.code(SCHEMA_SQL, language='sql')
        
        st.download_button(
            label="Descargar schema.sql",
            data=SCHEMA_SQL,
            file_name="schema.sql",
            mime="text/plain"
        )
    
    with col2:
        st.markdown("#### Datos de Ejemplo (DML)")
        st.code(SEED_SQL, language='sql')
        
        st.download_button(
            label="Descargar seed.sql",
            data=SEED_SQL,
            file_name="seed.sql",
            mime="text/plain"
        )
    
    st.divider()
    
    st.markdown("### Visualización de Datos")
    
    tab1, tab2, tab3 = st.tabs(["Tabla: alumno", "Tabla: curso", "Tabla: inscripcion"])
    
    with tab1:
        alumnos_data = {
            "alumno_id": [1, 2, 3],
            "nombre": ["Ana Gómez", "Luis Ríos", "Sara Díaz"],
            "email": ["ana.gomez@uni.edu", "luis.rios@uni.edu", "sara.diaz@uni.edu"],
            "ciudad": ["Medellín", "Bogotá", "Cali"]
        }
        st.table(alumnos_data)
    
    with tab2:
        cursos_data = {
            "curso_id": [1, 2],
            "nombre": ["Base de Datos I", "Programación I"],
            "creditos": [3, 4]
        }
        st.table(cursos_data)
    
    with tab3:
        inscripciones_data = {
            "inscripcion_id": [1, 2, 3],
            "alumno_id": [1, 2, 3],
            "curso_id": [1, 1, 2],
            "fecha": ["2025-01-15", "2025-01-15", "2025-01-16"]
        }
        st.table(inscripciones_data)
    
    if st.session_state.modo_docente:
        st.markdown("""
        <div class="solucion-card">
        <strong>Nota para el docente:</strong> 
        Este esquema es intencionalmente simple para facilitar el aprendizaje. 
        En producción, consideraría índices adicionales, constraints más complejos 
        y normalización adicional.
        </div>
        """, unsafe_allow_html=True)

def vista_ejercicios_guiados():
    st.markdown("## Ejercicios Guiados (Paso a Paso)")
    
    ejercicios = [
        {
            "titulo": "Ejercicio 1: INSERT de nuevos alumnos",
            "enunciado": "Inserta dos nuevos alumnos en la tabla alumno: 'Carlos Mendoza' (carlos.mendoza@uni.edu, Cali) y 'María López' (maria.lopez@uni.edu, Medellín).",
            "pista": "Usa INSERT INTO con VALUES para agregar múltiples registros. Recuerda que alumno_id es SERIAL y se genera automáticamente.",
            "plantilla": """-- Inserta dos nuevos alumnos
INSERT INTO alumno (nombre, email, ciudad) VALUES
    -- Completa aquí""",
            "solucion": """INSERT INTO alumno (nombre, email, ciudad) VALUES
    ('Carlos Mendoza', 'carlos.mendoza@uni.edu', 'Cali'),
    ('María López', 'maria.lopez@uni.edu', 'Medellín');"""
        },
        {
            "titulo": "Ejercicio 2: UPDATE de email",
            "enunciado": "Actualiza el email del alumno con alumno_id = 2 a 'luis.rios.nuevo@uni.edu'.",
            "pista": "UPDATE requiere WHERE para especificar qué registro modificar. Sin WHERE, actualizarías TODOS los registros.",
            "plantilla": """-- Actualiza el email de un alumno específico
UPDATE alumno 
SET -- Completa aquí
WHERE -- Completa aquí""",
            "solucion": """UPDATE alumno 
SET email = 'luis.rios.nuevo@uni.edu'
WHERE alumno_id = 2;"""
        },
        {
            "titulo": "Ejercicio 3: DELETE de inscripción",
            "enunciado": "Elimina la inscripción con inscripcion_id = 3.",
            "pista": "DELETE FROM es directo, pero siempre usa WHERE para evitar eliminar todos los registros.",
            "plantilla": """-- Elimina una inscripción específica
DELETE FROM -- Completa aquí
WHERE -- Completa aquí""",
            "solucion": """DELETE FROM inscripcion
WHERE inscripcion_id = 3;"""
        },
        {
            "titulo": "Ejercicio 4: SELECT con filtro por ciudad",
            "enunciado": "Selecciona el nombre y email de todos los alumnos que viven en 'Medellín'.",
            "pista": "SELECT columnas FROM tabla WHERE condición. Las cadenas de texto van entre comillas simples.",
            "plantilla": """-- Consulta alumnos de una ciudad específica
SELECT -- Completa aquí
FROM -- Completa aquí
WHERE -- Completa aquí""",
            "solucion": """SELECT nombre, email
FROM alumno
WHERE ciudad = 'Medellín';"""
        },
        {
            "titulo": "Ejercicio 5: SELECT con rango de créditos",
            "enunciado": "Selecciona todos los cursos que tienen entre 3 y 5 créditos.",
            "pista": "Puedes usar BETWEEN o combinar condiciones con AND.",
            "plantilla": """-- Consulta cursos por rango de créditos
SELECT * FROM curso
WHERE -- Completa aquí""",
            "solucion": """SELECT * FROM curso
WHERE creditos BETWEEN 3 AND 5;
-- Alternativa:
-- WHERE creditos >= 3 AND creditos <= 5;"""
        }
    ]
    
    for i, ejercicio in enumerate(ejercicios):
        with st.container():
            col1, col2 = st.columns([10, 1])
            
            with col1:
                st.markdown(f"### {ejercicio['titulo']}")
            
            with col2:
                st.session_state.ejercicios_completados[i] = st.checkbox(
                    "✓",
                    key=f"guiado_{i}",
                    value=st.session_state.ejercicios_completados[i]
                )
            
            st.markdown(f"**Enunciado:** {ejercicio['enunciado']}")
            
            with st.expander("💡 Ver pista"):
                st.info(ejercicio['pista'])
            
            
            codigo = st.text_area(
                "Tu solución:",
                value=ejercicio['plantilla'],
                height=100,
                key=f"codigo_guiado_{i}"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Validar sintaxis", key=f"validar_{i}"):
                    valido, mensaje = validar_sintaxis_sql(codigo)
                    if valido:
                        st.success(mensaje)
                    else:
                        st.warning(mensaje)
            
            with col2:
                if st.session_state.modo_docente or st.button(f"Ver solución", key=f"sol_{i}"):
                    st.session_state.soluciones_reveladas[i] = True
            
            if st.session_state.soluciones_reveladas[i]:
                if st.session_state.modo_docente:
                    st.markdown("**Solución (Modo Docente):**")
                    st.code(ejercicio['solucion'], language='sql')
                else:
                    st.info("Activa el 'Modo Docente' en el sidebar para ver la solución completa")
            
            st.divider()
    
    
    completados = sum(st.session_state.ejercicios_completados)
    total = len(ejercicios)
    
    if completados == total:
        st.success(f"¡Excelente! Has completado todos los {total} ejercicios guiados.")
    else:
        st.info(f"Progreso: {completados}/{total} ejercicios completados")

def vista_practica_autonoma():
    st.markdown("## Práctica Autónoma (Sandbox)")
    
    st.markdown("""
    Practica libremente con estos retos. Haz clic en los botones para cargar 
    snippets de código que puedes modificar y experimentar.
    """)
    
    retos = [
        {
            "titulo": "Agregar columna telefono",
            "descripcion": "Usa ALTER TABLE para agregar una columna telefono a la tabla alumno",
            "snippet": """-- Agregar columna telefono a tabla alumno
ALTER TABLE alumno 
ADD COLUMN telefono VARCHAR(20);"""
        },
        {
            "titulo": "INSERT masivo de cursos",
            "descripcion": "Inserta 3 cursos nuevos de una sola vez",
            "snippet": """-- INSERT masivo de 3 cursos
INSERT INTO curso (nombre, creditos) VALUES
    ('Cálculo I', 4),
    ('Física I', 3),
    ('Algoritmos', 5);"""
        },
        {
            "titulo": "UPDATE en cascada",
            "descripcion": "Cambia la ciudad de todos los alumnos de 'Bogotá' a 'Bogotá D.C.'",
            "snippet": """-- UPDATE múltiple por condición
UPDATE alumno 
SET ciudad = 'Bogotá D.C.'
WHERE ciudad = 'Bogotá';"""
        },
        {
            "titulo": "DELETE por condición",
            "descripcion": "Elimina todas las inscripciones anteriores a una fecha específica",
            "snippet": """-- DELETE con condición de fecha
DELETE FROM inscripcion
WHERE fecha < '2025-01-15';"""
        },
        {
            "titulo": "SELECT con alias",
            "descripcion": "Consulta con alias y concatenación de nombre completo",
            "snippet": """-- SELECT con alias y concatenación
SELECT 
    alumno_id AS "ID",
    nombre || ' (' || ciudad || ')' AS "Nombre Completo y Ciudad",
    email AS "Correo Electrónico"
FROM alumno
ORDER BY nombre;"""
        }
    ]
    
    
    if 'codigo_sandbox' not in st.session_state:
        st.session_state.codigo_sandbox = "-- Escribe tu código SQL aquí\n"
    
    st.markdown("### Editor SQL Sandbox")
    
    
    st.markdown("**Retos rápidos - Haz clic para cargar el código:**")
    
    cols = st.columns(3)
    for i, reto in enumerate(retos):
        with cols[i % 3]:
            if st.button(reto['titulo'], key=f"reto_{i}"):
                st.session_state.codigo_sandbox = reto['snippet']
                st.rerun()
            
            st.session_state.ejercicios_autonomos[i] = st.checkbox(
                f"✓ Completado",
                key=f"autonomo_{i}",
                value=st.session_state.ejercicios_autonomos[i]
            )
    
    # Editor
    codigo = st.text_area(
        "Código SQL:",
        value=st.session_state.codigo_sandbox,
        height=200,
        key="sandbox_editor"
    )
    st.session_state.codigo_sandbox = codigo
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Validar sintaxis"):
            valido, mensaje = validar_sintaxis_sql(codigo)
            if valido:
                st.success(mensaje)
            else:
                st.warning(mensaje)
    
    with col2:
        if st.button("Limpiar editor"):
            st.session_state.codigo_sandbox = "-- Escribe tu código SQL aquí\n"
            st.rerun()
    
    with col3:
        if st.button("Copiar al portapapeles"):
            st.info("Código listo para copiar (selecciona y copia manualmente)")
    
    # Descripción de retos expandible
    with st.expander("Ver descripción detallada de los retos"):
        for reto in retos:
            st.markdown(f"**{reto['titulo']}**: {reto['descripcion']}")
            st.code(reto['snippet'], language='sql')
    
    if st.session_state.modo_docente:
        st.markdown("""
        <div class="solucion-card">
        <strong>Nota docente:</strong> Los estudiantes pueden experimentar libremente aquí. 
        Considere revisar sus intentos y proporcionar retroalimentación personalizada.
        </div>
        """, unsafe_allow_html=True)

def vista_cheatsheet():
    st.markdown("## Cheat-sheet SQL")
    
    st.markdown("### Referencia Rápida de Comandos")
    
    comandos = {
        "Comando": [
            "INSERT INTO", "UPDATE", "DELETE FROM", "SELECT",
            "WHERE", "ORDER BY", "LIMIT", "ALTER TABLE ADD",
            "ALTER TABLE DROP", "CREATE TABLE", "DROP TABLE"
        ],
        "Categoría": [
            "DML", "DML", "DML", "DQL",
            "Filtro", "Orden", "Límite", "DDL",
            "DDL", "DDL", "DDL"
        ],
        "Descripción": [
            "Inserta nuevos registros en una tabla",
            "Actualiza registros existentes",
            "Elimina registros de una tabla",
            "Recupera datos de una o más tablas",
            "Filtra resultados según condiciones",
            "Ordena resultados (ASC/DESC)",
            "Limita cantidad de resultados",
            "Agrega nueva columna a tabla",
            "Elimina columna de tabla",
            "Crea nueva tabla",
            "Elimina tabla completamente"
        ]
    }
    
    st.table(comandos)
    
    st.divider()
    
    st.markdown("### Mini-Ejemplos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### DML - Manipulación de Datos")
        
        st.markdown("**INSERT**")
        st.code("""INSERT INTO tabla (col1, col2) 
VALUES (valor1, valor2);""", language='sql')
        
        st.markdown("**UPDATE**")
        st.code("""UPDATE tabla 
SET col1 = nuevo_valor 
WHERE condicion;""", language='sql')
        
        st.markdown("**DELETE**")
        st.code("""DELETE FROM tabla 
WHERE condicion;""", language='sql')
    
    with col2:
        st.markdown("#### DQL - Consultas")
        
        st.markdown("**SELECT básico**")
        st.code("""SELECT col1, col2 
FROM tabla 
WHERE condicion 
ORDER BY col1 DESC 
LIMIT 10;""", language='sql')
        
        st.markdown("**DDL - Modificación**")
        st.code("""ALTER TABLE tabla 
ADD COLUMN nueva_col VARCHAR(50);

ALTER TABLE tabla 
DROP COLUMN col_existente;""", language='sql')
    
    # guía
    st.download_button(
        label="Descargar Guía Completa (TXT)",
        data=GUIA_PDF,
        file_name="guia_taller_sql.txt",
        mime="text/plain"
    )

def vista_faq():
    st.markdown("## Dudas & Respuestas (FAQ Viva)")
    
    st.markdown("""
    Registra tus dudas aquí. El profesor las responderá y quedarán disponibles 
    para todos los estudiantes.
    """)
    
    
    with st.form("nueva_pregunta"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            nombre = st.text_input("Nombre (opcional)", placeholder="Anónimo")
        
        with col2:
            pregunta = st.text_area("Tu pregunta", placeholder="Escribe tu duda aquí...")
        
        enviado = st.form_submit_button("Enviar pregunta")
        
        if enviado and pregunta:
            nueva_faq = {
                'id': len(st.session_state.faq),
                'nombre': nombre if nombre else "Anónimo",
                'pregunta': pregunta,
                'respuesta': "",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'resuelta': False
            }
            st.session_state.faq.append(nueva_faq)
            st.success("Pregunta enviada correctamente")
            st.rerun()
    
    st.divider()
    
    
    if st.session_state.faq:
        st.markdown("### Banco de Preguntas y Respuestas")
        
        for i, item in enumerate(st.session_state.faq):
            with st.expander(f"Pregunta de {item['nombre']} - {item['timestamp']}"):
                st.markdown(f"**Pregunta:** {item['pregunta']}")
                
                if st.session_state.modo_docente:
                    # Modo docente
                    respuesta = st.text_area(
                        "Respuesta del docente:",
                        value=item['respuesta'],
                        key=f"respuesta_{i}"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Guardar respuesta", key=f"guardar_{i}"):
                            st.session_state.faq[i]['respuesta'] = respuesta
                            st.session_state.faq[i]['resuelta'] = True
                            st.success("Respuesta guardada")
                            st.rerun()
                    
                    with col2:
                        if st.button(f"Eliminar pregunta", key=f"eliminar_{i}"):
                            st.session_state.faq.pop(i)
                            st.rerun()
                else:
                    # Modo estudiante
                    if item['respuesta']:
                        st.markdown(f"**Respuesta:** {item['respuesta']}")
                        if item['resuelta']:
                            st.success("✓ Resuelta")
                    else:
                        st.info("Esperando respuesta del docente...")
    else:
        st.info("No hay preguntas registradas aún. ¡Sé el primero en preguntar!")

def vista_conexion():
    st.markdown("## Conexión a PostgreSQL (Opcional)")
    
    st.warning("""
    **Advertencia:** Esta sección es opcional y con fines demostrativos. 
    No se ejecutará código real contra la base de datos.
    """)
    
    st.markdown("""
    ### Configuración de Conexión
    
    Para conectarte a PostgreSQL desde Python, necesitas la librería `psycopg2`. 
    Los parámetros de conexión se configuran en el sidebar.
    """)
    

    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Parámetros actuales:**
        - Host: {st.session_state.get('db_host', 'localhost')}
        - Puerto: {st.session_state.get('db_puerto', '5432')}
        - Base de datos: {st.session_state.get('db_nombre', 'universidad')}
        - Usuario: {st.session_state.get('db_usuario', 'postgres')}
        """)
    
    with col2:
        st.info("""
        **Requisitos:**
        - PostgreSQL 17 instalado
        - psycopg2 instalado: `pip install psycopg2`
        - Credenciales válidas
        - Servicio PostgreSQL activo
        """)
    
    # Código de ejemplo
    if st.button("Mostrar ejemplo de conexión"):
        st.markdown("### Código de Ejemplo")
        
        codigo_conexion = f"""
import psycopg2
from psycopg2 import sql

# Parámetros de conexión
config = {{
    'host': '{st.session_state.get('db_host', 'localhost')}',
    'port': '{st.session_state.get('db_puerto', '5432')}',
    'database': '{st.session_state.get('db_nombre', 'universidad')}',
    'user': '{st.session_state.get('db_usuario', 'postgres')}',
    'password': 'tu_contraseña_aqui'
}}

def ejecutar_scripts():
    try:
        # Establecer conexión
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Leer y ejecutar schema.sql
        with open('schema.sql', 'r') as f:
            schema = f.read()
            cursor.execute(schema)
        
        # Leer y ejecutar seed.sql
        with open('seed.sql', 'r') as f:
            seed = f.read()
            cursor.execute(seed)
        
        # Confirmar cambios
        conn.commit()
        print("Scripts ejecutados exitosamente")
        
        # Consulta de verificación
        cursor.execute("SELECT COUNT(*) FROM alumno;")
        count = cursor.fetchone()[0]
        print(f"Total de alumnos: {{count}}")
        
    except psycopg2.Error as e:
        print(f"Error de PostgreSQL: {{e}}")
        conn.rollback()
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# NO EJECUTAR - Solo ejemplo
# ejecutar_scripts()
"""
        
        st.code(codigo_conexion, language='python')
        
        st.info("""
        **Nota:** Este código es solo un ejemplo. No lo ejecutes directamente 
        sin verificar las credenciales y tener respaldo de tu base de datos.
        """)


inicializar_estado()

# Sidebar
with st.sidebar:
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <div style="background: #3b5998; 
                    width: 60px; height: 60px; border-radius: 8px; 
                    margin: 0 auto; display: flex; align-items: center; 
                    justify-content: center; color: white; font-size: 1.5rem;">
            🗄️
        </div>
        <h3 style="margin-top: 1rem; color: #2d3748;">Base de Datos I</h3>
        <p style="color: #718096; font-size: 0.9rem;">Semana 3 - Taller SQL</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    
    st.markdown("### Navegación")
    vista = st.selectbox(
        "Selecciona una sección:",
        ["Inicio", "Contexto & Schema", "Ejercicios Guiados", 
         "Práctica Autónoma", "Cheat-sheet", "FAQ", "Conexión PostgreSQL"],
        index=["Inicio", "Contexto & Schema", "Ejercicios Guiados", 
               "Práctica Autónoma", "Cheat-sheet", "FAQ", 
               "Conexión PostgreSQL"].index(st.session_state.vista_actual)
    )
    st.session_state.vista_actual = vista
    
    st.divider()
    
    # Modo docente
    st.markdown("### Configuración")
    st.session_state.modo_docente = st.toggle(
        "Modo Docente",
        value=st.session_state.modo_docente,
        help="Activa para ver soluciones y notas para el profesor"
    )
    
    if st.session_state.modo_docente:
        st.markdown("""
        <div style="background: #ff9800; color: white; padding: 0.5rem; 
                    border-radius: 4px; text-align: center; margin-top: 0.5rem;">
            <strong>MODO DOCENTE ACTIVO</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Progreso general
    st.markdown("### Progreso del Taller")
    progreso = calcular_progreso()
    st.progress(progreso / 100)
    st.caption(f"{progreso:.1f}% completado")
    
    # Detalles del progreso
    with st.expander("Ver detalles"):
        guiados = sum(st.session_state.ejercicios_completados)
        autonomos = sum(st.session_state.ejercicios_autonomos)
        objetivos = sum(st.session_state.objetivos_completados.values())
        
        st.caption(f"Ejercicios guiados: {guiados}/5")
        st.caption(f"Práctica autónoma: {autonomos}/5")
        st.caption(f"Objetivos: {objetivos}/3")
    
    st.divider()
    
    # Configuración de conexión
    with st.expander("Config. PostgreSQL"):
        st.session_state.db_host = st.text_input("Host", value="localhost")
        st.session_state.db_puerto = st.text_input("Puerto", value="5432")
        st.session_state.db_nombre = st.text_input("BD", value="universidad")
        st.session_state.db_usuario = st.text_input("Usuario", value="postgres")
        st.session_state.db_password = st.text_input("Contraseña", type="password")
    
    st.divider()
    
    # Reiniciar progreso
    if st.button("Reiniciar Progreso", type="secondary"):
        if st.checkbox("Confirmar reinicio"):
            for key in st.session_state.keys():
                if key not in ['modo_docente', 'vista_actual']:
                    del st.session_state[key]
            st.success("Progreso reiniciado")
            st.rerun()

# CSS
aplicar_estilos()


if st.session_state.vista_actual == "Inicio":
    vista_inicio()
elif st.session_state.vista_actual == "Contexto & Schema":
    vista_contexto()
elif st.session_state.vista_actual == "Ejercicios Guiados":
    vista_ejercicios_guiados()
elif st.session_state.vista_actual == "Práctica Autónoma":
    vista_practica_autonoma()
elif st.session_state.vista_actual == "Cheat-sheet":
    vista_cheatsheet()
elif st.session_state.vista_actual == "FAQ":
    vista_faq()
elif st.session_state.vista_actual == "Conexión PostgreSQL":
    vista_conexion()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 2rem;">
    <p>Taller Interactivo SQL - Base de Datos I | Universidad Digital | 2025</p>
    <p style="font-size: 0.9rem;">Desarrollado con Streamlit para educación práctica en SQL</p>
</div>
""", unsafe_allow_html=True)