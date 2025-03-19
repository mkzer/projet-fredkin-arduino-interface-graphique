# Implémentation d'un Automate Cellulaire 2D de Fredkin sur Arduino

## Description
Ce projet consiste en la conception et l'implémentation d'un automate cellulaire bidimensionnel de Fredkin sur une plateforme Arduino Mega 2560, avec une interface graphique en Python utilisant Tkinter. L'objectif est d'offrir une visualisation en temps réel des évolutions de l'automate tout en assurant une synchronisation efficace des données et un enregistrement des logs.

## Fonctionnalités
- **Simulation d'un automate cellulaire de Fredkin** avec voisinages von Neumann et Moore.
- **Affichage graphique** via un écran TFT 3,5 pouces piloté par l'Arduino.
- **Interface en Python** permettant de contrôler et visualiser la simulation.
- **Gestion des logs** pour enregistrer l'évolution de l'automate.
- **Synchronisation des données** entre l'Arduino et l'interface PC.

## Matériel requis
- Arduino Mega 2560
  ![image](https://github.com/user-attachments/assets/f4ccfd8c-a6d9-4689-a145-531d486f2398)
- Écran TFT 3,5 pouces (ILI9486)
- Câble USB pour la communication avec le PC

## Bibliothèques utilisées
### Côté Arduino
- `MCUFRIEND_kbv` : Gestion de l'écran TFT
- `Adafruit_GFX` : Affichage des graphismes
- `Serial` : Communication avec l'interface PC

### Côté Python
- `pyserial` : Communication série avec l'Arduino
- `tkinter` : Interface graphique
- `matplotlib` : Visualisation des données

## Installation
1. **Arduino**
   - Installer les bibliothèques requises depuis le gestionnaire de bibliothèques de l'IDE Arduino.
   - Charger le fichier `fredkin.ino` sur l'Arduino Mega 2560.

2. **Python**
   - Installer les dépendances avec pip :
     ```sh
     pip install pyserial matplotlib
     ```
   - Exécuter `interface.py` pour lancer l'interface graphique.

## Utilisation
1. **Connexion**
   - Brancher l'Arduino et identifier le port série (à adapter dans `interface.py`).
   - Lancer `interface.py` et vérifier la connexion.

2. **Simulation**
   - Configurer la grille initiale et choisir le type d'automate de Fredkin.
   - Lancer la simulation et observer l'évolution en temps réel.
   - Exporter les logs pour analyse.

## Exemples de sortie
- **Affichage sur écran TFT** : Visualisation directe de la grille de l'automate.
- **Interface graphique Python** : Interaction et contrôle des paramètres.
- **Logs** : Fichier texte contenant l'évolution de l'automate.

## Améliorations futures
- Optimisation de la gestion mémoire pour supporter des grilles plus grandes.
- Ajout de nouvelles règles et types d'automates cellulaires.
- Migration vers des bibliothèques graphiques plus avancées (PyQt, Kivy).

## Auteurs
- **MAKHEZER Mohamed Anis**
- **ALLOUCHE Mohamed Abdelmalek**

Projet réalisé dans le cadre du Master 1 EEA - Mesure et Traitement de l'Information, Université de Lorraine, 2024-2025.
