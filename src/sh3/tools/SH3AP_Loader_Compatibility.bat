@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title SH3AP Loader Compatibility
set "SELF=%~f0"
set "REQUEST=%~1"
if not defined REQUEST (
  echo ============================================================
  echo   SH3AP - LOADER COMPATIBILITY
  echo ============================================================
  echo.
  echo This changes ONLY Ultimate ASI Loader startup timing/configuration.
  echo It does NOT modify sh3.exe, saves, pic.arc, PC Fix, or SH3AP ASIs.
  echo.
  echo [1] Standard - live-tested SH3AP timing ^(DontLoadFromDllMain=0^)
  echo [2] Deferred - cross-PC compatibility timing ^(DontLoadFromDllMain=1^)
  echo [3] Report only - change nothing
  echo [4] Exit
  echo.
  choice /C 1234 /N /M "Choose: "
  if errorlevel 4 exit /b 0
  if errorlevel 3 (set "REQUEST=report"& goto :compat_selected)
  if errorlevel 2 (set "REQUEST=deferred"& goto :compat_selected)
  set "REQUEST=standard"
)
:compat_selected

echo.
echo ============================================================
echo   SH3AP - LOADER COMPATIBILITY MODE

echo ============================================================
echo.
echo Standard  = live-tested SH3AP behavior ^(DontLoadFromDllMain=0^)
echo Deferred  = compatibility behavior      ^(DontLoadFromDllMain=1^)
echo Report    = write diagnostics only, change nothing

echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$s=[IO.File]::ReadAllText($env:SELF);$m=[char]35+'PS_BEGIN'+[char]35;$i=$s.LastIndexOf($m);if($i-lt0){throw 'Embedded payload missing'};&([scriptblock]::Create($s.Substring($i+$m.Length)))"
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (echo Loader compatibility operation completed successfully.) else (echo No loader compatibility change was completed.)
echo.
pause
exit /b %RC%

#PS_BEGIN#
$ErrorActionPreference='Stop'
$expectedLoader='d5a059aa467a7a7127c8f6169f79fa63ff0f55986ee9eb2fd9a281bebf2aa2e6'
$knownPcFix='3ad71981436184e669408b751e2b3170e856119de6cd68c4035193a6364f20ee'
$knownD3D8='ed6d4324146c525ec1de0662213ee2ba2b6dc311898f0977244536cd78ac1071'
$xipD8='3e0441bf07bd6529365d6c2b595007299bdf384299f3a0d325413f6be50a1a2b'
$xipDinput='e6ad898fdf197ffc71ed9a80912f4dc2b178331ebb1a16092cd256547dd3a6b2'
$xipX13='82c45d2a63ae7cc919afa86e9bc3dc0e57b0d4640e5dd68c5232cf67585028e3'
$runtimeNames=@('SH3AP.asi','SH3AP_UI.asi','SH3AP_Activity.asi','SH3AP_ItemMessage.asi','SH3AP_LiveBridge.asi','SH3AP_Controller.asi','SH3AP_Bindings_New.asi','SH3AP_Reset_Keybinds.asi','SH3AP_Rebind_FrameLock.asi')
$altProxyNames=@('d3d9.dll','d3d10.dll','d3d11.dll','d3d12.dll','dxgi.dll','ddraw.dll','dsound.dll','msacm32.dll','msvfw32.dll','version.dll','wininet.dll','winmm.dll','winhttp.dll','xlive.dll','binkw32.dll','bink2w32.dll','vorbisFile.dll','xinput1_1.dll','xinput1_2.dll','xinput1_4.dll','xinput9_1_0.dll','xinputuap.dll')

