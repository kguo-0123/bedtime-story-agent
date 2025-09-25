import uuid
from google.adk.agents import SequentialAgent
from google.adk.agents.callback_context import CallbackContext

from .sub_agents.character_creator.character_creator_agent import character_creator_agent
from .sub_agents.story_writer.story_writer_agent import story_writer_agent
from .sub_agents.scene_illustrator.scene_illustrator_agent import scene_illustrator_agent
from .sub_agents.audiobook_generator.audiobook_generator_agent import audiobook_generator_agent

async def set_session(callback_context: CallbackContext):
    """Initializes the session state from user input, saving the uploaded image as an artifact."""
    # Set a unique ID for this agent run for artifact organization.
    callback_context.state["unique_id"] = str(uuid.uuid4())

    # The text part of the user's input is in state['input']
    user_prompt = callback_context.state.get("input", "")

    # The file/image part of the user's input is in the user_content attribute
    image_bytes = None
    if callback_context.user_content and callback_context.user_content.parts:
        image_part = callback_context.user_content.parts[0]
        image_bytes = image_part.inline_data.data

    if image_bytes:
        await callback_context.save_artifact("user_image.png", image_bytes)
        callback_context.state['user_image_artifact_name'] = "user_image.png"
    
    callback_context.state['user_prompt'] = user_prompt

bedtime_story_agent = SequentialAgent(
    name="BedtimeStoryAgent",
    description="Orchestrates the creation of a personalized bedtime story.",
    sub_agents=[
        character_creator_agent,
        story_writer_agent,
        scene_illustrator_agent,
        audiobook_generator_agent,
    ],
    before_agent_callback=set_session,
)

root_agent = bedtime_story_agent