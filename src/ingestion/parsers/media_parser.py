import whisper
from moviepy.editor import VideoFileClip
from pathlib import Path
from typing import List
from src.ingestion.schemas import DocumentElement
from src.core.config import settings

class MediaParser:
    """
    Media Worker responsible for extracting text from Audio and Video files.
    Uses OpenAI Whisper for Speech-to-Text (STT).
    """
    def __init__(self):
        print("🎧 Loading OpenAI Whisper Model (this may take a moment)...")
        # We use the 'base' model: a great balance between speed and accuracy.
        # Options: 'tiny', 'base', 'small', 'medium', 'large'
        self.model = whisper.load_model("base")
        print("✅ Whisper Model Loaded.")

    def parse(self, path: Path) -> List[DocumentElement]:
        # Determine if it's a video or audio file
        if path.suffix.lower() in ['.mp4', '.mkv', '.mov', '.avi']:
            return self._parse_video(path)
        else:
            return self._parse_audio(path)

    def _parse_audio(self, path: Path) -> List[DocumentElement]:
        try:
            print(f"🎙️ Transcribing audio: {path.name}...")
            # transcribe() returns a dictionary containing the full text and segments
            result = self.model.transcribe(str(path))
            
            # We split the transcript into segments to keep the "Chunking" logic
            elements = []
            for i, segment in enumerate(result['segments']):
                elements.append(
                    DocumentElement(
                        element_type="text",
                        content=segment['text'].strip(),
                        source_file=path.name,
                        metadata={
                            "start": segment['start'],
                            "end": segment['end'],
                            "segment_index": i,
                            "method": "whisper_stt"
                        }
                    )
                )
            return elements
            
        except Exception as e:
            print(f"❌ Error transcribing audio {path.name}: {e}")
            return []

    def _parse_video(self, path: Path) -> List[DocumentElement]:
        try:
            print(f"🎥 Extracting audio from video: {path.name}...")
            # Create a temporary path for the extracted audio
            temp_audio_path = settings.TEMP_DIR / f"{path.stem}_temp_audio.wav"
            
            # Use MoviePy to extract the audio track
            video = VideoFileClip(str(path))
            video.audio.write_audiofile(str(temp_audio_path), logger=None)
            video.close()
            
            # Now use the existing audio parser logic on the extracted wav file
            elements = self._parse_audio(temp_audio_path)
            
            # Clean up the temporary audio file
            if temp_audio_path.exists():
                temp_audio_path.unlink()
                
            return elements
            
        except Exception as e:
            print(f"❌ Error processing video {path.name}: {e}")
            return []