import board
import digitalio
import time
import usb_hid
import usb_cdc
import json
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# Initialisation du clavier HID
keyboard = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

# Port série pour la communication
serial = usb_cdc.console

# Mapping des noms de touches vers les codes Keycode
KEYCODE_MAP = {
    "CONTROL": Keycode.CONTROL,
    "ALT": Keycode.ALT,
    "DELETE": Keycode.DELETE,
    "WINDOWS": Keycode.WINDOWS,
    "SHIFT": Keycode.SHIFT,
    "S": Keycode.S,
    "ESCAPE": Keycode.ESCAPE,
    "C": Keycode.C,
    "V": Keycode.V,
    "W": Keycode.W,
    "A": Keycode.A,
    "B": Keycode.B,
    "D": Keycode.D,
    "E": Keycode.E,
    "F": Keycode.F,
    "G": Keycode.G,
    "H": Keycode.H,
    "I": Keycode.I,
    "J": Keycode.J,
    "K": Keycode.K,
    "L": Keycode.L,
    "M": Keycode.M,
    "N": Keycode.N,
    "O": Keycode.O,
    "P": Keycode.P,
    "Q": Keycode.Q,
    "R": Keycode.R,
    "T": Keycode.T,
    "U": Keycode.U,
    "X": Keycode.X,
    "Y": Keycode.Y,
    "Z": Keycode.Z,
    "ENTER": Keycode.ENTER,
    "TAB": Keycode.TAB,
    "SPACE": Keycode.SPACE,
    "F1": Keycode.F1,
    "F2": Keycode.F2,
    "F3": Keycode.F3,
    "F4": Keycode.F4,
    "F5": Keycode.F5,
    "F6": Keycode.F6,
    "F7": Keycode.F7,
    "F8": Keycode.F8,
    "F9": Keycode.F9,
    "F10": Keycode.F10,
    "F11": Keycode.F11,
    "F12": Keycode.F12,
}

MEDIA_MAP = {
    "PLAY_PAUSE": ConsumerControlCode.PLAY_PAUSE,
    "NEXT_TRACK": ConsumerControlCode.SCAN_NEXT_TRACK,
    "PREVIOUS_TRACK": ConsumerControlCode.SCAN_PREVIOUS_TRACK,
    "VOLUME_UP": ConsumerControlCode.VOLUME_INCREMENT,
    "VOLUME_DOWN": ConsumerControlCode.VOLUME_DECREMENT,
    "MUTE": ConsumerControlCode.MUTE,
}

# Configuration par défaut
default_config = {
    "sw1": {"type": "keyboard", "keys": ["CONTROL", "ALT", "DELETE"]},
    "sw2": {"type": "keyboard", "keys": ["WINDOWS", "SHIFT", "S"]},
    "sw3": {"type": "keyboard", "keys": ["CONTROL", "SHIFT", "ESCAPE"]},
    "sw4": {"type": "keyboard", "keys": ["CONTROL", "C"]},
    "sw5": {"type": "keyboard", "keys": ["CONTROL", "V"]},
    "sw6": {"type": "keyboard", "keys": ["CONTROL", "W"]},
    "sw7": {"type": "media", "action": "PREVIOUS_TRACK"},
    "sw8": {"type": "media", "action": "NEXT_TRACK"},
    "sw9": {"type": "media", "action": "PLAY_PAUSE"},
}

# Configuration actuelle
config = default_config.copy()

# Configuration des switches
switches = {
    "sw1": board.GP28,
    "sw2": board.GP27,
    "sw3": board.GP26,
    "sw4": board.GP22,
    "sw5": board.GP21,
    "sw6": board.GP20,
    "sw7": board.GP19,
    "sw8": board.GP18,
    "sw9": board.GP17,
}

# Initialisation des pins
switch_pins = {}
for name, pin in switches.items():
    sw = digitalio.DigitalInOut(pin)
    sw.direction = digitalio.Direction.INPUT
    sw.pull = digitalio.Pull.DOWN
    switch_pins[name] = sw

