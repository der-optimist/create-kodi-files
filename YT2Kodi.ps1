# Einstellungen
[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")

write-host
write-host "Start"
write-host

# NFO-Dateien suchen
$AktuellerPfad = split-path $SCRIPT:MyInvocation.MyCommand.Path -parent
$mtnPfad = $AktuellerPfad + "\tools\mtn-200808a-win32\mtn.exe"
write-host $mtnPfad
$MP4Dateien = Get-ChildItem -Path $AktuellerPfad -Filter "*YTID-*.mp4"

ForEach ($Datei in $MP4Dateien) {
    # Namen und Adressen definieren
    $DateiName = $Datei.Name -replace(".mp4","")
    $DateiNameSplit = $DateiName -split("YTID-")
    $Name = $DateiNameSplit[0].trim(" ")
    $NameSplit = $Name -split(" - ")
    $Name = $NameSplit[0]
    $YTID = $DateiNameSplit[1].trim(" ")
    write-host "Name: " $Name 
    Write-Host "ID:   " $YTID
    $MaxResAdresse = "https://img.youtube.com/vi/" + $YTID + "/maxresdefault.jpg"
    $FanartName = $AktuellerPfad + "\" + $Name + "-fanart.jpg"
    $PosterName = "-poster.jpg"
    $FilmNameNeu = $AktuellerPfad + "\" + $Name + ".mp4"
    $NFOName = $AktuellerPfad + "\" + $Name + ".nfo"
    Rename-Item $Datei.Name $FilmNameNeu
    
    # Fanart Runterladen
    write-host "Lade Fanart herunter"
    $wc = New-Object System.Net.WebClient
    $wc.DownloadFile($MaxResAdresse, $FanartName)

    # Poster erstellen
    write-host "Erstelle Poster"
    $ErrorActionPreference = "SilentlyContinue"
    &$mtnPfad -c 1 -r 2 -i -o $PosterName -w 951 -P -t -g 7 -k 000000 $FilmNameNeu
    $ErrorActionPreference = "Continue"

    # NFO schreiben
    write-host "Schreibe NFO"
    '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' | Out-File $NFOName -Encoding UTF8
    '<movie>' | Out-File $NFOName -Append -Encoding UTF8
    ' <title>' + $Name + '</title>' | Out-File $NFOName -Append -Encoding UTF8
    ' <sorttitle>' + $Name + '</sorttitle>' | Out-File $NFOName -Append -Encoding UTF8
    ' <id>-1</id>' | Out-File $NFOName -Append -Encoding UTF8
    ' <trailer>plugin://plugin.video.youtube/?action=play_video&videoid=' + $YTID + '</trailer>' | Out-File $NFOName -Append -Encoding UTF8
    ' <genre>YoutubeKinderlieder</genre>' | Out-File $NFOName -Append -Encoding UTF8
    ' <set>YoutubeKinderlieder</set>' | Out-File $NFOName -Append -Encoding UTF8
    '</movie>' | Out-File $NFOName -Append -Encoding UTF8
    Write-Host
    
}

$InfoText = "Fertig. Jetzt sollte alles erledigt sein..."
[System.Windows.Forms.Messagebox]::Show($InfoText)
