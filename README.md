# Agenda de Reunión en Streamlit

Visualización simple de una agenda de reunión (sin dataset). Permite crear items, reordenarlos, ver la programación en formato tabla y timeline, y exportar a CSV/JSON/Markdown/ICS.

## Deploy en Streamlit Community Cloud (desde GitHub)
1. Crea un repositorio nuevo en GitHub y sube `app.py` y `requirements.txt`.
2. Ve a https://share.streamlit.io/, conecta tu cuenta de GitHub y selecciona el repositorio y la rama.
3. En "Main file path" coloca `app.py` y lanza el deploy.
4. Listo. Comparte la URL.

## Ejecutar local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Uso
- Define la fecha, hora, título y metadatos en el sidebar.
- Agrega items con tema, responsable y duración.
- Reordena con los botones por item.
- Visualiza en tabla o en timeline (Gantt).
- Exporta a CSV/JSON/Markdown/ICS.
