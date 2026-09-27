def get_voice_input():
    import speech_recognition as sr

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\n=== VOICE INPUT ===")
        print("Adjusting for background noise...")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("Speak now! I am listening...")

        try:
            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=10
            )

        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None

    print("Processing your voice...")

    try:
        text = recognizer.recognize_google(audio)

        print(f"You said: '{text}'")

        return text

    except sr.UnknownValueError:
        print("Could not understand the audio.")
        return None

    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return None
