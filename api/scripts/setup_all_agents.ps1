# Setup all agents with memory
$agents = @('AIR', 'CEO', 'CFO', 'CLO', 'CMO', 'COO', 'COS', 'CTO', 'SEC')

foreach ($agent in $agents) {
    Write-Host "Setting up $agent agent..." -ForegroundColor Green
    
    # Create agent's document directory if it doesn't exist
    $agentDir = "D:\ai\projects\vboarder\agents\$agent\docs"
    if (-not (Test-Path $agentDir)) {
        New-Item -ItemType Directory -Path $agentDir -Force
    }
    
    # Test ingestion with sample doc if exists
    $exampleDocs = "D:\ai\projects\vboarder\example_docs"
    if (Test-Path $exampleDocs) {
        python ingest_doc.py $agent $exampleDocs
    }
}

Write-Host "All agents configured!" -ForegroundColor Cyan
