import streamlit as st

labels = {0:'A',1:'B',2:'C',3:'D'}
letter = st.selectbox(label = 'label',options=range(4),format_func=lambda x:labels[x])

st.write(letter)