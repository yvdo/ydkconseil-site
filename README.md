# YDK Conseil — site web

Site vitrine de [ydkconseil.com](https://ydkconseil.com) : Product Manager freelance, e-commerce, conversion et génération de leads.

Site statique (HTML, CSS, JS) + un petit script PHP pour le formulaire de contact, hébergé chez IONOS.

## Organisation

```
public/                 ← tout ce qui est mis en ligne
  index.html            page d'accueil
  mentions-legales.html
  404.html
  contact.php           envoi du formulaire vers contact@ydkconseil.com
  .htaccess             HTTPS, redirections, cache, compression
  robots.txt, sitemap.xml, site.webmanifest, favicons
  assets/css/style.css
  assets/js/main.js
  assets/img/           photo (AVIF/WebP/JPEG) et image de partage
.github/workflows/deploy.yml   déploiement automatique vers IONOS
```

## Déploiement automatique

Chaque push sur `main` qui modifie `public/` envoie le site sur IONOS par SFTP (GitHub Actions).
On peut aussi le lancer à la main : onglet **Actions** → **Déploiement IONOS** → **Run workflow**.

### Configuration (une seule fois)

Dans le dépôt GitHub : **Settings → Secrets and variables → Actions**.

Onglet **Secrets** → **New repository secret** :

| Nom | Valeur (IONOS → Hébergement → SFTP & SSH) |
|---|---|
| `IONOS_SFTP_HOST` | le serveur, ex. `access-5012345678.webspace-host.com` |
| `IONOS_SFTP_USER` | l'identifiant SFTP |
| `IONOS_SFTP_PASSWORD` | le mot de passe SFTP |

Optionnel, onglet **Variables** : `IONOS_SFTP_DIR` si le site n'est pas à la racine du webspace (par défaut `/`).

Le déploiement ajoute et remplace les fichiers, mais **ne supprime rien** sur le serveur : un fichier retiré du dépôt reste en ligne jusqu'à ce qu'on le supprime à la main dans IONOS.

## Modifier le site

- Textes et sections : `public/index.html`
- Styles : `public/assets/css/style.css`
- Animations et menu : `public/assets/js/main.js`

Après une modification de `style.css` ou `main.js`, augmentez le numéro de version (`?v=2` → `?v=3`) dans les balises `<link>` et `<script>` des pages HTML : ces fichiers sont mis en cache un an par les navigateurs.

## Référencement

- Soumettre `https://ydkconseil.com/sitemap.xml` dans Google Search Console.
- Mettre à jour `<lastmod>` dans `sitemap.xml` après un changement de contenu important.
- Tester les données structurées : https://search.google.com/test/rich-results

## Blog

Les articles sont rédigés dans `content/blog/*.html` : un commentaire JSON en tête (titre, description SEO, catégorie, date, mots-clés, articles liés), puis le corps en HTML avec des `<h2>` pour les sections.

Pour publier un nouvel article :

1. Créer `content/blog/mon-article.html` sur le modèle d'un article existant.
2. Lancer `python3 tools/build_blog.py`.
3. Le script génère `public/blog/<slug>/index.html`, la page `/blog/`, le flux RSS, le `sitemap.xml` et le bloc « Derniers articles » de la page d'accueil.
4. Commit + push : le déploiement met tout en ligne.
