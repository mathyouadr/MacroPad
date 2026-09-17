# MacroPad

Pavé de 9 touches programmables basé sur un Raspberry Pi Pico (RP2040) sous CircuitPython.
Il se branche en USB et est reconnu comme un clavier (raccourcis + touches média), sans driver.
Un logiciel PC permet de changer l'action de chaque touche sans reprogrammer le Pico.

Projet réalisé par Mathyou ANDRE dans le cadre du chef-d'œuvre Bac Pro CIEL, au LPP Le Marais Sainte-Thérèse.

![MacroPad assemblé](docs/images/macropad.png)

## Sommaire

- [Structure du projet](#structure-du-projet)
- [Firmware](#firmware)
- [Configurateur PC](#configurateur-pc)
- [Configuration des touches](#configuration-des-touches)
- [Matériel](#matériel)
- [Licence](#licence)

## Structure du projet

```text
MACROPAD/
├── firmware/        Code CircuitPython à copier sur le Pico (boot.py, code.py)
├── configurator/    Logiciel PC de configuration (Python / Tkinter)
├── hardware/
│   ├── schematic/   Schéma électronique (PDF, PNG, source EasyEDA)
│   ├── pcb/         PCB : source Fritzing, Gerber pour la fabrication, PDF
│   ├── case/        Boîtier 3D (Fusion 360 + STL pour l'impression)
│   └── libraries/   Composants Fritzing nécessaires pour ouvrir le PCB
└── docs/            Images du README
```

## Firmware

Code CircuitPython du dossier `firmware/`, à copier sur le Raspberry Pi Pico.

- `code.py` : lit les 9 touches, envoie les raccourcis clavier/média en USB HID,
  et reçoit la configuration du logiciel PC par le port série.
- `boot.py` : cache le lecteur `CIRCUITPY` au démarrage (voir [Mode maintenance](#mode-maintenance)).

### Installation

1. Installer CircuitPython sur le Pico (fichier `.uf2` depuis circuitpython.org).
2. Copier le dossier `adafruit_hid` de l'*Adafruit CircuitPython Library Bundle*
   dans `CIRCUITPY/lib/`.
3. Copier `firmware/code.py` puis `firmware/boot.py` à la racine de `CIRCUITPY`.
4. Débrancher puis rebrancher le Pico (`boot.py` ne s'exécute qu'au démarrage).

### Mode maintenance

Une fois `boot.py` installé, le lecteur `CIRCUITPY` n'apparaît plus sur le PC.
Pour y accéder à nouveau (mise à jour du code), **maintenir SW1 enfoncé en branchant le Pico**.

## Configurateur PC

Logiciel Python / Tkinter du dossier `configurator/`, pour lire et modifier l'action de chaque touche.

### Lancement

Nécessite Python 3 :

```bash
cd configurator
pip install -r requirements.txt
python main.py
```

### Utilisation

1. Brancher le MacroPad, choisir son port COM puis cliquer sur **Connecter**.
   La configuration actuelle du Pico est chargée automatiquement.
2. Modifier les touches. En type `keyboard`, écrire les touches séparées par `+`
   (ex. `CONTROL+SHIFT+ESCAPE`) ; en type `media`, écrire l'action (ex. `PLAY_PAUSE`).
   Voir les [valeurs possibles](#valeurs-possibles).
3. Cliquer sur **Envoyer au Pico**.

Les boutons **Sauvegarder / Charger fichier** utilisent `macropad_config.json`
dans le dossier courant.

### Générer un exécutable Windows (optionnel)

Pour utiliser le configurateur sur un PC sans Python :

```bash
cd configurator
pip install pyinstaller
pyinstaller main.spec
```

L'exécutable est créé dans `configurator/dist/MacroPad-Configurator.exe`.

## Configuration des touches

### Configuration par défaut

| Touche | GPIO | Action |
|---|---|---|
| SW1 | GP28 | Ctrl + Alt + Suppr |
| SW2 | GP27 | Capture d'écran (Win + Shift + S) |
| SW3 | GP26 | Gestionnaire des tâches (Ctrl + Shift + Échap) |
| SW4 | GP22 | Copier (Ctrl + C) |
| SW5 | GP21 | Coller (Ctrl + V) |
| SW6 | GP20 | Fermer l'onglet (Ctrl + W) |
| SW7 | GP19 | Piste précédente |
| SW8 | GP18 | Piste suivante |
| SW9 | GP17 | Lecture / Pause |

### Valeurs possibles

- **Touches clavier** : `A`–`Z`, `F1`–`F12`, `CONTROL`, `ALT`, `SHIFT`, `WINDOWS`,
  `DELETE`, `ESCAPE`, `ENTER`, `TAB`, `SPACE`
- **Actions média** : `PLAY_PAUSE`, `NEXT_TRACK`, `PREVIOUS_TRACK`,
  `VOLUME_UP`, `VOLUME_DOWN`, `MUTE`

### Stockage et protocole série

La configuration est stockée dans `/config.json` sur le Pico.
Si le fichier est absent, la configuration par défaut de `code.py` est utilisée.

Format d'une touche :

```json
{"sw1": {"type": "keyboard", "keys": ["CONTROL", "ALT", "DELETE"]},
 "sw9": {"type": "media", "action": "PLAY_PAUSE"}}
```

Commandes série (une par ligne) :

| Commande envoyée | Réponse du Pico |
|---|---|
| `GET_CONFIG` | `CONFIG_DATA:{...}` |
| `CONFIG:{...}` | `OK` ou `ERROR` |

## Matériel

Chaque switch relie son GPIO au 3V3. Le firmware active la résistance de pull-down interne.

- **Schéma** : `hardware/schematic/schematic.pdf`
- **PCB** : conçu avec Fritzing 0.9.9 (`hardware/pcb/MACROPAD-FRIT.fzz`).
  Pour l'ouvrir, importer d'abord les composants de `hardware/libraries/fritzing/`.
  Les fichiers de fabrication sont dans `hardware/pcb/gerber.rar` (visualisables avec gerbv).
- **Boîtier** : `hardware/case/macropad-case.stl` pour l'impression, `.f3d` pour le modifier dans Fusion 360.

![Routage du PCB](docs/images/pcb.png)

## Licence

MIT — voir [LICENSE](LICENSE).
