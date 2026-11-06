# 🚀 Héberger l'invitation sur GitHub Pages (gratuit)

## Ce que GitHub Pages peut héberger
GitHub Pages ne sert que des **fichiers statiques** (HTML, CSS, JS, images).
Python n'y tourne pas : le **backend FastAPI ne peut pas y vivre**.

| Élément | Sur GitHub Pages | Dépend du serveur ? |
|---|---|---|
| Invitation (photos, compte à rebours, dress code, galerie) | ✅ 100 % | Non |
| 🎵 Musique à l'ouverture de l'enveloppe | ✅ | Non (YouTube exige juste une origine web — GitHub Pages la fournit) |
| Formulaire RSVP | ⚠️ Fonctionne mais les réponses restent **sur l'appareil de l'invité** tant que le backend n'est pas joignable | Oui pour centraliser |
| Livre d'or | ✅ (messages locaux) | — |
| Tableau de bord admin | ✅ La page s'affiche, **mais** elle doit pointer vers un serveur allumé | Oui |

---

## Étape 1 — Créer le dépôt
1. Connectez-vous sur https://github.com → bouton **New repository**
2. Nom : `mariage-diane-amon` (exemple) — visibilité **Public** (obligatoire pour Pages gratuit)
3. Cochez **Add a README** → **Create repository**

## Étape 2 — Envoyer les fichiers
Dans le dépôt : bouton **Add file → Upload files**, puis glissez-déposez :
- `index.html`
- `admin.html`
- le dossier `assets/` (les 5 photos)

⚠️ **N'uploadez pas** : `Images/` (photos privées non triées), `DEMARRER-SERVEUR.bat`.

> 💡 Si vous comptez héberger le backend sur Render (recommandé — voir
> `HEBERGER-SUR-RENDER.md`), uploadez **aussi** le dossier `backend/` et le
> fichier `render.yaml` : un seul dépôt servira alors tout le site.

Glisser le dossier `assets` en un seul geste fonctionne dans le navigateur.
Attendez la fin de l'upload (barre de progression) → **Commit changes**.

## Étape 3 — Activer GitHub Pages
1. Dans le dépôt : **Settings → Pages** (menu de gauche)
2. « Build and deployment » → **Source : Deploy from a branch**
3. **Branch : main** / dossier **/(root)** → **Save**
4. Attendez 1 à 2 minutes, rechargez la page : l'adresse s'affiche en haut :
   `https://VOTRE-PSEUDO.github.io/mariage-diane-amon/`

## Étape 4 — Tester vous-même
Ouvrez l'adresse ci-dessus sur votre téléphone :
- l'enveloppe s'ouvre → **la musique démarre** 🎵
- le formulaire RSVP se remplit (réponse gardée localement, message discret si le serveur est absent)
- `https://VOTRE-PSEUDO.github.io/mariage-diane-amon/admin.html` → écran de connexion admin

---

## 📡 Et pour RECEVOIR les RSVP des invités ?

Il faut que votre backend soit **joignable depuis Internet**. Trois options :

### Option A — Le plus simple : garder le serveur chez vous + tunnel
Pendant les semaines qui précèdent le mariage :
1. Double-clic sur `DEMARRER-SERVEUR.bat` (serveur sur 8010)
2. Installez un tunnel gratuit une fois : https://dashboard.ngrok.com (ou Cloudflare Tunnel)
3. `ngrok http 8010` → il vous donne une adresse du type `https://abcd-12.ngrok-free.app`
4. Dans `index.html` (ligne `CONFIG.api`), mettez `base: 'https://abcd-12.ngrok-free.app'`
5. Dans l'admin (écran de connexion), champ **Adresse du serveur** → la même adresse

Inconvénient : l'ordinateur doit rester allumé quand les invités répondent.

### Option B — Héberger le backend gratuitement 24h/24 (Render.com)
1. Créez un compte sur https://render.com → **New → Web Service**
2. Connectez votre dépôt GitHub (vous pouvez y pousser aussi le dossier `backend/`)
3. Build : `pip install -r requirements.txt` — Start : `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Render vous donne une adresse fixe → mettez-la dans `CONFIG.api.base` (index.html)
   et dans le champ « Adresse du serveur » de l'admin
5. Sur Render, utilisez un disque persistant ou acceptez que la base SQLite se réinitialise
   (sinon exportez régulièrement la liste via **Export CSV** de l'admin)

### Option C — Sans backend du tout
Les invités confirment via le bouton **WhatsApp** de la confirmation : vous recevez
les messages directement sur votre téléphone. Aucun serveur nécessaire.

---

## 🔐 Avant de partager le lien
- [ ] Changez le mot de passe admin (`backend/.env` → `ADMIN_PASSWORD`) **si le backend est en ligne**
- [ ] Remplacez `CONFIG.api.whatsappPhone` dans `index.html` par votre vrai numéro WhatsApp
- [ ] Testez un RSVP sur votre téléphone + vérifiez-le dans l'admin
