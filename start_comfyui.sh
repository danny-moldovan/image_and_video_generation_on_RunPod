#!/bin/bash

#echo "Copying models to ComfyUI started"
# cp /workspace/clip_l.safetensors ComfyUI/models/text_encoders/
# mkdir -p ComfyUI/models/text_encoders/t5
# cp /workspace/t5xxl_fp16.safetensors ComfyUI/models/text_encoders/t5/
# cp /workspace/ae.safetensors ComfyUI/models/vae/
# cp /workspace/pulsar-male-gay-nsfw-base-model-flux-990314.safetensors ComfyUI/models/checkpoints/
#echo "Copying models to ComfyUI done"

ln -s /workspace/clip_l.safetensors ComfyUI/models/text_encoders/clip_l.safetensors
mkdir -p ComfyUI/models/text_encoders/t5
ln -s /workspace/t5xxl_fp16.safetensors ComfyUI/models/text_encoders/t5/t5xxl_fp16.safetensors
ln -s /workspace/ae.safetensors ComfyUI/models/vae/ae.safetensors
ln -s /workspace/pulsar-male-gay-nsfw-base-model-flux-990314.safetensors ComfyUI/models/checkpoints/pulsar-male-gay-nsfw-base-model-flux-990314.safetensors

cd ComfyUI
python main.py --preview-method auto -- listen