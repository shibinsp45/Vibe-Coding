$content = @'
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": [
        "mcp-server-git"
      ]
    },
    "google-developer-knowledge": {
      "headers": {
        "X-Goog-Api-Key": "<AIzaSyACov0aq7pl_SSN-WE8DpDbw7wT61Qp61U>"
      },
      "serverUrl": "https://developerknowledge.googleapis.com/mcp"
    }
  }
}
'@

$path = "$HOME\.gemini\config\mcp_config.json"
Set-Content -Path $path -Value $content -Encoding utf8
