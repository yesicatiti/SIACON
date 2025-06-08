import streamlit as st
from chatbot.bot import responder
import pandas as pd
import os

st.set_page_config(page_title="Chatbot Contratos RRHH-TI", page_icon="🤖")
st.title("🤖 Chatbot Interno de Contratos y Accesos")

# Menú de opciones para elegir el tipo de chat
opciones = [
    "Consulta de contratos por vencimiento",
    "Ver todos los contratos",
    "Chat libre (pregunta lo que quieras)",
    "Buscar número de celular por nombre",
    "Buscar email por nombre",
    "Contratos por régimen laboral",
    "Contratos por tipo de contrato",
    "Contratos por usuario"
]
modo = st.selectbox("Selecciona el tipo de consulta:", opciones)

if 'history' not in st.session_state:
    st.session_state['history'] = []

# Cargar el CSV adaptado
contratos_path = os.path.join('data', 'contratos.csv')
df = pd.read_csv(contratos_path)

# Renombrar columnas si es necesario para mantener consistencia
col_rename = {
    'Fch. VENCIMIENTO': 'Fch. VENCIMIENTO',
    'Fch. Vto.': 'Fch. VENCIMIENTO',
    'Nº Celular': 'Nº Celular',
    'Email': 'Email',
    'DNI / C.E.': 'DNI / C.E.',
    'Apellidos y nombres': 'Apellidos y nombres',
    'Régimen Laboral': 'Régimen Laboral',
    'Tipo de Contrato': 'Tipo de Contrato',
    'Act': 'Act',
    'Usuario': 'Usuario'
}
df.rename(columns=col_rename, inplace=True)

# Seleccionar solo las columnas requeridas
columnas_requeridas = [
    'DNI / C.E.', 'Apellidos y nombres', 'Régimen Laboral', 'Tipo de Contrato',
    'Act', 'Usuario', 'Nº Celular', 'Fch. VENCIMIENTO', 'Email'
]
df = df[columnas_requeridas]

if modo == "Consulta de contratos por vencimiento":
    fecha = st.text_input("Fecha de vencimiento (YYYY-MM-DD o solo año-mes):")
    if st.button("Consultar") and fecha:
        # Filtrar por fecha exacta o por mes
        if len(fecha) == 7:  # año-mes
            resultados = df[df['Fch. VENCIMIENTO'].astype(str).str.startswith(fecha)]
        else:
            resultados = df[df['Fch. VENCIMIENTO'].astype(str) == fecha]
        if not resultados.empty:
            st.dataframe(resultados)
            from io import BytesIO
            output = BytesIO()
            resultados.to_excel(output, index=False, engine='openpyxl')
            st.download_button('Exportar resultados a Excel', output.getvalue(), file_name='contratos_vencidos.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            st.info("No se encontraron contratos para esa fecha.")
elif modo == "Ver todos los contratos":
    st.dataframe(df)
    from io import BytesIO
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    st.download_button('Exportar todos a Excel', output.getvalue(), file_name='contratos_todos.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
elif modo == "Chat libre (pregunta lo que quieras)":
    st.info("""
Puedes escribir preguntas abiertas como:
- ¿Qué contratos vencen en 2025-07?
- ¿Cuál es el email de un empleado?
- ¿Qué número de celular tiene tal persona?
El bot intentará interpretar tu consulta de la mejor manera posible.
""")
    user_input = st.text_input("Escribe tu pregunta:")
    if st.button("Enviar") and user_input:
        respuesta = responder(user_input)
        st.session_state['history'].append((user_input, respuesta))
elif modo == "Buscar número de celular por nombre":
    st.write("Puedes ingresar nombre, DNI o email:")
    valor = st.text_input("Nombre, DNI o Email del empleado:")
    if st.button("Buscar") and valor:
        from chatbot.datos import buscar_celular
        resultado = buscar_celular(df, valor)
        if resultado:
            st.success(f"El número de celular de {resultado['nombre']} es {resultado['celular']}")
        else:
            st.error("No se encontró información para ese valor.")
elif modo == "Buscar email por nombre":
    st.write("Puedes ingresar nombre o DNI:")
    valor = st.text_input("Nombre o DNI del empleado:")
    if st.button("Buscar") and valor:
        from chatbot.datos import buscar_email
        resultado = buscar_email(df, valor)
        if resultado:
            st.success(f"El email de {resultado['nombre']} es {resultado['email']}")
        else:
            st.error("No se encontró información para ese valor.")
elif modo == "Contratos por régimen laboral":
    regimen = st.selectbox("Selecciona el régimen laboral:", df['Régimen Laboral'].unique())
    if st.button("Consultar") and regimen:
        resultados = df[df['Régimen Laboral'] == regimen]
        if not resultados.empty:
            st.dataframe(resultados)
            from io import BytesIO
            output = BytesIO()
            resultados.to_excel(output, index=False, engine='openpyxl')
            st.download_button('Exportar resultados a Excel', output.getvalue(), file_name='contratos_regimen.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            st.info("No se encontraron contratos para ese régimen laboral.")
elif modo == "Contratos por tipo de contrato":
    tipo_contrato = st.selectbox("Selecciona el tipo de contrato:", df['Tipo de Contrato'].unique())
    if st.button("Consultar") and tipo_contrato:
        resultados = df[df['Tipo de Contrato'] == tipo_contrato]
        if not resultados.empty:
            st.dataframe(resultados)
            from io import BytesIO
            output = BytesIO()
            resultados.to_excel(output, index=False, engine='openpyxl')
            st.download_button('Exportar resultados a Excel', output.getvalue(), file_name='contratos_tipo.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            st.info("No se encontraron contratos para ese tipo de contrato.")
elif modo == "Contratos por usuario":
    usuario = st.selectbox("Selecciona el usuario:", df['Usuario'].unique())
    if st.button("Consultar") and usuario:
        resultados = df[df['Usuario'] == usuario]
        if not resultados.empty:
            st.dataframe(resultados)
            from io import BytesIO
            output = BytesIO()
            resultados.to_excel(output, index=False, engine='openpyxl')
            st.download_button('Exportar resultados a Excel', output.getvalue(), file_name='contratos_usuario.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            st.info("No se encontraron contratos para ese usuario.")

st.markdown("---")
st.subheader("Historial de consultas")
for pregunta, respuesta in reversed(st.session_state['history']):
    st.markdown(f"**Tú:** {pregunta}")
    st.markdown(f"**Bot:** {respuesta}")
