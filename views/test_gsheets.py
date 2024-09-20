
import streamlit as st

st.session_state["count"] = 0
st.session_state["text"] = "ISSO"

texto = st.session_state["text"]

st.write(texto)

if st.button("Change"):
  if st.session_state["count"] % 2 == 0:
    st.session_state["text"] = "AQUILO"
    st.session_state["count"] += 1
  elif st.session_state["count"] % 2 == 1:
    st.session_state["text"] = "Aquilo Outro"
    st.session_state["count"] += 1

st.write(texto)

