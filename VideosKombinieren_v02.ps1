# aktuellen Pfad ermitteln
$AktuellerPfad = split-path $SCRIPT:MyInvocation.MyCommand.Path -parent
$BackupPfad = $AktuellerPfad + "\BackupEinzelfilme"
# definierte Tool-Pfade
$FFPfad = $AktuellerPfad + "\tools\ffmpeg.exe"

# Steuerungs-Abfragen
Write-Host
Write-Host "########################"
Write-Host "###  Einstellungen  ####"
Write-Host "########################"
Write-Host
$Schnitt = if($Value=(Read-Host "Sollen Filme geschnitten werden? (Enter = ja)")){$Value}else{"ja"}
Write-Host
Write-Host "Schnitt = " $Schnitt
Write-Host
Write-Host "########################"
Write-Host

# Schnittinfo-Datei vorbereiten und Header schreiben
$SchnittinfoDatei = $AktuellerPfad + "\Schnittinfo.txt"
Remove-Item -Path $SchnittinfoDatei -ErrorAction SilentlyContinue
"# Info: 00:00:00 bis 00:00:00 = ganzer Film" | Out-File $SchnittinfoDatei -Encoding UTF8
" " | Out-File $SchnittinfoDatei -Append -Encoding UTF8

# ffmpeg-Input-Datei definieren
$ffmpegInput = $AktuellerPfad + "\ffmpegInput.txt"
Remove-Item -Path $ffmpegInput -ErrorAction SilentlyContinue

# MP4-Dateien suchen und in Schittinfo-Datei schreiben
# + Zeitstempel der letzten Datei auslesen (nimm den neuesten)
$MP4Dateien = Get-ChildItem -Path $AktuellerPfad -Filter "*.mp4"
if ($ZeitstempelAlt) {remove-variable "ZeitstempelAlt"}
if ($Zeitstempel) {remove-Variable "Zeitstempel"}
if ($NeuesteDateiAlt) {remove-variable "NeuesteDateiAlt"}
if ($NeuesteDatei) {remove-Variable "NeuesteDatei"}
ForEach ($Datei in $MP4Dateien) {
    "00:00:00 bis 00:00:00 => "+$Datei | Out-File $SchnittinfoDatei -Append -Encoding UTF8
    if ($Zeitstempel) {$ZeitstempelAlt = $Zeitstempel}
    if ($NeuesteDatei) {$NeuesteDateiAlt = $NeuesteDatei}
    $Zeitstempel = $Datei.LastWriteTime
    $NeuesteDatei = $Datei
    if ($Zeitstempel -lt $ZeitstempelAlt) {
        $Zeitstempel = $ZeitstempelAlt
        $NeuesteDatei = $NeuesteDateiAlt
        }
}


# Schnittinfo anzeigen und auf Aenderung warten
if ($Schnitt -eq "ja") {
    start "C:\Windows\System32\notepad.exe" $SchnittinfoDatei
    Write-Host
    Read-Host -Prompt "Ist die Liste fertig und gespeichert? Dann weiter mit Enter"
}

# Schau nach wie viele Filme es sind
$AnzahlFilme = 0
$ZeilenZaehler = 0
$SchnittinfoInhalt = get-content $SchnittinfoDatei
foreach ($Zeile in $SchnittinfoInhalt) {
    $ZeilenZaehler++
    If ($ZeilenZaehler -ge 3) {
        If ($Zeile.trim()) {$AnzahlFilme = $AnzahlFilme + 1}
    } 
}
Write-Host $AnzahlFilme "Filme sollen kombiniert werden"
Write-Host

