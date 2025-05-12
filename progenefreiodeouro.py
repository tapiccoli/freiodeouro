import streamlit as st
import pandas as pd
import openai
import os
import time

openai.api_key = os.getenv("OPENAI_API_KEY")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("dadosfreiodeourodomingueiro.xlsx")
    return df

df = carregar_dados()

st.title("progenefreiodeouro")
st.markdown("Faça uma pergunta livre sobre os dados do Freio de Ouro:")

pergunta = st.text_input("")

def responder_pergunta(pergunta):
    try:
        # Upload do arquivo
        file = openai.files.create(
            file=open("dadosfreiodeourodomingueiro.xlsx", "rb"),
            purpose="assistants"
        )

        # Criar assistant
        assistant = openai.assistants.create(
            name="Freio de Ouro Analyst",
            model="gpt-4-1106-preview",
            instructions="Você é um especialista em provas do Freio de Ouro. Use o arquivo enviado para responder com precisão.",
            tools=[{"type": "file_search"}]
        )

        # Criar thread e enviar mensagem
        thread = openai.threads.create()

        openai.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=pergunta
        )

        # Executar com o arquivo como ferramenta
        run = openai.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            tool_resources={"file_search": {"file_ids": [file.id]}}
        )

        # Aguardar execução
        while True:
            status = openai.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            elif status.status == "failed":
                return "A execução falhou."
            time.sleep(1)

        # Buscar resposta
        messages = openai.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value

    except Exception as e:
        return f"Erro ao consultar IA com assistant: {e}"

if pergunta:
    with st.spinner("Consultando IA..."):
        resposta = responder_pergunta(pergunta)
    st.markdown("### Resposta:")
    st.markdown(f"<div style='user-select: none'>{resposta}</div>", unsafe_allow_html=True)
