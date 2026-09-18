import os
# Import MCPServer instead of FastMCP for mcp version 2.x
from mcp.server.mcpserver import MCPServer

# Create the MCP server
# This connects our tools with the AI Agent
mcp = MCPServer("DeveloperAssistant")

@mcp.tool()
def list_files(directory_path: str) -> str:
    """
    List all files and folders in the given path.
    """
    try:
        # Check if the path exists
        if not os.path.exists(directory_path):
            return f"Error: The directory '{directory_path}' does not exist."
        
        # Check if the path is a real folder
        if not os.path.isdir(directory_path):
            return f"Error: '{directory_path}' is not a folder."
            
        # Get all items inside the folder
        items = os.listdir(directory_path)
        
        # Check if the folder is empty
        if not items:
            return "The directory is completely empty."
            
        # Combine the item names into one text block
        return "\n".join(items)
        
    except Exception as e:
        # Return any error that happens
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    # Start the server to talk with the AI Agent
    mcp.run()