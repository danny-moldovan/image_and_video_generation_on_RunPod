echo "Installing dependencies for FramePack started"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126 --upgrade
pip install -r FramePack/requirements.txt --upgrade
echo "Installing dependencies for FramePack done"

# echo "Copying models to FramePack started"
# mkdir -p FramePack/hf_download
# cp -r /workspace/FramePack/hf_download FramePack/
# echo "Copying models to FramePack done"

mkdir -p FramePack/hf_download
ln -s /workspace/FramePack/hf_download FramePack/hf_download

echo "Starting FastAPI app serving FramePack server"
python -m uvicorn FramePack_serving.app:app --host 0.0.0.0 --port 8000
echo "FastAPI app serving FramePack server started"