import tkinter as tk
from screeninfo import get_monitors
import threading
import os
import pygame

def show_black_screen(monitor):
    """
    Zeigt einen schwarzen Bildschirm auf dem angegebenen sekundären Monitor an.
    Beendet sich bei Mausbewegung oder Tastendruck.
    """
    def on_event(event):
        root.destroy()

    root = tk.Tk()
    root.title("Black Screen")
    root.attributes('-fullscreen', True)
    root.configure(background='black')
    root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
    root.bind_all("<Any-KeyPress>", on_event)
    root.bind_all("<Any-Button>", on_event)
    root.bind_all("<Motion>", on_event)
    root.attributes('-topmost', True)

    # Verstecke den Mauszeiger
    root.config(cursor="none")

    root.mainloop()

def main():
    """
    Hauptfunktion zur Anzeige von schwarzen Bildschirmen auf allen Monitoren.
    """
    # Erhalte Monitorinformationen
    monitors = get_monitors()
    
    # Zeige Informationen für alle Monitore
    for monitor in monitors:
        if monitor.is_primary:
            print(f"Primärer Monitor: {monitor.name} ({monitor.width}x{monitor.height})")
        else:
            print(f"Sekundärer Monitor: {monitor.name} ({monitor.width}x{monitor.height})")

    # Erstelle und starte einen Thread für jeden Monitor
    threads = []
    for monitor in monitors:  # Hier wurde die Schleife geändert, um alle Monitore einzuschließen
        t = threading.Thread(target=show_black_screen, args=(monitor,))
        t.start()
        threads.append(t)

    print("Schwarze Bildschirme werden auf allen Monitoren angezeigt.")
    print("Bewegen Sie die Maus, klicken Sie eine Taste oder drücken Sie eine Taste, um das Skript zu beenden.")

    # Warte darauf, dass alle Threads beendet werden
    for t in threads:
        t.join()

    print("Skript beendet.")

if __name__ == "__main__":
    main()
