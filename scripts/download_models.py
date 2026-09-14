#!/usr/bin/env python3
"""
Model download script for ComfyUI worker container build.
Downloads all required model weights with retries, progress reporting,
and parallel execution using Python's standard library.
"""

import argparse
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

MODELS = [
    {
        "name": "waiIllustriousSDXL_v170.safetensors",
        "path": "checkpoints/waiIllustriousSDXL_v170.safetensors",
        "url": "https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/resolve/main/waiIllustriousSDXL_v170.safetensors",
    },
    {
        "name": "sdxl_vae.safetensors",
        "path": "vae/SDXL/sdxl_vae.safetensors",
        "url": "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors",
    },
    {
        "name": "UmaDiffusionXL_4th.safetensors",
        "path": "loras/UmaDiffusionXL_4th.safetensors",
        "url": "https://huggingface.co/Astathe/uma/resolve/main/UmaDiffusionXL_4th.safetensors",
    },
    {
        "name": "4x_foolhardy_Remacri.pth",
        "path": "upscale_models/4x_foolhardy_Remacri.pth",
        "url": "https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/4x_foolhardy_Remacri.pth",
    },
    {
        "name": "sam_vit_b_01ec64.pth",
        "path": "sams/sam_vit_b_01ec64.pth",
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
    },
    {
        "name": "face_yolov9c.pt",
        "path": "ultralytics/bbox/face_yolov9c.pt",
        "url": "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov9c.pt",
    },
    {
        "name": "hand_yolov9c.pt",
        "path": "ultralytics/bbox/hand_yolov9c.pt",
        "url": "https://huggingface.co/Bingsu/adetailer/resolve/main/hand_yolov9c.pt",
    },
    {
        "name": "Eyeful_v2-Paired.pt",
        "path": "ultralytics/bbox/Eyeful_v2-Paired.pt",
        "url": "https://huggingface.co/GritTin/LoraStableDiffusion/resolve/c7766cc3c9b8b4f914932ce27f1cd48f25434636/Eyeful_v2-Paired.pt",
    },
    {
        "name": "ntd11_anime_nsfw_segm_v5-variant1.pt",
        "path": "ultralytics/segm/ntd11_anime_nsfw_segm_v5-variant1.pt",
        "url": "https://huggingface.co/adbrasi/wanlotest/resolve/main/ntd11_anime_nsfw_segm_v5-variant1.pt",
    },
]

CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB
USER_AGENT = "worker-comfyui-builder/1.0"


def format_bytes(size: int) -> str:
    if size >= 1024**3:
        return f"{size / (1024**3):.2f} GB"
    if size >= 1024**2:
        return f"{size / (1024**2):.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"


def download_one(model_info: dict, base_dir: str, max_retries: int = 3, dry_run: bool = False) -> None:
    name = model_info["name"]
    dest_path = os.path.join(base_dir, model_info["path"])
    temp_path = dest_path + ".downloading"
    url = model_info["url"]

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    headers = {"User-Agent": USER_AGENT}

    if dry_run:
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_length = int(resp.headers.get("Content-Length", 0))
            print(f"[DRY-RUN] {name}: {format_bytes(content_length)} (URL valid: {url})", flush=True)
            return

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                total_size = int(resp.headers.get("Content-Length", 0))
                size_str = format_bytes(total_size) if total_size > 0 else "unknown size"

                # Check if destination file already exists with same size
                if os.path.exists(dest_path) and total_size > 0:
                    local_size = os.path.getsize(dest_path)
                    if local_size == total_size:
                        print(f"[SKIP] {name} already exists ({size_str}) at {dest_path}", flush=True)
                        return

                print(f"[START] ({attempt}/{max_retries}) Downloading {name} ({size_str}) -> {dest_path}", flush=True)

                start_time = time.time()
                last_report_time = start_time
                downloaded = 0

                with open(temp_path, "wb") as f:
                    while True:
                        chunk = resp.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        now = time.time()
                        # Report progress at least every 15 seconds or on large transfers
                        if now - last_report_time >= 15:
                            elapsed = now - start_time
                            speed = downloaded / elapsed if elapsed > 0 else 0
                            speed_str = f"{format_bytes(int(speed))}/s"
                            if total_size > 0:
                                pct = (downloaded / total_size) * 100
                                print(
                                    f"[PROGRESS] {name}: {pct:.1f}% ({format_bytes(downloaded)} / {size_str}) @ {speed_str}",
                                    flush=True,
                                )
                            else:
                                print(f"[PROGRESS] {name}: {format_bytes(downloaded)} @ {speed_str}", flush=True)
                            last_report_time = now

                # Verify downloaded file size if content-length was given
                if total_size > 0 and downloaded != total_size:
                    raise IOError(
                        f"Size mismatch for {name}: expected {total_size} bytes, got {downloaded} bytes"
                    )

                # Atomically move temporary file to final path
                os.replace(temp_path, dest_path)
                total_time = max(time.time() - start_time, 0.01)
                avg_speed = format_bytes(int(downloaded / total_time)) + "/s"
                print(f"[DONE] {name} ({format_bytes(downloaded)}) completed in {total_time:.1f}s @ {avg_speed}", flush=True)
                return

        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

            print(f"[WARN] Failed attempt {attempt}/{max_retries} for {name}: {e}", flush=True)
            if attempt < max_retries:
                sleep_s = attempt * 3
                print(f"[RETRY] Retrying {name} in {sleep_s}s...", flush=True)
                time.sleep(sleep_s)
            else:
                print(f"[ERROR] All {max_retries} attempts failed for {name}!", flush=True)
                raise


def main():
    parser = argparse.ArgumentParser(description="Download ComfyUI model files")
    parser.add_argument(
        "--target-dir",
        default=os.environ.get("COMFYUI_MODELS_DIR", "/comfyui/models"),
        help="Base directory for ComfyUI models (default: /comfyui/models)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of concurrent download threads (default: 4)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify model URLs and content-length without downloading files",
    )
    args = parser.parse_args()

    print(f"=== Starting ComfyUI Model Downloader ===", flush=True)
    print(f"Target directory : {args.target_dir}", flush=True)
    print(f"Concurrent workers: {args.workers}", flush=True)
    print(f"Models to check  : {len(MODELS)}", flush=True)
    if args.dry_run:
        print(f"Mode              : DRY RUN", flush=True)
    print("=" * 41, flush=True)

    failed = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_model = {
            executor.submit(download_one, model, args.target_dir, 3, args.dry_run): model
            for model in MODELS
        }

        for future in as_completed(future_to_model):
            model = future_to_model[future]
            try:
                future.result()
            except Exception as e:
                failed.append((model["name"], str(e)))

    if failed:
        print("\n[FATAL] The following models failed to download:", file=sys.stderr, flush=True)
        for name, err in failed:
            print(f"  - {name}: {err}", file=sys.stderr, flush=True)
        sys.exit(1)

    print("\n[SUCCESS] All models downloaded and verified successfully!", flush=True)


if __name__ == "__main__":
    main()
