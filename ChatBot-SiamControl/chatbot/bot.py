from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from .datos import cargar_datos_contratos, buscar_vencimiento_por_nombre, listar_contratos_por_mes, estado_correo_bienvenida, buscar_celular, buscar_email
import re
import pandas as pd
import unicodedata
import difflib
import csv
import os

# --- Función utilitaria para normalizar texto ---
def normalizar_texto(texto):
    """
    Normaliza un texto eliminando tildes, convirtiendo a minúsculas y quitando espacios extra.
    Esto permite comparar cadenas de texto de forma robusta ante errores comunes de usuario.
    """
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return ' '.join(texto.lower().split())

def guardar_historial(pregunta, respuesta, archivo='data/historial_chat.csv'):
    """
    Guarda la pregunta y respuesta en un archivo CSV para trazabilidad.
    """
    existe = os.path.exists(archivo)
    with open(archivo, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['pregunta', 'respuesta'])
        writer.writerow([pregunta, respuesta])

# --- Función principal del chatbot ---
def responder(pregunta):
    """
    Procesa la pregunta del usuario y retorna una respuesta según los intents definidos:
    1. Consulta de vencimiento de contrato por nombre
    2. Listado de contratos que vencen en un mes
    3. Estado del correo de bienvenida
    4. Búsqueda de número de celular por nombre, DNI o Email
    5. Búsqueda de email por nombre, DNI o Email
    6. Búsqueda de contratos por régimen laboral
    7. Búsqueda de contratos por tipo de contrato
    8. Búsqueda de contratos por usuario
    Si la pregunta no coincide con ningún intent, responde con un mensaje genérico.
    """
    # Cargar los datos desde el CSV
    df = cargar_datos_contratos()
    # Convertir la columna de fechas a tipo datetime para evitar errores
    if not df.empty and 'Fch. VENCIMIENTO' in df.columns:
        df['Fch. VENCIMIENTO'] = pd.to_datetime(df['Fch. VENCIMIENTO'], errors='coerce').dt.strftime('%Y-%m-%d')
    # Normalizar la pregunta del usuario
    pregunta_l = normalizar_texto(pregunta)
    nombres = df['Apellidos y nombres'].tolist() if not df.empty else []
    nombres_normalizados = [normalizar_texto(n) for n in nombres]

    # --- Intent 1: Vencimiento por nombre ---
    match = re.search(r'vence el contrato de ([\w áéíóúüñ]+)', pregunta_l)
    if match:
        nombre = match.group(1).strip()
        df['nombre_normalizado'] = df['Apellidos y nombres'].apply(normalizar_texto)
        info = buscar_vencimiento_por_nombre(df.assign(**{'Apellidos y nombres': df['nombre_normalizado']}), nombre)
        if info:
            fecha = info['fecha_vencimiento']
            respuesta = f"El contrato de {info['nombre']} vence el {fecha} y está {info['estado']}."
            guardar_historial(pregunta, respuesta)
            return respuesta
        else:
            sugeridos = difflib.get_close_matches(nombre, nombres_normalizados, n=1, cutoff=0.7)
            if sugeridos:
                idx = nombres_normalizados.index(sugeridos[0])
                sugerido = nombres[idx]
                respuesta = f"No se encontró información para {nombre}. ¿Quiso decir {sugerido}?"
            else:
                relacionados = [n for n, n_norm in zip(nombres, nombres_normalizados) if nombre in n_norm]
                if relacionados:
                    respuesta = f"No se encontró información exacta para {nombre}. Coincidencias: {', '.join(relacionados)}"
                else:
                    respuesta = f"No se encontró información para {nombre}."
            guardar_historial(pregunta, respuesta)
            return respuesta

    # --- Intent 2: Contratos por mes ---
    match = re.search(r'contratos vencen en ([a-záéíóúüñ]+)', pregunta_l)
    if match:
        mes = match.group(1).strip()
        lista = listar_contratos_por_mes(df, mes)
        if lista:
            # Respuesta como tabla Markdown
            tabla = '| Nombre | Tipo de Contrato | Fecha Vencimiento |\n|---|---|---|\n'
            for x in lista:
                fecha = x['Fch. VENCIMIENTO']
                tabla += f"| {x['Apellidos y nombres']} | {x['Tipo de Contrato']} | {fecha} |\n"
            respuesta = f"Contratos que vencen en {mes}:\n" + tabla
            guardar_historial(pregunta, respuesta)
            return respuesta
        else:
            respuesta = f"No hay contratos que venzan en {mes}."
            guardar_historial(pregunta, respuesta)
            return respuesta

    # --- Intent 3: Estado correo bienvenida ---
    match = re.search(r'correo de bienvenida a ([\w áéíóúüñ@.]+)', pregunta_l)
    if match:
        nombre = match.group(1).strip()
        df['nombre_normalizado'] = df['Apellidos y nombres'].apply(normalizar_texto)
        info = estado_correo_bienvenida(df.assign(**{'Apellidos y nombres': df['nombre_normalizado']}), nombre)
        if info:
            if info['correo_bienvenida']:
                respuesta = f"El correo de bienvenida a {info['nombre']} fue enviado el {info['fecha_envio_correo']}."
            else:
                respuesta = f"No se ha enviado el correo de bienvenida a {info['nombre']}."
        else:
            sugeridos = difflib.get_close_matches(nombre, nombres_normalizados, n=1, cutoff=0.7)
            if sugeridos:
                idx = nombres_normalizados.index(sugeridos[0])
                sugerido = nombres[idx]
                respuesta = f"No se encontró información para {nombre}. ¿Quiso decir {sugerido}?"
            else:
                relacionados = [n for n, n_norm in zip(nombres, nombres_normalizados) if nombre in n_norm]
                if relacionados:
                    respuesta = f"No se encontró información exacta para {nombre}. Coincidencias: {', '.join(relacionados)}"
                else:
                    respuesta = f"No se encontró información para {nombre}."
        guardar_historial(pregunta, respuesta)
        return respuesta

    # --- Intent 4: Buscar número de celular por nombre, DNI o Email ---
    match = re.search(r'(n(ú|u)mero de celular (de|tiene) ([\w áéíóúüñ@.]+))', pregunta_l)
    if match:
        valor = match.group(4).strip()
        info = buscar_celular(df, valor)
        if info:
            respuesta = f"El número de celular de {info['nombre']} es {info['celular']}."
        else:
            respuesta = f"No se encontró información para {valor}."
        guardar_historial(pregunta, respuesta)
        return respuesta

    # --- Intent 5: Buscar email por nombre o DNI ---
    match = re.search(r'email (de|tiene) ([\w áéíóúüñ@.]+)', pregunta_l)
    if match:
        valor = match.group(2).strip()
        # Solo buscar por nombre o DNI (no email)
        if '@' in valor:
            respuesta = "Para buscar email, ingresa nombre o DNI, no un correo."
        else:
            info = buscar_email(df, valor)
            if info:
                respuesta = f"El email de {info['nombre']} es {info['email']}."
            else:
                respuesta = f"No se encontró información para {valor}."
        guardar_historial(pregunta, respuesta)
        return respuesta

    # --- Intent 6: Buscar contratos por régimen laboral (más flexible) ---
    match = re.search(r'(contratos (son|del|de|por) (r(é|e)gimen laboral|r(é|e)gimen) ([\w]+))', pregunta_l)
    if match:
        regimen = match.group(6).strip().lower()
        resultados = df[df['Régimen Laboral'].str.lower() == regimen]
        if not resultados.empty:
            tabla = '| Nombre | Régimen Laboral | Fecha Vencimiento |\n|---|---|---|\n'
            for _, x in resultados.iterrows():
                tabla += f"| {x['Apellidos y nombres']} | {x['Régimen Laboral']} | {x['Fch. VENCIMIENTO']} |\n"
            respuesta = f"Contratos del régimen laboral {regimen}:\n" + tabla
        else:
            respuesta = f"No se encontraron contratos para el régimen laboral {regimen}."
        guardar_historial(pregunta, respuesta)
        return respuesta

    # --- Intent 7: Buscar contratos por tipo de contrato ---
    match = re.search(r'contratos (del|de) tipo de contrato ([\w]+)', pregunta_l)
    if match:
        tipo = match.group(2).strip().lower()
        resultados = df[df['Tipo de Contrato'].str.lower() == tipo]
        if not resultados.empty:
            tabla = '| Nombre | Tipo de Contrato | Fecha Vencimiento |\n|---|---|---|\n'
            for _, x in resultados.iterrows():
                tabla += f"| {x['Apellidos y nombres']} | {x['Tipo de Contrato']} | {x['Fch. VENCIMIENTO']} |\n"
            respuesta = f"Contratos del tipo de contrato {tipo}:\n" + tabla
        else:
            respuesta = f"No se encontraron contratos para el tipo de contrato {tipo}."
        guardar_historial(pregunta, respuesta)
        return respuesta

    # --- Intent 8: Buscar contratos por usuario ---
    match = re.search(r'contrato (de|para) usuario ([\w]+)', pregunta_l)
    if match:
        usuario = match.group(2).strip().lower()
        resultados = df[df['Usuario'].str.lower() == usuario]
        if not resultados.empty:
            tabla = '| Nombre | Usuario | Fecha Vencimiento |\n|---|---|---|\n'
            for _, x in resultados.iterrows():
                tabla += f"| {x['Apellidos y nombres']} | {x['Usuario']} | {x['Fch. VENCIMIENTO']} |\n"
            respuesta = f"Contratos para el usuario {usuario}:\n" + tabla
        else:
            respuesta = f"No se encontraron contratos para el usuario {usuario}."
        guardar_historial(pregunta, respuesta)
        return respuesta

    # --- Intent por defecto: pregunta no reconocida ---
    ayuda = (
        "Ejemplos de preguntas válidas:\n"
        "- ¿Qué contratos vencen en 2025-07?\n"
        "- ¿Cuál es el email de Juan Pérez?\n"
        "- ¿Qué número de celular tiene 12345678?\n"
        "- ¿Qué contratos son del régimen laboral CAS?\n"
        "- ¿Qué contratos tiene el usuario jperez?\n"
        "Puedes preguntar por vencimientos, emails, celulares, régimen laboral, tipo de contrato o usuario."
    )
    respuesta = f"Lo siento, no entiendo la pregunta. {ayuda}"
    guardar_historial(pregunta, respuesta)
    return respuesta
