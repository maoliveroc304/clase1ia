import json
from datetime import datetime, date, time, timedelta
from typing import List, Dict

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Agenda de Reunión", page_icon="📅", layout="wide")

# -----------------------
# Helpers
# -----------------------
def init_state():
    if "agenda_items" not in st.session_state:
        st.session_state.agenda_items: List[Dict] = []

def to_datetime(d: date, t: time) -> datetime:
    return datetime.combine(d, t)

def compute_schedule(items: List[Dict], meeting_date: date, meeting_start: time) -> pd.DataFrame:
    # Compute start/end sequentially
    start_dt = to_datetime(meeting_date, meeting_start)
    rows = []
    current = start_dt
    for idx, it in enumerate(items, start=1):
        duration = timedelta(minutes=int(it["duration_min"]))
        row = {
            "Orden": idx,
            "Tema": it["topic"],
            "Responsable": it.get("owner") or "",
            "Inicio": current,
            "Fin": current + duration,
            "Duración (min)": int(it["duration_min"]),
            "Notas": it.get("notes") or "",
        }
        rows.append(row)
        current = row["Fin"]
    return pd.DataFrame(rows)

def df_to_ics(df: pd.DataFrame, meeting_title: str) -> str:
    # Basic ICS without TZ conversion
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Streamlit Agenda//ES",
        f"X-WR-CALNAME:{meeting_title}",
    ]
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for _, r in df.iterrows():
        dtstart = r["Inicio"].strftime("%Y%m%dT%H%M%S")
        dtend = r["Fin"].strftime("%Y%m%dT%H%M%S")
        summary = f"{meeting_title} — {r['Tema']}"
        desc_parts = []
        if str(r.get("Responsable", "")).strip():
            desc_parts.append(f"Responsable: {r['Responsable']}")
        if str(r.get("Notas", "")).strip():
            desc_parts.append(f"Notas: {r['Notas']}")
        description = "\n".join(desc_parts)
        uid = f"{dtstart}-{abs(hash(summary))}@streamlit-agenda"
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\n".join(lines)

def df_to_markdown(df: pd.DataFrame, meeting_title: str, meeting_date: date, start_time: time, location: str, description: str) -> str:
    header = f"# {meeting_title}\n\n**Fecha:** {meeting_date.isoformat()}  \\ **Inicio:** {start_time.strftime('%H:%M')}  \\ **Lugar:** {location or '-'}\n\n{description or ''}\n\n"
    body = "| # | Inicio | Fin | Duración | Tema | Responsable | Notas |\n|---:|:-----:|:---:|:-------:|------|-------------|-------|\n"
    for _, r in df.iterrows():
        body += f"| {int(r['Orden'])} | {r['Inicio'].strftime('%H:%M')} | {r['Fin'].strftime('%H:%M')} | {int(r['Duración (min)'])} | {r['Tema']} | {r['Responsable']} | {r['Notas']} |\n"
    return header + body

init_state()

# -----------------------
# Sidebar: meeting meta
# -----------------------
with st.sidebar:
    st.title("📅 Agenda de reunión")
    meeting_title = st.text_input("Título de la reunión", value="Reunión de alineación")
    meeting_date = st.date_input("Fecha", value=date.today())
    meeting_start = st.time_input("Hora de inicio", value=time(9, 0))
    location = st.text_input("Lugar / enlace", value="")
    description = st.text_area("Descripción (opcional)", value="", height=80)
    st.divider()
    uploaded = st.file_uploader("Cargar agenda (JSON)", type=["json"])
    colu1, colu2 = st.columns(2)
    with colu1:
        if st.button("🧹 Limpiar agenda"):
            st.session_state.agenda_items = []
    with colu2:
        if uploaded is not None:
            try:
                data = json.load(uploaded)
                if isinstance(data, list):
                    st.session_state.agenda_items = data
                    st.success("Agenda cargada.")
                else:
                    st.error("El JSON debe ser una lista de items.")
            except Exception as e:
                st.error(f"JSON inválido: {e}")

