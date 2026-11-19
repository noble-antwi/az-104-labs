# Bulk-creates Entra ID users from the portal's bulk-create CSV, through
# Microsoft Graph. Used because the portal's Bulk create job failed on
# 14 Nov 2026 before adding a single user (see the README, Break it).
#
# Usage:  .\bulk-create-users.ps1 -CsvPath ..\other_files\bulk-create-users-v2.WITH-PASSWORDS.csv
#
# Same CSV the portal takes; same result: one POST /users per row.
# Passwords are read from the file and sent only to Graph; nothing is printed or saved.

param(
    [Parameter(Mandatory)] [string] $CsvPath
)

$rows = Import-Csv -Path $CsvPath -Encoding UTF8
$tmp  = New-TemporaryFile

foreach ($r in $rows) {
    $upn = $r.'User name [userPrincipalName] Required'

    $user = [ordered]@{
        displayName       = $r.'Name [displayName] Required'
        userPrincipalName = $upn
        mailNickname      = $upn.Split('@')[0]
        accountEnabled    = ($r.'Account enabled (true/false) [accountEnabled]' -eq 'true')
        givenName         = $r.'First name [givenName]'
        surname           = $r.'Last name [surname]'
        jobTitle          = $r.'Job title [jobTitle]'
        department        = $r.'Department [department]'
        usageLocation     = $r.'Usage location [usageLocation]'
        passwordProfile   = @{
            password                      = $r.'Initial password [passwordProfile] Required'
            forceChangePasswordNextSignIn = $true
        }
    }

    # The body goes through a temp file so PowerShell never mangles the quotes.
    # WriteAllText writes UTF-8 without a BOM, which az rest needs.
    [IO.File]::WriteAllText($tmp, ($user | ConvertTo-Json -Depth 3))

    $result = az rest --method post --url "https://graph.microsoft.com/v1.0/users" `
        --headers "Content-Type=application/json" --body "@$tmp" `
        --query "{created:userPrincipalName, id:id}" -o tsv 2>&1

    if ($LASTEXITCODE -eq 0) { Write-Host "created  $upn" -ForegroundColor Green }
    else                     { Write-Host "FAILED   $upn  $result" -ForegroundColor Red }
}

Remove-Item $tmp
