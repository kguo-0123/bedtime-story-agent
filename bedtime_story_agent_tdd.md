### **Technical Design Document: Bedtime Story Agent**

**Version:** 1.4
**Author:** Senior Software Engineer
**Date:** September 24, 2025

### 1. Overview

This document outlines the technical design for the "Bedtime Story Agent," an AI-powered agent that generates personalized, illustrated, and narrated bedtime stories for children. The agent will leverage a multi-agent architecture, orchestrating specialized sub-agents to handle distinct tasks: character creation, story writing, illustration, and audio narration. The primary input is a user-provided image of a child, which is used to create a unique cartoon character that becomes the protagonist of the story.

### 2. Goals and Non-Goals

#### **Goals**

*   To create a personalized 5-minute bedtime story consisting of 6-7 scenes.
*   To generate a unique, cartoon-style main character based on a user-uploaded image.
*   To produce a unique narrative for each story.
*   To generate a unique illustration for each scene, featuring the main character and matching the scene's narrative.
*   To generate a single audio file (MP3 or similar) narrating the entire story.
*   To structure the system as a team of collaborating agents using the Agent Development Kit (ADK).

#### **Non-Goals**

*   **Real-time generation:** The process will be asynchronous due to the multiple steps involved. We will not aim for instantaneous story creation.
*   **User interaction during story generation:** The user provides the initial image and prompt, but will not interact with the agent during the creation process in v1. This includes a character approval step.
*   **Complex character animation:** Illustrations will be static images, not animated videos.

### 3. High-Level Architecture

The system will be built as a `SequentialAgent` within the ADK framework. This root agent, the `BedtimeStoryAgent`, will orchestrate a series of specialized sub-agents, passing state between them using the ADK's `Session State`.

```
+-----------------------+
|   User (via an API)   |
|  - Uploads image      |
|  - Provides prompt    |
+-----------+-----------+
            |
            v
+---------------------------+
|  BedtimeStoryAgent (Root) | (SequentialAgent)
|---------------------------|
|  1. CharacterCreatorAgent |
|  2. StoryWriterAgent      |
|  3. SceneIllustratorAgent |
|  4. AudiobookGeneratorAgent |
+-----------+-----------+
            |
            v
+-----------------------+
|  Final Output (JSON)  |
|  - story_scenes: []   |
|  - audiobook_gcs_uri  |
+-----------------------+
```

### 4. ADK Implementation Details

*   **Agent Definition**: Each sub-agent (`CharacterCreatorAgent`, `StoryWriterAgent`, etc.) will be an instance of `google.adk.agents.Agent`. Each will be configured with a specific model, instructions, and a list of tools.

*   **Orchestration**: The top-level `BedtimeStoryAgent` will be an instance of `google.adk.agents.SequentialAgent`. This allows for a deterministic, step-by-step execution of the sub-agents in the correct order. If one agent fails, the sequence will halt.

*   **Tool Definition**: All tools (e.g., `vision_tool`, `generate_image_tool`) will be defined as `google.adk.tools.FunctionTool`. These tools will encapsulate the logic for interacting with external APIs and will be explicitly passed to the agents that need them. A `before_tool_callback` can be used to inject additional data or log tool inputs, such as constructing the final, detailed prompt for image generation.

*   **State Management**: The `google.adk.agents.CallbackContext` will be used as the single source of truth for the workflow. Data produced by one agent (e.g., `character_description`) will be written to `callback_context.state` and read by subsequent agents.

### 5. Configuration Management

Inspired by the `image-scoring` sample, a central `config.py` file will be used to manage key constants and settings. This improves maintainability and allows for easy adjustments.

*   `MODEL_TEXT_GENERATION = "gemini-2.5-flash"`
*   `MODEL_IMAGE_GENERATION = "gemini-2.5-flash"`
*   `MODEL_AUDIO_GENERATION = "gemini-2.5-flash"`
*   `ART_STYLE_PROMPT = "in a gentle, friendly cartoon style suitable for a children's bedtime story"`
*   `NARRATOR_VOICE = "en-US-Wavenet-J"` (Example voice)

### 6. Agent & Component Breakdown

#### **6.1. `CharacterCreatorAgent`**

*   **Responsibility:** To analyze the user-provided image and generate a detailed, reusable textual description of a cartoon character.
*   **Tools:**
    *   `vision_tool`: Uses `Gemini 2.5 Flash` to analyze the image and generate the `character_description` string.

