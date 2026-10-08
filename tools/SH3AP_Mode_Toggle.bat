@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "SH3AP_SELF=%~f0"
set "SH3AP_BASE=%~dp0"
set "SH3AP_REQUEST=%~1"
set "SH3AP_NOPAUSE=%~2"
set "SH3AP_PS=%TEMP%\SH3AP_Mode_Toggle_%RANDOM%_%RANDOM%.ps1"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$l=Get-Content -LiteralPath $env:SH3AP_SELF; $i=[Array]::IndexOf($l,'#PS_BEGIN'); if($i -lt 0){exit 91}; [IO.File]::WriteAllLines($env:SH3AP_PS,$l[($i+1)..($l.Count-1)],(New-Object Text.UTF8Encoding($false)))"
if errorlevel 1 (
  echo ERROR: Could not extract the embedded mode switch.
  if /I not "%SH3AP_NOPAUSE%"=="--no-pause" pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%SH3AP_PS%"
set "RC=%ERRORLEVEL%"
del /q "%SH3AP_PS%" >nul 2>&1
if not "%RC%"=="0" (
  echo.
  echo SH3AP mode switch did not complete.
  if /I not "%SH3AP_NOPAUSE%"=="--no-pause" pause
  exit /b %RC%
)

echo.
if /I not "%SH3AP_NOPAUSE%"=="--no-pause" pause
exit /b 0

#PS_BEGIN
$ErrorActionPreference = 'Stop'
$BaseDir = $env:SH3AP_BASE
if ([string]::IsNullOrWhiteSpace($BaseDir)) { throw 'Internal error: SH3AP_BASE was not passed to the mode switch.' }

$AP_EXE_HASH = '339377564d7764d34e94eb4e4f7dadbacb233f625ca66321d08c22f6b813ff57'
$PREVIOUS_207_AP_EXE_HASH = 'f392c40f8fec8875de8694abeeaffdc843b7f5627128a7dfa3b5230662de80ce'
$PREVIOUS_206_AP_EXE_HASH = '44559c26044f0777fe3bd1764bfb795e13557b2514e1c9c6ed09b4ada8d6fe79'
$PREVIOUS_205_AP_EXE_HASH = '628eee68f65be396630d70cfaaf2034b0e3f756ea35ceb62425f1e5e6c430b6c'
$PREVIOUS_203_AP_EXE_HASH = '1e00230decc2e2ccfec8b4351c10f749efe348292609a67fecdfc20ca972b5f4'
$PREVIOUS_193_AP_EXE_HASH = 'b898bcfe92c7fbefe2f39fe6ddb3810a271d956190127de36dcb6f70578d9617'
$CANONICAL_AP_EXE_HASH = '01ee53535712f640215d07f3cbb65499c14bdbb71063eda67c03c60065ee400e'
$BROKEN_186_AP_EXE_HASH = '76e4dc8da85cc7cf9d7f1f37b10483d18d0937aa6beba7066bdec99dcbb09974'
$VANILLA_EXE_HASH = '8ff8f74806f55843b9bc277508b17c8926999f292c65dbe7949325087d460918'
$MarkerName = 'SH3AP_DISABLED.flag'
$DisabledSuffix = '.sh3ap-disabled'
$RuntimeNames = @('SH3AP.asi','SH3AP_UI.asi','SH3AP_Activity.asi','SH3AP_ItemMessage.asi','SH3AP_LiveBridge.asi','SH3AP_Controller.asi','SH3AP_Bindings_New.asi','SH3AP_Reset_Keybinds.asi','SH3AP_Rebind_FrameLock.asi')
$RuntimeHashes = @{
    'SH3AP.asi'='c3ad8abb0c89408365e0919cfab86a3e9a11402867431119c187d275cdd0bee3'
    'SH3AP_UI.asi'='fe2ac87570d998df86c9d1b78c781ac5666f07312d7e076168de12d5582b0050'
    'SH3AP_Activity.asi'='48d552aeb309caf8c814a8153108e916b362c2599c3e5835e3ff8fa321339a0b'
    'SH3AP_ItemMessage.asi'='f77302e69a94f018d8fdf6e654f54cb45f5222726f8731be1d19a9405f0a0ead'
    'SH3AP_LiveBridge.asi'='12dbb9520f13127e5f457040a261430d8c11cb4b4508ca20f2700abaf34e3e0f'
    'SH3AP_Controller.asi'='868652a3635c2b3f68f30c9a86ed8c1a6bc15b038e50c2244115f3fbee819017'
    'SH3AP_Bindings_New.asi'='0e7a853c814991c460039aab0548e5aae028ba06d3920c44e55d0b475c5bdebc'
    'SH3AP_Reset_Keybinds.asi'='ca6fb3581ffa990ec0e43a366356ee897d1144440b61f7322c309c410c00979f'
    'SH3AP_Rebind_FrameLock.asi'='4957e576a594286018c242962092b5e85047615f112a66eabca1ea30b2de9f43'
}
$UAL_HASH = 'd5a059aa467a7a7127c8f6169f79fa63ff0f55986ee9eb2fd9a281bebf2aa2e6'
$XIP_D8_HASH = '3e0441bf07bd6529365d6c2b595007299bdf384299f3a0d325413f6be50a1a2b'
$XIP_DINPUT_HASH = 'e6ad898fdf197ffc71ed9a80912f4dc2b178331ebb1a16092cd256547dd3a6b2'
$XIP_XINPUT13_HASH = '82c45d2a63ae7cc919afa86e9bc3dc0e57b0d4640e5dd68c5232cf67585028e3'
$AltProxyNames = @('d3d9.dll','d3d10.dll','d3d11.dll','d3d12.dll','dxgi.dll','ddraw.dll','dsound.dll','msacm32.dll','msvfw32.dll','version.dll','wininet.dll','winmm.dll','winhttp.dll','xlive.dll','binkw32.dll','bink2w32.dll','vorbisFile.dll','xinput1_1.dll','xinput1_2.dll','xinput1_4.dll','xinput9_1_0.dll','xinputuap.dll')
$ExternalSupportNames = @('dinput8.dll','dinput8Hooked.dll','Dinput.dll','XInput1_3.dll','XInputPlus.ini','Silent_Hill_3_PC_Fix.dll','Silent_Hill_3_PC_Fix.ini','d3d8.dll','d3d9on12.dll','dxbcSigner.dll')

function HexBytes([string]$s) {
    $s = $s.Replace(' ','')
    $b = New-Object byte[] ($s.Length / 2)
    for ($i=0; $i -lt $b.Length; $i++) { $b[$i] = [Convert]::ToByte($s.Substring($i*2,2),16) }
    return $b
}

$ExePatches = @(
    @{ Off=0x0A19D7; Vanilla='6A04'; AP='EB1F' },
    @{ Off=0x1D773D; Vanilla='FEC8'; AP='B001' },
    @{ Off=0x1D7745; Vanilla='E8964C0300'; AP='B001909090' },
    # 0.0.204 title navigation: keep native New Game in slot 0 internally,
    # force only the title-menu clear-state callers true, then rely on the
    # existing AP navigation/render/input patches to hide and skip New Game.
    # This makes Extra New Game occupy native slot 1 and restores Up/Down access
    # without touching the shared fresh-session serial getter at 0x20C470.
    @{ Off=0x1D76EA; Vanilla='E8814D0300'; AP='B001909090' },
    @{ Off=0x1D80CD; Vanilla='C744241803000000'; AP='C744241803000000' },
    @{ Off=0x1D80DA; Vanilla='E891430300'; AP='B001909090' },
    @{ Off=0x1D8F10; Vanilla='E85B350300'; AP='B001909090' },
    @{ Off=0x1D81C1; Vanilla='8A0683C414A2F8BFBC00'; AP='E9537610009090909090' },
    @{ Off=0x1D821C; Vanilla='79'; AP='7F' },
    @{ Off=0x1D8283; Vanilla='18'; AP='1C' },
    @{ Off=0x1D8384; Vanilla='18FBFFFF'; AP='79170000' },
    @{ Off=0x1D8516; Vanilla='FEC8'; AP='B001' },
    @{ Off=0x1D8555; Vanilla='FEC8'; AP='B001' },
    @{ Off=0x1D85A2; Vanilla='FEC0'; AP='B001' },
    @{ Off=0x1D8709; Vanilla='E8223B0200'; AP='9090909090' },
    @{ Off=0x1D8724; Vanilla='78F7FFFF'; AP='58150B00' },
    @{ Off=0x1D8868; Vanilla='FECB'; AP='B301' },
    @{ Off=0x1D88A9; Vanilla='FEC8'; AP='B001' },
    @{ Off=0x1D88EF; Vanilla='FEC0'; AP='B001' },
    @{ Off=0x1D89AC; Vanilla='F0F4FFFF'; AP='D0120B00' },
    @{ Off=0x1D9B01; Vanilla='90909090909090909090909090'; AP='837C24044D7405E993E3FFFFC3' },
    @{ Off=0x289C80; Vanilla='0000000000000000000000'; AP='83FD017505E916E2F4FFC3' },
    @{ Off=0x2DF819; Vanilla='909090909090909090909090909090909090909090'; AP='8A0683C4143C037502B004A2F8BFBC00E99D89EFFF' },
    # 0.0.206: local Extra Options clear-count callers only. Never touch the
    # shared fresh-session getter at 0x20C470.
    @{ Off=0x1E44B9; Vanilla='E8B27F0200'; AP='B001909090' },
    @{ Off=0x1E5859; Vanilla='E8126C0200'; AP='B001909090' },
    # 0.0.208: the Naked Douglas new-game branch selects SFX 0x84 whenever
    # unlock ID 10 reports available. Force both known New Game sound selectors
    # onto the normal 0x83 path. This is deliberately separate from the unlock
    # function so the moan cannot return through stale system state.
    @{ Off=0x1D7858; Vanilla='7407'; AP='EB07' },
    @{ Off=0x1D87B6; Vanilla='7407'; AP='EB07' },
    # Native extra-content availability. All normal extra IDs are forced available.
    # ID 10 is Naked Douglas. Do NOT force it available in AP mode: return false
    # for ID 10 and true for the other extra-content IDs. This prevents the easter
    # egg from becoming active through the all-extras override. The shared
    # fresh-session getter remains untouched. Fully reversible in Vanilla mode.
    @{ Off=0x20D020; Vanilla='8B4C240483F9060F849D00000083'; AP='8B44240483F80A0F95C00FB6C0C3' }
)

function Get-Hash([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-PE32X86Dll([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    try {
        [byte[]]$b=[IO.File]::ReadAllBytes($Path)
        if($b.Length-lt0x100 -or $b[0]-ne0x4D -or $b[1]-ne0x5A){return $false}
        $pe=[BitConverter]::ToInt32($b,0x3C)
        if($pe-lt0x40 -or $pe+26-ge$b.Length){return $false}
        if($b[$pe]-ne0x50 -or $b[$pe+1]-ne0x45 -or $b[$pe+2]-ne0 -or $b[$pe+3]-ne0){return $false}
        $machine=[BitConverter]::ToUInt16($b,$pe+4)
        $chars=[BitConverter]::ToUInt16($b,$pe+22)
        $magic=[BitConverter]::ToUInt16($b,$pe+24)
        return $machine-eq0x14C -and $magic-eq0x10B -and (($chars-band0x2000)-ne0)
    } catch { return $false }
}

function Test-XInputPlusComponent([string]$Path,[string]$KnownHash,[string]$Hint) {
    if(-not(Test-PE32X86Dll $Path)){return $false}
    if((Get-Hash $Path)-eq$KnownHash){return $true}
    try {
        $vi=(Get-Item -LiteralPath $Path).VersionInfo
        $identity=((([string]$vi.CompanyName)+' '+([string]$vi.FileDescription)+' '+([string]$vi.ProductName))).ToLowerInvariant()
        return $identity.Contains('0dd14') -and $identity.Contains('xinput plus') -and $identity.Contains($Hint.ToLowerInvariant())
    } catch { return $false }
}

function Assert-NativePathSafe([string]$Root) {
    if($Root.Length-gt180){throw "The game folder path is too long for SH3AP native state files. Move SH3 to a shorter path such as C:\Games\Silent Hill 3."}
    if($Root.StartsWith('\\')){throw 'Network/UNC game folders are not supported by SH3AP save-profile junctions.'}
    try {
        $cp=[Globalization.CultureInfo]::CurrentCulture.TextInfo.ANSICodePage
        $enc=[Text.Encoding]::GetEncoding($cp,[Text.EncoderExceptionFallback]::new(),[Text.DecoderExceptionFallback]::new())
        $round=$enc.GetString($enc.GetBytes($Root))
        if($round-ne$Root){throw 'roundtrip'}
    } catch { throw 'The game path contains characters the SH3AP native ANSI file APIs cannot represent on this Windows locale. Move SH3 to a simple local path such as C:\Games\Silent Hill 3.' }
    try {
        $drive=[IO.DriveInfo]::new([IO.Path]::GetPathRoot($Root))
        if($drive.DriveFormat -notin @('NTFS','ReFS')){throw ("SH3AP save-profile junctions require NTFS/ReFS; this game is on "+$drive.DriveFormat+'.')}
    } catch [IO.IOException] { throw 'SH3AP could not verify a local junction-capable filesystem for this game folder.' }
}

function Assert-LoaderConfig([string]$Root,[string]$Scripts) {
    $rootIni=Join-Path $Root 'dinput8.ini'
    if(-not(Test-Path -LiteralPath $rootIni -PathType Leaf)){throw 'dinput8.ini is missing. Reopen Silent Hill 3 Client to repair loader configuration.'}
    $rootText=[IO.File]::ReadAllText($rootIni)
    $rootExpected=@{LoadPlugins='1';LoadFromScriptsOnly='1';LoadRecursively='0';UseD3D8to9='0';DisableCrashDumps='0'}
    foreach($k in $rootExpected.Keys){$ms=[regex]::Matches($rootText,'(?im)^[ \t]*'+[regex]::Escape($k)+'[ \t]*=[ \t]*([^\r\n]+)');if($ms.Count-ne1 -or $ms[0].Groups[1].Value.Trim()-ne$rootExpected[$k]){throw "dinput8.ini has an ambiguous/unsafe $k setting. Reopen Silent Hill 3 Client to normalize it."}}
    $dm=[regex]::Matches($rootText,'(?im)^[ \t]*DontLoadFromDllMain[ \t]*=[ \t]*([^\r\n]+)');if($dm.Count-ne1 -or $dm[0].Groups[1].Value.Trim()-notin @('0','1')){throw 'dinput8.ini has an ambiguous DontLoadFromDllMain setting.'};$dllMain=$dm[0].Groups[1].Value.Trim()
    if([regex]::IsMatch($rootText,'(?im)^[ \t]*LoadFromAPI[ \t]*=')){throw 'dinput8.ini contains LoadFromAPI, which can override SH3AP loader timing. Reopen Silent Hill 3 Client to normalize it.'}
    $plugins=Join-Path $Root 'plugins'
    foreach($ini in @((Join-Path $Root 'global.ini'),(Join-Path $Scripts 'global.ini'),(Join-Path $plugins 'global.ini'))){if(-not(Test-Path -LiteralPath $ini -PathType Leaf)){continue};$txt=[IO.File]::ReadAllText($ini);foreach($k in $rootExpected.Keys){$ms=[regex]::Matches($txt,'(?im)^[ \t]*'+[regex]::Escape($k)+'[ \t]*=[ \t]*([^\r\n]+)');if($ms.Count-gt1 -or ($ms.Count-eq1 -and $ms[0].Groups[1].Value.Trim()-ne$rootExpected[$k])){throw ((Split-Path -Leaf $ini)+" overrides SH3AP loader setting $k. Reopen the client to normalize it.")}};$ms=[regex]::Matches($txt,'(?im)^[ \t]*DontLoadFromDllMain[ \t]*=[ \t]*([^\r\n]+)');if($ms.Count-gt1 -or ($ms.Count-eq1 -and $ms[0].Groups[1].Value.Trim()-ne$dllMain)){throw ((Split-Path -Leaf $ini)+' overrides SH3AP loader timing. Reopen the client to normalize it.')};if([regex]::IsMatch($txt,'(?im)^[ \t]*LoadFromAPI[ \t]*=')){throw ((Split-Path -Leaf $ini)+' contains LoadFromAPI. Reopen the client to normalize it.')}}
}

function Assert-NoActivePluginConflicts([string]$Root,[string]$Scripts) {
    $bad=New-Object Collections.Generic.List[string]
    foreach($f in @(Get-ChildItem -LiteralPath $Root -Filter '*.asi' -File -ErrorAction SilentlyContinue)){$bad.Add($f.Name)}
    foreach($f in @(Get-ChildItem -LiteralPath $Scripts -Filter '*.asi' -File -ErrorAction SilentlyContinue)){
        if($RuntimeNames-notcontains$f.Name){$bad.Add(('scripts\'+$f.Name))}
    }
    $plugins=Join-Path $Root 'plugins'
    if(Test-Path -LiteralPath $plugins -PathType Container){foreach($f in @(Get-ChildItem -LiteralPath $plugins -Filter '*.asi' -File -ErrorAction SilentlyContinue)){$bad.Add(('plugins\'+$f.Name))}}
    $update=Join-Path $Root 'update'
    if(Test-Path -LiteralPath $update){
        if(-not(Test-Path -LiteralPath $update -PathType Container)){$bad.Add('update (not a normal folder)')}
        elseif(@(Get-ChildItem -LiteralPath $update -Force -ErrorAction SilentlyContinue).Count-gt0){$bad.Add('update\ (non-empty UAL overload folder)')}
    }
    if($bad.Count){throw ('Other Ultimate ASI Loader plugin/overload content can conflict with SH3AP startup: '+(($bad|Sort-Object)-join', '))}
    foreach($ini in @((Join-Path $Root 'dinput8.ini'),(Join-Path $Root 'global.ini'),(Join-Path $Scripts 'global.ini'),(Join-Path $plugins 'global.ini'))){
        if(Test-Path -LiteralPath $ini -PathType Leaf){
            $text=[IO.File]::ReadAllText($ini)
            $m=[regex]::Match($text,'(?im)^[ \t]*OverloadFromFolder[ \t]*=[ \t]*([^\r\n;#]+)')
            if($m.Success -and -not[string]::IsNullOrWhiteSpace($m.Groups[1].Value)){
                $active=New-Object Collections.Generic.List[string]
                foreach($part in ($m.Groups[1].Value -split '\|')){
                    $v=$part.Trim().Trim('\"');if([string]::IsNullOrWhiteSpace($v)){continue}
                    $candidate=if([IO.Path]::IsPathRooted($v)){$v}else{Join-Path $Root $v}
                    if(Test-Path -LiteralPath $candidate -PathType Container){if(@(Get-ChildItem -LiteralPath $candidate -Force -ErrorAction SilentlyContinue).Count-gt0){$active.Add($v)}}
                }
                if($active.Count){throw ((Split-Path -Leaf $ini)+' enables active UAL file overloading: '+($active-join' | '))}
            }
        }
    }
}

function Assert-NoAlternateProxyLoaders([string]$Root) {
    $bad=New-Object Collections.Generic.List[string]
    foreach($n in $AltProxyNames){if(Test-Path -LiteralPath (Join-Path $Root $n) -PathType Leaf){$bad.Add($n)}}
    if(Test-Path -LiteralPath (Join-Path $Root 'wndmode.ini') -PathType Leaf){$bad.Add('wndmode.ini (UAL built-in windowed-mode hook)')}
    if($bad.Count){throw ('Additional local proxy/hook features can create a second injection chain in AP mode: '+($bad-join', '))}
}

function Assert-XInputChainSafe([string]$Root) {
    $paths=@{
      hook=Join-Path $Root 'dinput8Hooked.dll'; dinput=Join-Path $Root 'Dinput.dll'; x13=Join-Path $Root 'XInput1_3.dll'; ini=Join-Path $Root 'XInputPlus.ini'
    }
    $present=@($paths.Values|Where-Object{Test-Path -LiteralPath $_ -PathType Leaf}).Count
    if($present-eq0){return}
    foreach($k in @('hook','dinput','x13','ini')){if(-not(Test-Path -LiteralPath $paths[$k] -PathType Leaf)){throw ('Partial XInput Plus/controller proxy chain: missing '+(Split-Path -Leaf $paths[$k]))}}
    if(-not(Test-XInputPlusComponent $paths.hook $XIP_D8_HASH 'directinput8')){throw 'dinput8Hooked.dll is not a recognized x86 XInput Plus DirectInput8 proxy.'}
    if(-not(Test-XInputPlusComponent $paths.dinput $XIP_DINPUT_HASH 'directinput')){throw 'Dinput.dll is not a recognized x86 XInput Plus DirectInput proxy.'}
    if(-not(Test-XInputPlusComponent $paths.x13 $XIP_XINPUT13_HASH 'xinput')){throw 'XInput1_3.dll is not a recognized x86 XInput Plus proxy.'}
}

function Assert-APStartupEnvironment([string]$Root,[string]$Scripts) {
    Assert-NativePathSafe $Root
    $loader=Join-Path $Root 'dinput8.dll'
    if(-not(Test-Path -LiteralPath $loader -PathType Leaf) -or (Get-Hash $loader)-ne$UAL_HASH){throw 'The verified SH3AP Ultimate ASI Loader is missing or changed.'}
    if(-not(Test-PE32X86Dll $loader)){throw 'dinput8.dll is not a valid x86 PE32 DLL.'}
    Assert-LoaderConfig $Root $Scripts
    Assert-NoActivePluginConflicts $Root $Scripts
    Assert-NoAlternateProxyLoaders $Root
    Assert-XInputChainSafe $Root
}

function Capture-ExternalSupport([string]$Root) {
    $state = [ordered]@{}
    foreach ($name in $ExternalSupportNames) {
        $p = Join-Path $Root $name
        if (Test-Path -LiteralPath $p -PathType Leaf) {
            $state[$name] = Get-Hash $p
        }
    }
    return $state
}

function Assert-ExternalSupportUnchanged([string]$Root, $Before) {
    foreach ($name in $Before.Keys) {
        $p = Join-Path $Root $name
        if (-not (Test-Path -LiteralPath $p -PathType Leaf)) {
            throw "External support file disappeared during SH3AP mode switch: $name"
        }
        $after = Get-Hash $p
        if ($after -ne [string]$Before[$name]) {
            throw "External support file changed during SH3AP mode switch: $name"
        }
    }
}


function Find-GameRoot([string]$Start) {
    $p = [IO.Path]::GetFullPath($Start)
    if (Test-Path -LiteralPath (Join-Path $p 'sh3.exe') -PathType Leaf) { return $p }
    $parent = Split-Path -Path $p -Parent
    if ($parent -and (Test-Path -LiteralPath (Join-Path $parent 'sh3.exe') -PathType Leaf)) { return $parent }
    throw 'Put this BAT in the Silent Hill 3 game folder (or its scripts folder).'
}

function Assert-Game-Closed {
    if (Get-Process -Name 'sh3' -ErrorAction SilentlyContinue) {
        throw 'Silent Hill 3 is running. Close the game before switching modes.'
    }
}

function Patch-Exe([string]$Exe, [ValidateSet('AP','Vanilla')] [string]$Target) {
    $hash = Get-Hash $Exe
    $supported = @($VANILLA_EXE_HASH,$BROKEN_186_AP_EXE_HASH,$CANONICAL_AP_EXE_HASH,$PREVIOUS_193_AP_EXE_HASH,$PREVIOUS_203_AP_EXE_HASH,$PREVIOUS_205_AP_EXE_HASH,$PREVIOUS_206_AP_EXE_HASH,$PREVIOUS_207_AP_EXE_HASH,$AP_EXE_HASH)
    if ($supported -notcontains $hash) { throw "Unsupported sh3.exe hash: $hash" }
    if ($Target -eq 'AP' -and $hash -eq $AP_EXE_HASH) { return }
    if ($Target -eq 'Vanilla' -and $hash -eq $VANILLA_EXE_HASH) { return }

    $bytes = [IO.File]::ReadAllBytes($Exe)

    # The 0.0.184 title-list bytes are now the verified AP target again; unlike
    # 0.0.186 they do not alter the fresh-session serial getter.

    # 0.0.193 added two UI caller overrides that did not unlock the real post-clear
    # state. Revert only those exact bytes to the verified 0.0.192 target before
    # applying the normal AP/Vanilla patch table.
    if ($hash -eq $PREVIOUS_193_AP_EXE_HASH) {
        $r1bad = HexBytes 'B001909090'
        $r1good = HexBytes 'E8B27F0200'
        $r2bad = HexBytes 'B001909090'
        $r2good = HexBytes 'E8126C0200'
        foreach ($entry in @(@(0x1E44B9,$r1bad,$r1good),@(0x1E5859,$r2bad,$r2good))) {
            $off = [int]$entry[0]; $bad = $entry[1]; $good = $entry[2]
            for ($i=0; $i -lt $bad.Length; $i++) {
                if ($bytes[$off+$i] -ne $bad[$i]) { throw ('0.0.193 executable migration verification failed at 0x{0:X}' -f $off) }
            }
            [Array]::Copy($good,0,$bytes,$off,$good.Length)
        }
        $normalized = $Exe + '.sh3ap-193-normalize.tmp'
        [IO.File]::WriteAllBytes($normalized,$bytes)
        $normalizedHash = Get-Hash $normalized
        Remove-Item -LiteralPath $normalized -Force -ErrorAction SilentlyContinue
        if ($normalizedHash -ne $PREVIOUS_203_AP_EXE_HASH) { throw "0.0.193 executable normalization hash verification failed: $normalizedHash" }
        $hash = $PREVIOUS_203_AP_EXE_HASH
    }

    # 0.0.203 used the older Extra-New-Game-only builder trick: it moved ENG
    # into slot 0 while the later navigation patch intentionally skipped slot 0.
    # Normalize those two exact title-builder regions to the 0.0.204 native-list
    # layout before applying the normal patch table.
    if ($hash -eq $PREVIOUS_203_AP_EXE_HASH) {
        $old1 = HexBytes 'C744241804000000'
        $new1 = HexBytes 'C744241803000000'
        $old2 = HexBytes 'E911000000'
        $new2 = HexBytes 'B001909090'
        foreach ($entry in @(@(0x1D80CD,$old1,$new1),@(0x1D80DA,$old2,$new2))) {
            $off = [int]$entry[0]; $old = $entry[1]; $new = $entry[2]
            for ($i=0; $i -lt $old.Length; $i++) {
                if ($bytes[$off+$i] -ne $old[$i]) { throw ('0.0.203 title-navigation migration verification failed at 0x{0:X}' -f $off) }
            }
            [Array]::Copy($new,0,$bytes,$off,$new.Length)
        }
        # Two additional title-only clear-state callers are applied by the main
        # patch table below, so leave hash recognition in the previous state here.
    }

    # 0.0.186-0.0.190 misidentified 0x60C470 as a clear-count getter and
    # forced it to return 1. It is actually the live fresh-session serial getter;
    # forcing it broke fresh-New-Game classification and Random Starting Area.
    # Restore that one exact function before applying normal AP/Vanilla bytes.
    if ($hash -eq $BROKEN_186_AP_EXE_HASH) {
        $bad = HexBytes 'B001C3909090'
        $good = HexBytes 'A0AC660E07C3'
        for ($i=0; $i -lt $bad.Length; $i++) {
            if ($bytes[0x20C470+$i] -ne $bad[$i]) { throw '0.0.186-0.0.190 executable migration verification failed at 0x20C470.' }
        }
        [Array]::Copy($good,0,$bytes,0x20C470,$good.Length)
        $normalized = $Exe + '.sh3ap-186-normalize.tmp'
        [IO.File]::WriteAllBytes($normalized,$bytes)
        $normalizedHash = Get-Hash $normalized
        Remove-Item -LiteralPath $normalized -Force -ErrorAction SilentlyContinue
        if ($normalizedHash -ne $CANONICAL_AP_EXE_HASH) { throw "0.0.186-0.0.190 executable normalization hash verification failed: $normalizedHash" }
        $hash = $CANONICAL_AP_EXE_HASH
    }

    # 0.0.206 forced the first six bytes of the extra-content availability
    # function to return true for every ID. Normalize that exact state back to
    # the stock 12-byte function head so 0.0.207 can apply the selective
    # all-extras-except-Douglas patch below.
    if ($hash -eq $PREVIOUS_206_AP_EXE_HASH) {
        $old = HexBytes 'B801000000C3060F849D00000083F9'
        $stock = HexBytes '8B4C240483F9060F849D00000083F9'
        for ($i=0; $i -lt $old.Length; $i++) {
            if ($bytes[0x20D020+$i] -ne $old[$i]) { throw '0.0.206 extra-content migration verification failed at 0x20D020.' }
        }
        [Array]::Copy($stock,0,$bytes,0x20D020,$stock.Length)
    }

    # 0.0.207 returned ID 10 to stock logic. Normalize that selective function
    # head back to stock before applying the 0.0.208 ID10-false patch and normal
    # New Game sound selectors.
    if ($hash -eq $PREVIOUS_207_AP_EXE_HASH) {
        $old = HexBytes '8B4C240483F90A740DB801000000C3'
        $stock = HexBytes '8B4C240483F9060F849D00000083F9'
        for ($i=0; $i -lt $old.Length; $i++) {
            if ($bytes[0x20D020+$i] -ne $old[$i]) { throw '0.0.207 Douglas-state migration verification failed at 0x20D020.' }
        }
        [Array]::Copy($stock,0,$bytes,0x20D020,$stock.Length)
    }

    $targetKey = if ($Target -eq 'AP') { 'AP' } else { 'Vanilla' }
    $otherKey = if ($Target -eq 'AP') { 'Vanilla' } else { 'AP' }
    $expected = if ($Target -eq 'AP') { $AP_EXE_HASH } else { $VANILLA_EXE_HASH }
    # Each known patch region may already be in either verified state, so the
    # exact Vanilla, canonical AP, safe-title AP, and normalized 0.0.186-0.0.190 states can all be
    # migrated without touching unrelated executable bytes.
    foreach ($p in $ExePatches) {
        $targetBytes = HexBytes $p[$targetKey]
        $otherBytes = HexBytes $p[$otherKey]
        if ($targetBytes.Length -ne $otherBytes.Length) { throw 'Internal executable patch length mismatch.' }
        $isTarget = $true
        $isOther = $true
        for ($i=0; $i -lt $targetBytes.Length; $i++) {
            $cur = $bytes[[int]$p.Off+$i]
            if ($cur -ne $targetBytes[$i]) { $isTarget = $false }
            if ($cur -ne $otherBytes[$i]) { $isOther = $false }
        }
        if (-not $isTarget -and -not $isOther) {
            throw ('Executable byte verification failed at patch region 0x{0:X}' -f [int]$p.Off)
        }
        if ($isOther) { [Array]::Copy($targetBytes,0,$bytes,[int]$p.Off,$targetBytes.Length) }
    }
    $tmp = $Exe + '.sh3ap-mode.tmp'
    [IO.File]::WriteAllBytes($tmp,$bytes)
    $th = Get-Hash $tmp
    if ($th -ne $expected) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue; throw "Patched executable hash verification failed: $th" }
    Move-Item -LiteralPath $tmp -Destination $Exe -Force
}

function Is-Reparse([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $i = Get-Item -LiteralPath $Path -Force
    return (($i.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Normalize-Path([string]$Path) {
    return ([IO.Path]::GetFullPath($Path)).TrimEnd('\')
}

function Get-JunctionTarget([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    if (-not (Is-Reparse $Path)) { return $null }
    $item = Get-Item -LiteralPath $Path -Force
    $target = $item.Target
    if ($target -is [array]) { $target = $target[0] }
    if ([string]::IsNullOrWhiteSpace([string]$target)) { return $null }
    if (-not [IO.Path]::IsPathRooted([string]$target)) {
        $target = Join-Path (Split-Path -Path $Path -Parent) ([string]$target)
    }
    return (Normalize-Path ([string]$target))
}

function Remove-JunctionOnly([string]$Link) {
    if (-not (Test-Path -LiteralPath $Link)) { return }
    if (-not (Is-Reparse $Link)) { throw "Refusing to remove normal folder: $Link" }
    # IMPORTANT: use CMD's non-recursive RMDIR for directory junctions.
    # Do not use PowerShell Remove-Item here: Windows PowerShell can prompt
    # as if the junction's target children would be recursively removed.
    $cmdLine = 'rmdir "' + $Link.Replace('"','""') + '"'
    & $env:ComSpec /d /c $cmdLine | Out-Null
    if ($LASTEXITCODE -ne 0 -or (Test-Path -LiteralPath $Link)) {
        throw "Could not remove junction link safely: $Link"
    }
}

function Set-Junction([string]$Link, [string]$Target) {
    if (-not (Test-Path -LiteralPath $Target -PathType Container)) { New-Item -ItemType Directory -Path $Target | Out-Null }
    $wanted = Normalize-Path $Target
    if (Test-Path -LiteralPath $Link) {
        if (-not (Is-Reparse $Link)) { throw "Refusing to replace normal folder: $Link" }
        $currentTarget = Get-JunctionTarget $Link
        if ($currentTarget -and $currentTarget.Equals($wanted,[StringComparison]::OrdinalIgnoreCase)) { return }
        Remove-JunctionOnly $Link
    }
    New-Item -ItemType Junction -Path $Link -Target $Target | Out-Null
    if (-not (Is-Reparse $Link)) { throw "Junction verification failed: $Link" }
    $actual = Get-JunctionTarget $Link
    if (-not $actual -or -not $actual.Equals($wanted,[StringComparison]::OrdinalIgnoreCase)) {
        throw "Junction target verification failed: $Link"
    }
}

function Get-RelativeFileMap([string]$RootPath) {
    $rootNorm = (Normalize-Path $RootPath) + '\'
    $map = [ordered]@{}
    if (-not (Test-Path -LiteralPath $RootPath -PathType Container)) { return $map }
    foreach ($f in @(Get-ChildItem -LiteralPath $RootPath -File -Recurse -Force -ErrorAction Stop)) {
        $full = Normalize-Path $f.FullName
        if (-not $full.StartsWith($rootNorm,[StringComparison]::OrdinalIgnoreCase)) { throw 'Save backup path escaped its source root.' }
        $rel = $full.Substring($rootNorm.Length)
        $map[$rel] = [ordered]@{ Length=[int64]$f.Length; SHA256=(Get-Hash $f.FullName) }
    }
    return $map
}

function Snapshot-SaveFolder([string]$Source,[string]$SafetyRoot,[string]$Label) {
    if (-not (Test-Path -LiteralPath $Source -PathType Container)) { return }
    if (Is-Reparse $Source) { throw "Refusing to snapshot a save junction as a real save folder: $Source" }
    $srcMap = Get-RelativeFileMap $Source
    if ($srcMap.Count -eq 0) { return }
    $stamp = (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '-' + ([Guid]::NewGuid().ToString('N').Substring(0,8))
    $dest = Join-Path (Join-Path $SafetyRoot $Label) $stamp
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    foreach ($entry in @(Get-ChildItem -LiteralPath $Source -Force -ErrorAction Stop)) {
        Copy-Item -LiteralPath $entry.FullName -Destination $dest -Recurse -Force -ErrorAction Stop
    }
    $dstMap = Get-RelativeFileMap $dest
    if ($srcMap.Count -ne $dstMap.Count) { throw "Save safety copy verification failed for $Label (file count mismatch)." }
    foreach ($k in $srcMap.Keys) {
        if (-not $dstMap.Contains($k)) { throw "Save safety copy verification failed for $Label (missing $k)." }
        if ($srcMap[$k].Length -ne $dstMap[$k].Length -or $srcMap[$k].SHA256 -ne $dstMap[$k].SHA256) {
            throw "Save safety copy verification failed for $Label ($k differs)."
        }
    }
    Write-Host ("Verified safety copy of {0} save file(s): {1}" -f $srcMap.Count,$Label)
}

function Protect-SavesBeforeSwitch([string]$Root,[string]$LiveSave,[string]$APSave,[string]$VanSave) {
    $safety = Join-Path $Root 'scripts\SH3AP_Mode_Data\SaveSafety'
    if (-not (Test-Path -LiteralPath $safety -PathType Container)) { New-Item -ItemType Directory -Path $safety -Force | Out-Null }
    Snapshot-SaveFolder $APSave $safety 'AP'
    Snapshot-SaveFolder $VanSave $safety 'Vanilla'
    if ((Test-Path -LiteralPath $LiveSave -PathType Container) -and -not (Is-Reparse $LiveSave)) {
        Snapshot-SaveFolder $LiveSave $safety 'PreInstall_savedata'
    }
}

function Test-FileMapsEqual($A,$B) {
    if ($A.Count -ne $B.Count) { return $false }
    foreach ($k in $A.Keys) {
        if (-not $B.Contains($k)) { return $false }
        if ($A[$k].Length -ne $B[$k].Length -or $A[$k].SHA256 -ne $B[$k].SHA256) { return $false }
    }
    return $true
}

function Move-RealSaveFolderToSafety([string]$Source,[string]$Root,[string]$Label) {
    if (-not (Test-Path -LiteralPath $Source -PathType Container)) { throw "Save recovery source is missing: $Source" }
    if (Is-Reparse $Source) { throw "Refusing to archive a save junction as a real save folder: $Source" }
    $before = Get-RelativeFileMap $Source
    $safety = Join-Path $Root 'scripts\SH3AP_Mode_Data\SaveSafety'
    $bucket = Join-Path $safety $Label
    if (-not (Test-Path -LiteralPath $bucket -PathType Container)) { New-Item -ItemType Directory -Path $bucket -Force | Out-Null }
    $stamp = (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '-' + ([Guid]::NewGuid().ToString('N').Substring(0,8))
    $dest = Join-Path $bucket $stamp
    Move-Item -LiteralPath $Source -Destination $dest
    if ((Test-Path -LiteralPath $Source) -or -not (Test-Path -LiteralPath $dest -PathType Container) -or (Is-Reparse $dest)) {
        throw "Could not move the conflicting save folder into verified safety storage: $Source"
    }
    $after = Get-RelativeFileMap $dest
    if (-not (Test-FileMapsEqual $before $after)) {
        # Same-volume directory moves should preserve the files exactly. If that
        # invariant somehow fails, restore the original path when it is safe to do so.
        if (-not (Test-Path -LiteralPath $Source) -and (Test-Path -LiteralPath $dest -PathType Container)) {
            Move-Item -LiteralPath $dest -Destination $Source -ErrorAction SilentlyContinue
        }
        throw "Recovered save-folder verification failed for $Label."
    }
    Write-Host ("Preserved conflicting real save folder in safety storage: {0}" -f $Label)
    return $dest
}

function Prepare-SaveLayout([string]$Root,[string]$LiveSave,[string]$APSave,[string]$VanSave,[bool]$AllowExistingVanillaRecovery=$false) {
    # Permanent invariant: savedataAP and savedata_Vanilla are real folders.
    # The public name savedata is only a junction. Never recursively delete,
    # empty, merge, or overwrite either real save folder.
    if (Test-Path -LiteralPath $APSave) {
        if (-not (Test-Path -LiteralPath $APSave -PathType Container) -or (Is-Reparse $APSave)) { throw 'savedataAP must be a normal directory.' }
    } else { New-Item -ItemType Directory -Path $APSave | Out-Null }

    if (Test-Path -LiteralPath $VanSave) {
        if (-not (Test-Path -LiteralPath $VanSave -PathType Container) -or (Is-Reparse $VanSave)) { throw 'savedata_Vanilla must be a normal directory.' }
    }

    if (Test-Path -LiteralPath $LiveSave -PathType Container) {
        if (Is-Reparse $LiveSave) {
            if (-not (Test-Path -LiteralPath $VanSave -PathType Container)) {
                New-Item -ItemType Directory -Path $VanSave | Out-Null
            }
            return
        }

        # First-time / recovery install with an ordinary live savedata folder.
        if (Test-Path -LiteralPath $VanSave -PathType Container) {
            if (-not $AllowExistingVanillaRecovery) {
                throw 'Both savedata and savedata_Vanilla already exist as real folders. Refusing to replace either one.'
            }

            # This recovery is allowed only while explicitly enabling AP from the
            # verified Vanilla executable. Therefore the ordinary live savedata is
            # the profile the Vanilla game was actually using immediately before
            # setup. Both folders were already hash-verified into SaveSafety above.
            $liveMap = Get-RelativeFileMap $LiveSave
            $vanMap = Get-RelativeFileMap $VanSave
            if (Test-FileMapsEqual $liveMap $vanMap) {
                # Exact duplicate: keep the established canonical Vanilla folder
                # and archive the redundant live directory rather than deleting it.
                $null = Move-RealSaveFolderToSafety $LiveSave $Root 'Recovered_duplicate_savedata'
                Write-Host 'Recovered duplicate savedata/savedata_Vanilla layout without deleting either save set.'
            } else {
                # Different contents: the live normal savedata is authoritative for
                # this Vanilla->AP bootstrap. Archive the pre-existing Vanilla-named
                # folder, then promote the live folder to the canonical Vanilla slot.
                $null = Move-RealSaveFolderToSafety $VanSave $Root 'Recovered_previous_savedata_Vanilla'
                Move-Item -LiteralPath $LiveSave -Destination $VanSave
                if ((Test-Path -LiteralPath $LiveSave) -or -not (Test-Path -LiteralPath $VanSave -PathType Container) -or (Is-Reparse $VanSave)) {
                    throw 'Could not promote the active vanilla savedata folder to savedata_Vanilla.'
                }
                $promotedMap = Get-RelativeFileMap $VanSave
                if (-not (Test-FileMapsEqual $liveMap $promotedMap)) {
                    throw 'Promoted vanilla savedata verification failed.'
                }
                Write-Host 'Recovered conflicting save layout: active vanilla savedata is now savedata_Vanilla; the previous folder was preserved in SaveSafety.'
            }
        } else {
            Move-Item -LiteralPath $LiveSave -Destination $VanSave
            if ((Test-Path -LiteralPath $LiveSave) -or -not (Test-Path -LiteralPath $VanSave -PathType Container)) {
                throw 'Could not preserve the original vanilla savedata folder.'
            }
            Write-Host 'Preserved the existing vanilla savedata folder byte-for-byte as savedata_Vanilla.'
        }
    } elseif (-not (Test-Path -LiteralPath $VanSave -PathType Container)) {
        New-Item -ItemType Directory -Path $VanSave | Out-Null
    }

    if (Is-Reparse $VanSave) { throw 'savedata_Vanilla must be a normal directory.' }

    # key.ini and disp.ini are deliberately NOT AP-profile state.  They are
    # synchronized separately so changing AP/Vanilla mode never swaps the
    # player's display or controller configuration.
}

function Sync-SharedGameSettings([string]$Root,[string]$LiveSave,[string]$APSave,[string]$VanSave,[ValidateSet('AP','Vanilla')] [string]$CurrentHint) {
    # SH3 stores key.ini/disp.ini inside savedata, but these are user/game
    # configuration rather than AP progress.  Keep one effective setting set
    # across both real save profiles so the mode toggle/uninstaller never swaps
    # controller or display options.
    $backupRoot = Join-Path $Root 'scripts\SH3AP_Mode_Data\SharedSettingsBackups'
    foreach ($n in @('key.ini','disp.ini')) {
        $candidates = New-Object System.Collections.Generic.List[string]
        $liveFile = Join-Path $LiveSave $n
        if (Test-Path -LiteralPath $liveFile -PathType Leaf) { $candidates.Add($liveFile) }
        if ($CurrentHint -eq 'AP') {
            $candidates.Add((Join-Path $APSave $n))
            $candidates.Add((Join-Path $VanSave $n))
        } else {
            $candidates.Add((Join-Path $VanSave $n))
            $candidates.Add((Join-Path $APSave $n))
        }
        $source = $null
        foreach ($candidate in $candidates) {
            if (Test-Path -LiteralPath $candidate -PathType Leaf) { $source = $candidate; break }
        }
        if ($null -eq $source) { continue }
        $sourceHash = Get-Hash $source
        foreach ($entry in @(@{Label='AP';Dir=$APSave}, @{Label='Vanilla';Dir=$VanSave})) {
            $dst = Join-Path $entry.Dir $n
            if (Test-Path -LiteralPath $dst) {
                $item = Get-Item -LiteralPath $dst -Force
                if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Shared game setting is an unexpected link: $dst" }
                $oldHash = Get-Hash $dst
                if ($oldHash -eq $sourceHash) { continue }
                if (-not (Test-Path -LiteralPath $backupRoot -PathType Container)) { New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null }
                $backup = Join-Path $backupRoot (('{0}_{1}.{2}.bak' -f $entry.Label,$n,$oldHash.Substring(0,12)))
                if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) { Copy-Item -LiteralPath $dst -Destination $backup }
            }
            Copy-Item -LiteralPath $source -Destination $dst -Force
            if ((Get-Hash $dst) -ne $sourceHash) { throw "Shared game setting verification failed: $dst" }
        }
    }
}

function Prepare-Backup-Split([string]$Root, [ValidateSet('AP','Vanilla')] [string]$CurrentMode) {
    $live = Join-Path $Root 'SavedataBackup'
    $ap = Join-Path $Root 'SavedataBackupAP'
    $van = Join-Path $Root 'SavedataBackup_Vanilla'
    if (Test-Path -LiteralPath $live -PathType Container) {
        if (-not (Is-Reparse $live)) {
            $dest = if ($CurrentMode -eq 'AP') { $ap } else { $van }
            if (Test-Path -LiteralPath $dest) {
                $has = @(Get-ChildItem -LiteralPath $dest -Force -ErrorAction SilentlyContinue).Count
                if ($has -gt 0) { throw "Cannot safely migrate $live because $dest already contains files." }
                if (Is-Reparse $dest) { throw "Refusing to remove unexpected junction while preparing backup split: $dest" }
                Remove-Item -LiteralPath $dest -Force
            }
            Move-Item -LiteralPath $live -Destination $dest
            Write-Host "Preserved existing PC Fix backups as $(Split-Path -Leaf $dest)."
        }
    }
    if (-not (Test-Path -LiteralPath $ap -PathType Container)) { New-Item -ItemType Directory -Path $ap | Out-Null }
    if (-not (Test-Path -LiteralPath $van -PathType Container)) { New-Item -ItemType Directory -Path $van | Out-Null }
    return @{ Live=$live; AP=$ap; Vanilla=$van }
}

function Neutralize-LegacyDisabledRuntime([string]$Scripts) {
    $disabled = Join-Path $Scripts 'SH3AP_Disabled_Runtime'
    if (-not (Test-Path -LiteralPath $disabled -PathType Container)) { return 0 }
    $legacy = @(Get-ChildItem -LiteralPath $disabled -Filter 'SH3AP*.asi' -File -ErrorAction SilentlyContinue)
    $changed = 0
    foreach ($f in $legacy) {
        $dst = Join-Path $disabled ($f.Name + $DisabledSuffix)
        if (Test-Path -LiteralPath $dst -PathType Leaf) {
            if ((Get-Hash $dst) -ne (Get-Hash $f.FullName)) {
                throw "Conflicting legacy/safe disabled copies exist for $($f.Name)."
            }
            Remove-Item -LiteralPath $f.FullName -Force
        } else {
            Move-Item -LiteralPath $f.FullName -Destination $dst
        }
        $changed++
    }
    if ($changed -gt 0) {
        Write-Host ("Neutralized {0} recursively-loadable disabled ASI file(s)." -f $changed) -ForegroundColor Yellow
    }
    return $changed
}

function Disable-Runtime([string]$Scripts) {
    $disabled = Join-Path $Scripts 'SH3AP_Disabled_Runtime'
    if (-not (Test-Path -LiteralPath $disabled -PathType Container)) { New-Item -ItemType Directory -Path $disabled | Out-Null }
    [void](Neutralize-LegacyDisabledRuntime $Scripts)
    $active = @(Get-ChildItem -LiteralPath $Scripts -Filter 'SH3AP*.asi' -File -ErrorAction SilentlyContinue)
    foreach ($f in $active) {
        $dst = Join-Path $disabled ($f.Name + $DisabledSuffix)
        if (Test-Path -LiteralPath $dst -PathType Leaf) {
            if ((Get-Hash $dst) -ne (Get-Hash $f.FullName)) {
                throw "Both active and disabled copies exist for $($f.Name), but their hashes differ."
            }
            Remove-Item -LiteralPath $f.FullName -Force
        } else {
            Move-Item -LiteralPath $f.FullName -Destination $dst
        }
    }
    $remaining = @(Get-ChildItem -LiteralPath $Scripts -Filter 'SH3AP*.asi' -File -ErrorAction SilentlyContinue)
    if ($remaining.Count -ne 0) { throw 'One or more top-level SH3AP ASIs remained active after disable.' }
    Write-Host ("Disabled {0} SH3AP ASI file(s) using a non-.asi extension." -f $active.Count)
}

function Enable-Runtime([string]$Scripts) {
    $disabled = Join-Path $Scripts 'SH3AP_Disabled_Runtime'
    if (-not (Test-Path -LiteralPath $disabled -PathType Container)) { return }
    [void](Neutralize-LegacyDisabledRuntime $Scripts)
    $restored = 0
    foreach ($name in $RuntimeNames) {
        $src = Join-Path $disabled ($name + $DisabledSuffix)
        $dst = Join-Path $Scripts $name
        if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
            if (Test-Path -LiteralPath $dst -PathType Leaf) { continue }
            throw "Required SH3AP runtime file is missing from both active and disabled locations: $name"
        }
        if (Test-Path -LiteralPath $dst -PathType Leaf) {
            if ((Get-Hash $dst) -ne (Get-Hash $src)) { throw "Conflicting active/disabled copies exist for $name." }
            Remove-Item -LiteralPath $src -Force
        } else {
            Move-Item -LiteralPath $src -Destination $dst
        }
        $final=Get-Hash $dst
        if($final-ne[string]$RuntimeHashes[$name]){throw "Post-restore runtime verification failed for $name."}
        $restored++
    }
    # Development/stale SH3AP ASIs (for example SH3AP_Research.asi) deliberately
    # remain with the non-.asi disabled suffix and are not reactivated.
    Write-Host ("Restored {0} production SH3AP ASI file(s)." -f $restored)
}

function Assert-CanEnableRuntime([string]$Scripts) {
    $disabled = Join-Path $Scripts 'SH3AP_Disabled_Runtime'
    [void](Neutralize-LegacyDisabledRuntime $Scripts)
    foreach ($name in $RuntimeNames) {
        $src = Join-Path $disabled ($name + $DisabledSuffix)
        $dst = Join-Path $Scripts $name
        $hasSrc = Test-Path -LiteralPath $src -PathType Leaf
        $hasDst = Test-Path -LiteralPath $dst -PathType Leaf
        if (-not $hasSrc -and -not $hasDst) { throw "Required SH3AP runtime file is missing from both active and disabled locations: $name" }
        if ($hasSrc -and $hasDst -and (Get-Hash $src) -ne (Get-Hash $dst)) { throw "Conflicting active/disabled copies exist for $name." }
        $candidate=if($hasSrc){$src}else{$dst}
        $actual=Get-Hash $candidate
        if($actual-ne[string]$RuntimeHashes[$name]){throw "SH3AP runtime hash mismatch for $name. Expected $($RuntimeHashes[$name]), found $actual. Reopen Silent Hill 3 Client to repair the runtime before enabling AP mode."}
    }
}

function Assert-CanDisableRuntime([string]$Scripts) {
    $disabled = Join-Path $Scripts 'SH3AP_Disabled_Runtime'
    if (Test-Path -LiteralPath $disabled -PathType Container) { [void](Neutralize-LegacyDisabledRuntime $Scripts) }
    foreach ($f in @(Get-ChildItem -LiteralPath $Scripts -Filter 'SH3AP*.asi' -File -ErrorAction SilentlyContinue)) {
        $dst = Join-Path $disabled ($f.Name + $DisabledSuffix)
        if (Test-Path -LiteralPath $dst -PathType Leaf) {
            if ((Get-Hash $dst) -ne (Get-Hash $f.FullName)) { throw "Both active and disabled copies exist for $($f.Name), but their hashes differ." }
        }
    }
}

function Quarantine-ActiveRuntimeForRecovery([string]$Root,[string]$Scripts) {
    $active = @(Get-ChildItem -LiteralPath $Scripts -Filter 'SH3AP*.asi' -File -ErrorAction SilentlyContinue)
    if ($active.Count -eq 0) { return $null }
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $dest = Join-Path $Root ('_SH3AP_Archive\failed_mode_switch_runtime_' + $stamp)
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    foreach ($f in $active) {
        $target = Join-Path $dest $f.Name
        if (Test-Path -LiteralPath $target) { throw "Recovery quarantine target already exists: $target" }
        Move-Item -LiteralPath $f.FullName -Destination $target
        if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "Could not quarantine runtime file: $($f.Name)" }
    }
    $remaining = @(Get-ChildItem -LiteralPath $Scripts -Filter 'SH3AP*.asi' -File -ErrorAction SilentlyContinue)
    if ($remaining.Count -ne 0) { throw 'One or more SH3AP ASIs remained active after recovery quarantine.' }
    Write-Host ('Preserved active runtime in recovery quarantine: ' + $dest) -ForegroundColor Yellow
    return $dest
}

function Switch-TitleBlock([string]$Root, [ValidateSet('AP','Vanilla')] [string]$Target) {
    # Compliance build: do not distribute or write packaged Silent Hill title textures.
    Write-Host 'Title-screen switching is disabled in this compliance build; data\pic.arc was left unchanged.' -ForegroundColor DarkGray
    return
}

try {
    $Root = Find-GameRoot $BaseDir
    $Exe = Join-Path $Root 'sh3.exe'
    $Scripts = Join-Path $Root 'scripts'
    Assert-NativePathSafe $Root
    if (-not (Test-Path -LiteralPath $Scripts -PathType Container)) { New-Item -ItemType Directory -Path $Scripts | Out-Null }
    $Marker = Join-Path $Scripts $MarkerName
    Assert-Game-Closed
    # SH3AP mode switching must not remove, replace, disable, or rewrite the
    # Steam006 PC Fix, its INI, Ultimate ASI Loader, or XInputPlus trigger chain.
    # These are permanent game-compatibility fixes, completely separate from SH3AP.
    # Hash every external support file that is present and verify it again after
    # the switch, including Silent_Hill_3_PC_Fix.ini.
    $externalSupportBefore = Capture-ExternalSupport $Root

    $exeHash = Get-Hash $Exe
    if ($exeHash -ne $AP_EXE_HASH -and $exeHash -ne $PREVIOUS_207_AP_EXE_HASH -and $exeHash -ne $PREVIOUS_206_AP_EXE_HASH -and $exeHash -ne $PREVIOUS_205_AP_EXE_HASH -and $exeHash -ne $PREVIOUS_203_AP_EXE_HASH -and $exeHash -ne $PREVIOUS_193_AP_EXE_HASH -and $exeHash -ne $CANONICAL_AP_EXE_HASH -and $exeHash -ne $BROKEN_186_AP_EXE_HASH -and $exeHash -ne $VANILLA_EXE_HASH) { throw "Unsupported sh3.exe hash: $exeHash" }

    $LiveSave = Join-Path $Root 'savedata'
    $APSave = Join-Path $Root 'savedataAP'
    $VanSave = Join-Path $Root 'savedata_Vanilla'

    # Before changing links, formats, or mode-owned settings, make verified
    # copies of every real save directory that currently exists. These safety
    # copies are additive and are never used as working save directories.
    $liveWasNormal = (Test-Path -LiteralPath $LiveSave -PathType Container) -and -not (Is-Reparse $LiveSave)
    $preMarker = Test-Path -LiteralPath $Marker -PathType Leaf
    $preActiveRuntime = @(Get-ChildItem -LiteralPath $Scripts -Filter 'SH3AP*.asi' -File -ErrorAction SilentlyContinue).Count
    $preDisabledDir = Join-Path $Scripts 'SH3AP_Disabled_Runtime'
    $preDisabledRuntime = if (Test-Path -LiteralPath $preDisabledDir -PathType Container) { @(Get-ChildItem -LiteralPath $preDisabledDir -Filter 'SH3AP*.asi*' -File -ErrorAction SilentlyContinue).Count } else { 0 }
    $preAPSaveExists = Test-Path -LiteralPath $APSave -PathType Container
    $requestedForRecovery = [string]$env:SH3AP_REQUEST
    # 0.0.185 recovery is intentionally narrow: only the Silent Hill 3 Client's
    # explicit Vanilla -> AP bootstrap may resolve two simultaneous real save
    # folders automatically. No manual/ambiguous toggle state is guessed.
    $allowExistingVanillaRecovery = $liveWasNormal -and ($exeHash -eq $VANILLA_EXE_HASH) -and (-not [string]::IsNullOrWhiteSpace($requestedForRecovery)) -and $requestedForRecovery.Equals('AP',[StringComparison]::OrdinalIgnoreCase)

    Protect-SavesBeforeSwitch $Root $LiveSave $APSave $VanSave
    Prepare-SaveLayout $Root $LiveSave $APSave $VanSave $allowExistingVanillaRecovery

    # Whichever profile is active immediately before the switch is authoritative
    # for key.ini/disp.ini. Mirror those exact bytes into both real profiles so
    # AP/Vanilla toggling and uninstall never exchange the user's settings.
    $settingsCurrentHint = if ($exeHash -eq $VANILLA_EXE_HASH) { 'Vanilla' } else { 'AP' }
    Sync-SharedGameSettings $Root $LiveSave $APSave $VanSave $settingsCurrentHint

    $markerExists = Test-Path -LiteralPath $Marker -PathType Leaf
    $liveTarget = Get-JunctionTarget $LiveSave
    $apSaveNorm = Normalize-Path $APSave
    $vanSaveNorm = Normalize-Path $VanSave

    $activeRuntimeCount = @(Get-ChildItem -LiteralPath $Scripts -Filter 'SH3AP*.asi' -File -ErrorAction SilentlyContinue).Count
    $requiredActiveCount = @($RuntimeNames | Where-Object { Test-Path -LiteralPath (Join-Path $Scripts $_) -PathType Leaf }).Count
    $disabledDir = Join-Path $Scripts 'SH3AP_Disabled_Runtime'
    $legacyDisabledCount = if (Test-Path -LiteralPath $disabledDir -PathType Container) { @(Get-ChildItem -LiteralPath $disabledDir -Filter 'SH3AP*.asi' -File -ErrorAction SilentlyContinue).Count } else { 0 }
    $safeDisabledCount = if (Test-Path -LiteralPath $disabledDir -PathType Container) { @(Get-ChildItem -LiteralPath $disabledDir -Filter ('SH3AP*.asi' + $DisabledSuffix) -File -ErrorAction SilentlyContinue).Count } else { 0 }

    $apExeKnown = ($exeHash -eq $AP_EXE_HASH -or $exeHash -eq $PREVIOUS_207_AP_EXE_HASH -or $exeHash -eq $PREVIOUS_206_AP_EXE_HASH -or $exeHash -eq $PREVIOUS_205_AP_EXE_HASH -or $exeHash -eq $PREVIOUS_203_AP_EXE_HASH -or $exeHash -eq $PREVIOUS_193_AP_EXE_HASH -or $exeHash -eq $CANONICAL_AP_EXE_HASH -or $exeHash -eq $BROKEN_186_AP_EXE_HASH)
    $fullyAP = (-not $markerExists) -and $apExeKnown -and ($requiredActiveCount -eq $RuntimeNames.Count) -and ($activeRuntimeCount -eq $RuntimeNames.Count) -and $liveTarget -and $liveTarget.Equals($apSaveNorm,[StringComparison]::OrdinalIgnoreCase)
    $fullyVanilla = $markerExists -and ($exeHash -eq $VANILLA_EXE_HASH) -and ($activeRuntimeCount -eq 0) -and (($safeDisabledCount + $legacyDisabledCount) -gt 0) -and $liveTarget -and $liveTarget.Equals($vanSaveNorm,[StringComparison]::OrdinalIgnoreCase)

    $requested = [string]$env:SH3AP_REQUEST
    if (-not [string]::IsNullOrWhiteSpace($requested)) {
        if ($requested.Equals('AP',[StringComparison]::OrdinalIgnoreCase)) { $target = 'AP' }
        elseif ($requested.Equals('Vanilla',[StringComparison]::OrdinalIgnoreCase) -or $requested.Equals('Off',[StringComparison]::OrdinalIgnoreCase)) { $target = 'Vanilla' }
        else { throw "Unknown requested mode '$requested'. Use AP or Vanilla." }
    } elseif ($fullyAP) {
        $target = 'Vanilla'
    } elseif ($fullyVanilla) {
        $target = 'AP'
    } elseif ($markerExists) {
        # A previous AP -> Vanilla switch may have stopped after writing the
        # fail-closed marker / patching the EXE / disabling ASIs but before
        # redirecting savedata. Resume that transition instead of toggling back.
        $target = 'Vanilla'
        Write-Host 'Detected an incomplete AP -> Vanilla switch. Resuming it safely.' -ForegroundColor Yellow
    } else {
        # Symmetric recovery for an interrupted Vanilla -> AP switch.
        $target = 'AP'
        Write-Host 'Detected an incomplete Vanilla -> AP switch. Resuming it safely.' -ForegroundColor Yellow
    }

    $current = if ($fullyAP) { 'AP' } elseif ($fullyVanilla) { 'Vanilla' } elseif ($target -eq 'Vanilla') { 'AP (partial)' } else { 'Vanilla (partial)' }
    $backupCurrentMode = if ($fullyAP) { 'AP' } elseif ($fullyVanilla) { 'Vanilla' } elseif ($target -eq 'Vanilla') { 'AP' } else { 'Vanilla' }
    $backups = Prepare-Backup-Split $Root $backupCurrentMode

    Write-Host ''
    Write-Host ('Switching SH3AP mode: {0} -> {1}' -f $current,$target)
    Write-Host ('Game folder: ' + $Root)
    Write-Host ''

    try {
        # Preflight every runtime move inside the transactional recovery scope.
        # If an older/partial install is already inconsistent, the catch below can
        # still normalize it to a coherent Vanilla/off state instead of stranding it.
        if ($target -eq 'Vanilla') { Assert-CanDisableRuntime $Scripts } else { Assert-APStartupEnvironment $Root $Scripts; Assert-CanEnableRuntime $Scripts }
        if ($target -eq 'Vanilla') {
            # Fail closed first so a concurrently opened client cannot reinstall SH3AP.
            [IO.File]::WriteAllText($Marker,"SH3AP disabled by SH3AP_Mode_Toggle.bat`r`n",(New-Object Text.UTF8Encoding($false)))
            # Remove native plugins from the load path before changing executable
            # bytes. If anything below fails, the local catch restores a coherent
            # Vanilla/off state rather than leaving a mixed AP/Vanilla install.
            Disable-Runtime $Scripts
            Patch-Exe $Exe 'Vanilla'
            Set-Junction $LiveSave $VanSave
            Set-Junction $backups.Live $backups.Vanilla
            try { Switch-TitleBlock $Root 'Vanilla' } catch { Write-Host ('WARNING: optional title switch skipped: ' + $_.Exception.Message) -ForegroundColor Yellow }
            Write-Host ''
            Write-Host 'VANILLA / SH3AP-OFF MODE IS ACTIVE.' -ForegroundColor Green
            Write-Host 'The original supported sh3.exe bytes are restored.'
            Write-Host 'SH3AP ASIs use a non-.asi disabled extension and AP saves remain untouched in savedataAP.'
            Write-Host 'Steam006 PC Fix and its configuration remain installed and byte-for-byte unchanged.'
            Write-Host 'Controller trigger support remains installed and unchanged.'
        } else {
            # Restore the verified native runtime first. Only after it is complete
            # do we patch the EXE and expose AP saves.
            Enable-Runtime $Scripts
            Patch-Exe $Exe 'AP'
            Set-Junction $LiveSave $APSave
            Set-Junction $backups.Live $backups.AP
            try { Switch-TitleBlock $Root 'AP' } catch { Write-Host ('WARNING: optional title switch skipped: ' + $_.Exception.Message) -ForegroundColor Yellow }
            Remove-Item -LiteralPath $Marker -Force -ErrorAction SilentlyContinue
            Write-Host ''
            Write-Host 'SH3AP MODE IS ACTIVE.' -ForegroundColor Green
            Write-Host 'AP executable bytes and AP save area are active.'
            Write-Host 'If you installed a newer APWorld while SH3AP was off, open Silent Hill 3 Client once before starting SH3 so it can refresh the runtime ASIs.'
            Write-Host 'PC Fix and controller trigger support remain installed and unchanged.'
        }
        Assert-ExternalSupportUnchanged $Root $externalSupportBefore
    }
    catch {
        $switchError = $_.Exception.Message
        Write-Host ''
        Write-Host ('Mode switch failed: ' + $switchError) -ForegroundColor Red
        Write-Host 'Restoring a coherent Vanilla / SH3AP-off state...' -ForegroundColor Yellow
        try {
            [IO.File]::WriteAllText($Marker,"SH3AP disabled after a failed mode switch.`r`n",(New-Object Text.UTF8Encoding($false)))
            # Prefer the normal disabled-runtime layout. If an already-partial
            # install has conflicting/missing disabled files, preserve any live
            # ASIs in a timestamped quarantine so they cannot load, then continue
            # the fail-safe Vanilla recovery.
            try {
                Assert-CanDisableRuntime $Scripts
                Disable-Runtime $Scripts
            }
            catch {
                Write-Host ('Normal runtime disable was unavailable during recovery: ' + $_.Exception.Message) -ForegroundColor Yellow
                [void](Quarantine-ActiveRuntimeForRecovery $Root $Scripts)
            }
            Patch-Exe $Exe 'Vanilla'
            Set-Junction $LiveSave $VanSave
            Set-Junction $backups.Live $backups.Vanilla
            try { Switch-TitleBlock $Root 'Vanilla' } catch { Write-Host ('WARNING: optional title recovery skipped: ' + $_.Exception.Message) -ForegroundColor Yellow }
            Assert-ExternalSupportUnchanged $Root $externalSupportBefore
        }
        catch {
            $recoveryError = $_.Exception.Message
            throw ("Mode switch failed: $switchError`nAutomatic safe-state recovery also failed: $recoveryError`nDo not launch SH3 until the installation is repaired.")
        }
        throw ("Mode switch failed: $switchError`nA coherent Vanilla / SH3AP-off state was restored automatically.")
    }
    Write-Host 'Verified: PC Fix / PC Fix INI / loader / XInputPlus files were not changed by the mode switch.'
    Write-Host 'key.ini / disp.ini are shared across AP and Vanilla, so mode switching does not swap those options.'
    exit 0
}
catch {
    Write-Host ''
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    Write-Host 'The switch stopped rather than overwriting an ambiguous file/folder.'
    exit 1
}
