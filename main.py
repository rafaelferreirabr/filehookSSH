from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os.path
import threading
import paramiko

class Ssh():
    def __init__(self, host, user, pwd):
          self.host = host
          self.user = user
          self.pwd = pwd

    def send_file(self, local_file_path, remote_file_path):
        try:     
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host, username=self.user, password=self.pwd)

            sftp = ssh.open_sftp()
            sftp.put(local_file_path, remote_file_path)
            print('arquivo enviado com sucesso')
            sftp.close()
            ssh.close()
        except Exception as e:
            print(f"Erro: {e}")
            sftp.close()
            ssh.close()
    

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
                    ssh = Ssh(host='10.0.50.5', user='localadmin', pwd='Ssi01022023')
                    relative_path = event.src_path
                    relative_path = relative_path.replace("/home/ferreira/code/ciweb/public_ciweb","")
                    ssh.send_file(local_file_path=event.src_path +'/'+ self.file_name,
                                  remote_file_path=f"/var/www/html{relative_path}/{self.file_name}")
                    
                    print(f"arquivo {self.file_name} enviado por ssh para /var/www/html{relative_path}/{self.file_name}")
                    self.last_file = self.file_name

observer = Observer()
handler = MyHandler()
path = "/home/ferreira/code/ciweb/public_ciweb"
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