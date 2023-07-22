import requests
import os
import streamlit as st
import io
from PIL import Image
import time
import random
import html
import openai

def generate_story_openai(characters, age, moral):
    # Combine the inputs into a prompt for the model
    characters = html.escape(characters)
    moral = html.escape(moral)

    openai.api_key = st.secrets["openai_key"]
    
    prompt = f"Write a 200 words story about {characters}, for an audience around {age} years old, with a moral that {moral}."

    # Initialize the story
    story = ""

    # Make the POST request
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,  
        temperature=0.9
    )

    # Extract the generated text
    story = response.choices[0].text.strip()

    return story

def generate_story_huggingface(characters, age, moral):
    # Combine the inputs into a prompt for the model
    characters = html.escape(characters)
    moral = html.escape(moral)
    
    prompt = f" Write A story about {characters}, for an audience around {age} years old, with a moral that {moral}. Just write the story with moral in the end and nothing more, do not write any extra text."

    # Set the model id and API URL
    model_id = "OpenAssistant/oasst-sft-1-pythia-12b"
    model_id = "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5"
    
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    # Get the API token from the environment variables
    api_token = st.secrets["nothin"]

    # Set the headers for the API request
    headers = {
        "Authorization": f"Bearer {api_token}",
    }

    # Prepare the payload
    payload = {
        "inputs": prompt,
        "options": {
            "max_length": 500,
            "min_length":100,
            "temperature": 0.9
        }
    }

    # Initialize the story
    story = ""

    # Maximum number of words
    max_words = 500

    while True:
        # Update the inputs in the payload
        payload["inputs"] = prompt + story

        # Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)

        # Raise an exception if the request was not successful
        response.raise_for_status()

        # Extract the generated text
        generated_text = response.json()[0]['generated_text']

        # Remove the prompt from the generated text
        new_story = generated_text[len(payload["inputs"]):]

        # If the new story is empty or the story has reached the maximum number of words, break the loop
        if not new_story.strip() or len(story.split()) >= max_words:
            break

        # Add the new story to the existing story
        story += new_story

    return story

def generate_image(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-davinci-2-1"
    API_URL = "https://api-inference.huggingface.co/models/SG161222/Realistic_Vision_V1.4"
    api_token = st.secrets["nothin"]
    headers = {"Authorization": f"Bearer {api_token}"}
    
    append_prompt = f"comic book style super detailed illustration of {prompt} walking together, highly cute and friendly characters, colorful background, trending on artstation, aimed at children age 6 to 12 years old, simple storytelling, 8k resolution"

    response = requests.post(API_URL, headers=headers, json={"inputs": append_prompt + prompt})
    response.raise_for_status()
    
    image_bytes = response.content
    image = Image.open(io.BytesIO(image_bytes))

    return image

# Creators Information
st.sidebar.markdown("## Creators")
st.sidebar.markdown("[Chandni](https://www.linkedin.com/in/chandni-ramdasan-a7b1571a)")
st.sidebar.markdown("[Harshad](https://www.linkedin.com/in/harshadsuryawanshi)")

st.sidebar.markdown("## Disclaimer")
st.sidebar.markdown("""
Please note that our AI-driven story generator currently utilizes an open-source Language Model (LLM). As with any AI tool, there may be instances where the generated content could be of lower quality or include unintended results. We encourage users to review the generated stories and exercise discretion.
""")

st.title('Story Generator')

characters = st.text_input("Enter the characters for the story:", "A rabbit and a tortoise")
age = st.number_input("Enter the target audience age:", min_value=0, max_value=100, step=1, value=7)
moral = st.text_input("Enter the moral of the story:")
model_choice = st.selectbox("Choose the model for story generation", ["OpenAssistant LLM", "OpenAI"])

if st.button('Generate Story'):
    if characters and age and moral:
        with st.spinner('Generating Story...'):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)  # This is just to simulate the process taking time
                progress_bar.progress(i)
            if model_choice == "OpenAI":
                story = generate_story_openai(characters, age, moral)
                image = generate_image(characters)
                st.image(image, use_column_width=True)  # Display the generated image
            else:
                story = generate_story_huggingface(characters, age, moral)
                image = generate_image(characters)
            progress_bar.empty() 
        st.markdown(story)
        if model_choice == "OpenAssistant LLM":
            st.image(image, use_column_width=True)  # Display the generated image
    else:
        st.write('Please fill in all fields to generate a story.')
