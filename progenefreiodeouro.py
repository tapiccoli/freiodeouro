import streamlit as st
import pandas as pd
import openai
import os
import time

# =============================
#  App: progenefreiodeouro
#  Descrição: Chatbot de análise dos dados do Freio de Ouro
# =============================

openai.api_key = os.getenv("OPENAI_API_KEY")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("dadosfreiodeourodomingueiro.xlsx")
    if 'Prova' in df.columns:
        df['Prova'] = df['Prova'].replace({"F.O.": "Freio de Ouro"})
    return df

df = carregar_dados()

st.title("progenefreiodeouro")
st.subheader("Faça uma pergunta livre sobre os dados do Freio de Ouro:")

st.sidebar.markdown("Esses são apenas exemplos para orientar o tipo de pergunta que você pode fazer:")
st.sidebar.markdown("- Quantos domingueiros possuem linhas maternas repetidas?")
st.sidebar.markdown("- Qual o pai com mais filhos finalistas?")
st.sidebar.markdown("- Qual a nota média na coluna 'Final' por categoria?")

pergunta = st.text_input("")

def responder_pergunta(pergunta: str) -> str:
    try:
        # Upload do arquivo
        file_upload = openai.files.create(
            file=open("dadosfreiodeourodomingueiro.xlsx", "rb"),
            purpose="assistants"
        )

        # Criação do assistant
        assistant = openai.beta.assistants.create(
            name="Freio de Ouro Analyst",
            instructions="Você é um especialista em provas do Freio de Ouro. Use o arquivo fornecido para responder perguntas com base nos dados.",
            model="gpt-4-1106-preview",
            tools=[{"type": "file_search"}]
        )

        # Criar thread e enviar a pergunta
        thread = openai.beta.threads.create()

        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=pergunta
        )

        # Executar a IA vinculando o arquivo
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            tool_resources={"file_search": {"file_ids": [file_upload.id]}}
        )

        # Esperar a resposta
        while True:
            status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            elif status.status == "failed":
                return "A execução da IA falhou."
            time.sleep(1)

        # Obter a resposta final
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value
        return resposta

    except Exception as e:
        return f"Erro ao consultar IA com assistant: {e}"

if pergunta:
    with st.spinner("Consultando IA..."):
        resposta = responder_pergunta(pergunta)
    st.markdown("### Resposta:")
    st.markdown(f"<div style='user-select: none;'>{resposta}</div>", unsafe_allow_html=True)
