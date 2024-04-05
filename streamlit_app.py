### References: data_professor - https://tinyurl.com/bdhsrm84
# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

import streamlit as st
import json
import openai
import os
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import glob


dir_path = Path.cwd()
data_path = (dir_path / "data").resolve()
images_path = (dir_path / "images").resolve()
temp_path = (dir_path / "temp").resolve()
env_path = (dir_path / ".env").resolve()


OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
    
# Define a function to check if a file is a PDF

def is_pdf_file(file):
    return file.name.endswith('.pdf')

# Streamlit app

# File upload widget

with st.sidebar:
    st.sidebar.title("PDF Upload")
        
    uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is None:
        st.sidebar.success("No file uploaded. Loaded example `**2023 Dental plan benefit table**` PDF from a Delta. Feel free to upload your own plan benefit or EoB pdf...")
        file_path = Path("plans_table.pdf")
            
        def create_contexts(input_path = file_path):

            from pypdf import PdfReader

            reader = PdfReader(input_path)
            text = ""
            contexts = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
                if len(text) > 0:
                    contexts += f"### Here is the context: \n#\n# " 
                    contexts += ''.join(text)
                else:
                    contexts +="### There is no text here"

            return contexts
        
    if uploaded_file is not None:
        if is_pdf_file(uploaded_file):
            st.sidebar.success("PDF file uploaded successfully!")
            file_path = uploaded_file.name
            # Add your chat input or interaction components here
            # st.write("You can now interact with the chat input or other components.")

            def create_contexts(uploaded_file):

                from pypdf import PdfReader

                reader = PdfReader(uploaded_file)
                text = ""
                contexts = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                    if len(text) > 0:
                        contexts += f"### Here is the context: \n#\n# " 
                        contexts += ''.join(text)
                    else:
                        contexts +="### There is no text here"

                return contexts

        else:
            st.sidebar.error("Please upload a valid PDF file.")


if file_path !=None:
    def create_prompt():
        context = create_contexts()
        chat_prompt = [
            {
                "role": "system", #prompt created by chat.openai.com based on prompting.
                "content": 
                    """Your name is `Clarity`. You are a truthful and friendly dental insurance assistant. Your role is to simplify explanation of benefits (EoBs) and plan benefits for members / enrollees. You will already have the context so don't ask the user for it again.
                    Please follow this conversation flow:
                    1. Begin by introducing yourself and role.
                    2. Engage in a natural conversation with the user, addressing any questions or concerns they may have about dental insurance.
                    Remember to maintain a helpful and informative tone throughout the conversation.
                    3. Don't ask again for information they've given you in the chat history.
                    4. If they ask you to recommend a plan based on existing context confirm that it's not your role. That you a simply a conversational AI to make benefits simple to understand.
                    5. Feel free to clean up typos and make conservative guesses about mispelled words. The context is the result of an OCR process.
                    6. Lastly but important, don't make errors, fix typos, be concise and if the question can't be answered based on the context, acknowledge that you don't know and respond with \"I can connect you with a customer service representative who can better assist you if you'd like.\"" Feel free to provide this link [Elijah Adeoye](mailto:eadeoye@deltadentalwa.com). \n#\n
                    ### Here is the context: {}\n#\n#
                    """.format(context)
            }
        ]

        return chat_prompt


    if "messages" not in st.session_state:
        st.session_state.messages = create_prompt()
        print(st.session_state.messages)

    if "num_tokens" not in st.session_state:
        st.session_state.num_tokens = 0

    for message in st.session_state.messages:
        if message["role"] != "system" and message["role"] != "function":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    chat_model = "gpt-4" #"gpt-3.5-turbo-16k-0613" # "gpt-3.5-turbo-0613" #
    def run_conversation(messages):
        response = openai.ChatCompletion.create(
            model=chat_model,
            messages=messages,
            max_tokens = 500,
            temperature = 0.3,
            presence_penalty = 0.2,
            frequency_penalty = 1,
        )

        return response

    # Display assistant response in chat message container
    def generate_reply(query, messages, num_tokens = 0):
                    
            if messages == None and len(messages) == 0:
                    messages = []
                    messages.append(create_system_prompt()[0])
            else:
                    messages.append({"role": "user", "content": query})
                    response_message = run_conversation(messages)
                    assistant_message = response_message["choices"][0]["message"]
                    messages.append(assistant_message)
                    # message_content = response_message["choices"][0]["message"]['content'].replace("\n", " ")
                    num_tokens = response_message["usage"]["total_tokens"]
            
            return num_tokens, messages, assistant_message
        
    import time

    def typing_indicator():
        st.write("Clarity is thinking...")
        # st.timeout(2000)
        st.empty()  # Clears the typing indicator after a few seconds


    if prompt := st.chat_input("Let's chat about your dental benefits!"):
        # st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
                
        with st.chat_message("assistant"):
            typing_indicator()
            print(st.session_state.messages)
            
            st.session_state.num_tokens, st.session_state.messages, assistant_response = generate_reply(prompt, st.session_state.messages, st.session_state.num_tokens)
            message_placeholder = st.empty()
            full_response = ""
            # Simulate stream of response with milliseconds delay

            for chunk in assistant_response['content'].split():
                if "conversation_summary" not in assistant_response and assistant_response != None and assistant_response !="None" and assistant_response !="none":
                    full_response += chunk + " "
                    time.sleep(0.1)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        # Add assistant response to chat history
        # st.session_state.messages.append({"role": "assistant", "content": full_response})
    # print(st.session_state)

st.sidebar.write(f"""
    ### Description
    This application is a Generative AI proof-of-concept. It features an AI chatbot assistant that can intelligently hold long form conversations with dental plan members. This bot helps members provide clarity 😂 and simplify plan benefits, Explanation of Benefits (EoBs), and dental insurance all together. **Note** that this is ***not production-grade*** but a simple deployment for a demonstration. So feel free to break it 😉
    
    ---
    
    ### App info

    **App name**: *Clarity - Your Dental Benefits Assistant*
    
    **How to use**: Upload a plan benefit, brochure, or EOB in **PDF** format and chat away!

    ---

    **How do I make something like this for my organization?**

    Contact **Elijah Adeoye** via email [Elijah Adeoye](mailto:elijah.adeoye@weunveil.ai)
    or [LinkedIn](https://www.linkedin.com/in/elijahaadeoye/)!
    """)
