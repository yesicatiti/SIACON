# Chatbot Interno para Consulta de Contratos

Este proyecto implementa un asistente virtual para RRHH y TI que responde consultas frecuentes sobre contratos, vencimientos y accesos.

## Tecnologías principales
- Python 3.x
- pandas (manejo de datos)
- SQLite (opcional, para persistencia)
- ChatterBot (chatbot)
- Streamlit (interfaz web)

## Funcionalidades
- Consulta de vencimiento de contrato por nombre
- Listado de contratos que vencen en un mes
- Consulta de estado de correo de bienvenida

## Instalación rápida
1. Clona este repositorio o copia los archivos en tu entorno local.
2. Instala las dependencias:
   ```bash
   pip install pandas chatterbot chatterbot_corpus streamlit openpyxl
   ```
3. Ejecuta la app:
   ```bash
   streamlit run app.py
   ```

## Estructura sugerida
- `app.py`: Interfaz principal con Streamlit
- `data/contratos.xlsx`: Archivo de datos de ejemplo
- `chatbot/`: Lógica del bot e intents
- `README.md`: Este archivo

## Notas
- Asegúrate de tener Python 3.8 o superior.
- Los datos personales deben protegerse y no mostrarse innecesariamente.
- El bot es extensible para nuevos intents y fuentes de datos.

---

Para dudas o mejoras, contacta al equipo de TI.
