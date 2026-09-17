# Configurateur MacroPad

Logiciel PC (Python / Tkinter) pour lire et modifier l'action de chaque touche du MacroPad.

## Utilisation

Nécessite Python 3 :

```
pip install -r requirements.txt
python main.py
```

1. Brancher le MacroPad, choisir son port COM puis cliquer sur **Connecter**.
   La configuration actuelle du Pico est chargée automatiquement.
2. Modifier les touches. En type `keyboard`, écrire les touches séparées par `+`
   (ex. `CONTROL+SHIFT+ESCAPE`) ; en type `media`, écrire l'action (ex. `PLAY_PAUSE`).
   La liste des valeurs possibles est dans [firmware/README.md](../firmware/README.md).
3. Cliquer sur **Envoyer au Pico**.

Les boutons **Sauvegarder / Charger fichier** utilisent `macropad_config.json`
dans le dossier courant.

## Générer un exécutable Windows (optionnel)

Pour utiliser le configurateur sur un PC sans Python :

```
pip install pyinstaller
pyinstaller main.spec
```

L'exécutable est créé dans `dist/MacroPad-Configurator.exe`.
