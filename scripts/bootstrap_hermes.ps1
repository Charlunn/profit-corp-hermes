param(
  [switch]$SkipCron,
  [switch]$SkipProfiles,
  [switch]$SkipSmoke,
  [switch]$SkipMigration,
  [switch]$SkipDoctor
)

$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$HermesHome = Join-Path $env:USERPROFILE '.hermes'
$HermesConfig = Join-Path $HermesHome 'config.yaml'
$TemplateConfig = Join-Path $RootDir 'config/hermes.config.yaml.example'
$Profiles = @('ceo','scout','cmo','arch','accountant')
$GlobalConfigOverwritten = $false
$ProfileConfigOverwritten = $false
$ChangedProfiles = @()
$OverwriteSyncedSkills = $false

function Log([string]$Message) {
  Write-Host "[bootstrap-ps] $Message"
}

function Warn([string]$Message) {
  Write-Warning "[bootstrap-ps] $Message"
}

function Resolve-Python {
  foreach ($cmd in @('python3','python')) {
    $candidate = Get-Command $cmd -ErrorAction SilentlyContinue
    if (-not $candidate) { continue }

    try {
      & $candidate.Source -V *> $null
      if ($LASTEXITCODE -eq 0) {
        return $candidate.Source
      }
    } catch {
    }
  }

  throw 'Missing usable command: python3 or python'
}

function Require-Command([string]$Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Missing required command: $Name"
  }
}

function Install-HermesIfMissing {
  if (Get-Command hermes -ErrorAction SilentlyContinue) {
    Log 'Hermes already installed'
    return
  }

  if (-not (Get-Command bash -ErrorAction SilentlyContinue)) {
    throw 'Hermes is missing and bash is required to run the official installer.'
  }

  Log 'Hermes not found. Installing via official installer...'
  $installCmd = 'curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash'
  & bash -lc $installCmd

  if (-not (Get-Command hermes -ErrorAction SilentlyContinue)) {
    throw 'Hermes install finished but command not found. Open a new shell and rerun.'
  }

  Log 'Hermes installed successfully'
}

function Setup-DefaultConfig {
  New-Item -ItemType Directory -Path $HermesHome -Force | Out-Null

  if (-not (Test-Path $HermesConfig)) {
    Copy-Item -Path $TemplateConfig -Destination $HermesConfig -Force
    $script:GlobalConfigOverwritten = $true
    Log "Created $HermesConfig from template"
    return
  }

  $ans = Read-Host '~/.hermes/config.yaml exists. Overwrite with project template? [y/N]'
  if ($ans -match '^(?i)y(es)?$') {
    Copy-Item -Path $TemplateConfig -Destination $HermesConfig -Force
    $script:GlobalConfigOverwritten = $true
    Log "Overwrote $HermesConfig"
  } else {
    Log 'Keeping existing Hermes config'
  }
}

function Sync-Profile([string]$Profile) {
  $profileHome = Join-Path $HermesHome "profiles/$Profile"
  $profileTemplate = Join-Path $RootDir "profiles/$Profile/config.yaml.example"
  $soulSrc = Join-Path $RootDir "profiles/$Profile/SOUL.md"

  if (-not (Test-Path $profileHome)) {
    Log "Creating profile: $Profile"
    & hermes profile create $Profile | Out-Null
  } else {
    Log "Profile exists: $Profile"
  }

  New-Item -ItemType Directory -Path $profileHome -Force | Out-Null

  $profileConfigPath = Join-Path $profileHome 'config.yaml'
  if (Test-Path $profileConfigPath) {
    $ans = Read-Host "Profile '$Profile' config exists. Overwrite with project template? [y/N]"
    if ($ans -notmatch '^(?i)y(es)?$') {
      Log "Keeping existing profile config: $Profile"
    } else {
      Copy-Item -Path $profileTemplate -Destination $profileConfigPath -Force
      $script:ProfileConfigOverwritten = $true
      $script:ChangedProfiles += $Profile
      Log "Overwrote profile config: $Profile"
    }
  } else {
    Copy-Item -Path $profileTemplate -Destination $profileConfigPath -Force
    $script:ProfileConfigOverwritten = $true
    $script:ChangedProfiles += $Profile
    Log "Created profile config: $Profile"
  }

  Copy-Item -Path $soulSrc -Destination (Join-Path $profileHome 'SOUL.md') -Force

  if (Test-Path (Join-Path $RootDir 'skills')) {
    New-Item -ItemType Directory -Path (Join-Path $profileHome 'skills') -Force | Out-Null
  }

  Log "Profile synced: $Profile"
}

