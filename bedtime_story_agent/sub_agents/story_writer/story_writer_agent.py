from google.adk.agents import Agent
from bedtime_story_agent import config
from .tools.story_writer_tool import write_story_tool

story_writer_agent = Agent(
    name="StoryWriterAgent",
    model=config.MODEL_TEXT_GENERATION,
    instruction=(
        "Your task is to write a bedtime story. "
        "To do this, you must invoke the `write_story` tool."
    ),
    tools=[write_story_tool],
    output_key="story_output",
)