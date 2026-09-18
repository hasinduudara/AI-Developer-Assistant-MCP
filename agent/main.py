import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def run_agent():
    # Define how to connect to our MCP server
    # We are telling it to run 'python mcp_server/server.py'
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server/server.py"]
    )

    print("Connecting to MCP Server...")
    
    # Establish the connection using standard input/output
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the session
            await session.initialize()
            print("Connected successfully!\n")
            
            # Request the list of available tools from the server
            tools_response = await session.list_tools()
            print("Available Tools:")
            for tool in tools_response.tools:
                print(f"- {tool.name}: {tool.description}")
            
            # Test calling the 'list_files' tool directly from our client
            print("\nTesting 'list_files' tool from Client...")
            result = await session.call_tool(
                "list_files", 
                arguments={"directory_path": "./test_project"}
            )
            
            # Print the result returned by the server
            print("Result from server:")
            print(result.content[0].text)

if __name__ == "__main__":
    # Run the asynchronous function
    asyncio.run(run_agent())