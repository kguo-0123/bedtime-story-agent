#!/bin/bash

# This script downloads the generated images and audio from GCS and uses FFmpeg
# to create a final video.

# --- Configuration ---
# The GCS path you provided for the generated assets.
GCS_PATH="gs://jane-first-project-adk-staging/2025-09-25/97fa7d83-a789-4974-a8bd-0a04428ca7b7"

# The local directory where we'll do the work.
WORK_DIR="./generated_story_video"

# The final output video file.
FINAL_VIDEO="bedtime_story.mp4"

# --- Script Start ---

echo "Starting video creation process..."

# 1. Check for FFmpeg
if ! command -v ffmpeg &> /dev/null
then
    echo "Error: ffmpeg is not installed."
    echo "Please install it to proceed. If you use Homebrew, run: brew install ffmpeg"
    exit 1
fi

# 2. Create a clean working directory
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

echo "Downloading assets from GCS..."

# 3. Download all image and audio files from GCS
gsutil -m cp "$GCS_PATH/*.png" "$GCS_PATH/*.mp3" "$WORK_DIR/"

if [ $? -ne 0 ]; then
    echo "Error: Failed to download files from GCS. Please check the path and your permissions."
    exit 1
fi

echo "Assets downloaded successfully."

# 4. Create a video clip for each scene
cd "$WORK_DIR" || exit

for i in {0..6}
do
    SCENE_IMAGE="scene_${i}.png"
    SCENE_AUDIO="scene_${i}_audio.mp3"
    OUTPUT_CLIP="clip_${i}.mp4"

    if [ -f "$SCENE_IMAGE" ] && [ -f "$SCENE_AUDIO" ]; then
        echo "Creating video clip for scene ${i}..."
        # -loop 1: loop the input image
        # -i "$SCENE_IMAGE": the input image
        # -i "$SCENE_AUDIO": the input audio
        # -c:v libx264: use the H.264 video codec
        # -tune stillimage: optimize for static images
        # -c:a aac: use the AAC audio codec
        # -b:a 192k: set audio bitrate to 192kbps
        # -pix_fmt yuv420p: use a common pixel format for compatibility
        # -shortest: make the video clip as long as the shortest input (the audio)
        ffmpeg -loop 1 -i "$SCENE_IMAGE" -i "$SCENE_AUDIO" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "$OUTPUT_CLIP" -y
    else
        echo "Warning: Assets for scene ${i} not found. Skipping."
    fi
done

# 5. Concatenate all video clips into the final video
echo "Concatenating all clips into the final video..."

# Create a file list for FFmpeg to concatenate
for f in clip_*.mp4; do echo "file '$f'" >> file_list.txt; done

if [ -f "file_list.txt" ]; then
    # -f concat: use the concatenation function
    # -safe 0: allow unsafe file paths (needed for this method)
    # -i file_list.txt: the list of files to join
    # -c copy: copy the streams without re-encoding for speed
    ffmpeg -f concat -safe 0 -i file_list.txt -c copy "../$FINAL_VIDEO" -y
    echo "Final video created: ../$FINAL_VIDEO"
else
    echo "Error: No video clips were created to concatenate."
    cd ..
    exit 1
fi

# 6. Clean up temporary files
cd ..
rm -rf "$WORK_DIR"

echo "Cleanup complete."
echo "Video generation finished successfully!"
