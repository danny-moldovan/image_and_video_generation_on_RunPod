#pip install --upgrade --force-reinstall uvicorn --target /workspace/python_libraries
#export PYTHONPATH="/workspace/python_libraries"
#export PATH=$PATH:/workspace/python_libraries/bin
#cd /workspace
python -m uvicorn FramePack_serving.app:app --host 0.0.0.0 --port 8000