# 🎵 TikSave — Téléchargeur TikTok

Application web locale pour télécharger des vidéos TikTok (MP4) ou leur audio (MP3), sans watermark.

## Stack technique
- **Backend** : Python + Flask + yt-dlp
- **Frontend** : HTML/CSS/JS (aucune dépendance)

## Installation

```bash
# 1. Installer les dépendances Python
pip install flask flask-cors yt-dlp

# 2. Lancer le serveur
cd tiktok-downloader
python app.py
```

## Utilisation
1. Ouvre http://localhost:5000 dans ton navigateur
2. Copie l'URL d'une vidéo TikTok
3. Choisis MP4 (vidéo) ou MP3 (audio)
4. Clique sur "Télécharger"
5. Sauvegarde le fichier une fois prêt

## Formats d'URL supportés
- `https://www.tiktok.com/@username/video/1234567890`
- `https://vm.tiktok.com/XXXXX/` (liens courts)
- `https://vt.tiktok.com/XXXXX/`

## Notes
- Les fichiers sont supprimés automatiquement après 10 minutes
- Usage **personnel** uniquement — respecte les CGU TikTok
- Nécessite une connexion internet active

## Mise à jour yt-dlp (si TikTok change son API)
```bash
pip install -U yt-dlp
```