"""
Standalone TTS Worker Script
=============================
Synthesizes a single text string into a WAV file in an isolated process.
Prevents Windows COM / SAPI event loop collisions across multiple utterances.
"""

import sys
import pyttsx3


def main():
    if len(sys.argv) < 3:
        print("Usage: python tts_worker.py <text> <output_wav>")
        sys.exit(1)

    text = sys.argv[1]
    output_wav = sys.argv[2]

    engine = pyttsx3.init()
    engine.setProperty("rate", 155)
    engine.setProperty("volume", 1.0)

    # Prefer female/natural voice if available, else default
    voices = engine.getProperty("voices")
    for v in voices:
        if "zira" in v.name.lower() or "david" in v.name.lower():
            engine.setProperty("voice", v.id)
            break

    engine.save_to_file(text, output_wav)
    engine.runAndWait()
    print(f"[TTSWorker] Synthesized audio to {output_wav}")


if __name__ == "__main__":
    main()