# -----------------------
# Main: add items
# -----------------------
st.subheader("Alta de items")
with st.form("new_item_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 1.2, 1])
    topic = c1.text_input("Tema")
    owner = c2.text_input("Responsable")
    duration_min = c3.number_input("Duración (min)", min_value=1, max_value=480, value=15, step=5)
    notes = st.text_area("Notas (opcional)", height=80)
    submitted = st.form_submit_button("➕ Agregar")
    if submitted:
        if not topic.strip():
            st.warning("El tema es obligatorio.")
        else:
            st.session_state.agenda_items.append({
                "topic": topic.strip(),
                "owner": owner.strip(),
                "duration_min": int(duration_min),
                "notes": notes.strip(),
            })
            st.toast("Item agregado.", icon="✅")

# -----------------------
# Items table with actions
# -----------------------
if not st.session_state.agenda_items:
    st.info("La agenda está vacía. Agrega tu primer item arriba.")
    st.stop()

st.subheader("Agenda")
items_df = compute_schedule(st.session_state.agenda_items, meeting_date, meeting_start)

# Show actions per row
for i, item in enumerate(st.session_state.agenda_items):
    with st.expander(f"{i+1}. {item['topic']} ({item['duration_min']} min)", expanded=False):
        cc1, cc2, cc3, cc4 = st.columns(4)
        if cc1.button("⬆️ Subir", key=f"up_{i}") and i > 0:
            st.session_state.agenda_items[i-1], st.session_state.agenda_items[i] = st.session_state.agenda_items[i], st.session_state.agenda_items[i-1]
            st.experimental_rerun()
        if cc2.button("⬇️ Bajar", key=f"down_{i}") and i < len(st.session_state.agenda_items)-1:
            st.session_state.agenda_items[i+1], st.session_state.agenda_items[i] = st.session_state.agenda_items[i], st.session_state.agenda_items[i+1]
            st.experimental_rerun()
        if cc3.button("✏️ Editar", key=f"edit_{i}"):
            with st.form(f"edit_form_{i}"):
                e1, e2, e3 = st.columns([2, 1.2, 1])
                new_topic = e1.text_input("Tema", value=item["topic"])
                new_owner = e2.text_input("Responsable", value=item.get("owner", ""))
                new_duration = e3.number_input("Duración (min)", min_value=1, max_value=480, value=int(item["duration_min"]), step=5, key=f"dur_{i}")
                new_notes = st.text_area("Notas", value=item.get("notes", ""), height=80, key=f"notes_{i}")
                ok = st.form_submit_button("Guardar cambios")
                if ok:
                    st.session_state.agenda_items[i] = {
                        "topic": new_topic.strip(),
                        "owner": new_owner.strip(),
                        "duration_min": int(new_duration),
                        "notes": new_notes.strip(),
                    }
                    st.experimental_rerun()
        if cc4.button("🗑️ Eliminar", key=f"del_{i}"):
            st.session_state.agenda_items.pop(i)
            st.experimental_rerun()

# Recompute after potential changes
items_df = compute_schedule(st.session_state.agenda_items, meeting_date, meeting_start)

ctab1, ctab2 = st.tabs(["📋 Tabla", "📈 Timeline (Gantt)"])
with ctab1:
    st.dataframe(
        items_df.assign(
            Inicio=items_df["Inicio"].dt.strftime("%H:%M"),
            Fin=items_df["Fin"].dt.strftime("%H:%M")
        ),
        use_container_width=True,
        hide_index=True,
    )
with ctab2:
    if not items_df.empty:
        gantt_df = items_df.rename(columns={"Inicio":"Start", "Fin":"End", "Tema":"Item"})
        fig = px.timeline(gantt_df, x_start="Start", x_end="End", y="Item", hover_data=["Responsable","Notas","Duración (min)"])
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=420, margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nada que graficar.")

# -----------------------
# Exports
# -----------------------
st.subheader("Exportar")
exp1, exp2, exp3, exp4 = st.columns(4)

csv_bytes = items_df.to_csv(index=False).encode("utf-8")
json_bytes = json.dumps(st.session_state.agenda_items, ensure_ascii=False, indent=2).encode("utf-8")
md_text = df_to_markdown(items_df, meeting_title, meeting_date, meeting_start, location, description)
ics_text = df_to_ics(items_df, meeting_title)

exp1.download_button("📄 CSV", data=csv_bytes, file_name="agenda.csv", mime="text/csv")
exp2.download_button("🧾 JSON", data=json_bytes, file_name="agenda.json", mime="application/json")
exp3.download_button("📝 Markdown", data=md_text.encode("utf-8"), file_name="agenda.md", mime="text/markdown")
exp4.download_button("📆 ICS (calendario)", data=ics_text.encode("utf-8"), file_name="agenda.ics", mime="text/calendar")

st.caption("Tip: guarda y comparte tu JSON para versionar tu agenda desde GitHub.")
