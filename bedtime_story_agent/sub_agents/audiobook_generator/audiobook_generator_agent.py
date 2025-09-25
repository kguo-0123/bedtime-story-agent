
from google.adk.agents import Agent
from bedtime_story_agent import config
from .tools.text_to_speech_tool import text_to_speech_tool

audiobook_generator_agent = Agent(
    name="AudiobookGeneratorAgent",
    model=config.MODEL_AUDIO_GENERATION,
    instruction=(
        "Your task is to generate an audiobook from the story's full narrative. "
        "You must use the text_to_speech_tool to perform this task. "
        "The full narrative will be available in the session state."
    ),
    tools=[text_to_speech_tool],
    output_key="audiobook_output",
)
