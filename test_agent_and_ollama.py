from abc import ABC, abstractmethod
from typing import *
import time
from ollama import Client
import requests
import asyncio

class RunpodInstance:
    def __init__(self, runpod_id):
        self.runpod_id = runpod_id

runpod_instance = RunpodInstance('gmbb4g7rl9t7ey')
# Use localhost since Ollama is running locally
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "huihui_ai/qwen3-abliterated:latest"

# Stub implementations for tool functions
def generate_image(prompt: str) -> dict:
    """Stub implementation for image generation"""
    print(f"Would generate image with prompt: {prompt}")
    return {"status": "success", "message": f"Image generation requested for: {prompt}"}

def generate_video(image_b64: str, prompt: str, total_second_length: int = 5) -> dict:
    """Stub implementation for video generation"""
    print(f"Would generate video with prompt: {prompt}, length: {total_second_length}s")
    return {"status": "success", "message": f"Video generation requested for: {prompt}"}

tools=[
    {
      'type': 'function',
      'function': {
            "name": "generate_image",
            "description": "Generates an image based on a prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The prompt (description) based on which the image will be generated"}
                },
                "required": ["prompt"]
            }
        },
    },
    {
      'type': 'function',
      'function': {
            "name": "generate_video",
            "description": "Generates a video from an image and a prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Prompt describing the video to generate."},
                    "total_second_length": {"type": "integer", "description": "Total length of the video in seconds.", "default": 5}
                },
                "required": ["prompt"]
            }
        },
    }
]

