# transcribe.py

import whisper

import os



# Load Whisper model

model = whisper.load_model("base")



def transcribe_audio_local(audio_path: str) -> str:

    """

    Transcribes an audio file using Whisper and returns plain text.

    """

    if not os.path.exists(audio_path):

        return f"File not found: {audio_path}"



    try:

        result = model.transcribe(audio_path)

        return result["text"]

    except Exception as e:

        return f"Transcription failed: {str(e)}"



# Build the full path safely

# audio_path = os.path.join(os.path.dirname(__file__), "calls", "120250613094357OUTBOUNDSAMPLE_02.mp3")



# print("Trying to transcribe:", audio_path)



# # Run transcription

# res = transcribe_audio_local(audio_path)

# print(res)

# # transcribe.py
# import whisper
# import os

# # Load Whisper model
# model = whisper.load_model("base")

# def transcribe_audio_local(audio_path: str) -> str:
#     """
#     Transcribes an audio file using Whisper and returns plain text.
#     """
#     if not os.path.exists(audio_path):
#         return f"File not found: {audio_path}"

#     try:
#         result = model.transcribe(audio_path)
#         return result["text"]
#     except Exception as e:
#         return f"Transcription failed: {str(e)}"

# # Build the full path safely
# audio_path = os.path.join(os.path.dirname(__file__), "calls", "demo.mp3")

# print("Trying to transcribe:", audio_path)

# # Run transcription
# res = transcribe_audio_local(audio_path)
# print(res)
