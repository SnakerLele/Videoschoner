import pygame
import sys
import os
import random
import vlc
from pathlib import Path
import time
from screeninfo import get_monitors

def play_video(screen, video_path):
    """
    Spielt ein einzelnes Video per VLC im Vollbild ab.
    Bricht ab, wenn das Video endet oder ein Eingabeereignis (Maus/Keyboard) auftritt.
    """
    # Pygame zwingt alle Events zu erkennen
    pygame.event.set_grab(True)
    
    instance = vlc.Instance(
        "--avcodec-hw=dxva2",         # Hardware-Beschleunigung
        "--no-video-title-show",      # Kein Titel-Overlay
        "--fullscreen",               # VLC-internes Vollbild
        "--quiet",                    # Keine Ausgaben
        "--no-spu"                    # Untertitel aus
    )
    
    player = instance.media_player_new()
    
    # Fenster-Handle für VLC setzen
    if sys.platform == "win32":
        player.set_hwnd(pygame.display.get_wm_info()['window'])
    elif sys.platform == "linux":
        player.set_xwindow(pygame.display.get_wm_info()['window'])
    elif sys.platform == "darwin":
        player.set_nsobject(pygame.display.get_wm_info()['window'])

    try:
        # Media laden und Video abspielen
        media = instance.media_new(video_path)
        player.set_media(media)
        player.play()
        
        # Kurze Wartezeit, damit das Video sicher startet
        time.sleep(0.5)
        
        running = True
        while running and player.get_state() not in (vlc.State.Ended, vlc.State.Stopped):
            mouse_pos_old = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos_new = pygame.mouse.get_pos()
                    if abs(mouse_pos_new[0] - mouse_pos_old[0]) > 5 or \
                       abs(mouse_pos_new[1] - mouse_pos_old[1]) > 5:
                        running = False
            
            # Reduzierte Wartezeit für bessere Reaktion
            pygame.time.wait(50)
            
        return running
    finally:
        # Aufräumen
        player.stop()
        player.release()
        instance.release()
        # Event-Grabbing wieder deaktivieren
        pygame.event.set_grab(False)

def get_primary_monitor():
    """
    Liefert Position und Größe des primären Monitors
    anhand der 'screeninfo'-Bibliothek.
    """
    monitors = get_monitors()
    primary_monitor = next((m for m in monitors if m.is_primary), monitors[0])
    return {
        'left': primary_monitor.x,
        'top': primary_monitor.y,
        'width': primary_monitor.width,
        'height': primary_monitor.height
    }

def main():
    pygame.init()
    
    # Fenster-Setup auf dem Hauptmonitor
    primary_monitor = get_primary_monitor()
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{primary_monitor['left']},{primary_monitor['top']}"
    screen = pygame.display.set_mode(
        (primary_monitor['width'], primary_monitor['height']), 
        pygame.FULLSCREEN
    )
    pygame.mouse.set_visible(False)
    
    # Warten, bis das Fenster korrekt initialisiert ist
    pygame.time.wait(1000)
    pygame.event.clear()

    # Pfad zum Videoverzeichnis
    video_folder = Path("C:/Users/plimp/OneDrive/Drohne/Bildschirmschoner")
    print(f"Suche in Ordner: {video_folder}")
    
    try:
        if not video_folder.exists():
            raise FileNotFoundError(f"Ordner nicht gefunden: {video_folder}")

        # Alle unterstützten Videoformate
        video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".hevc", ".265"]
        
        # Sammle alle Videos
        video_files = []
        for ext in video_extensions:
            video_files.extend(video_folder.glob(f"*{ext}"))

        video_files = list(video_files)  # Generator in Liste umwandeln
        if not video_files:
            raise FileNotFoundError("Keine Videodateien im Ordner gefunden.")
            
        print(f"\nGefundene Videos: {len(video_files)}")
        for video in video_files:
            print(f"- {video.name}")

        running = True
        while running:
            # Wähle zufällig ein Video aus
            selected_video = random.choice(video_files)
            video_path = str(selected_video).replace('\\', '/')
            print(f"\nStarte Video: {video_path}")
            
            # Starte das Video. Falls der Nutzer Maus/Tastatur bewegt, wird abgebrochen.
            running = play_video(screen, video_path)

    except Exception as e:
        print("Fehler aufgetreten:")
        print(f"Fehlertyp: {type(e)}")
        print(f"Fehlermeldung: {str(e)}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
