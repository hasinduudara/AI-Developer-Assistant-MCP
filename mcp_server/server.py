import os
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
        if not os.path.exists(directory_path):
            return f"Error: The directory '{directory_path}' does not exist."
        if not os.path.isdir(directory_path):
            return f"Error: '{directory_path}' is not a folder."
            
        items = os.listdir(directory_path)
        
        if not items:
            return "The directory is completely empty."
            
        return "\n".join(items)
    except Exception as e:
        return f"An error occurred: {str(e)}"

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read and return the text content of a file.
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            return f"Error: The file '{file_path}' does not exist."
        
        # Check if it is a real file (not a folder)
        if not os.path.isfile(file_path):
            return f"Error: '{file_path}' is not a file."
        
        # Open the file and read its text
        # We use utf-8 to support standard text characters
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        return content
    except Exception as e:
        return f"An error occurred while reading the file: {str(e)}"

@mcp.tool()
def search_text(directory_path: str, search_query: str) -> str:
    """
    Search for a specific text or word inside all files in a folder.
    """
    try:
        if not os.path.exists(directory_path):
            return f"Error: The directory '{directory_path}' does not exist."
        
        results = []
        
        # Look through every file in the folder
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            # Only check text files (skip folders)
            if os.path.isfile(file_path):
                try:
                    # Open each file and check if the search_query is inside it
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if search_query in content:
                            results.append(f"Found in {filename}")
                except:
                    # Skip files that are not readable text (like images)
                    continue
                    
        if not results:
            return f"No files found containing '{search_query}'."
            
        return "\n".join(results)
    except Exception as e:
        return f"An error occurred while searching: {str(e)}"

if __name__ == "__main__":
    # Start the server to talk with the AI Agent
    mcp.run()