# Firmware

Code CircuitPython pour le Raspberry Pi Pico.

- `code.py` : lit les 9 touches, envoie les raccourcis clavier/média en USB HID,
  et reçoit la configuration du logiciel PC par le port série.
- `boot.py` : cache le lecteur `CIRCUITPY` au démarrage (voir « Mode maintenance »).

## Installation

1. Installer CircuitPython sur le Pico (fichier `.uf2` depuis circuitpython.org).
2. Copier le dossier `adafruit_hid` de l'*Adafruit CircuitPython Library Bundle*
   dans `CIRCUITPY/lib/`.
3. Copier `code.py` puis `boot.py` à la racine de `CIRCUITPY`.
4. Débrancher puis rebrancher le Pico (`boot.py` ne s'exécute qu'au démarrage).

## Mode maintenance

Une fois `boot.py` installé, le lecteur `CIRCUITPY` n'apparaît plus sur le PC.
Pour y accéder à nouveau (mise à jour du code), **maintenir SW1 enfoncé en branchant le Pico**.

## Configuration

La configuration est stockée dans `/config.json` sur le Pico.
Si le fichier est absent, la configuration par défaut de `code.py` est utilisée.

Protocole série (une commande par ligne) :

| Commande envoyée | Réponse du Pico |
|---|---|
| `GET_CONFIG` | `CONFIG_DATA:{...}` |
| `CONFIG:{...}` | `OK` ou `ERROR` |

Format d'une touche :

```json
{"sw1": {"type": "keyboard", "keys": ["CONTROL", "ALT", "DELETE"]},
 "sw9": {"type": "media", "action": "PLAY_PAUSE"}}
```

- **Touches clavier** : `A`–`Z`, `F1`–`F12`, `CONTROL`, `ALT`, `SHIFT`, `WINDOWS`,
  `DELETE`, `ESCAPE`, `ENTER`, `TAB`, `SPACE`
- **Actions média** : `PLAY_PAUSE`, `NEXT_TRACK`, `PREVIOUS_TRACK`,
  `VOLUME_UP`, `VOLUME_DOWN`, `MUTE`
