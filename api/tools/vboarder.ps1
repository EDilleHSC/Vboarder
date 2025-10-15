function Invoke-VBoarderStream {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateCount(1,100)]
        [string[]]$Agents,

        [Parameter(Mandatory=$true)]
        [ValidateNotNullOrEmpty()]
        [string]$Message,

        [int]$Timeout = 30,

        [string]$SessionId
    )

    if ($Agents.Count -lt 1) { throw "At least one agent is required." }
    if ([string]::IsNullOrWhiteSpace($Message)) { throw "Message cannot be empty." }

    foreach ($agent in $Agents) {
        $uri = "http://127.0.0.1:3737/chat/{0}" -f $agent
        $bodyHash = @{ message = $Message }
        if ($SessionId) { $bodyHash.session_id = $SessionId }
        $body = $bodyHash | ConvertTo-Json -Depth 3 -Compress

        Write-Host ("[{0}] -> {1}" -f $agent, $Message) -ForegroundColor Cyan
        try {
            $resp = Invoke-RestMethod -Uri $uri -Method POST -Body $body -ContentType "application/json" -TimeoutSec $Timeout
            # Print a reasonable field from response
            if ($resp -and $resp.reply) {
                Write-Host ("[{0}] <- {1}" -f $agent, $resp.reply) -ForegroundColor Green
            } else {
                Write-Host ("[{0}] (raw) {1}" -f $agent, ($resp | ConvertTo-Json -Depth 5)) -ForegroundColor Yellow
            }
        } catch {
            Write-Error ("[{0}] call failed: {1}" -f $agent, $_.Exception.Message)
        }
    }
}

Set-Alias ivbs Invoke-VBoarderStream
