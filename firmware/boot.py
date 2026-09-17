import board
import digitalio
import storage
import time

# Utilise SW1 (GP28) comme bouton de sécurité
safe_mode_button = digitalio.DigitalInOut(board.GP28)
safe_mode_button.direction = digitalio.Direction.INPUT
safe_mode_button.pull = digitalio.Pull.DOWN

# Attendre un peu que le bouton se stabilise
time.sleep(0.1)

# Si SW1 n'est PAS appuyé au démarrage, désactiver le stockage
if not safe_mode_button.value:
    storage.disable_usb_drive()