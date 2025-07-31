#!/usr/bin/env python3
from datetime import datetime
import runpod
import asyncio
import os
from dotenv import load_dotenv
import glob

load_dotenv('/root/env')
RUNPOD_API_KEY = os.environ.get('RUNPOD_API_KEY')
runpod.api_key = RUNPOD_API_KEY

runpod_id = os.getenv("RUNPOD_POD_ID")
print(f"Runpod ID: {runpod_id}")

COMFYUI_OUTPUT_FOLDER = '/workspace/ComfyUI_outputs/'
FRAMEPACK_OUTPUT_FOLDER = '/workspace/FramePack_outputs/'


async def _poll_app_utilisation_and_terminate_idle_pod(poll_interval: int = 30, max_idle_time: int = 900):
    """Poll app utilization and terminate idle pod if no requests for specified time"""
    idle_start_time = None
    
    while True:
        await asyncio.sleep(poll_interval)
        
        # Check if there have been any recent files in the output folders
        current_time = datetime.now()
        recent_requests = False
        
        # Check COMFYUI_OUTPUT_FOLDER
        if os.path.exists(COMFYUI_OUTPUT_FOLDER):
            for file_path in glob.glob(os.path.join(COMFYUI_OUTPUT_FOLDER, "**"), recursive=True):
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if (current_time - file_time).total_seconds() <= poll_interval:
                        recent_requests = True
                        break
        
        # Check FRAMEPACK_OUTPUT_FOLDER if no recent files found in ComfyUI folder
        if not recent_requests and os.path.exists(FRAMEPACK_OUTPUT_FOLDER):
            for file_path in glob.glob(os.path.join(FRAMEPACK_OUTPUT_FOLDER, "**"), recursive=True):
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if (current_time - file_time).total_seconds() <= poll_interval:
                        recent_requests = True
                        break
        
        if not recent_requests:
            # No recent requests, start or continue idle timer
            if idle_start_time is None:
                idle_start_time = current_time
                print(f"No recent files in last {poll_interval} seconds, starting idle timer at {idle_start_time}")
            
            # Check if we've been idle for max_idle_time
            idle_duration = (current_time - idle_start_time).total_seconds()
            if idle_duration >= max_idle_time:
                print(f"Pod idle for {idle_duration} seconds, terminating...")
                try:
                    # Terminate the pod
                    runpod.terminate_pod(runpod_id)
                    print(f"Pod {runpod_id} terminated successfully")
                except Exception as e:
                    print(f"Error terminating pod: {e}")
                break
            else:
                print(f"Pod idle for {idle_duration} seconds, {max_idle_time - idle_duration} seconds remaining before termination")
        else:
            # Reset idle timer if there are recent requests
            if idle_start_time is not None:
                print("Recent files detected, resetting idle timer")
                idle_start_time = None


# Start the polling task
try:
    loop = asyncio.get_running_loop()
    loop.create_task(_poll_app_utilisation_and_terminate_idle_pod())
except RuntimeError:
    asyncio.run(_poll_app_utilisation_and_terminate_idle_pod())