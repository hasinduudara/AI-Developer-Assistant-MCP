import asyncio
import json
import os
from dotenv import load_dotenv
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from openai import AsyncOpenAI

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    exit(1)

# Set up the OpenAI client to use Google's Gemini API
llm_client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Use the free Gemini Flash model
MODEL_NAME = "gemini-1.5-flash" 

async def run_agent():
    # Define how to connect to our MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server/server.py"]
    )

    print("Starting AI Agent with Gemini API...")
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Request the list of available tools from the MCP server
            tools_response = await session.list_tools()
            
            # Convert MCP tools format into OpenAI tool calling format
            llm_tools = []
            for tool in tools_response.tools:
                llm_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        # Update property name from inputSchema to input_schema
                        "parameters": tool.input_schema
                    }
                })

            print("\nAI Agent is ready! Type 'exit' to quit.")
            
            # Create a history array to store the conversation
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful AI developer assistant. Use the provided tools to help the user manage and search their project files. Always analyze the tool output before answering."
                }
            ]

            # Start the continuous chat loop
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() == 'exit':
                    break
                    
                # Add user message to history
                messages.append({"role": "user", "content": user_input})

                try:
                    # Send the conversation and tools to the Gemini API
                    response = await llm_client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=messages,
                        tools=llm_tools
                    )
                    
                    response_message = response.choices[0].message
                    messages.append(response_message)

                    # Check if the AI decided to use any of our tools
                    if response_message.tool_calls:
                        for tool_call in response_message.tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            
                            print(f"\n[AI is using tool: {tool_name} with arguments {tool_args}]")
                            
                            # Execute the tool via the MCP server
                            mcp_result = await session.call_tool(tool_name, arguments=tool_args)
                            tool_result_text = mcp_result.content[0].text
                            
                            # Add the tool result back into the conversation history
                            messages.append({
                                "role": "tool",
                                "name": tool_name,
                                "tool_call_id": tool_call.id,
                                "content": tool_result_text
                            })
                            
                        # Get the final answer from AI after it reads the tool results
                        final_response = await llm_client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=messages
                        )
                        final_text = final_response.choices[0].message.content
                        messages.append({"role": "assistant", "content": final_text})
                        print(f"\nAI: {final_text}")
                        
                    else:
                        # The AI replied with normal text without using any tools
                        print(f"\nAI: {response_message.content}")
                        
                except Exception as e:
                    print(f"\nAn error occurred: {str(e)}")
                    print("Hint: Make sure your Gemini API key is correct and you have an active internet connection.")

if __name__ == "__main__":
    asyncio.run(run_agent())