import serial
import tkinter as tk
from tkinter import messagebox, filedialog
import datetime
import time
import os

# Configuration du port série
SERIAL_PORT = "COM3"  # À adapter à ta machine
BAUD_RATE = 115200
TIMEOUT = 1  # Timeout en secondes

class FredkinInterface:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 48, 32
        self.CELL_SIZE = 10
        self.serial = None
        self.running = False
        self.log_file = None
        
        # Grille en mémoire Python (0 = mort/blanc, 1 = vivant/rouge)
        self.grille = [[0]*self.HEIGHT for _ in range(self.WIDTH)]
        
        self.setup_gui()
        self.connect_serial()
        
    def connect_serial(self):
        """Établit la connexion série avec gestion d'erreur."""
        try:
            self.serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
            time.sleep(2)  # Attente de la connexion série
            self.status_label.config(text="Connecté", fg="green")
        except serial.SerialException as e:
            self.status_label.config(text="Non connecté", fg="red")
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le port {SERIAL_PORT}. {e}")
            self.serial = None

    def setup_gui(self):
        """Initialise l'interface graphique."""
        self.root = tk.Tk()
        self.root.title("Automate Fredkin 48x32")
        
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=10, pady=10)
        
        # Canvas pour dessiner la grille
        self.canvas = tk.Canvas(
            main_frame,
            width=self.WIDTH * self.CELL_SIZE,
            height=self.HEIGHT * self.CELL_SIZE,
            bg="white"
        )
        self.canvas.pack()
        
        # Frame pour les contrôles
        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(pady=10)
        
        # Frame pour le fichier de logs
        log_frame = tk.Frame(main_frame)
        log_frame.pack(pady=5)
        
        # Label et bouton pour le fichier de logs
        self.log_label = tk.Label(log_frame, text="Aucun fichier de logs sélectionné", wraplength=400)
        self.log_label.pack(side=tk.LEFT, padx=5)
        tk.Button(log_frame, text="Choisir fichier logs", command=self.select_log_file).pack(side=tk.LEFT, padx=5)
        
        # Étiquette pour le nombre de générations
        tk.Label(controls_frame, text="Générations:").pack(side=tk.LEFT)
        
        # Champ pour choisir le nombre de générations
        self.entry_generations = tk.Entry(controls_frame, width=10)
        self.entry_generations.insert(0, "10")
        self.entry_generations.pack(side=tk.LEFT, padx=5)
        
        # Boutons de contrôle
        tk.Button(controls_frame, text="Envoyer Grille", command=self.envoyer_grille).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Fredkin 1", command=lambda: self.set_mode("FREDKIN1")).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Fredkin 2", command=lambda: self.set_mode("FREDKIN2")).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Effacer", command=self.clear_grid).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Non connecté", fg="red")
        self.status_label.pack(pady=5)
        
        # Binding des événements
        self.canvas.bind("<Button-1>", self.clic_souris)
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup_and_exit)
        
        self.dessiner_grille()

    def select_log_file(self):
        """Permet à l'utilisateur de choisir l'emplacement du fichier de logs."""
        initial_dir = os.path.dirname(self.log_file) if self.log_file else os.getcwd()
        filename = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            title="Choisir le fichier de logs",
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
            initialfile="logs_fredkin.txt"
        )
        if filename:
            self.log_file = filename
            self.log_label.config(text=f"Logs: {os.path.basename(filename)}")
            # Créer le fichier s'il n'existe pas
            with open(self.log_file, "a") as f:
                f.write(f"[{datetime.datetime.now()}] Fichier de logs créé/ouvert\n")

    def write_log(self, message, with_timestamp=True):
        """Écrit un message dans le fichier de logs."""
        if not self.log_file:
            return
            
        try:
            with open(self.log_file, "a") as f:
                if with_timestamp:
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{now}] {message}\n")
                else:
                    # Pour les lignes de grille, pas d'horodatage
                    prefix_len = len("YYYY-MM-DD HH:MM:SS") + 3
                    spaces = " " * prefix_len
                    f.write(f"{spaces}{message}\n")
        except IOError as e:
            messagebox.showerror("Erreur", f"Impossible d'écrire dans le fichier de logs: {e}")

    def clear_grid(self):
        """Efface toute la grille."""
        self.grille = [[0]*self.HEIGHT for _ in range(self.WIDTH)]
        self.dessiner_grille()

    def dessiner_grille(self):
        """Dessine la grille sur le Canvas Tkinter."""
        self.canvas.delete("all")
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                color = "red" if self.grille[x][y] else "white"
                self.canvas.create_rectangle(
                    x * self.CELL_SIZE, y * self.CELL_SIZE,
                    (x+1) * self.CELL_SIZE, (y+1) * self.CELL_SIZE,
                    fill=color, outline="black"
                )

    def clic_souris(self, event):
        """Gère les clics de souris sur la grille."""
        cx = event.x // self.CELL_SIZE
        cy = event.y // self.CELL_SIZE
        if 0 <= cx < self.WIDTH and 0 <= cy < self.HEIGHT:
            self.grille[cx][cy] = 1 - self.grille[cx][cy]
            self.dessiner_grille()

    def envoyer_grille(self):
        """Envoie la grille à l'Arduino avec gestion d'erreur."""
        if not self.log_file:
            if not messagebox.askyesno("Attention", "Aucun fichier de logs sélectionné. Voulez-vous en choisir un maintenant?"):
                return
            self.select_log_file()
            if not self.log_file:
                return

        if not self.serial or not self.serial.is_open:
            messagebox.showerror("Erreur", "Port série non disponible")
            return

        try:
            generations = int(self.entry_generations.get())
            if generations <= 0:
                raise ValueError("Le nombre de générations doit être >= 1")

            # Réinitialisation du fichier de logs
            self.write_log("Début nouvelle simulation")

            # Conversion de la grille en chaîne binaire
            grille_str = "".join(str(self.grille[x][y]) for y in range(self.HEIGHT) for x in range(self.WIDTH))
            
            # Envoi des données
            data = f"GEN:{generations}:{grille_str}\n"
            self.serial.write(data.encode())
            self.serial.flush()

        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
        except serial.SerialException as e:
            messagebox.showerror("Erreur", f"Erreur de communication série: {e}")
            self.status_label.config(text="Déconnecté", fg="red")

    def set_mode(self, mode):
        """Configure le mode de simulation avec gestion d'erreur."""
        if not self.serial or not self.serial.is_open:
            messagebox.showerror("Erreur", "Port série non disponible")
            return

        try:
            cmd = f"MODE:{mode}\n"
            self.serial.write(cmd.encode())
            self.serial.flush()
        except serial.SerialException as e:
            messagebox.showerror("Erreur", f"Erreur de communication série: {e}")
            self.status_label.config(text="Déconnecté", fg="red")

    def lire_logs(self):
        """Lit les données de l'Arduino avec timeout."""
        if not self.serial or not self.serial.is_open:
            self.root.after(100, self.lire_logs)
            return

        try:
            if self.serial.in_waiting:
                ligne_complete = self.serial.readline().decode().rstrip('\r\n')
                if ligne_complete:
                    if ligne_complete.startswith("LOG,"):
                        self.write_log(ligne_complete, with_timestamp=True)
                    else:
                        self.write_log(ligne_complete, with_timestamp=False)

                    self.serial.write(b"OK\n")
                    self.serial.flush()

        except (serial.SerialException, IOError) as e:
            print(f"Erreur de communication: {e}")
            self.status_label.config(text="Déconnecté", fg="red")

        self.root.after(100, self.lire_logs)

    def cleanup_and_exit(self):
        """Nettoie les ressources avant de quitter."""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.root.destroy()

    def run(self):
        """Lance l'interface."""
        self.lire_logs()
        self.root.mainloop()

if __name__ == "__main__":
    app = FredkinInterface()
    app.run()
