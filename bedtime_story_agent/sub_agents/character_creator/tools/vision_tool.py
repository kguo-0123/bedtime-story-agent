from google.adk.tools import FunctionTool, ToolContext
import google.generativeai as genai
from google.generativeai import types

from bedtime_story_agent import config

async def analyze_image_for_character_description(tool_context: ToolContext) -> dict:
    """Analyzes the user-provided image and generates a cartoon character description."""
    client = genai.Client(vertexai=True)
    model = client.models.get(config.MODEL_TEXT_GENERATION)

    image_artifact_name = tool_context.state.get('user_image_artifact_name')
    if not image_artifact_name:
        return {"status": "error", "message": "Image artifact name not found in session state."}

    image_bytes = await tool_context.load_artifact(image_artifact_name)
    if not image_bytes:
        return {"status": "error", "message": f"Artifact {image_artifact_name} not found or is empty."}

    image_part = types.Part(inline_data=types.Blob(data=image_bytes, mime_type="image/png"))

    prompt = (
        "You are a creative assistant. Analyze the provided image of a child and create a detailed, "
        "friendly, and imaginative description of a cartoon character inspired by the child. "
        "Focus on key features like hair color, eye color, and clothing, but translate them into a "
        "charming cartoon style. Do not mention the real child. The description should be reusable "
        "as a prompt for generating images of this character. For example: 'A cheerful cartoon boy "
        "with curly brown hair, bright blue eyes, and wearing a red t-shirt with a star on it.'"
    )

    response = await model.generate_content_async([image_part, prompt])

    character_description = response.text
    tool_context.state['character_description'] = character_description

    return {"status": "success", "character_description": character_description}

vision_tool = FunctionTool(
    func=analyze_image_for_character_description,
)