# État précédent des boutons pour détecter les appuis
previous_state = {name: False for name in switches.keys()}

# Buffer pour la réception série
serial_buffer = ""

def load_config_from_file():
    """Charge la configuration depuis le fichier config.json"""
    global config
    try:
        with open("/config.json", "r") as f:
            config = json.load(f)
        print("Configuration chargée depuis le fichier")
    except:
        print("Pas de fichier de configuration, utilisation de la config par défaut")
        config = default_config.copy()

def save_config_to_file():
    """Sauvegarde la configuration dans config.json"""
    try:
        with open("/config.json", "w") as f:
            json.dump(config, f)
        print("Configuration sauvegardée")
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")

def execute_action(sw_name):
    """Exécute l'action configurée pour un switch"""
    if sw_name not in config:
        return
    
    action_config = config[sw_name]
    
    if action_config["type"] == "keyboard":
        # Convertir les noms de touches en keycodes
        keycodes = []
        for key_name in action_config["keys"]:
            if key_name in KEYCODE_MAP:
                keycodes.append(KEYCODE_MAP[key_name])
        
        if keycodes:
            keyboard.press(*keycodes)
            keyboard.release_all()
    
    elif action_config["type"] == "media":
        action_name = action_config["action"]
        if action_name in MEDIA_MAP:
            cc.send(MEDIA_MAP[action_name])

def check_serial_config():
    """Vérifie si une nouvelle configuration est reçue via série (NON BLOQUANT)"""
    global config, serial_buffer
    
    # Vérifier s'il y a des données disponibles
    if serial and serial.in_waiting > 0:
        try:
            # Lire les données disponibles
            data = serial.read(serial.in_waiting)
            if data:
                try:
                    serial_buffer += data.decode('utf-8')
                except:
                    serial_buffer += data.decode('utf-8', 'ignore')
                
                # Chercher une ligne complète (terminée par \n)
                if '\n' in serial_buffer:
                    lines = serial_buffer.split('\n')
                    for line in lines[:-1]:  # Traiter toutes les lignes complètes
                        line = line.strip()
                        
                        # Commande pour recevoir une nouvelle config
                        if line.startswith("CONFIG:"):
                            try:
                                json_str = line[7:]  # Enlever "CONFIG:"
                                new_config = json.loads(json_str)
                                config = new_config
                                save_config_to_file()
                                print("Configuration mise a jour!")
                                serial.write(b"OK\n")
                            except Exception as e:
                                print(f"Erreur parsing config: {e}")
                                serial.write(b"ERROR\n")
                        
                        # Commande pour envoyer la config actuelle
                        elif line == "GET_CONFIG":
                            try:
                                json_config = json.dumps(config)
                                serial.write(f"CONFIG_DATA:{json_config}\n".encode('utf-8'))
                                print("Config envoyee au PC")
                            except Exception as e:
                                print(f"Erreur envoi config: {e}")
                                serial.write(b"ERROR\n")
                    
                    # Garder la dernière partie incomplète dans le buffer
                    serial_buffer = lines[-1]
        except Exception as e:
            print(f"Erreur lecture serie: {e}")
            serial_buffer = ""

# Charger la configuration au démarrage
load_config_from_file()

print("Macro Pad démarré!")

# Boucle principale
while True:
    # Vérifier les commandes série (non bloquant)
    check_serial_config()
    
    # Vérifier l'état de chaque bouton
    for sw_name, sw_pin in switch_pins.items():
        current_state = sw_pin.value
        
        # Détecter un front montant (bouton pressé)
        if current_state and not previous_state[sw_name]:
            execute_action(sw_name)
            time.sleep(0.3)  # Anti-rebond
        
        previous_state[sw_name] = current_state
    
    time.sleep(0.01)  # Petite pause pour ne pas surcharger le CPU