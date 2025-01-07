import pygame
import sys
import os
import random
import cv2
import vlc
from pathlib import Path
import time
from screeninfo import get_monitors

def play_with_vlc(screen, video_path):
    instance = vlc.Instance()
    player = instance.media_player_new()
    
    # Pygame Fenster-Handle für VLC setzen
    if sys.platform == "win32":
        player.set_hwnd(pygame.display.get_wm_info()['window'])
    elif sys.platform == "linux":
        player.set_xwindow(pygame.display.get_wm_info()['window'])
    elif sys.platform == "darwin":
        player.set_nsobject(pygame.display.get_wm_info()['window'])

    try:
        media = instance.media_new(video_path)
        player.set_media(media)
        player.play()
        
        time.sleep(0.5)  # Warten bis Video geladen ist
        
        running = True
        while running and player.get_state() != vlc.State.Ended:
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
            
            pygame.time.wait(100)
            
        return running
    finally:
        player.stop()
        player.release()
        instance.release()

def play_with_cv2(screen, video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Konnte Video nicht öffnen: {video_path}")

    screen_width, screen_height = screen.get_size()
    print(f"Erkannte Bildschirmauflösung: {screen_width}x{screen_height}")
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    clock = pygame.time.Clock()
    
    try:
        running = True
        while running:
            ret, frame = cap.read()
            
            if not ret:
                break

            frame = cv2.resize(frame, (screen_width, screen_height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            
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

            screen.blit(frame_surface, (0, 0))
            pygame.display.flip()
            clock.tick(fps)
            
        return running
    finally:
        cap.release()

def get_screen_resolution():
    # Zeige Information über alle Monitore
    monitors = get_monitors()
    for i, monitor in enumerate(monitors):
        print(f"Monitor {i+1}: {monitor.width}x{monitor.height}")
    
    # Verwende den primären Monitor für die Rückgabewerte
    primary_monitor = monitors[0]
    return primary_monitor.width, primary_monitor.height

def main():
    pygame.init()
    
    # Hole Bildschirmauflösung vor dem Setzen des Vollbildmodus
    screen_width, screen_height = get_screen_resolution()
    print(f"Erkannte Bildschirmauflösung: {screen_width}x{screen_height}")
    
    # Setze Bildschirmmodus mit erkannter Auflösung
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    
    pygame.time.wait(1000)
    pygame.event.clear()

    video_folder = Path("C:/Users/plimp/OneDrive/Drohne/Bildschirmschoner")
    print(f"Suche in Ordner: {video_folder}")
    
    try:
        if not os.path.exists(video_folder):
            raise FileNotFoundError(f"Ordner nicht gefunden: {video_folder}")

        hevc_extensions = [".hevc", ".265"]
        standard_extensions = [".mp4", ".avi", ".mov", ".mkv"]
        
        video_files = {
            "hevc": [],
            "standard": []
        }
        
        # Dateien nach Typ sortieren
        for ext in hevc_extensions:
            video_files["hevc"].extend(list(video_folder.glob(f"*{ext}")))
        for ext in standard_extensions:
            video_files["standard"].extend(list(video_folder.glob(f"*{ext}")))

        # Neue Ausgabe der gefundenen Videos
        print("\nGefundene HEVC Videos:")
        for video in video_files["hevc"]:
            print(f"- {video.name}")
            
        print("\nGefundene Standard Videos:")
        for video in video_files["standard"]:
            print(f"- {video.name}")

        all_videos = video_files["hevc"] + video_files["standard"]
        if not all_videos:
            raise FileNotFoundError("Keine Videodateien im Ordner gefunden.")
            
        print(f"\nGesamtanzahl gefundener Videos: {len(all_videos)}\n")

        running = True
        while running:
            selected_video = random.choice(all_videos)
            video_path = str(selected_video).replace('\\', '/')
            print(f"Starte Video: {video_path}")
            
            # Prüfen ob HEVC Video
            is_hevc = any(video_path.lower().endswith(ext) for ext in hevc_extensions)
            
            if is_hevc:
                print("Verwende VLC Player für HEVC Video")
                running = play_with_vlc(screen, video_path)
            else:
                print("Verwende CV2 für Standard Video")
                running = play_with_cv2(screen, video_path)

    except Exception as e:
        print(f"Fehler aufgetreten:")
        print(f"Fehlertyp: {type(e)}")
        print(f"Fehlermeldung: {str(e)}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()