import os
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
# This acts as the bridge between our tools and the AI Agent
mcp = FastMCP("DeveloperAssistant")

@mcp.tool()
def list_files(directory_path: str) -> str:
    """
    List all files and directories in the given directory path.
    """
    try:
        # Check if the provided path actually exists
        if not os.path.exists(directory_path):
            return f"Error: The directory '{directory_path}' does not exist."
        
        # Check if the path is a directory
        if not os.path.isdir(directory_path):
            return f"Error: '{directory_path}' is not a directory."
            
        # Get all items in the directory
        items = os.listdir(directory_path)
        
        # If the folder is empty, return a simple message
        if not items:
            return "The directory is completely empty."
            
        # Join the list of files into a single string separated by newlines
        return "\n".join(items)
        
    except Exception as e:
        # Catch and return any errors (like permission issues)
        return f"An error occurred while reading the directory: {str(e)}"

if __name__ == "__main__":
    # Start the server using standard input/output (stdio)
    # This is how the AI Agent will communicate with this server
    mcp.run()