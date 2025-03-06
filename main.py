import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configuración del cliente de Groq
qclient = Groq()

def analyze_voting_intention(text):
    # Etiquetas para votos
    text = str(text).lower()
    if 'noboa' in text:
        return 'Voto Noboa'
    elif 'luisa' in text:
        return 'Voto Luisa'
    else:
        return 'Voto Nulo'

def main():
    st.title("📊 Predicción Electoral")
    st.markdown("Análisis de Votos")

    uploaded_file = st.file_uploader('Cargar archivo de datos (XLSX)', type="xlsx")

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if 'text' not in df.columns:
            st.error("Error al leer archivo ")
            return

        sample_size = st.slider("Publicaciones más relevantes:",
                                min_value=1,
                                max_value=len(df),
                                value=min(10, len(df)))

        sample_df = df.sample(n=sample_size)
        st.write("", sample_df[['text']])

        # Etiquetar votos basado en el texto
        df['intencion_voto'] = df['text'].apply(analyze_voting_intention)

        # Contar los votos
        vote_counts = df['intencion_voto'].value_counts()


        option = st.selectbox("Selecciona una opción:", 
                              ["Opción 1: Gráfico de barras", 
                               "Opción 2: Votos nulos y conclusión", 
                               "Opción 3: Interacción con el chatbot"])

        if option == "Opción 1: Gráfico de barras":
            # Gráfico de barras de intención de voto
            fig = px.bar(
                x=vote_counts.index,
                y=vote_counts.values,
                title="Distribución de Intención de Voto",
                labels={'x': 'Candidato', 'y': 'Cantidad de Menciones'},
                color=vote_counts.index,
                color_discrete_map={
                    'Voto Noboa': 'green',
                    'Voto Luisa': 'black',
                    'Voto Nulo': 'blue'
                }
            )
            st.plotly_chart(fig)

        elif option == "Opción 2: Votos nulos y conclusión":
            votos_nulos = vote_counts.get('Voto Nulo', 0)
            total_votos = len(df)
            porcentaje_nulos = (votos_nulos / total_votos) * 100

            st.markdown("Análisis de Resultados")
            st.markdown("Conclusión")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total de respuestas", total_votos)
            with col2:
                st.metric("Votos nulos", votos_nulos)
            with col3:
                st.metric("Porcentaje nulos", f"{porcentaje_nulos:.2f}%")


            ganador = vote_counts.index[0] if not vote_counts.empty else "No hay datos suficientes"
            st.write(f" El candidato con mas votos es: {ganador}")

        elif option == "Opción 3: Interacción con el chatbot":
            st.markdown("Consultas sobre los datos")
            user_question = st.text_input("Realiza una pregunta sobre los resultados:")

            if user_question:
                with st.spinner("Analizando"):
                    # Preparar un resumen de los datos para el contexto
                    data_summary = f"""
                    Total de respuestas analizadas: {len(df)}
                    Distribución de votos:
                    {vote_counts.to_string()}
                    """

                    response = qclient.chat.completions.create(
                        messages=[
                            {"role": "system",
                             "content": "Eres un analista de votos. Responde preguntas de acuerdo a los resultados de la predicción electoral basándote en los datos proporcionados."},
                            {"role": "user",
                             "content": f"Datos del análisis:\n{data_summary}\n\nPregunta: {user_question}"},
                        ],
                        model="llama3-8B-8192",
                        stream=False
                    )
                    st.write("Respuesta:", response.choices[0].message.content)

if __name__ == "__main__":
    main()