class Agent(ABC):
    """
    Abstract base class for AI agents.
    """
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def ask_agent(self, messages: list[dict[str, str]]) -> Any:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: The message to send to the agent
            context: Optional context information for the agent
            
        Returns:
            The agent's response as a string
        """
        pass


class OllamaAgent(Agent):
    """
    A simple implementation of the Agent class using Ollama.
    """
    
    def __init__(self, host_name: str = OLLAMA_HOST, model_name: str = MODEL_NAME, tools: list = tools):
        """
        Initialize the OllamaAgent.
        
        Args:
            host_name: Name of the host
            model_name: Name of the model
        """
        super().__init__()

        self.host_name = host_name
        self.model_name = model_name
        self.tools = tools

        attempts = 0
        max_attempts = 20
        while attempts < max_attempts:
            try:
                response = requests.get(OLLAMA_HOST, timeout=10)
                if response.status_code == 200:
                    print("Ollama is up!")
                    time.sleep(1)
                    break
                else:
                    print(f"Trying to connect to Ollama: got status {response.status_code}, retrying... (attempt {attempts + 1}/{max_attempts})")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                print(f"Trying to connect to Ollama: Ollama is not up yet, retrying... (attempt {attempts + 1}/{max_attempts})")

            attempts += 1
            time.sleep(3)  # wait 3 seconds before retrying
        
        if attempts >= max_attempts:
            print(f"Failed to connect to Ollama after {max_attempts} attempts. Please check if Ollama is running.")
            raise ConnectionError("Could not connect to Ollama service")

        self.ollama_client = Client(host=self.host_name)

        # Simplified system prompt to reduce processing time
        self.system_prompt = {
            "role": "system",
            # "content": (
            #     "You are a helpful assistant. "
            #     "First determine if the user wants to generate an image or a video. Exactly one of these options is possible. If it is not clear, please ask for clarification."
            
            #     "Please construct the prompt for image generation based on the user's request and make it very detailed. Please also add creative elements (for example a fight scene, a nice scenery or romantic setting or dancing or a beach or in the woods) and detailed description of the image, without contradicting the user's request."
            #     "Please add the following phrases to the image generation prompt: ultra detailed, masterpiece, high resolution. Please make sure that the prompt is between 2 and 5 sentences long."
                
            #     "When you receive an input that could be the description of an image or you are specifically asked to generate an image, call the function `generate_image` with JSON argument `prompt` of type string"
            #     "Please construct the prompt for image generation based on the user's request and make it very detailed. Please also add creative elements (for example a fight scene, a nice scenery or romantic setting or dancing or a beach or in the woods) and detailed description of the image, without contradicting the user's request."
            #     "Please add the following phrases to the image generation prompt: ultra detailed, masterpiece, high resolution. Please make sure that the prompt is at most 5 sentences long."
                
            #     "When you receive an input that could be the description of a video or you are specifically asked to generate a video, call the function `generate_video` with JSON arguments `prompt` (which is the description of the video to generate) of type string and `total_second_length` (which is the total length in seconds of the video to generate) of type integer. If total length of the video is not provided by the user, please leave it empty."
            #     "Please construct the prompt for video generation based on the user's request and make it very succint and exact. Please extract it from the user's request, don't add any other creative elements and don't add the following phrases: ultra detailed, masterpiece, high resolution."
                
            #     "Please only call the functions `generate_image` or `generate_video` if you have to, otherwise just return a message to the user."
            #     "If it is not clear what the user wants, please ask for clarification."
            #     "If the description of the image or of the video is not clear or you lack context, please ask for clarification."
            #     "If the input is not related to image generation or video generation, please return a message to the user saying that you can only assist with image generation or video generation. Please mention that you were created for image generation or video generation only."
            # )

            "content": (
                "You are a helpful assistant. Determine if the user wants to generate an image or a video. "
                "If unclear, ask for clarification. For image requests, create a detailed prompt (2–5 sentences) "
                "with creative elements (e.g., fight scene, scenery, romance, beach, woods) and include "
                "'ultra detailed, masterpiece, high resolution'. For video requests, extract the prompt exactly "
                "from the user's request (no extra details) and call `generate_video` with `prompt` (string) "
                "and `total_second_length` (int, or empty if not provided). Only call `generate_image` or "
                "`generate_video` when needed; otherwise reply normally. If the input is unrelated, explain "
                "that you only help with image/video generation."
            )
        }

        print("Agent initialized")

    
    def ask_agent(self, messages: list[dict[str, str]], image_height: int = 256, image_width: int = 256, num_images: int = 4) -> Any:
        """
        Send a list of messages to the agent and get a response.

        Args:
            messages: The list of messages to be sent to the agent
            image_height: The height of the image to be generated
            image_width: The width of the image to be generated
            num_images: The number of images to be generated
            
        Returns:
            The agent's response
        """

        try:
            print("Sending the following messages to the agent:")
            print([m for m in messages if m['role'] == 'user'])
            print()

            print(f"Connecting to Ollama at: {self.host_name}")
            print(f"Using model: {self.model_name}")
            print(f"Number of messages: {len([self.system_prompt] + messages)}")
            
            # Add timeout to the chat request
            start_time = time.time()
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[self.system_prompt] + messages,
                tools=self.tools,
                options={"timeout": 300}  # 5 minute timeout
            )
            end_time = time.time()
            print(f"Ollama response received in {end_time - start_time:.2f} seconds")

            post_processed_response = []

            message_text = response.message.content.strip() if response.message.content is not None else None
            print(f"Raw message from agent: {repr(response.message.content)}")
            if message_text is not None:
                import re
                # Remove <think>...</think> and then strip leading/trailing whitespace
                message_text_clean = re.sub(r'<think>[\s\S]*?</think>', '', message_text).strip()
                print(f"Parsed message text (after strip and remove <think>): {repr(message_text_clean)}")
                if len(message_text_clean) > 0:
                    post_processed_response.append({'response_type': 'message', 'content': message_text_clean})
                    print(f"Appended to post_processed_response: {{'response_type': 'message', 'content': {repr(message_text_clean)}}}")
            
            # Extract tool calls if any
            tool_calls = getattr(response.message, "tool_calls", [])
            print(f"Tool calls found: {len(tool_calls) if tool_calls else 0}")
            if tool_calls is not None:
                for i, tool_call in enumerate(tool_calls):
                    print(f"Processing tool call {i+1}/{len(tool_calls)}")
                    tool_name = tool_call.function.name
                    tool_handle = globals().get(tool_name)
                    parameters = tool_call.function.arguments
                    print(f"Tool call: {tool_name}, Parameters: {parameters}")
                    print(f"Tool handle found: {tool_handle is not None}")

                    post_processed_response.append({
                        'response_type': 'tool_call', 
                        'content': {'tool_name':tool_name, 'parameters': parameters}
                        })

            return {'status': True, 'error': None, 'response': post_processed_response}

        except Exception as e:
            print(f"Error asking the agent: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return {'status': False, 'error': str(e), 'response': []}


agent = OllamaAgent()
    

messages = []

def process_agent_request(messages):
    print(f"Sent request to Ollama with: messages={messages}")

    response = agent.ask_agent(messages, 512, 512, 4)

    return response

def main():
    user_input = 'a'

    while True and user_input != 'exit':
        user_input = input("User: ")
        print()
        
        if user_input.strip().lower() == "exit":
            print("Exiting...")
            break

        messages.append({"role": "user", "content": user_input})

        # Append the user's message
        payload = {
            "token": "1234567890",
            "messages": messages
        }
        
        # Send the conversation to the endpoint
        response = process_agent_request(messages)

        if response and response.get('status'):
            print("Assistant:")
            for m in response['response']:
                if m['response_type'] == 'tool_call':
                    print(f"Tool call: {m['content']['tool_name']}")
                    print(f"Parameters: {m['content']['parameters']}")

                if m['response_type'] == 'message':
                    print(m['content'])

                # Append the assistant's reply to the conversation
                if m['response_type'] == 'message':
                    messages.append({"role": "assistant", "content": m['content']})
                elif m['response_type'] == 'tool_call':
                    # For tool calls, we can append a message indicating the tool was called
                    tool_name = m['content']['tool_name']
                    parameters = m['content']['parameters']
                    messages.append({"role": "assistant", "content": f"I'm calling the {tool_name} function with parameters: {parameters}"})
        else:
            error_msg = response.get('error', 'Unknown error') if response else 'No response received'
            print(f"Error: {error_msg}")

if __name__ == "__main__":
    main()





