from pathlib import Path
import textwrap

import pandas as pd
import streamlit as st

from batch_processing import extract_queries
from inference import DEFAULT_MODEL_DIR, ResponseGenerator


st.set_page_config(page_title="Customer Support Assistant", page_icon="💬", layout="centered")


@st.cache_resource(show_spinner="Loading the response-generation model...")
def load_generator(model_dir: str) -> ResponseGenerator:
    return ResponseGenerator(model_dir)


st.title("Customer Support Assistant")
st.caption("Encoder-decoder response generation for orders, billing, refunds, connectivity, and accounts.")

with st.sidebar:
    st.subheader("Application")
    model_directory = st.text_input("Model folder", value=str(DEFAULT_MODEL_DIR))
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    generator = load_generator(model_directory)
except Exception as error:
    st.error(f"The model could not be loaded: {error}")
    st.info("Place the saved Keras models and tokenizer in the Assgnment folder, or set the model folder in the sidebar.")
    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask a customer-support question...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Drafting response..."):
            response = generator.generate(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

st.divider()
st.subheader("Batch responses")
st.write("Upload a text file with one query per line or a CSV containing a query, question, instruction, text, or message column.")
uploaded_file = st.file_uploader("Upload queries", type=["txt", "csv"])

if uploaded_file is not None:
    try:
        queries = extract_queries(uploaded_file)
    except Exception as error:
        st.error(f"Could not read the uploaded file: {error}")
    else:
        st.write(f"Found {len(queries)} quer{'y' if len(queries) == 1 else 'ies'}.")
        if st.button("Generate batch responses", type="primary", disabled=not queries):
            with st.spinner("Generating responses..."):
                responses = [generator.generate(query) for query in queries]
            results = pd.DataFrame({"query": queries, "response": responses})
            display_results = results.copy()
            display_results["response"] = display_results["response"].map(
                lambda response: textwrap.fill(response, width=75)
            )
            st.dataframe(
                display_results,
                use_container_width=True,
                hide_index=True,
                height=min(700, 120 + len(display_results) * 220),
                row_height=220,
                column_config={
                    "query": st.column_config.TextColumn("Query", width="medium"),
                    "response": st.column_config.TextColumn(
                        "Generated response", width="large"
                    ),
                },
            )
            st.download_button(
                "Download responses as CSV",
                data=results.to_csv(index=False).encode("utf-8"),
                file_name="customer_support_responses.csv",
                mime="text/csv",
            )
