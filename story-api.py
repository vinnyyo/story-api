from fastapi import FastAPI, File, UploadFile, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import shutil
import uuid
import openai
from io import BytesIO
from fastapi.responses import HTMLResponse, FileResponse
import tempfile
import json

# token goes here
OPENAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

conversation = []

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("record13-local.html", "r") as f:
        html_content = f.read()
    global conversation 
    conversation = [{"role": "system", "content": "You are a dungeon master for the game dungeons and dragons. You narrate the game as the dungeon master. The user is playing the game. "}]
    return html_content

@app.post("/process_audio")
async def process_audio(audio: UploadFile = File(...)):
    # # Save the uploaded audio file

    # Save the uploaded audio file as a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
        shutil.copyfileobj(audio.file, temp_audio)
        temp_audio.flush()  # Ensure the data is written to disk
    try:
        # Re-open the temporary file and process the audio
        with open(temp_audio.name, "rb") as audio_file:
            try:
                text_response = openai.Audio.transcribe(model='whisper-1', file=audio_file)
            except openai.error.APIConnectionError:
                text_response = openai.Audio.transcribe(model='whisper-1', file=audio_file)

        # Delete the temporary file
        os.unlink(temp_audio.name)
        print("loading")
        print(text_response)
        ai_response = converse_respond(text_response["text"])
        # Return the image URL as a response
        picture = convert_narration_to_picture(ai_response)
        print(picture)
        return JSONResponse([{"words": ai_response, "image": picture}])
    except Exception as err:
        create_dummy_image("static/error.png", err)
        print(err)
        return JSONResponse([{"words": str(err), "image": "http://127.0.0.1/static/error.png"}])

@app.post("/process_text")
async def process_text(request: Request):
    body = await request.json()
    text = body.get("text", "")
    try:
        print("loading")
        ai_response = converse_respond(text)
        # Return the image URL as a response
        picture = convert_narration_to_picture(ai_response)
        print(picture)
        return JSONResponse([{"words": ai_response, "image": picture}])
    except Exception as err:
        create_dummy_image("static/error.png", err)
        print(err)
        return JSONResponse([{"words": str(err), "image": "http://127.0.0.1/static/error.png"}])

def create_dummy_image(output_path: str, message):
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (300, 300), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((100, 100), str(message), fill="black")

    image.save(output_path)


def convert_narration_to_picture(narration):
    response = openai.Completion.create(
      #model="text-davinci-003",
      model="davinci",
      prompt="Convert this text to a descriptive picture:\n\nExample: Scott climbs a tower, then battles the wolf queen.\nOutput: Adventurer standing and facing wolf queen, on top of tower.\n\n" + narration,
      temperature=0,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0.2,
      presence_penalty=0
    )
    print(response)
    output = response["choices"][0]["text"].replace("\n\nOutput: ", "")
    picture_url = convert_description_to_picture(output)
    return picture_url

def convert_description_to_picture(description):
    image = openai.Image.create(
        prompt = "Make a realistic medieval painting: " + description,
        size='1024x1024'
    )
    # Return the image URL as a response
    image_url = image["data"][0]["url"]
    return image_url

def chat_completion(conversation):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      temperature=0.7,
      max_tokens=556,
      top_p=1,
      frequency_penalty=0.42,
      presence_penalty=0.17,
      messages=conversation
    )
    return response

def converse_respond(message):
    conversation.append({"role": "user", "content": message})
    response = chat_completion(conversation)
    print(conversation)
    print(response)
    responding_message = response["choices"][0]["message"]
    conversation.append({'role':responding_message['role'], 'content': responding_message['content']})
    print(conversation)
    return responding_message["content"]

