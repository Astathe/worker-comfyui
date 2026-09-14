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
# Download all workflow models in parallel with retries and progress reporting
COPY scripts/download_models.py /download_models.py
RUN python3 /download_models.py && rm /download_models.py

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
COPY src/custom_nodes/comfyui-core-compat /comfyui/custom_nodes/comfyui-core-compat
RUN chmod +x /start.sh

# Start using the custom handler
CMD ["/start.sh"]