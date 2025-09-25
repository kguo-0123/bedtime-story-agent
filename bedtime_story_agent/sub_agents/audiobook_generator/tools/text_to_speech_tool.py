from google.adk.tools import FunctionTool, ToolContext
from google.cloud import texttospeech, storage
from datetime import datetime

from bedtime_story_agent import config

def save_to_gcs(tool_context: ToolContext, audio_bytes: bytes) -> str:
    """Saves audio bytes to GCS and returns the GCS URI."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
    
    unique_id = tool_context.state.get("unique_id", "run")
    current_date_str = datetime.utcnow().strftime("%Y-%m-%d")
    blob_name = f"{current_date_str}/{unique_id}/story_audio.mp3"
    
    blob = bucket.blob(blob_name)
    blob.upload_from_string(audio_bytes, content_type="audio/mpeg")
    
    return f"gs://{config.GCS_BUCKET_NAME}/{blob_name}"

async def generate_audio_from_text(tool_context: ToolContext) -> dict:
    """Generates an audio file from the full story narrative using Gemini TTS."""
    try:
        full_narrative = tool_context.state.get('full_narrative')
        if not full_narrative:
            return {"status": "error", "message": "Full narrative not found in state."}

        client = texttospeech.TextToSpeechAsyncClient()

        synthesis_input = texttospeech.SynthesisInput(text=full_narrative)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Studio-O",
            model=config.MODEL_AUDIO_GENERATION
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = await client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        audio_bytes = response.audio_content
        
        gcs_uri = save_to_gcs(tool_context, audio_bytes)
        tool_context.state['audiobook_gcs_uri'] = gcs_uri

        # Also save to ADK artifact system for internal consistency
        artifact_name = "story_audio.mp3"
        await tool_context.save_artifact(artifact_name, audio_bytes)

        return {"status": "success", "audiobook_gcs_uri": gcs_uri}

    except Exception as e:
        return {"status": "error", "message": str(e)}

text_to_speech_tool = FunctionTool(
    func=generate_audio_from_text,
)