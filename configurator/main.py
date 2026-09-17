import tkinter as tk
from tkinter import ttk, messagebox
import json
import serial
import serial.tools.list_ports
import time

class MacroPadConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurateur Macro Pad")
        self.root.geometry("800x600")
        
        self.serial_port = None
        self.config = self.load_default_config()
        
        self.create_ui()
        
    def load_default_config(self):
        """Configuration par défaut"""
        return {
            "sw1": {"type": "keyboard", "keys": ["CONTROL", "ALT", "DELETE"], "name": "Ctrl+Alt+Del"},
            "sw2": {"type": "keyboard", "keys": ["WINDOWS", "SHIFT", "S"], "name": "Screenshot"},
            "sw3": {"type": "keyboard", "keys": ["CONTROL", "SHIFT", "ESCAPE"], "name": "Task Manager"},
            "sw4": {"type": "keyboard", "keys": ["CONTROL", "C"], "name": "Copier"},
            "sw5": {"type": "keyboard", "keys": ["CONTROL", "V"], "name": "Coller"},
            "sw6": {"type": "keyboard", "keys": ["CONTROL", "W"], "name": "Fermer"},
            "sw7": {"type": "media", "action": "PREVIOUS_TRACK", "name": "Piste précédente"},
            "sw8": {"type": "media", "action": "NEXT_TRACK", "name": "Piste suivante"},
            "sw9": {"type": "media", "action": "PLAY_PAUSE", "name": "Play/Pause"},
        }
    
    def create_ui(self):
        # Frame de connexion
        conn_frame = ttk.LabelFrame(self.root, text="Connexion", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=0, padx=5)
        self.port_combo = ttk.Combobox(conn_frame, width=30)
        self.port_combo.grid(row=0, column=1, padx=5)
        
        ttk.Button(conn_frame, text="Rafraîchir", command=self.refresh_ports).grid(row=0, column=2, padx=5)
        self.connect_btn = ttk.Button(conn_frame, text="Connecter", command=self.connect)
        self.connect_btn.grid(row=0, column=3, padx=5)
        
        self.status_label = ttk.Label(conn_frame, text="Déconnecté", foreground="red")
        self.status_label.grid(row=0, column=4, padx=5)
        
        # Frame de configuration
        config_frame = ttk.LabelFrame(self.root, text="Configuration des touches", padding=10)
        config_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Canvas avec scrollbar pour les boutons
        canvas = tk.Canvas(config_frame)
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Créer les configurations pour chaque bouton
        self.button_frames = {}
        for i in range(1, 10):
            sw_name = f"sw{i}"
            self.create_button_config(scrollable_frame, sw_name, i-1)
        
        # Frame de contrôle
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(control_frame, text="📥 Lire config du Pico", command=self.read_config_from_pico).pack(side="left", padx=5)
        ttk.Button(control_frame, text="📤 Envoyer au Pico", command=self.send_config).pack(side="left", padx=5)
        ttk.Button(control_frame, text="💾 Charger fichier", command=self.load_config).pack(side="left", padx=5)
        ttk.Button(control_frame, text="💾 Sauvegarder fichier", command=self.save_config).pack(side="left", padx=5)
        
        self.refresh_ports()
    
    def create_button_config(self, parent, sw_name, row):
        frame = ttk.LabelFrame(parent, text=f"Bouton {sw_name.upper()}", padding=5)
        frame.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
        parent.columnconfigure(0, weight=1)
        
        # Nom
        ttk.Label(frame, text="Nom:").grid(row=0, column=0, sticky="w", padx=5)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.grid(row=0, column=1, sticky="ew", padx=5)
        name_entry.insert(0, self.config[sw_name]["name"])
        
        # Type
        ttk.Label(frame, text="Type:").grid(row=1, column=0, sticky="w", padx=5)
        type_combo = ttk.Combobox(frame, values=["keyboard", "media"], state="readonly", width=28)
        type_combo.grid(row=1, column=1, sticky="ew", padx=5)
        type_combo.set(self.config[sw_name]["type"])
        
        # Configuration
        config_label = ttk.Label(frame, text="Config:")
        config_label.grid(row=2, column=0, sticky="w", padx=5)
        config_entry = ttk.Entry(frame, width=30)
        config_entry.grid(row=2, column=1, sticky="ew", padx=5)
        
        if self.config[sw_name]["type"] == "keyboard":
            config_entry.insert(0, "+".join(self.config[sw_name]["keys"]))
        else:
            config_entry.insert(0, self.config[sw_name]["action"])
        
        frame.columnconfigure(1, weight=1)
        
        # Stocker les widgets pour récupération
        self.button_frames[sw_name] = {
            "name": name_entry,
            "type": type_combo,
            "config": config_entry
        }
    
    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)
    
    def connect(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_port = None
            self.status_label.config(text="Déconnecté", foreground="red")
            self.connect_btn.config(text="Connecter")
        else:
            try:
                port = self.port_combo.get()
                self.serial_port = serial.Serial(port, 115200, timeout=1)
                time.sleep(2)  # Attendre la connexion
                self.status_label.config(text=f"Connecté sur {port}", foreground="green")
                self.connect_btn.config(text="Déconnecter")
                
                # Lire automatiquement la config du Pico
                self.read_config_from_pico()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de se connecter: {str(e)}")
    
    def read_config_from_pico(self):
        """Lit la configuration actuelle du Pico"""
        if not self.serial_port or not self.serial_port.is_open:
            messagebox.showwarning("Attention", "Veuillez vous connecter au macro pad d'abord")
            return
        
        try:
            # Vider les buffers
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            # Demander la config au Pico
            self.serial_port.write(b"GET_CONFIG\n")
            
            # Attendre la réponse (max 2 secondes)
            timeout = time.time() + 2
            response = ""
            
            while time.time() < timeout:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='ignore')
                    response += data
                    
                    # Si on a reçu une ligne complète avec CONFIG_DATA:
                    if "CONFIG_DATA:" in response:
                        break
                time.sleep(0.1)
            
            print(f"Réponse brute: {response}")  # Debug
            
            # Extraire le JSON de la réponse
            if "CONFIG_DATA:" in response:
                # Trouver la ligne qui commence par CONFIG_DATA:
                for line in response.split('\n'):
                    if line.startswith("CONFIG_DATA:"):
                        json_str = line[12:].strip()  # Enlever "CONFIG_DATA:"
                        print(f"JSON reçu: {json_str}")  # Debug
                        
                        pico_config = json.loads(json_str)
                        
                        # Mettre à jour l'interface avec la config du Pico
                        for sw_name, sw_config in pico_config.items():
                            if sw_name in self.button_frames:
                                widgets = self.button_frames[sw_name]
                                
                                # Nom (garder celui actuel si absent du Pico)
                                if "name" in sw_config:
                                    widgets["name"].delete(0, tk.END)
                                    widgets["name"].insert(0, sw_config["name"])
                                
                                # Type
                                widgets["type"].set(sw_config["type"])
                                
                                # Config
                                widgets["config"].delete(0, tk.END)
                                if sw_config["type"] == "keyboard":
                                    widgets["config"].insert(0, "+".join(sw_config["keys"]))
                                else:
                                    widgets["config"].insert(0, sw_config["action"])
                        
                        messagebox.showinfo("Succès", "Configuration du Pico chargée !")
                        return
            
            messagebox.showwarning("Attention", "Pas de réponse du Pico. Vérifiez le code.py")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("Erreur", f"Erreur de parsing JSON: {str(e)}\nRéponse: {response}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la lecture: {str(e)}")
    
    def test_connection(self):
        """Test la connexion série en envoyant un simple message"""
        if not self.serial_port or not self.serial_port.is_open:
            messagebox.showwarning("Attention", "Veuillez vous connecter au macro pad d'abord")
            return
        
        try:
            # Vider le buffer
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            # Envoyer un test
            self.serial_port.write(b"TEST\n")
            messagebox.showinfo("Test", "Commande de test envoyée")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de test: {str(e)}")
    
    def get_current_config(self):
        """Récupère la configuration depuis l'interface"""
        config = {}
        for sw_name, widgets in self.button_frames.items():
            sw_type = widgets["type"].get()
            config_str = widgets["config"].get()
            
            config[sw_name] = {
                "name": widgets["name"].get(),
                "type": sw_type
            }
            
            if sw_type == "keyboard":
                config[sw_name]["keys"] = [k.strip() for k in config_str.split("+")]
            else:
                config[sw_name]["action"] = config_str
        
        return config
    
    def send_config(self):
        if not self.serial_port or not self.serial_port.is_open:
            messagebox.showwarning("Attention", "Veuillez vous connecter au macro pad d'abord")
            return
        
        try:
            config = self.get_current_config()
            
            # Préparer le JSON (enlever les champs "name" pour le Pico)
            pico_config = {}
            for sw_name, sw_data in config.items():
                pico_config[sw_name] = {
                    "type": sw_data["type"]
                }
                if sw_data["type"] == "keyboard":
                    pico_config[sw_name]["keys"] = sw_data["keys"]
                else:
                    pico_config[sw_name]["action"] = sw_data["action"]
            
            json_config = json.dumps(pico_config)
            
            # Vider les buffers
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            # Envoyer la configuration
            message = f"CONFIG:{json_config}\n"
            print(f"Envoi: {message}")  # Debug
            self.serial_port.write(message.encode('utf-8'))
            
            # Attendre la réponse
            time.sleep(0.5)
            if self.serial_port.in_waiting > 0:
                response = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='ignore')
                print(f"Réponse: {response}")  # Debug
                if "OK" in response:
                    messagebox.showinfo("Succès", "Configuration envoyée et confirmée !")
                else:
                    messagebox.showwarning("Attention", f"Réponse du Pico: {response}")
            else:
                messagebox.showinfo("Envoyé", "Configuration envoyée (pas de réponse)")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'envoi: {str(e)}")
    
    def save_config(self):
        try:
            config = self.get_current_config()
            with open("macropad_config.json", "w") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Succès", "Configuration sauvegardée dans macropad_config.json")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def load_config(self):
        try:
            with open("macropad_config.json", "r") as f:
                config = json.load(f)
            
            # Mettre à jour l'interface
            for sw_name, sw_config in config.items():
                if sw_name in self.button_frames:
                    widgets = self.button_frames[sw_name]
                    widgets["name"].delete(0, tk.END)
                    widgets["name"].insert(0, sw_config["name"])
                    widgets["type"].set(sw_config["type"])
                    
                    widgets["config"].delete(0, tk.END)
                    if sw_config["type"] == "keyboard":
                        widgets["config"].insert(0, "+".join(sw_config["keys"]))
                    else:
                        widgets["config"].insert(0, sw_config["action"])
            
            messagebox.showinfo("Succès", "Configuration chargée")
        except FileNotFoundError:
            messagebox.showwarning("Attention", "Fichier de configuration non trouvé")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroPadConfigurator(root)
    root.mainloop()