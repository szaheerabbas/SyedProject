
def get_voice_input():
    import speech_recognition as sr

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\n=== MICROPHONE TEST ===")
        print("Adjusting for background noise... Please wait 1 second.")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("Speak now! I am listening...")
        audio_data = recognizer.listen(source)

        print("Processing your voice...")
        try:
            text = recognizer.recognize_google(audio_data)
            print(f"\nYou said: '{text}'")
        except sr.UnknownValueError:
            print("Could not understand the audio. Speak a bit clearer!")
        except sr.RequestError:
            print("Network error. Make sure you are online.")
