import asyncio
import os
from dotenv import load_dotenv
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    exit(1)

# Initialize the new Google GenAI client
client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"

async def run_agent():
    server_params = StdioServerParameters(command="python", args=["mcp_server/server.py"])
    print("Starting AI Agent with new Google GenAI SDK...")
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_response = await session.list_tools()
            
            # Convert MCP tools to Gemini Function Declarations
            gemini_tools = []
            for tool in tools_response.tools:
                gemini_tools.append(
                    types.FunctionDeclaration(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.input_schema
                    )
                )
            
            # Configure the chat session with tools and system instruction
            config = types.GenerateContentConfig(
                tools=[types.Tool(function_declarations=gemini_tools)],
                system_instruction="You are a helpful AI developer assistant. Use the provided tools to help the user manage and search their project files. Always analyze the tool output before answering."
            )
            
            # Create an asynchronous chat session (client.aio for async)
            chat = client.aio.chats.create(model=MODEL_NAME, config=config)

            print("\nAI Agent is ready! Type 'exit' to quit.")

            while True:
                user_input = input("\nYou: ")
                if user_input.lower() == 'exit':
                    break

                try:
                    # Send the user message
                    response = await chat.send_message(user_input)

                    # Check if the AI wants to use a tool
                    while response.function_calls:
                        function_call = response.function_calls[0]
                        tool_name = function_call.name
                        
                        # Convert arguments safely to a Python dictionary
                        tool_args = dict(function_call.args) if function_call.args else {}
                        
                        print(f"\n[AI is using tool: {tool_name} with arguments {tool_args}]")
                        
                        # Call the MCP server
                        mcp_result = await session.call_tool(tool_name, arguments=tool_args)
                        tool_result_text = mcp_result.content[0].text
                        
                        # Send the tool result back to Gemini
                        response = await chat.send_message(
                            types.Part.from_function_response(
                                name=tool_name,
                                response={"result": tool_result_text}
                            )
                        )
                        
                    # Print the final text answer
                    print(f"\nAI: {response.text}")
                    
                except Exception as e:
                    print(f"\nAn error occurred: {str(e)}")
                    print("Hint: Check your API key and connection.")

if __name__ == "__main__":
    asyncio.run(run_agent())