
from google.adk.agents import Agent
from bedtime_story_agent import config
from .tools.generate_scene_images_tool import generate_scene_images_tool

scene_illustrator_agent = Agent(
    name="SceneIllustratorAgent",
    model=config.MODEL_IMAGE_GENERATION,
    instruction=(
        "Your task is to generate an illustration for each scene of the story. "
        "You must use the generate_scene_images_tool to perform this task. "
        "The character description and story scenes will be available in the session state."
    ),
    tools=[generate_scene_images_tool],
    output_key="illustrated_scenes_output",
)
