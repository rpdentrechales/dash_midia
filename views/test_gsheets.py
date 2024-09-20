
import streamlit as st

st.session_state["count"] = 0
st.session_state["text"] = "ISSO"

texto = st.session_state["text"]

st.write(texto)

def change_state():
  if st.session_state["count"] % 2 == 0:
    st.session_state["text"] = "AQUILO"
  
  elif st.session_state["count"] % 2 == 1:
    st.session_state["text"] = "Aquilo Outro"
  
  st.session_state["count"] += 1

st.button("change",on_click = change_state)

st.write(st.session_state["text"])
st.write(st.session_state["count"])

