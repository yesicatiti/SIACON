import pandas as pd
import os

# Cargar datos desde CSV (ejemplo)
def cargar_datos_contratos(ruta_csv='data/contratos.csv'):
    if not os.path.exists(ruta_csv):
        # Retorna un DataFrame vacío si no existe el archivo
        return pd.DataFrame(columns=[
            'DNI / C.E.', 'Apellidos y nombres', 'Régimen Laboral', 'Tipo de Contrato',
            'Act', 'Usuario', 'Nº Celular', 'Fch. VENCIMIENTO', 'Email'])
    return pd.read_csv(ruta_csv)

# Funciones de consulta

# Buscar vencimiento de contrato por nombre (Apellidos y nombres)
def buscar_vencimiento_por_nombre(df, valor):
    valor = valor.lower()
    fila = df[(df['Apellidos y nombres'].str.lower() == valor) |
              (df['DNI / C.E.'].astype(str).str.lower() == valor) |
              (df['Email'].str.lower() == valor)]
    if fila.empty:
        return None
    datos = fila.iloc[0]
    return {
        'nombre': datos['Apellidos y nombres'],
        'fecha_vencimiento': datos['Fch. VENCIMIENTO'],
        'estado': datos['Act']
    }

# Listar contratos que vencen en un mes (por Fch. VENCIMIENTO)
def listar_contratos_por_mes(df, mes):
    df['mes_vencimiento'] = pd.to_datetime(df['Fch. VENCIMIENTO']).dt.month
    meses = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    mes_num = [k for k, v in meses.items() if v == mes.lower()]
    if not mes_num:
        return []
    return df[df['mes_vencimiento'] == mes_num[0]][['Apellidos y nombres', 'Tipo de Contrato', 'Fch. VENCIMIENTO']].to_dict('records')

# Estado del correo de bienvenida (por nombre, DNI o Email)
def estado_correo_bienvenida(df, valor):
    valor = valor.lower()
    fila = df[(df['Apellidos y nombres'].str.lower() == valor) |
              (df['DNI / C.E.'].astype(str).str.lower() == valor) |
              (df['Email'].str.lower() == valor)]
    if fila.empty:
        return None
    datos = fila.iloc[0]
    correo_bienvenida = datos['Act'].lower() == 'activo'
    return {
        'nombre': datos['Apellidos y nombres'],
        'correo_bienvenida': correo_bienvenida,
        'fecha_envio_correo': datos['Fch. VENCIMIENTO'] if correo_bienvenida else None
    }

# Buscar número de celular por nombre, DNI o Email
def buscar_celular(df, valor):
    valor = valor.lower()
    fila = df[(df['Apellidos y nombres'].str.lower() == valor) |
              (df['DNI / C.E.'].astype(str).str.lower() == valor) |
              (df['Email'].str.lower() == valor)]
    if fila.empty:
        return None
    datos = fila.iloc[0]
    return {
        'nombre': datos['Apellidos y nombres'],
        'celular': datos['Nº Celular']
    }

# Buscar email por nombre, DNI o Email
def buscar_email(df, valor):
    valor = valor.lower()
    fila = df[(df['Apellidos y nombres'].str.lower() == valor) |
              (df['DNI / C.E.'].astype(str).str.lower() == valor) |
              (df['Email'].str.lower() == valor)]
    if fila.empty:
        return None
    datos = fila.iloc[0]
    return {
        'nombre': datos['Apellidos y nombres'],
        'email': datos['Email']
    }
