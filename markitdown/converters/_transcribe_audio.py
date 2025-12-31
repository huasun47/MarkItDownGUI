import io
import sys
from typing import BinaryIO
from .._exceptions import MissingDependencyException

# Try loading optional (but in this case, required) dependencies
# Save reporting of any exceptions for later
_dependency_exc_info = None
try:
    # Suppress some warnings on library import
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=SyntaxWarning)
        import speech_recognition as sr
        import pydub
except ImportError:
    # Preserve the error and stack trace for later
    _dependency_exc_info = sys.exc_info()


def transcribe_audio(file_stream: BinaryIO, *, audio_format: str = "wav") -> str:
    # Check for installed dependencies
    if _dependency_exc_info is not None:
        raise MissingDependencyException(
            "Speech transcription requires installing MarkItdown with the [audio-transcription] optional dependencies. E.g., `pip install markitdown[audio-transcription]` or `pip install markitdown[all]`"
        ) from _dependency_exc_info[
            1
        ].with_traceback(  # type: ignore[union-attr]
            _dependency_exc_info[2]
        )

    if audio_format in ["wav", "aiff", "flac"]:
        audio_source = file_stream
    elif audio_format in ["mp3", "mp4"]:
        # Use imageio-ffmpeg directly to avoid pydub/ffprobe dependency
        try:
            import imageio_ffmpeg
            import subprocess
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            # Read input content
            content = file_stream.read()
            
            # Convert to wav using ffmpeg
            process = subprocess.run(
                [ffmpeg_exe, "-i", "pipe:0", "-f", "wav", "pipe:1"],
                input=content,
                capture_output=True,
                check=True
            )
            
            audio_source = io.BytesIO(process.stdout)
        except Exception as e:
            # Fallback to pydub if something fails (though pydub might fail too)
            # or just raise the error
            if _dependency_exc_info is not None:
                 raise MissingDependencyException(
                    "Conversion failed and optional dependencies missing."
                ) from e
            
            # If pydub is available, try it as last resort (but it likely failed before)
            # Actually, let's just raise the ffmpeg error if it occurred
            raise RuntimeError(f"Audio conversion failed: {str(e)}")

    else:
        raise ValueError(f"Unsupported audio format: {audio_format}")

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_source) as source:
        audio = recognizer.record(source)
        transcript = recognizer.recognize_google(audio).strip()
        return "[No speech detected]" if transcript == "" else transcript
