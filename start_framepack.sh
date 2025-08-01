echo "Installing dependencies for FramePack started"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126 --upgrade
pip install -r FramePack/requirements.txt --upgrade
echo "Installing dependencies for FramePack done"

echo "Copying models to ComfyUI started"
cp /workspace/clip_l.safetensors ComfyUI/models/text_encoders/
mkdir -p ComfyUI/models/text_encoders/t5
cp /workspace/t5xxl_fp16.safetensors ComfyUI/models/text_encoders/t5/
cp /workspace/ae.safetensors ComfyUI/models/vae/
cp /workspace/pulsar-male-gay-nsfw-base-model-flux-990314.safetensors ComfyUI/models/checkpoints/
echo "Copying models to ComfyUI done"

echo "Copying models to FramePack started"
mkdir -p FramePack/hf_download
cp -r /workspace/FramePack/hf_download FramePack/
echo "Copying models to FramePack done"

echo "Starting FastAPI app serving FramePack server"
python -m uvicorn FramePack_serving.app:app --host 0.0.0.0 --port 8000
echo "FastAPI app serving FramePack server started"