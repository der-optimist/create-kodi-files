# create-kodi-files
Scenario: You take some videos with your Smartphone and want to have them in your Kodi library with a readable name, a fanart and a poster image
This Python Programm will:
  - give you a GUI (but will not be very beautiful)
  - let you select frames to be used as fanart and poster images (poster: 2 frames combined)
  - create the nfo file with information for Kodi
  - create a subfolder for each video and move the related files there
  - normalize audio volume using EBU R128 algorithm (like TV stations use)
  - backup the original audio streams before normalizing
  - have german labels and buttons (should be easy to change)
  - be able to mark videos as "peinlich" (=> embarrassing) => I use this in kodi for filtering playlists
  - add the videos to the set "Eigene Videos" and the genre "EigeneVideos" (Own videos)
  - ask you for a title for each video and tell kodi to use "YYYY-MM-DD Given-Title" as title
  - use UTF-8, so there are hopefully no problems with äüöß...
  - need some time after you select a folder ("Ordner") - the frames are extracted at that time
  - be fast afterwards (=> select your folder and then get yourself a beer)
  - need some time at the end again (when you click "Arbeite!" - "Work!") - but then it won't need you anymore
  - require python3, ffmpeg and ffmpeg-normalize installed
  - hopefully run on every OS (Win, Linux, MacOS) - but is tested only on Win10
  - hopefully help you!
You can see a preview here:
https://www.kodinerds.net/index.php/Attachment/31559-Unbenannt-png/