#### **6.2. `StoryWriterAgent`**

*   **Responsibility:** To write a 6-7 scene bedtime story.
*   **Tools:**
    *   `write_story_tool`: Calls `Gemini 2.5 Flash` with a controlled, text-only context to produce a structured JSON output containing `story_scenes` and `full_narrative`.

#### **6.3. `SceneIllustratorAgent`**

*   **Responsibility:** To orchestrate the creation of an illustration for each scene.
*   **Tools:**
    *   `generate_scene_images_tool`: Iterates through the `story_scenes`. For each scene, it generates an image, directly uploads it to Google Cloud Storage (GCS), and returns a list of dictionaries containing the scene text and the public `gcs_uri` for each image.

#### **6.4. `AudiobookGeneratorAgent`**

*   **Responsibility:** To convert the full story narrative into a single audio file.
*   **Tools:**
    *   `text_to_speech_tool`: Generates the audio from `full_narrative`, directly uploads the MP3 file to GCS, and returns the public `gcs_uri` for the audio file.

### 7. Workflow and Final Output

The `BedtimeStoryAgent` (`google.adk.agents.SequentialAgent`) manages the workflow. The final, successful output of the agent run will be a JSON object stored in the `output` key of the `CallbackContext`, structured as follows:

```json
{
  "character_description": "A cheerful cartoon boy...",
  "story_title": "The Magical Forest Adventure",
  "scenes": [
    {
      "scene_text": "Once upon a time, a boy named Leo...",
      "gcs_uri": "gs://your-bucket-name/2025-09-24/run-id/scene_0.png"
    },
    {
      "scene_text": "He followed a sparkling butterfly...",
      "gcs_uri": "gs://your-bucket-name/2025-09-24/run-id/scene_1.png"
    }
  ],
  "audiobook_gcs_uri": "gs://your-bucket-name/2025-09-24/run-id/story_audio.mp3"
}
```

### 8. Error Handling

*   **Tool Failure:** Each `FunctionTool` will include `try...except` blocks. If an API call fails (e.g., image generation returns an error), the tool will return a dictionary with `{"status": "error", "message": "..."}`. This will be logged by the agent.
*   **Agent Failure:** The `SequentialAgent` will halt execution if any sub-agent fails. The error message from the failing tool or agent will be propagated up, ensuring that the run terminates gracefully and the issue can be diagnosed.
*   **Validation:** The `StoryWriterAgent` is critical. If it fails to produce a valid JSON with the expected structure, the sequence cannot continue. A validation step can be added in the `StoryWriterAgent` itself or as a `before_tool_callback` in the `SceneIllustratorAgent` to check the data structure before proceeding.

### 9. Testing Strategy

*   **Unit Tests:** Each `FunctionTool` will have a corresponding unit test that mocks its external API calls. This verifies the tool's internal logic (e.g., prompt construction) without incurring API costs.
*   **Agent Tests:** Each sub-agent will be tested individually by providing mock data in the `CallbackContext` and asserting that the correct tools are called with the expected parameters.
*   **Integration Test:** A full integration test will run the entire `BedtimeStoryAgent` sequence with a sample image, using real (but potentially lower-cost) model settings to ensure the end-to-end workflow and state transitions function correctly.

### 10. Risks and Mitigations

*   **Character Inconsistency:** The generated illustrations might not look like the same character in every scene.
    *   **Mitigation:** The `character_description` must be highly detailed. The `generate_scene_images_tool` will be carefully engineered to prepend this description to every image generation request.
*   **Inappropriate Content:** The models could generate non-child-friendly text or images.
    *   **Mitigation:** All agent and tool prompts will have strong safety instructions. We will use the highest safety filter levels available on the respective models.

### 11. Future Enhancements

*   **User-in-the-loop:** Add a `CharacterApprovalAgent` after the `CharacterCreatorAgent`. This would be a `HumanInputAgent` that presents the character description and a sample image to the user for approval before proceeding.
*   **Custom Art Styles:** The `art_style_prompt` in `config.py` can be exposed as a user-selectable option.
*   **Personalization:** Allow the user to provide more details (e.g., child's name, favorite animal) that are passed into the `CallbackContext` and used by the `StoryWriterAgent`.