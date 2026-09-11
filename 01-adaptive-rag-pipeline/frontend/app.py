import streamlit as st
import requests

BASE_URL = st.secrets["BACKEND_URL"]

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 RAG Application")

files = st.file_uploader(
    "Upload PDF Files",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Upload Files"):

    if not files:
        st.error("Please upload at least one PDF.")

    else:
        for file in files:

            response = requests.post(
                f"{BASE_URL}/upload",
                files={
                    "file": (
                        file.name,
                        file.getvalue(),
                        file.type
                    )
                }
            )

            if response.status_code == 200:
                st.success(
                    f"{file.name} uploaded successfully."
                )
            else:
                st.error(response.text)

# Display Chat History
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and "sources" in message
            and message["sources"]
        ):

            st.markdown("### 📚 Sources")

            for source in set(message["sources"]):

                st.markdown(f"- {source}")

prompt = st.chat_input(
    "Ask a question about the uploaded document"
)

if prompt:

    # User Message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # API Call
    with st.spinner("Generating answer..."):

        response = requests.post(
            f"{BASE_URL}/ask",
            json={
                "text": prompt
            }
        )

    if response.status_code == 200:

        data = response.json()

        answer = data["answer"]

        sources = data.get(
            "sources",
            []
        )

        # Save Assistant Response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources
            }
        )

        # Display Assistant Response
        with st.chat_message("assistant"):

            st.markdown(answer)

            if sources:

                st.markdown("### 📚 Sources")

                for source in set(sources):

                    st.markdown(
                        f"- {source}"
                    )

    else:

        st.error(response.text)