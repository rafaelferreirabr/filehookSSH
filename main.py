from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os.path
import threading

class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.file_name = None
        self.last_file = None
        self.lock = threading.Lock()

    def on_any_event(self, event):
        if event.event_type == "modified":
            if not event.is_directory:
                self.file_name = os.path.basename(event.src_path)
            def reset_last_file():
                with self.lock:
                    self.last_file = None
            with self.lock:
                if hasattr(self, "timer"):
                    self.timer.cancel()
                self.timer = threading.Timer(1.0, self.print_event, args=[event])
                # Iniciar o timer
                self.timer.start()

    def print_event(self, event):
        
        if self.file_name != self.last_file or not self.last_file:
                    print(f"enviar arquivo por ssh - {event.src_path}{self.file_name}")
                    self.last_file = self.file_name

observer = Observer()
handler = MyHandler()
path = "./obs"
observer.schedule(handler, path, recursive=True)
observer.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    # Parar o observador quando o usuário pressionar Ctrl+C
    observer.stop()

# Aguardar até que todas as threads sejam encerradas 
observer.join()