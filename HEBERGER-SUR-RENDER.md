# 🌍 Héberger TOUT sur Render.com (gratuit) — invitation + RSVP + admin + WhatsApp

## Pourquoi Render ?
Render exécute votre **backend Python en ligne 24h/24** — et comme le backend
sert déjà l'invitation entière, **un seul hébergement suffit** :

| Fonctionnalité | Render gratuit |
|---|---|
| 💌 Invitation (photos, compte à rebours, galerie) | ✅ |
| 🎵 Musique à l'ouverture de l'enveloppe | ✅ (HTTPS → YouTube accepte le lecteur intégré) |
| 📥 Réception centralisée des RSVP (base de données) | ✅ |
| 👑 Tableau de bord admin (stats, gestion, CSV) | ✅ |
| 💬 WhatsApp (liens wa.me, diffusion) | ✅ |

Adresse obtenue : `https://VOTRE-PROJET.onrender.com` — partageable aux invités.

> ⚠️ **À savoir sur le gratuit** : le serveur s'endort après 15 min d'inactivité ;
> le premier visiteur attend ~50 secondes le temps du réveil. Sans base externe,
> les données SQLite sont réinitialisées à chaque redéploiement → voir la
> section « Base permanente » ci-dessous pour ne plus jamais perdre de RSVP.

---

## Étapes (≈ 15 minutes)

### 🚀 Option express — avec le fichier `render.yaml` (recommandé)
Le projet contient un fichier **`render.yaml`** qui pré-remplit toute la configuration :
1. Poussez le projet sur GitHub **y compris `render.yaml`** (à la racine du dépôt)
2. https://render.com → **New + → Blueprint** → sélectionnez le dépôt
3. Render lit `render.yaml` : il vous demande juste le **mot de passe admin**
4. Cliquez **Apply** → attendez le déploiement (~3-5 min)
5. Ouvrez `https://VOTRE-PROJET.onrender.com` → l'invitation est en ligne 🎉

*(La méthode manuelle ci-dessous fait exactement la même chose, à la main.)*

### 1. Poussez le projet sur GitHub
Créez un dépôt (ex. `mariage-diane-amon`) et **uploadez TOUT le projet** :
- `index.html`, `admin.html`, `assets/`
- `playlists/` avec les **15 chansons complètes MP3** (⚠️ PAS le sous-dossier `originals/`,
  réservé à votre archive personnelle)
- le dossier `backend/` entier (requirements.txt, app/, .env.example)