# Zeilenweise einlesen und ffmpeg-Inputdatei schreiben
$Filmnummer = 0
$ZeilenZaehler = 0
foreach ($Zeile in $SchnittinfoInhalt) {
    $ZeilenZaehler++
    # Inhalt ab Zeile 3 lesen
    If ($ZeilenZaehler -ge 3) {
        $Filmnummer = $Filmnummer + 1
        $Dateiname = $Zeile.Substring(25)
        $DateinameMitPfad = $AktuellerPfad + "\" + $Dateiname
        
        If ($Zeile -like "*00:00:00 bis 00:00:00*") {
            write-host Film $Filmnummer : - Ganzer Film -: $Dateiname
            # konvertiere in Schnitt-freundliches Format
            write-host Film $Filmnummer : konvertiere zu schnittfreundlichem Format: $Dateiname
            Write-Host
            $DateinameIntermediate = $Dateiname -replace(".mp4","-Intermediate.mov")
            $DateinameIntermediateMitPfad = $AktuellerPfad + "\" + $DateinameIntermediate
            &$FFPfad -loglevel error -i $DateinameMitPfad -c:v dnxhd -vf "scale=1920:1080,fps=30,format=yuv422p10le" -profile:v dnxhr_hqx -acodec alac -ar 48000 -sample_fmt s16p $DateinameIntermediateMitPfad
            
            # setze Zeitstempel von geschnittener Datei gleich wie Originaldatei
            $DateinameIntermediateMitPfadDatei = Get-Item $DateinameIntermediateMitPfad
            $DateinameMitPfadDatei = Get-Item $DateinameMitPfad
            $ZeitstempelSchnitt = $DateinameMitPfadDatei.LastWriteTime
            $DateinameIntermediateMitPfadDatei.LastWriteTime = $ZeitstempelSchnitt
            $DateinameIntermediateMitPfadDatei.LastAccessTime = $ZeitstempelSchnitt
            $DateinameIntermediateMitPfadDatei.CreationTime = $ZeitstempelSchnitt
    
            # verschiebe das Original-Video
            $BackupDateinameMitPfad = $BackupPfad + "\" + $Dateiname
            Move-Item $DateinameMitPfad $BackupDateinameMitPfad
        
            "file '"+$AktuellerPfad+"\"+$DateinameIntermediate+"'" | out-file $ffmpegInput -Append -Encoding ASCII
            
        } else {
        
            write-host Film $Filmnummer : --- Schnitt ---: $Dateiname
            
            # Zeiten einlesen und umrechnen
            $StartStunden = $Zeile.Substring(0,2)
            $StartMinuten = $Zeile.Substring(3,2)
            $StartSekunden = $Zeile.Substring(6,2)
            $EndStunden = $Zeile.Substring(13,2)
            $EndMinuten = $Zeile.Substring(16,2)
            $EndSekunden = $Zeile.Substring(19,2)
            $StartZeit = New-TimeSpan -Hour $StartStunden -Minute $StartMinuten -Second $StartSekunden
            $EndZeit = New-TimeSpan -Hour $EndStunden -Minute $EndMinuten -Second $EndSekunden
            $ZeitDauer = $EndZeit - $StartZeit
            $StartZeitString = $StartStunden + ":" + $StartMinuten + ":" + $StartSekunden
            $ZeitDauerString = $ZeitDauer.ToString()
            Write-Host Schneide Filme $Filmnummer : Start $StartZeitString : Dauer $ZeitDauerString
            Write-Host
            
            # definieren Dateinamen und schneide das Video
            $DateinameSchnitt = $Dateiname -replace(".mp4","-Schnitt.mov")
            $DateinameSchnittMitPfad = $AktuellerPfad + "\" + $DateinameSchnitt
            &$FFPfad -loglevel error -i $DateinameMitPfad -c:v dnxhd -vf "scale=1920:1080,fps=30,format=yuv422p10le" -profile:v dnxhr_hqx -acodec alac -ar 48000 -sample_fmt s16p -ss $StartZeitString -t $ZeitDauerString $DateinameSchnittMitPfad

            # setze Zeitstempel von geschnittener Datei gleich wie Originaldatei
            $DateinameSchnittMitPfadDatei = Get-Item $DateinameSchnittMitPfad
            $DateinameMitPfadDatei = Get-Item $DateinameMitPfad
            $ZeitstempelSchnitt = $DateinameMitPfadDatei.LastWriteTime
            $DateinameSchnittMitPfadDatei.LastWriteTime = $ZeitstempelSchnitt
            $DateinameSchnittMitPfadDatei.LastAccessTime = $ZeitstempelSchnitt
            $DateinameSchnittMitPfadDatei.CreationTime = $ZeitstempelSchnitt
    
            # verschiebe das Original-Video
            $BackupDateinameMitPfad = $BackupPfad + "\" + $Dateiname
            Move-Item $DateinameMitPfad $BackupDateinameMitPfad
            
            # schreibe den Schnitt-Dateinamen in die ffmpeg-Input-Datei
            "file '"+$AktuellerPfad+"\"+$DateinameSchnitt+"'" | out-file $ffmpegInput -Append -Encoding ASCII
        }

    } 
}

# Check ob mehr nur 1 Film geschnitten werden sollte
if ($AnzahlFilme -le 1) {
    write-host "Es ist nur ein Film vorhanden, deswegen ueberspringe ich das Zusammfuegen"
} else {

    # Fuege die Videos zusammen
    Write-Host "Ich klebe jetzt die Videos zusammen"
    Write-Host
    $KombiName = $AktuellerPfad+"\"+$NeuesteDatei -replace(".mp4","-Kombi.mp4")
    &$FFPfad -loglevel error -f concat -safe 0 -i $ffmpegInput -c:v libx264 -crf 20 -profile:v main -pix_fmt yuv420p -c:a aac $KombiName
    #&$FFPfad -loglevel error -f concat -safe 0 -i $ffmpegInput -codec:v h264_nvenc -profile high -level 4.0 -pix_fmt yuvj420p -c:a aac $KombiName

    # setze Zeitstempel
    $KombiNameDatei = Get-Item $KombiName
    $KombiNameDatei.LastWriteTime = $Zeitstempel
    $KombiNameDatei.LastAccessTime = $Zeitstempel
    $KombiNameDatei.CreationTime = $Zeitstempel

    # Schiebe die Einzelvideos ins Backup
    $ZeilenZaehler = 0
    $ffmpegInputInhalt = get-content $ffmpegInput
    foreach ($Zeile in $ffmpegInputInhalt) {
        $ZeilenZaehler++
        # Inhalt lesen
        $DateinameMitPfad = $Zeile.Substring(6)
        $DateinameMitPfad = $DateinameMitPfad.Substring(0,$DateinameMitPfad.Length-1)
        #$BackupDateinameMitPfad = $DateinameMitPfad.Replace($AktuellerPfad,$BackupPfad)
        Remove-Item -Path $DateinameMitPfad -ErrorAction SilentlyContinue
        #Move-Item $DateinameMitPfad $BackupDateinameMitPfad
    }
}

# aufraeumen
Remove-Item -Path $SchnittinfoDatei -ErrorAction SilentlyContinue
Remove-Item -Path $ffmpegInput -ErrorAction SilentlyContinue
Write-Host "########################"
write-host "#######  Fertig  #######"
Write-Host "########################"
