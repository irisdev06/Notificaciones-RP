import streamlit as st
from views.proceso1 import procesar_archivos
from views.proceso2 import procesar_archivos2

# Título
st.title("🔔 Alertas RP")

# Menú 
opciones_menu = ["Notificación Alerta", "Notificación Botón"]

# Mostrar el menú en la barra lateral
opcion_seleccionada = st.sidebar.selectbox("Seleccione un proceso", opciones_menu)

# ------------------------------------------------------------------------------ Proceso 1 ---------------------------------------------------------------------------------
if opcion_seleccionada == "Notificación Alerta":
    st.subheader("Graficación año DTO y PCL")
    procesar_archivos()  
# ------------------------------------------------------------------------------ Notificación Botón ---------------------------------------------------------------------------------
elif opcion_seleccionada == "Notificación Botón":
    st.subheader("Graficación Medicina Laboral")
    procesar_archivos2()
else:
    st.write("Por favor, selecciona un proceso del menú.")