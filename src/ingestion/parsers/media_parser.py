import openai
from moviepy.editor import VideoFileClip
from pathlib import Path
from typing import List
from src.ingestion.schemas import DocumentElement
from src.core.config import settings

class MediaParser:
    """
    Media Worker responsible for extracting text from Audio and Video files.
    Uses Groq's cloud Whisper API for Speech-to-Text (STT) to save RAM.
    """
    def __init__(self):
        print("🎧 Initializing Cloud Audio Transcription Client (Groq)...")
        if not getattr(settings, "GROQ_API_KEY", None):
            raise ValueError("GROQ_API_KEY is required for cloud audio transcription.")
        self.client = openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY
        )
        self.model = "whisper-large-v3" # Groq's free, lightning-fast Whisper model
        print("✅ Cloud Audio Client Initialized.")

    def parse(self, path: Path) -> List[DocumentElement]:
        # Determine if it's a video or audio file
        if path.suffix.lower() in ['.mp4', '.mkv', '.mov', '.avi']:
            return self._parse_video(path)
        else:
            return self._parse_audio(path)

    def _parse_audio(self, path: Path) -> List[DocumentElement]:
        try:
            print(f"🎙️ Sending audio to Groq API: {path.name}...")
            
            with open(path, "rb") as audio_file:
                # We request verbose_json to get segment timestamps
                result = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.model,
                    response_format="verbose_json"
                )
            
            # OpenAI/Groq verbose_json returns an object, not a dict. 
            elements = []
            segments = getattr(result, "segments", [])
            
            if not segments:
                # Fallback if the API only returns a single text block
                elements.append(
                    DocumentElement(
                        element_type="text",
                        content=getattr(result, "text", ""),
                        source_file=path.name,
                        metadata={"method": "groq_whisper_stt"}
                    )
                )
                return elements
                
            for i, segment in enumerate(segments):
                # segment is typically a pydantic model or dict depending on SDK version
                seg_text = segment.text if hasattr(segment, "text") else segment.get("text", "")
                seg_start = segment.start if hasattr(segment, "start") else segment.get("start", 0)
                seg_end = segment.end if hasattr(segment, "end") else segment.get("end", 0)
                
                elements.append(
                    DocumentElement(
                        element_type="text",
                        content=seg_text.strip(),
                        source_file=path.name,
                        metadata={
                            "start": seg_start,
                            "end": seg_end,
                            "segment_index": i,
                            "method": "groq_whisper_stt"
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
            
            if video.audio is None:
                print(f"⚠️ Video {path.name} has no audio track. Skipping transcription.")
                video.close()
                return []
                
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