function Sync-ProfileSkills([string]$Profile) {
  $profileHome = Join-Path $HermesHome "profiles/$Profile"
  $targetDir = Join-Path $profileHome 'skills'
  $commonDir = Join-Path $RootDir 'skills/common'
  $roleDir = Join-Path $RootDir "skills/$Profile"

  New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

  if (-not (Test-Path $commonDir) -and -not (Test-Path $roleDir)) {
    return
  }

  $targetHasFiles = (Get-ChildItem -Path $targetDir -File -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0
  if (-not $script:OverwriteSyncedSkills -and $targetHasFiles) {
    $ans = Read-Host "Profile '$Profile' skills exist. Overwrite synced skills from project? [y/N]"
    if ($ans -match '^(?i)y(es)?$') {
      $script:OverwriteSyncedSkills = $true
    } else {
      Log "Keeping existing profile skills: $Profile"
      return
    }
  }

  if (Test-Path $commonDir) {
    Copy-Item -Path (Join-Path $commonDir '*.md') -Destination $targetDir -Force -ErrorAction SilentlyContinue
  }
  if (Test-Path $roleDir) {
    Copy-Item -Path (Join-Path $roleDir '*.md') -Destination $targetDir -Force -ErrorAction SilentlyContinue
  }

  Log "Skills synced: $Profile"
}

function Setup-Profiles {
  if ($SkipProfiles) {
    Log 'Skipping profile setup'
    return
  }

  foreach ($p in $Profiles) {
    Sync-Profile -Profile $p
    Sync-ProfileSkills -Profile $p
  }
}

function Ensure-CeoDefaultProfile {
  try {
    & hermes profile use ceo | Out-Null
  } catch {
    Warn 'Failed to set ceo as active profile'
  }

  $removed = $false
  try {
    & hermes profile remove default | Out-Null
    $removed = $true
  } catch {
  }

  if (-not $removed) {
    try {
      & hermes profile delete default | Out-Null
      $removed = $true
    } catch {
    }
  }

  if ($removed) {
    Log 'Removed default profile'
  } else {
    Log 'Default profile removal skipped (may already be absent or command unsupported)'
  }
}

function Run-MigrationDryRun {
  if ($SkipMigration) {
    Log 'Skipping claw migration dry-run'
    return
  }

  $openclawHome = Join-Path $env:USERPROFILE '.openclaw'
  if (-not (Test-Path $openclawHome)) {
    Warn '~/.openclaw not found; skipping claw migration dry-run'
    return
  }

  $ans = Read-Host "Run 'hermes claw migrate --dry-run' now? [Y/n]"
  if ($ans -match '^(?i)n(o)?$') {
    Log 'Skipped migration dry-run'
    return
  }

  try {
    & hermes claw migrate --dry-run
  } catch {
    Warn 'Dry-run reported issues; inspect output'
  }
}

function Setup-CronJobs {
  if ($SkipCron) {
    Log 'Skipping cron job setup'
    return
  }

  try {
    & bash (Join-Path $RootDir 'orchestration/cron/commands.sh') 'ensure'
  } catch {
    Warn 'Cron setup reported issues'
  }
}

function Run-SmokeTest {
  if ($SkipSmoke) {
    Log 'Skipping smoke test'
    return
  }

  try {
    & bash (Join-Path $RootDir 'scripts/smoke_test_pipeline.sh')
  } catch {
    Warn 'Smoke test reported failures'
  }
}

function Configure-ModelsInteractive {
  if (-not (Get-Command hermes -ErrorAction SilentlyContinue)) {
    Warn 'Hermes not found; skipping interactive model configuration'
    return
  }

  if ($GlobalConfigOverwritten) {
    $ans = Read-Host 'Global Hermes config changed. Configure default provider/model now? [Y/n]'
    if ($ans -notmatch '^(?i)n(o)?$') {
      try {
        & hermes model
      } catch {
        Warn 'Default model setup did not complete'
      }
    } else {
      Warn "Skipped default model setup; run 'hermes model' later"
    }
  }

  foreach ($p in $ChangedProfiles) {
    $ans = Read-Host "Profile '$p' config changed. Configure provider/model for this profile now? [Y/n]"
    if ($ans -match '^(?i)n(o)?$') {
      Warn "Skipped model setup for $p; run '$p model' later"
      continue
    }

    try {
      & hermes -p $p model
    } catch {
      Warn "Model setup failed for profile: $p"
    }
  }
}

function Print-Sanity([string]$PythonBin) {
  Log 'Running Hermes doctor'
  try {
    & hermes doctor
  } catch {
    Warn 'Hermes doctor reported an error (often encoding in ~/.hermes/.env on Windows); continue with manual checks below.'
  }

  Log 'Checking finance script syntax'
  try {
    & $PythonBin -m py_compile (Join-Path $RootDir 'assets/shared/manage_finance.py')
  } catch {
    Warn 'Ledger syntax check failed'
  }

  Log 'Current profiles'
  try { & hermes profile list } catch { }

  Log 'Current cron jobs (ceo profile)'
  try { & hermes -p ceo cron list } catch { }
}

Require-Command -Name git
Require-Command -Name curl
$pythonBin = Resolve-Python

$needsBash = (-not $SkipCron) -or (-not $SkipSmoke)
if ($needsBash -and -not (Get-Command bash -ErrorAction SilentlyContinue)) {
  if (-not $SkipCron) {
    Warn 'bash not found; auto-skipping cron setup (equivalent to -SkipCron).'
    $SkipCron = $true
  }
  if (-not $SkipSmoke) {
    Warn 'bash not found; auto-skipping smoke test (equivalent to -SkipSmoke).'
    $SkipSmoke = $true
  }
}

Log "Project root: $RootDir"
Install-HermesIfMissing
Setup-DefaultConfig
Setup-Profiles
Ensure-CeoDefaultProfile
Configure-ModelsInteractive

Log "Tip: run 'ceo gateway setup' as primary messaging entrypoint"

Run-MigrationDryRun
Setup-CronJobs
Run-SmokeTest

if ($SkipDoctor) {
  Log 'Skipping Hermes doctor and sanity checks'
} else {
  Print-Sanity -PythonBin $pythonBin
}

if ($GlobalConfigOverwritten -or $ProfileConfigOverwritten) {
  Log 'Model/provider interactive setup completed for overwritten configs where approved.'
}

Log 'Bootstrap complete'