function SHA([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function Find-GameRoot([string]$start){
  $p=[IO.DirectoryInfo]([IO.Path]::GetFullPath($start))
  for($i=0;$i-lt10 -and $null-ne$p;$i++){
    if(Test-Path -LiteralPath (Join-Path $p.FullName 'sh3.exe') -PathType Leaf){return $p.FullName}
    $p=$p.Parent
  }
  $fallback=Join-Path $env:USERPROFILE 'Documents\Other Games\Silent Hill 3'
  if(Test-Path -LiteralPath (Join-Path $fallback 'sh3.exe') -PathType Leaf){return $fallback}
  throw 'Could not locate the Silent Hill 3 folder containing sh3.exe.'
}
function Atomic-Text([string]$path,[string]$text,[Text.Encoding]$encoding){
  $tmp=$path+'.sh3ap-loader.tmp'
  [IO.File]::WriteAllText($tmp,$text,$encoding)
  Move-Item -LiteralPath $tmp -Destination $path -Force
}
function Normalize-Ini([string]$path,[bool]$create,[string]$dllMain){
  if(-not(Test-Path -LiteralPath $path -PathType Leaf)){
    if(-not$create){return $false}
    $text="[GlobalSets]`r`nLoadPlugins=1`r`nLoadFromScriptsOnly=1`r`nLoadRecursively=0`r`nDontLoadFromDllMain=$dllMain`r`nUseD3D8to9=0`r`nDisableCrashDumps=0`r`nDirect3D8DisableMaximizedWindowedModeShim=0`r`n"
    Atomic-Text $path $text (New-Object Text.ASCIIEncoding)
    return $true
  }
  [byte[]]$raw=[IO.File]::ReadAllBytes($path)
  $bom=$raw.Length-ge3 -and $raw[0]-eq0xEF -and $raw[1]-eq0xBB -and $raw[2]-eq0xBF
  if($bom){$enc=New-Object Text.UTF8Encoding($true);$text=$enc.GetString($raw)}
  else{try{$enc=New-Object Text.UTF8Encoding($false,$true);$text=$enc.GetString($raw)}catch{$enc=[Text.Encoding]::Default;$text=$enc.GetString($raw)}}
  $nl=if($text.Contains("`r`n")){"`r`n"}else{"`n"}
  $desired=[ordered]@{LoadPlugins='1';LoadFromScriptsOnly='1';LoadRecursively='0';DontLoadFromDllMain=$dllMain;UseD3D8to9='0';DisableCrashDumps='0'}
  $updated=$text
  foreach($key in @($desired.Keys)+@('LoadFromAPI')){
    $pattern='(?im)^[ \t]*'+[regex]::Escape([string]$key)+'[ \t]*=[^\r\n]*(?:\r?\n|$)'
    $updated=[regex]::Replace($updated,$pattern,'')
  }
  $section=[regex]::Match($updated,'(?im)^([ \t]*\[GlobalSets\][ \t]*)(\r?\n|$)')
  $assign='';foreach($key in $desired.Keys){$assign+="$key=$($desired[$key])$nl"}
  if($section.Success){$at=$section.Index+$section.Length;$prefix=if($section.Groups[2].Value){''}else{$nl};$updated=$updated.Insert($at,$prefix+$assign)}
  else{$updated=$updated.TrimEnd("`r","`n")+$nl+'[GlobalSets]'+$nl+$assign}
  $new=$enc.GetBytes($updated)
  if([Convert]::ToBase64String($new)-eq[Convert]::ToBase64String($raw)){return $false}
  $tmp=$path+'.sh3ap-loader.tmp';[IO.File]::WriteAllBytes($tmp,$new);Move-Item -LiteralPath $tmp -Destination $path -Force
  return $true
}

function Test-PE32X86Dll([string]$path){
  if(-not(Test-Path -LiteralPath $path -PathType Leaf)){return $false}
  try{[byte[]]$b=[IO.File]::ReadAllBytes($path);if($b.Length-lt0x100 -or $b[0]-ne0x4D -or $b[1]-ne0x5A){return $false};$pe=[BitConverter]::ToInt32($b,0x3C);if($pe-lt0x40 -or $pe+26-ge$b.Length){return $false};if($b[$pe]-ne0x50 -or $b[$pe+1]-ne0x45 -or $b[$pe+2]-ne0 -or $b[$pe+3]-ne0){return $false};$machine=[BitConverter]::ToUInt16($b,$pe+4);$chars=[BitConverter]::ToUInt16($b,$pe+22);$magic=[BitConverter]::ToUInt16($b,$pe+24);return $machine-eq0x14C -and $magic-eq0x10B -and (($chars-band0x2000)-ne0)}catch{return $false}
}
function Test-XIP([string]$path,[string]$known,[string]$hint){
  if(-not(Test-PE32X86Dll $path)){return $false};if((SHA $path)-eq$known){return $true}
  try{$vi=(Get-Item -LiteralPath $path).VersionInfo;$id=((([string]$vi.CompanyName)+' '+([string]$vi.FileDescription)+' '+([string]$vi.ProductName))).ToLowerInvariant();return $id.Contains('0dd14') -and $id.Contains('xinput plus') -and $id.Contains($hint.ToLowerInvariant())}catch{return $false}
}
function Active-PluginConflicts([string]$root,[string]$scripts){
  $bad=New-Object Collections.Generic.List[string]
  foreach($f in @(Get-ChildItem -LiteralPath $root -Filter '*.asi' -File -ErrorAction SilentlyContinue)){$bad.Add($f.Name)}
  foreach($f in @(Get-ChildItem -LiteralPath $scripts -Filter '*.asi' -File -ErrorAction SilentlyContinue)){if($runtimeNames-notcontains$f.Name){$bad.Add(('scripts\'+$f.Name))}}
  $plugins=Join-Path $root 'plugins';if(Test-Path -LiteralPath $plugins -PathType Container){foreach($f in @(Get-ChildItem -LiteralPath $plugins -Filter '*.asi' -File -ErrorAction SilentlyContinue)){$bad.Add(('plugins\'+$f.Name))}}
  $update=Join-Path $root 'update';if(Test-Path -LiteralPath $update){if(-not(Test-Path -LiteralPath $update -PathType Container)){$bad.Add('update (not folder)')}elseif(@(Get-ChildItem -LiteralPath $update -Force -ErrorAction SilentlyContinue).Count){$bad.Add('update\ (non-empty)')}}
  return @($bad|Sort-Object)
}


$root=Find-GameRoot (Split-Path -Parent $env:SELF)
if(Get-Process -Name sh3 -ErrorAction SilentlyContinue){throw 'Silent Hill 3 is running. Close it first.'}
$loader=Join-Path $root 'dinput8.dll'
if(-not(Test-Path -LiteralPath $loader -PathType Leaf)){throw 'dinput8.dll is missing.'}
$lh=SHA $loader
if($lh-ne$expectedLoader){throw "dinput8.dll is not the SH3AP-supported Ultimate ASI Loader. SHA256: $lh"}
$scripts=Join-Path $root 'scripts';New-Item -ItemType Directory -Path $scripts -Force|Out-Null
$modeData=Join-Path $scripts 'SH3AP_Mode_Data';New-Item -ItemType Directory -Path $modeData -Force|Out-Null
$deferredMarker=Join-Path $modeData 'loader_deferred.flag'
$standardMarker=Join-Path $modeData 'loader_standard.flag'
$request=[string]$env:REQUEST
if([string]::IsNullOrWhiteSpace($request)){throw 'No compatibility mode was selected.'}
$isReport=$request.Equals('report',[StringComparison]::OrdinalIgnoreCase)
if($request.Equals('deferred',[StringComparison]::OrdinalIgnoreCase) -or $request-eq'1'){$deferred=$true}
elseif($request.Equals('standard',[StringComparison]::OrdinalIgnoreCase) -or $request-eq'0'){$deferred=$false}
elseif($isReport){
  $hasDeferred=Test-Path -LiteralPath $deferredMarker -PathType Leaf
  $hasStandard=Test-Path -LiteralPath $standardMarker -PathType Leaf
  if($hasDeferred -and $hasStandard){throw 'Both loader timing override markers are present.'}
  if($hasDeferred){$deferred=$true}
  elseif($hasStandard){$deferred=$false}
  else{
    $pcFixPath=Join-Path $root 'Silent_Hill_3_PC_Fix.dll'
    $d3d8Path=Join-Path $root 'd3d8.dll'
    $deferred=(-not(Test-Path -LiteralPath $pcFixPath -PathType Leaf)) -or (-not(Test-Path -LiteralPath $d3d8Path -PathType Leaf)) -or ((SHA $pcFixPath)-ne$knownPcFix) -or ((SHA $d3d8Path)-ne$knownD3D8)
  }
}
else{throw "Unknown mode '$request'. Use standard, deferred, or report."}

function SafeHash([string]$p){if(Test-Path -LiteralPath $p -PathType Leaf){return SHA $p};return 'MISSING'}
function IniValue([string]$path,[string]$key){
  if(-not(Test-Path -LiteralPath $path -PathType Leaf)){return 'MISSING'}
  $txt=[IO.File]::ReadAllText($path)
  $m=[regex]::Match($txt,'(?im)^[ \t]*'+[regex]::Escape($key)+'[ \t]*=[ \t]*([^\r\n]+)')
  if($m.Success){return $m.Groups[1].Value.Trim()};return 'UNSET'
}

$reportPath=Join-Path $root 'SH3AP_STARTUP_COMPATIBILITY_REPORT.txt'
$pcfix=Join-Path $root 'Silent_Hill_3_PC_Fix.dll'
$d3d8=Join-Path $root 'd3d8.dll'
$hooked=Join-Path $root 'dinput8Hooked.dll'
$xinput=Join-Path $root 'XInput1_3.dll'
$rootIni=Join-Path $root 'dinput8.ini'
$foreign=Active-PluginConflicts $root $scripts
$altProxies=@($altProxyNames|Where-Object{Test-Path -LiteralPath (Join-Path $root $_) -PathType Leaf});if(Test-Path -LiteralPath (Join-Path $root 'wndmode.ini') -PathType Leaf){$altProxies+= 'wndmode.ini (UAL built-in windowed-mode hook)'}
$overloads=New-Object Collections.Generic.List[string]
$plugins=Join-Path $root 'plugins'
foreach($ini in @((Join-Path $root 'dinput8.ini'),(Join-Path $root 'global.ini'),(Join-Path $scripts 'global.ini'),(Join-Path $plugins 'global.ini'))){if(Test-Path -LiteralPath $ini -PathType Leaf){$txt=[IO.File]::ReadAllText($ini);$m=[regex]::Match($txt,'(?im)^[ \t]*OverloadFromFolder[ \t]*=[ \t]*([^\r\n;#]+)');if($m.Success -and -not[string]::IsNullOrWhiteSpace($m.Groups[1].Value)){$overloads.Add(((Split-Path -Leaf $ini)+': '+$m.Groups[1].Value.Trim()))}}}
$xipIssues=New-Object Collections.Generic.List[string]
$hook=Join-Path $root 'dinput8Hooked.dll';$din=Join-Path $root 'Dinput.dll';$x13=Join-Path $root 'XInput1_3.dll';$xini=Join-Path $root 'XInputPlus.ini'
$xipPresent=@($hook,$din,$x13,$xini|Where-Object{Test-Path -LiteralPath $_ -PathType Leaf}).Count
if($xipPresent){foreach($p in @($hook,$din,$x13,$xini)){if(-not(Test-Path -LiteralPath $p -PathType Leaf)){$xipIssues.Add('missing '+(Split-Path -Leaf $p))}};if((Test-Path $hook)-and -not(Test-XIP $hook $xipD8 'directinput8')){$xipIssues.Add('dinput8Hooked.dll not recognized x86 XInput Plus')};if((Test-Path $din)-and -not(Test-XIP $din $xipDinput 'directinput')){$xipIssues.Add('Dinput.dll not recognized x86 XInput Plus')};if((Test-Path $x13)-and -not(Test-XIP $x13 $xipX13 'xinput')){$xipIssues.Add('XInput1_3.dll not recognized x86 XInput Plus')}}

if(-not$isReport){
  $stamp=Get-Date -Format 'yyyyMMdd-HHmmss'
  $backup=Join-Path $root ('_SH3AP_Archive\loader_compat_'+$stamp)
  New-Item -ItemType Directory -Path $backup -Force|Out-Null
  $paths=@(Join-Path $root 'dinput8.ini',Join-Path $root 'global.ini',Join-Path $scripts 'global.ini')
  $plugins=Join-Path $root 'plugins';if(Test-Path -LiteralPath $plugins -PathType Container){$paths+=Join-Path $plugins 'global.ini'}
  foreach($p in $paths){if(Test-Path -LiteralPath $p -PathType Leaf){Copy-Item -LiteralPath $p -Destination (Join-Path $backup ([IO.Path]::GetFileName($p)+'.'+([Math]::Abs($p.GetHashCode()))+'.bak'))}}
  $dllMain=if($deferred){'1'}else{'0'}
  [void](Normalize-Ini (Join-Path $root 'dinput8.ini') $true $dllMain)
  [void](Normalize-Ini (Join-Path $root 'global.ini') $false $dllMain)
  [void](Normalize-Ini (Join-Path $scripts 'global.ini') $false $dllMain)
  if(Test-Path -LiteralPath $plugins -PathType Container){[void](Normalize-Ini (Join-Path $plugins 'global.ini') $false $dllMain)}
  if($deferred){
    [IO.File]::WriteAllText($deferredMarker,"Deferred Ultimate ASI Loader timing enabled by user.`r`n",(New-Object Text.UTF8Encoding($false)))
    Remove-Item -LiteralPath $standardMarker -Force -ErrorAction SilentlyContinue
  }else{
    [IO.File]::WriteAllText($standardMarker,"Standard Ultimate ASI Loader timing enabled by user.`r`n",(New-Object Text.UTF8Encoding($false)))
    Remove-Item -LiteralPath $deferredMarker -Force -ErrorAction SilentlyContinue
  }
}else{$backup='(report only - no backup needed)'}

$crash=Join-Path $root 'CrashDumps';if(Test-Path -LiteralPath $crash){if(-not(Test-Path -LiteralPath $crash -PathType Container)){throw 'CrashDumps exists but is not a folder.'}}else{New-Item -ItemType Directory -Path $crash|Out-Null}

$lines=@(
  'SH3AP Startup Compatibility Report',
  ('Generated: '+(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')),
  ('Game root: '+$root),
  ('sh3.exe SHA256: '+(SafeHash (Join-Path $root 'sh3.exe'))),
  ('dinput8.dll SHA256: '+$lh),
  ('dinput8Hooked.dll SHA256: '+(SafeHash $hooked)),
  ('Silent_Hill_3_PC_Fix.dll SHA256: '+(SafeHash $pcfix)),
  ('d3d8.dll SHA256: '+(SafeHash $d3d8)),
  ('XInput1_3.dll SHA256: '+(SafeHash $xinput)),
  ('LoadPlugins: '+(IniValue $rootIni 'LoadPlugins')),
  ('LoadFromScriptsOnly: '+(IniValue $rootIni 'LoadFromScriptsOnly')),
  ('LoadRecursively: '+(IniValue $rootIni 'LoadRecursively')),
  ('DontLoadFromDllMain: '+(IniValue $rootIni 'DontLoadFromDllMain')),
  ('UseD3D8to9: '+(IniValue $rootIni 'UseD3D8to9')),
  ('DisableCrashDumps: '+(IniValue $rootIni 'DisableCrashDumps')),
  ('Deferred marker: '+(Test-Path -LiteralPath $deferredMarker -PathType Leaf)),
  ('Standard marker: '+(Test-Path -LiteralPath $standardMarker -PathType Leaf)),
  ('Active UAL plugin/overload conflicts: '+($(if($foreign.Count){$foreign -join ', '}else{'none'}))),
  ('Alternate proxy DLLs: '+($(if($altProxies.Count){$altProxies -join ', '}else{'none'}))),
  ('Custom UAL OverloadFromFolder settings: '+($(if($overloads.Count){$overloads -join ' | '}else{'none'}))),
  ('XInput Plus chain issues: '+($(if($xipIssues.Count){$xipIssues -join ' | '}else{'none'}))),
  ('Game root length: '+$root.Length),
  ('Game root PE32 UAL: '+(Test-PE32X86Dll $loader))
)
[IO.File]::WriteAllLines($reportPath,$lines,(New-Object Text.UTF8Encoding($false)))

Write-Host ''
Write-Host ('Game root: '+$root)
Write-Host ('Ultimate ASI Loader: '+$lh)
if($isReport){Write-Host 'Selected: REPORT ONLY - no loader setting changed.' -ForegroundColor Cyan}
elseif($deferred){Write-Host 'Selected: DEFERRED COMPATIBILITY MODE (DontLoadFromDllMain=1)' -ForegroundColor Yellow}
else{Write-Host 'Selected: LIVE-TESTED STANDARD MODE (DontLoadFromDllMain=0)' -ForegroundColor Green}
Write-Host 'Plugin discovery: scripts only, non-recursive.'
Write-Host 'UAL D3D8-to-9: disabled (Steam006 owns the graphics compatibility layer).'
Write-Host 'UAL crash dumps: enabled.'
if(-not$isReport){Write-Host ('INI backup folder: '+$backup)}
if($foreign.Count){Write-Host ('WARNING: active UAL plugin/overload conflicts: '+($foreign -join ', ')) -ForegroundColor Yellow}
if($altProxies.Count){Write-Host ('WARNING: alternate proxy DLLs: '+($altProxies -join ', ')) -ForegroundColor Yellow}
if($overloads.Count){Write-Host ('WARNING: custom UAL file overloads: '+($overloads -join ' | ')) -ForegroundColor Yellow}
if($xipIssues.Count){Write-Host ('WARNING: XInput Plus chain issues: '+($xipIssues -join ' | ')) -ForegroundColor Yellow}
try{$mit=Get-ProcessMitigation -Name 'sh3.exe' -ErrorAction Stop|Out-String;Add-Content -LiteralPath $reportPath -Value "`r`nExploit Protection for sh3.exe:`r`n$mit" -Encoding UTF8}catch{}
Write-Host ('Compatibility report: '+$reportPath)
Write-Host 'Launch sh3.exe directly to test.'
