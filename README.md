
# Bedtime Story Agent

This agent creates personalized, illustrated, and narrated bedtime stories.

## Overview

The Bedtime Story Agent is an AI-powered agent that generates a complete, multi-scene bedtime story from a single user-provided image. It leverages a team of specialized sub-agents, built using the Agent Development Kit (ADK), to perform a sequence of tasks:

1.  **Character Creation**: Analyzes a user-provided image to create a description of a cartoon character.
2.  **Story Writing**: Writes a unique, 6-7 scene story featuring the character.
3.  **Illustration**: Generates a unique image for each scene of the story.
4.  **Audio Narration**: Creates a full audiobook of the story with a calming narrator's voice.

## Setup and Installation

1.  **Prerequisites**
    *   Python 3.11+
    *   A Google Cloud Platform (GCP) project with the AI Platform and Text-to-Speech APIs enabled.
    *   Authenticated `gcloud` CLI.

2.  **Installation**

    ```bash
    # Clone this repository (or navigate to the agent's directory)
    # cd bedtime_story_agent

    # Create a virtual environment
    python3 -m venv .venv

    # Activate the virtual environment
    source .venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    pip install -e .
    ```

3.  **Configuration**

    *   Copy the `.env.example` file to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and add your GCP Project ID and your GCS bucket name.

        ```
        GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
        GCS_BUCKET_NAME="your-gcs-bucket-name"
        # This URI tells the ADK to use your GCS bucket for artifact storage.
        ARTIFACT_SERVICE_URI="gs://your-gcs-bucket-name"
        ```

    *   Authenticate with Google Cloud:
        ```bash
        gcloud auth application-default login
        gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
        ```

## Running the Agent

Before running the agent, ensure your virtual environment is activated:

```bash
source .venv/bin/activate
```

You can run the agent using the ADK's command-line interface.

```bash
adk run bedtime_story_agent
```

To run the agent, you will need to provide the initial input, which includes the path to the image and an optional prompt. The exact format for passing this input will depend on the final implementation of the ADK runner.

Alternatively, you can interact with the agent via a web interface:

```bash
adk web
```

Navigate to the provided URL, select `bedtime_story_agent`, and provide the necessary inputs.

## Final Output

The agent will produce a JSON object containing the story details and the names of the generated artifacts (images and audio), which will be saved in your configured GCS bucket.