*(Contrairement à un hébergement 100 % statique, le backend doit être dans le dépôt.
Votre mot de passe admin par défaut reste dans le code — changez-le à l'étape 5.)*

### 2. Créez le service
1. https://render.com → inscrivez-vous **avec votre compte GitHub**
2. **New + → Web Service** → choisissez votre dépôt
3. Remplissez :

| Champ | Valeur |
|---|---|
| Name | `mariage-diane-amon` |
| **Root Directory** | `backend` ← important ! |
| Runtime | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance type | **Free** |

### 3. Forcez une version de Python compatible
Dans **Environment** → ajoutez une variable :
- `PYTHON_VERSION` = `3.12.4`

*(la base SQLite + les dépendances sont stables sur 3.12)*

### 4. Déployez
Cliquez **Create Web Service** → le build prend 3-5 minutes.
Quand le log affiche `Uvicorn running`, ouvrez l'adresse :
- `https://VOTRE-PROJET.onrender.com` → l'invitation 💌
- `https://VOTRE-PROJET.onrender.com/admin.html` → l'admin 👑
- `https://VOTRE-PROJET.onrender.com/docs` → la documentation API

**Aucune configuration supplémentaire n'est nécessaire** : la page détecte
automatiquement l'adresse du serveur (CONFIG.api.base = origine de la page).

### 5. Sécurisez (avant de partager aux invités)
Dans **Environment** de Render, ajoutez :
- `ADMIN_PASSWORD` = `votre-nouveau-mot-de-passe`
- `SECRET_KEY` = `une-longue-chaine-aleatoire`

Render redémarre le service → l'admin utilisera le nouveau mot de passe.
*(Identifiant admin : toujours `admin`. Après coup, changez le mot de passe
directement depuis l'admin : bouton **« Mot de passe »** en haut du tableau de
bord — actif immédiatement, sans redéploiement.)*

---

## 🗄️ Base permanente — ne plus jamais perdre de RSVP (5 min, gratuit)

Sur le plan gratuit, le disque de Render est **éphémère** : à chaque push GitHub
ou redémarrage, la base SQLite repart à zéro. La solution : brancher une base
**Postgres gratuite chez Neon** (le serveur de la base reste en ligne, lui).

1. Créez un compte sur **https://neon.com** (gratuit, sans carte bancaire)
2. **Create project** → puis copiez la **connection string** affichée, elle
   ressemble à :
   `postgresql://utilisateur:motdepasse@ep-xxxx.eu-central-1.aws.neon.tech/neondb?sslmode=require`
3. Sur **Render** → votre service → **Environment** → **Add Environment Variable** :
   - clé : `DATABASE_URL`
   - valeur : la connection string copiée
4. **Save** → le service redémarre → la base Postgres est créée et remplie
   automatiquement (tables + compte admin) au premier démarrage
5. Ouvrez `/admin.html`, connectez-vous : la base est **définitive** 🎉
   *(Supabase fonctionne pareil : Project Settings → Database → Connection string.)*

> 💡 À partir de là, l'**Export CSV** devient une simple précaution, plus une
> urgence. Vos RSVP survivent aux redéploiements, aux redémarrages et aux mises
> à jour du code.

---

## 🔔 Notifications des mariés — être alerté à chaque interaction (5 min, gratuit)

Recevez un **email** (kpadonouhermann@gmail.com) et/ou un **WhatsApp** (07 57 67 77 07)
quand un invité répond au RSVP, écrit dans le livre d'or, ou consulte
l'invitation (visites regroupées : 1 message au maximum toutes les 15 min).

### Email (API Brevo — la seule méthode qui marche sur Render gratuit)

> ⚠️ Depuis septembre 2025, le plan **gratuit** de Render bloque les ports
> SMTP (25, 465, 587) : le SMTP Gmail classique renvoie
> `[Errno 101] Network is unreachable`. On passe donc par l'**API HTTP**
> de Brevo, qui parle HTTPS (port 443, jamais bloqué) — gratuit 300
> emails/jour, sans carte bancaire.

1. Créez un compte sur **https://app.brevo.com** avec
   **kpadonouhermann@gmail.com** (« Continue with Google »)
2. Vérifiez l'adresse d'expédition : menu **Expéditeurs & IP → Senders** →
   **Add a sender** avec kpadonouhermann@gmail.com → validez l'email reçu
3. Créez la clé API : **https://app.brevo.com/settings/keys/api** →
   **Generate a new API key** → copiez la clé (elle commence par `xkeysib-`)
4. Sur **Render** → votre service → **Environment** → **Add Environment Variable** :

   | Clé | Valeur |
   |---|---|
   | `BREVO_API_KEY` | la clé `xkeysib-…` copiée |
   | `SMTP_USER` | `kpadonouhermann@gmail.com` *(sert d'expéditeur)* |

5. **Save** → le service redémarre → testez : répondez au RSVP depuis
   votre téléphone → l'alerte arrive dans la foulée 🎉

*(Les variables `SMTP_HOST`/`SMTP_PORT`/`SMTP_PASSWORD` peuvent rester :
elles ne servent qu'en local ou sur un hébergeur qui autorise le SMTP.)*

### WhatsApp (CallMeBot — gratuit)

1. Sur le téléphone **07 57 67 77 07** : ajoutez aux contacts le numéro du bot
   affiché sur https://www.callmebot.com/whatsapp.php *(ex. +34 644 26 33 77 —
   si le bot est « full », réessayez dans quelques jours)*
2. Envoyez-lui en WhatsApp : `I allow callmebot to send me messages`
3. Le bot répond en ~1 min avec votre **apikey** → sur Render, ajoutez :
   - clé : `CALLMEBOT_APIKEY` — valeur : l'apikey reçue
4. (Facultatif) `NOTIFY_WHATSAPP_TO` pour notifier un autre numéro

**Save** → redémarrage → testez : répondez au RSVP depuis votre téléphone,
vous recevez l'alerte dans la foulée 🎉

> ⚠️ Ces variables sont **optionnelles** : sans elles, le site fonctionne
> normalement, simplement sans notification.

---

## Test de bout en bout (à faire vous-même)
1. Ouvrez l'invitation sur **votre téléphone**
2. Ouvrez l'enveloppe → la musique joue 🎵
3. Remplissez le RSVP (nom + téléphone WhatsApp + présent·e)
4. Ouvrez `/admin.html` sur l'ordinateur → connectez-vous
   → votre réponse apparaît dans la liste + les compteurs bougent
5. Onglet WhatsApp de l'admin → **Générer les envois** → liens wa.me personnalisés
6. **Export CSV** → la liste est sauvegardée

## Rappels
- WhatsApp **Cloud API automatique** (optionnel) : variables `WHATSAPP_PHONE_ID`
  et `WHATSAPP_API_TOKEN` dans l'environnement Render (voir `backend/.env.example`)
- `CONFIG.api.whatsappPhone` dans `index.html` : mettez votre vrai numéro
- Les réponses d'invités qui consultent la page pendant un réveil du serveur
  sont gardées sur leur appareil — ils peuvent resoumettre plus tard
