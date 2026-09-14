# Start from the official RunPod worker-comfyui base image
FROM runpod/worker-comfyui:5.1.0-base

# =============================================================================
# Install Custom Nodes
# =============================================================================
# We use the GitHub URLs to ensure we get exactly the repos previously installed.
RUN comfy-node-install \
    https://github.com/Comfy-Org/ComfyUI-Manager \
    https://github.com/ltdrdata/ComfyUI-Impact-Pack \
    https://github.com/ltdrdata/ComfyUI-Impact-Subpack \
    https://github.com/ssitu/ComfyUI_UltimateSDUpscale \
    https://github.com/rgthree/rgthree-comfy \
    https://github.com/alexopus/ComfyUI-Image-Saver \
    https://github.com/kijai/ComfyUI-KJNodes \
    https://github.com/willmiao/ComfyUI-Lora-Manager \
    https://github.com/pythongosssss/ComfyUI-Custom-Scripts \
    https://github.com/Miosp/ComfyUI-FBCNN \
    https://github.com/Fannovel16/comfyui_controlnet_aux \
    https://github.com/cubiq/ComfyUI_IPAdapter_plus \
    https://github.com/KohakuBlueleaf/z-tipo-extension \
    https://github.com/pamparamm/ComfyUI-ppm \
    https://github.com/1038lab/ComfyUI-QwenVL \
    https://github.com/mirabarukaso/ComfyUI_Mira \
    https://github.com/shadowcz007/comfyui-mixlab-nodes

# comfyui_controlnet_aux pulls in scipy>=1.14 which requires NumPy>=2.0,
# but the base image ships NumPy 1.26.4. Pin scipy to a compatible version.
RUN pip install "scipy<1.14"

# =============================================================================
# Download Models
# =============================================================================
# Switch to bash — required for array syntax (pids=(), pids+=($!)) used below.
# /bin/sh (dash) is Docker's default and does not support bash arrays.
SHELL ["/bin/bash", "-c"]

# All models are downloaded in parallel using curl with retries.
# Removed unused 6.6GB FLUX ControlNet to stay well within build time/size limits.
RUN set -euo pipefail; \
    mkdir -p /comfyui/models/checkpoints \
             /comfyui/models/vae/SDXL \
             /comfyui/models/loras \
             /comfyui/models/upscale_models \
             /comfyui/models/sams \
             /comfyui/models/ultralytics/bbox \
             /comfyui/models/ultralytics/segm; \
    pids=(); \
    \
    # Checkpoint (~7 GB) \
    curl -fL --retry 3 --retry-delay 2 -sS \
        -o /comfyui/models/checkpoints/waiIllustriousSDXL_v170.safetensors \
        "https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/resolve/main/waiIllustriousSDXL_v170.safetensors" & pids+=($!); \
    \
    # VAE (~330 MB) \
    curl -fL --retry 3 --retry-delay 2 -sS \
        -o /comfyui/models/vae/SDXL/sdxl_vae.safetensors \
        "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors" & pids+=($!); \
    \
    # LoRA (~150 MB) \
    curl -fL --retry 3 --retry-delay 2 -sS \
        -o /comfyui/models/loras/UmaDiffusionXL_4th.safetensors \
        "https://huggingface.co/Astathe/uma/resolve/main/UmaDiffusionXL_4th.safetensors" & pids+=($!); \
    \
    # Upscale model (~64 MB) \
    curl -fL --retry 3 --retry-delay 2 -sS \
        -o /comfyui/models/upscale_models/4x_foolhardy_Remacri.pth \
        "https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/4x_foolhardy_Remacri.pth" & pids+=($!); \
    \
    # SAM (~375 MB) \
    curl -fL --retry 3 --retry-delay 2 -sS \
        -o /comfyui/models/sams/sam_vit_b_01ec64.pth \
        "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth" & pids+=($!); \
    \
    # Ultralytics bbox detectors \
    curl -fL --retry 3 --retry-delay 2 -sS \
        -o /comfyui/models/ultralytics/bbox/face_yolov9c.pt \
        "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov9c.pt" & pids+=($!); \
    curl -fL --retry 3 --retry-delay 2 -sS \
        -o /comfyui/models/ultralytics/bbox/hand_yolov9c.pt \
        "https://huggingface.co/Bingsu/adetailer/resolve/main/hand_yolov9c.pt" & pids+=($!); \
    curl -fL --retry 3 --retry-delay 2 -sS \
        -o /comfyui/models/ultralytics/bbox/Eyeful_v2-Paired.pt \
        "https://huggingface.co/GritTin/LoraStableDiffusion/resolve/c7766cc3c9b8b4f914932ce27f1cd48f25434636/Eyeful_v2-Paired.pt" & pids+=($!); \
    \
    # Ultralytics segm detector \
    curl -fL --retry 3 --retry-delay 2 -sS \
        -o /comfyui/models/ultralytics/segm/ntd11_anime_nsfw_segm_v5-variant1.pt \
        "https://huggingface.co/adbrasi/wanlotest/resolve/main/ntd11_anime_nsfw_segm_v5-variant1.pt" & pids+=($!); \
    \
    # Wait for all downloads and propagate any failure \
    failed=0; \
    for pid in "${pids[@]}"; do \
        wait "$pid" || failed=$?; \
    done; \
    exit $failed

# =============================================================================
# RunPod SDK and Custom Handler
# =============================================================================
# Install dependencies
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Copy the comfy-manager-set-mode helper (called by start.sh at runtime)
COPY scripts/comfy-manager-set-mode.sh /usr/local/bin/comfy-manager-set-mode
RUN chmod +x /usr/local/bin/comfy-manager-set-mode

# Copy handler, workflow, and startup script
WORKDIR /
COPY handler.py /handler.py
COPY src/network_volume.py /network_volume.py
COPY src/start.sh /start.sh
COPY ["Advanced_Gemma_V38 UMA.json", "/workflow.json"]
COPY ["Advanced_Gemma_V38 UMA API.json", "/workflow_api.json"]
RUN chmod +x /start.sh

# Start using the custom handler
CMD ["/start.sh"]