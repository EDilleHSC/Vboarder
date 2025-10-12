# query_agent_memory.ps1
param (
    [string]$AgentName,
    [string]$QueryText
)

Write-Host "🔍 Querying memory for agent: $AgentName"
.\.venv\Scripts\Activate.ps1
python query_agent_memory.py $AgentName $QueryText
