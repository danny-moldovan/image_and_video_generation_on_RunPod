git clone https://github.com/lllyasviel/FramePack.git
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126 --upgrade
pip install -r FramePack/requirements.txt --upgrade

git clone https://github.com/danny-moldovan/image_and_video_generation_on_RunPod.git
cp -r image_and_video_generation_on_RunPod/. .
pip install -r FramePack_serving/requirements.txt
mv demo_gradio.py FramePack/
mv download_models_for_FramePack.py FramePack/
chmod +x start_ollama.sh
chmod +x start_framepack.sh
chmod +x monitor_pod_and_terminate.py
pip install runpod python-dotenv asyncio

cp /workspace/clip_l.safetensors ComfyUI/models/text_encoders/
mkdir -p ComfyUI/models/text_encoders/t5
cp /workspace/t5xxl_fp16.safetensors ComfyUI/models/text_encoders/t5/
cp /workspace/ae.safetensors ComfyUI/models/vae/
cp /workspace/pulsar-male-gay-nsfw-base-model-flux-990314.safetensors ComfyUI/models/checkpoints/

mkdir -p FramePack/hf_download
cp /workspace/FramePack/hf_download FramePack/hf_download

python -m uvicorn FramePack_serving.app:app --host 0.0.0.0 --port 8000