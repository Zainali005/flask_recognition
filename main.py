from flask import Flask, request, jsonify
import speech_recognition as sr
from difflib import SequenceMatcher
from flask_cors import CORS
from pydub import AudioSegment
import io

app = Flask(__name__)
CORS(app)

paragraph = "The quick brown fox jumps over the lazy dog."

def evaluate_pronunciation(user_speech):
    similarity = SequenceMatcher(None, paragraph.lower(), user_speech.lower()).ratio()
    return round(similarity * 100, 2)

@app.route('/get-paragraph', methods=['GET'])
def get_paragraph():
    return jsonify({"paragraph": paragraph})

@app.route('/evaluate', methods=['POST'])
def evaluate():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file found"}), 400

    audio_file = request.files['audio']
    audio_data = audio_file.read()
    
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
    except:
        return jsonify({"error": "Invalid audio format"}), 400

    wav_buffer = io.BytesIO()
    audio.export(wav_buffer, format="wav")
    wav_buffer.seek(0)

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_buffer) as source:
        audio = recognizer.record(source)

    try:
        user_speech = recognizer.recognize_google(audio)
        accuracy = evaluate_pronunciation(user_speech)
        return jsonify({"recognized_text": user_speech, "accuracy": accuracy})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand the audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech recognition service error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
