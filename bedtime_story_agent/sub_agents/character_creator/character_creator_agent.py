from google.adk.agents import Agent
from bedtime_story_agent import config
from .tools.vision_tool import vision_tool

character_creator_agent = Agent(
    name="CharacterCreatorAgent",
    model=config.MODEL_TEXT_GENERATION,
    instruction=(
        "Your task is to create a character description from a user-provided image. "
        "To do this, you must invoke the `vision_tool`."
    ),
    tools=[vision_tool],
    output_key="character_description",
)