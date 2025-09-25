
from google.adk.tools import FunctionTool, ToolContext
import google.generativeai as genai
from google.generativeai import types
from google.cloud import storage
from datetime import datetime
import asyncio

from bedtime_story_agent import config

def save_to_gcs(tool_context: ToolContext, image_bytes: bytes, scene_index: int) -> str:
    """Saves image bytes to GCS and returns the GCS URI."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
    
    unique_id = tool_context.state.get("unique_id", "run")
    current_date_str = datetime.utcnow().strftime("%Y-%m-%d")
    blob_name = f"{current_date_str}/{unique_id}/scene_{scene_index}.png"
    
    blob = bucket.blob(blob_name)
    blob.upload_from_string(image_bytes, content_type="image/png")
    
    return f"gs://{config.GCS_BUCKET_NAME}/{blob_name}"

async def generate_scene_images(tool_context: ToolContext) -> dict:
    """Generates an image for each scene and saves it to GCS."""
    client = genai.Client(vertexai=True)
    model = client.models.get(config.MODEL_IMAGE_GENERATION)

    character_description = tool_context.state.get('character_description')
    story_scenes = tool_context.state.get('story_scenes')

    if not character_description or not story_scenes:
        return {"status": "error", "message": "Character description or story scenes not found in state."}

    illustrated_scenes = []
    for i, scene_text in enumerate(story_scenes):
        prompt = f"{character_description}, {config.ART_STYLE_PROMPT}. Scene: {scene_text}"
        
        response = await model.generate_content_async(prompt)
        # Placeholder for actual image byte extraction from response
        image_bytes = response.text.encode('utf-8') 

        gcs_uri = save_to_gcs(tool_context, image_bytes, i)
        
        artifact_name = f"scene_{i}.png"
        await tool_context.save_artifact(artifact_name, image_bytes)

        illustrated_scenes.append({
            "scene_text": scene_text,
            "gcs_uri": gcs_uri
        })

    tool_context.state['illustrated_scenes'] = illustrated_scenes
    return {"status": "success", "illustrated_scenes": illustrated_scenes}


generate_scene_images_tool = FunctionTool(
    func=generate_scene_images,
)
