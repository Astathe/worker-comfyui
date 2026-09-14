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
    https://github.com/yolain/ComfyUI-Easy-Use \
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

# =============================================================================
# Download Models
# =============================================================================
# Switch to bash — required for array syntax (pids=(), pids+=($!)) used below.
# /bin/sh (dash) is Docker's default and does not support bash arrays.
SHELL ["/bin/bash", "-c"]

# All models are downloaded in parallel to stay within the 30-minute build limit.
# Each download is backgrounded (&); pids are collected and checked individually
# so the build fails immediately if any single download exits non-zero.
# Only models actually referenced by the workflow are downloaded here.
# Unused models (SDXL ControlNets, IP-Adapters, CLIP Vision) have been
# removed to keep the build well within RunPod's 30-minute limit.
RUN set -euo pipefail; \
    pids=(); \
    \
    # Checkpoint (~7 GB) \
    comfy model download \
        --url "https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/resolve/main/waiIllustriousSDXL_v170.safetensors" \
        --relative-path models/checkpoints \
        --filename waiIllustriousSDXL_v170.safetensors & pids+=($!); \
    \
    # ControlNet — Union Pro (~4 GB, used by workflow ControlNetLoader node) \
    comfy model download \
        --url "https://huggingface.co/Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro/resolve/main/diffusion_pytorch_model.safetensors" \
        --relative-path models/controlnet \
        --filename "FLUX.1-dev-ControlNet-Union-Pro .safetensors" & pids+=($!); \
    \
    # VAE (~330 MB) \
    comfy model download \
        --url "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors" \
        --relative-path models/vae/SDXL \
        --filename sdxl_vae.safetensors & pids+=($!); \
    \
    # LoRA (~150 MB) \
    comfy model download \
        --url "https://huggingface.co/Astathe/uma/resolve/main/UmaDiffusionXL_4th.safetensors?download=true" \
        --relative-path models/loras \
        --filename UmaDiffusionXL_4th.safetensors & pids+=($!); \
    \
    # Upscale model (~64 MB) \
    comfy model download \
        --url "https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/4x_foolhardy_Remacri.pth" \
        --relative-path models/upscale_models \
        --filename 4x_foolhardy_Remacri.pth & pids+=($!); \
    \
    # SAM (~375 MB) \
    comfy model download \
        --url "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth" \
        --relative-path models/sams \
        --filename sam_vit_b_01ec64.pth & pids+=($!); \
    \
    # Ultralytics bbox detectors \
    comfy model download \
        --url "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov9c.pt" \
        --relative-path models/ultralytics/bbox \
        --filename face_yolov9c.pt & pids+=($!); \
    comfy model download \
        --url "https://huggingface.co/Bingsu/adetailer/resolve/main/hand_yolov9c.pt" \
        --relative-path models/ultralytics/bbox \
        --filename hand_yolov9c.pt & pids+=($!); \
    comfy model download \
        --url "https://huggingface.co/GritTin/LoraStableDiffusion/resolve/c7766cc3c9b8b4f914932ce27f1cd48f25434636/Eyeful_v2-Paired.pt" \
        --relative-path models/ultralytics/bbox \
        --filename Eyeful_v2-Paired.pt & pids+=($!); \
    \
    # Ultralytics segm detector \
    comfy model download \
        --url "https://huggingface.co/adbrasi/wanlotest/resolve/main/ntd11_anime_nsfw_segm_v5-variant1.pt" \
        --relative-path models/ultralytics/segm \
        --filename ntd11_anime_nsfw_segm_v5-variant1.pt & pids+=($!); \
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