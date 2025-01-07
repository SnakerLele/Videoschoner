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
    # VLC-Instanz mit Hardware-Decoding und einigen Optimierungen
    # (Passe 'dxva2' für andere Betriebssysteme an, z.B. 'vaapi' oder 'videotoolbox')
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
        last_check_time = time.time()
        last_mouse_pos = pygame.mouse.get_pos()

        while running and player.get_state() not in (vlc.State.Ended, vlc.State.Stopped):
            current_time = time.time()
            
            # Ereignisse häufiger prüfen
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.KEYDOWN):
                    running = False
                    break
            
            # Mausposition alle 50ms prüfen
            if current_time - last_check_time >= 0.05:
                current_mouse_pos = pygame.mouse.get_pos()
                if (abs(current_mouse_pos[0] - last_mouse_pos[0]) > 5 or
                    abs(current_mouse_pos[1] - last_mouse_pos[1]) > 5):
                    running = False
                
                last_mouse_pos = current_mouse_pos
                last_check_time = current_time
            
            # Kürzere Wartezeit
            pygame.time.wait(10)
            
        return running
    finally:
        player.stop()
        player.release()
        instance.release()

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
