#requires -Version 5.1
<#
.SYNOPSIS
    Set the two Cloudflare secrets and the Pages project name for the daily job.

.WHAT IT DOES
    Prompts for a Cloudflare API token and Account ID, writes them as GitHub
    Actions secrets on Parasocialite/parasocialize, sets the Pages project
    variable, and triggers one daily run so you can watch the optional publish
    step.

.WHERE TO GET THE TWO VALUES
    API token:  https://dash.cloudflare.com/profile/api-tokens
                Create Token -> Create Custom Token
                Permissions: Account -> Cloudflare Pages -> Edit
                Account Resources: your account
                Create, then copy the token (it is shown once).

    Account ID: https://dash.cloudflare.com/ -> Workers & Pages -> Overview
                The 32-character Account ID is in the right-hand panel.

    Project:    Workers & Pages -> your Pages project -> the name at the top.
                The workflow defaults to "parasocialize"; if yours is different,
                enter it when prompted.

.USAGE
    Run this in a normal PowerShell window, not through an agent:

      powershell -ExecutionPolicy Bypass -File tools\setup_cloudflare_deploy.ps1

    Check what is already set without changing anything:

      powershell -ExecutionPolicy Bypass -File tools\setup_cloudflare_deploy.ps1 -Check
#>
param(
    [switch]$Check,
    [string]$Repo = "Parasocialite/parasocialize"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) is not on PATH. Install it, or use the GitHub web UI."
}
gh auth status *> $null
if ($LASTEXITCODE -ne 0) {
    throw "gh is not logged in. Run: gh auth login"
}

if ($Check) {
    Write-Host "Repository: $Repo"
    Write-Host "`nSecrets (names only):"
    gh secret list -R $Repo
    Write-Host "`nVariables:"
    gh variable list -R $Repo
    Write-Host "`nLatest daily runs:"
    gh run list -R $Repo --workflow daily --limit 3
    exit 0
}

Write-Host "Cloudflare API token"
Write-Host "  Create at https://dash.cloudflare.com/profile/api-tokens"
Write-Host "  Permissions: Account -> Cloudflare Pages -> Edit"
$secure = Read-Host "Paste the token (input hidden)" -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $token = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}
$token = ($token -as [string]).Trim()
if (-not $token) { throw "No token entered." }

Write-Host "`nAccount ID"
Write-Host "  Cloudflare dashboard -> Workers & Pages -> Overview (right panel)"
$account = (Read-Host "Paste the 32-character Account ID").Trim()
if (-not $account) { throw "No account ID entered." }

Write-Host "`nPages project name"
Write-Host "  Workers & Pages -> your Pages project -> the name at the top"
$project = (Read-Host "Project name (Enter for 'parasocialize')").Trim()
if (-not $project) { $project = "parasocialize" }

# gh secret set reads the value from stdin when --body is omitted. Pipe the
# value so it never appears in the process argument list or the shell history.
$token | gh secret set CLOUDFLARE_API_TOKEN -R $Repo
if ($LASTEXITCODE -ne 0) { throw "Could not set CLOUDFLARE_API_TOKEN" }
$account | gh secret set CLOUDFLARE_ACCOUNT_ID -R $Repo
if ($LASTEXITCODE -ne 0) { throw "Could not set CLOUDFLARE_ACCOUNT_ID" }
gh variable set CLOUDFLARE_PAGES_PROJECT -R $Repo --body $project
if ($LASTEXITCODE -ne 0) { throw "Could not set CLOUDFLARE_PAGES_PROJECT" }
Remove-Variable token, account, secure -ErrorAction SilentlyContinue

Write-Host "`nSet. Triggering one daily run so the publish step can be checked."
gh workflow run daily -R $Repo
if ($LASTEXITCODE -ne 0) { throw "Could not trigger the daily workflow" }
Start-Sleep -Seconds 5
gh run list -R $Repo --workflow daily --limit 1

Write-Host "`nIf the publish step fails:"
Write-Host "  - the project name must match the Pages project exactly;"
Write-Host "  - the token needs Account -> Cloudflare Pages -> Edit;"
Write-Host "  - the project's production branch must be 'main' (the workflow"
Write-Host "    deploys --branch=main); if it is not, change it in Pages settings."
