
from google.adk.tools import FunctionTool, ToolContext
import google.generativeai as genai
import json

from bedtime_story_agent import config

async def write_story(tool_context: ToolContext) -> dict:
    """Writes a 6-7 scene bedtime story based on a character description."""
    client = genai.Client(vertexai=True)
    model = client.models.get(config.MODEL_TEXT_GENERATION)

    character_description = tool_context.state.get('character_description')
    user_prompt = tool_context.state.get('user_prompt', "a fun adventure")

    if not character_description:
        return {"status": "error", "message": "Character description not found in state."}

    prompt = (
        f"You are a creative author of children's bedtime stories. "
        f"Your task is to write a short, gentle, and positive story with 6-7 scenes. "
        f"The main character is: {character_description}.\n"
        f"The story should be about: {user_prompt}.\n"
        f"Your output must be a JSON object containing two keys: 'story_scenes' "
        f"(a list of strings, where each string is a scene's narrative) and 'full_narrative' "
        f"(the concatenated text of all scenes)."
    )

    response = await model.generate_content_async(prompt)

    json_response_text = response.text.strip().replace('
', '').replace('```json', '').replace('```', '')
    story_data = json.loads(json_response_text)

    tool_context.state['story_scenes'] = story_data.get('story_scenes')
    tool_context.state['full_narrative'] = story_data.get('full_narrative')

    return {"status": "success", "story_data": story_data}

write_story_tool = FunctionTool(
    func=write_story,
)
