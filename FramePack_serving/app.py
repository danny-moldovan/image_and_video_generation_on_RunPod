import base64
import io
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import sys
import os
import json
import gzip
import re

# Ensure FramePack is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../FramePack')))

from FramePack import demo_gradio

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health():
    return {"message": "OK"}

    
@app.post('/create_video')
async def create_video(request: Request):
    try:
        data = await request.json()
        image_b64 = data['image']
        prompt = data['prompt']
        total_second_length = data.get('total_second_length', 5)
        # Decode base64 image to numpy array
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        input_image = np.array(image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Invalid input: {e}')

    n_prompt = ""
    seed = 31337
    latent_window_size = 9
    steps = 25
    cfg = 1.0
    gs = 10.0
    rs = 0.0
    gpu_memory_preservation = 6
    use_teacache = True
    mp4_crf = 16

    def event_stream():
        import time
        from FramePack.diffusers_helper.thread_utils import AsyncStream, async_run

        #with demo_gradio.stream.output_queue.lock:
        #    demo_gradio.stream.output_queue.queue.clear()

        demo_gradio.stream = AsyncStream()
        
        async_run(
            demo_gradio.worker,
            input_image,
            prompt,
            n_prompt,
            seed,
            total_second_length,
            latent_window_size,
            steps,
            cfg,
            gs,
            rs,
            gpu_memory_preservation,
            use_teacache,
            mp4_crf
        )
        while True:
            flag, data = demo_gradio.stream.output_queue.next()
            #print('RECEIVED FROM QUEUE:', {'flag': flag, 'data': data})

            if flag == 'progress':
                # Extract the 3rd component of data (which is a tuple)
                if isinstance(data, tuple) and len(data) > 2:
                    third_component = data[2]
                    
                    # Extract string between <span> and </span>
                    span_match = re.search(r'<span[^>]*>(.*?)</span>', third_component)
                    if span_match:
                        progress_text = span_match.group(1)
                        print(f"Sent to the client: {progress_text}")
                        yield json.dumps({'flag': flag, 'data': progress_text}, default=str) + '\n'

                time.sleep(1)

            if flag == 'file':
                print(f"Sent to the client: {data}")
                yield json.dumps({'flag': flag, 'data': data}, default=str) + '\n'
                time.sleep(1)

            if flag == 'end':
                print(f"Sent to the client: {data}")
                yield json.dumps({'flag': flag, 'data': data}, default=str) + '\n'
                break

    from fastapi.responses import StreamingResponse
    return StreamingResponse(event_stream(), media_type='text/plain') 


@app.post('/read_progress_messages')
async def read_progress_messages(request: Request):
    def event_stream():
        import time
        
        while True:
            flag, data = demo_gradio.stream.output_queue.next()
            #print('RECEIVED FROM QUEUE:', {'flag': flag, 'data': data})

            if flag == 'progress':
                # Extract the 3rd component of data (which is a tuple)
                if isinstance(data, tuple) and len(data) > 2:
                    third_component = data[2]
                    
                    # Extract string between <span> and </span>
                    span_match = re.search(r'<span[^>]*>(.*?)</span>', third_component)
                    if span_match:
                        progress_text = span_match.group(1)
                        print(f"Sent to the client: {progress_text}")
                        yield json.dumps({'flag': flag, 'data': progress_text}, default=str) + '\n'

                time.sleep(1)

            if flag == 'file':
                print(f"Sent to the client: {data}")
                yield json.dumps({'flag': flag, 'data': data}, default=str) + '\n'
                time.sleep(1)

            if flag == 'end':
                print(f"Sent to the client: {data}")
                yield json.dumps({'flag': flag, 'data': data}, default=str) + '\n'
                break

    from fastapi.responses import StreamingResponse
    return StreamingResponse(event_stream(), media_type='text/plain') 


@app.post('/test_stream')
def test_stream():
    import time
    def gen():
        for i in range(10):
            yield f"data: {i}\n"
            time.sleep(1)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(gen(), media_type='text/plain')


@app.post('/get_video')
async def get_video(request: Request):
    try:
        data = await request.json()
        filename = data['filename']
        
        # Check if file exists
        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        # Check if file is an MP4 file
        if not filename.lower().endswith('.mp4'):
            raise HTTPException(status_code=400, detail="File must be an MP4 file")
        
        # Read the video file
        with open(filename, 'rb') as video_file:
            video_bytes = video_file.read()
        
        # Gzip compress and base64 encode
        video_compressed = gzip.compress(video_bytes)
        video_encoded = base64.b64encode(video_compressed).decode('utf-8')
        
        return {
            "filename": filename,
            "original_size": len(video_bytes),
            "compressed_size": len(video_compressed),
            "encoded_size": len(video_encoded),
            "compression_ratio": f"{len(video_compressed)/len(video_bytes)*100:.1f}%",
            "video_data": video_encoded
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")