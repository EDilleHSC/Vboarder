function Write-ErrorLine($prefix, $ex) {
    Write-Host ("{0}: {1}" -f $prefix, $ex.Message) -ForegroundColor Red
}


