<?php
/* YDK Conseil — envoi du formulaire de contact (hébergement IONOS) */

$destinataire = 'contact@ydkconseil.com';
/* Adresse d'expédition : une boîte existante sur votre domaine chez IONOS */
$expediteur   = 'contact@ydkconseil.com';

function retour($etat) {
    header('Location: /?envoi=' . $etat . '#contact', true, 303);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    retour('erreur');
}

/* Piège à robots : ce champ caché doit rester vide */
if (!empty($_POST['site'])) {
    retour('ok');
}

$nom     = trim(strip_tags($_POST['nom'] ?? ''));
$email   = trim($_POST['email'] ?? '');
$message = trim(strip_tags($_POST['message'] ?? ''));

/* Supprime les retours à la ligne pour empêcher l'injection d'en-têtes */
$nom   = str_replace(["\r", "\n"], ' ', $nom);
$email = str_replace(["\r", "\n"], '', $email);

if ($nom === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)
    || mb_strlen($nom) > 120 || mb_strlen($message) > 4000) {
    retour('erreur');
}

$sujet = '=?UTF-8?B?' . base64_encode('Nouvelle demande YDK Conseil — ' . $nom) . '?=';
$corps = "Nom : $nom\nEmail : $email\n\nMessage :\n$message\n\n— Envoyé depuis ydkconseil.com le " . date('d/m/Y H:i');

$entetes  = "From: YDK Conseil <$expediteur>\r\n";
$entetes .= "Reply-To: $email\r\n";
$entetes .= "MIME-Version: 1.0\r\n";
$entetes .= "Content-Type: text/plain; charset=UTF-8\r\n";
$entetes .= "Content-Transfer-Encoding: 8bit\r\n";

$ok = mail($destinataire, $sujet, $corps, $entetes, '-f' . $expediteur);
retour($ok ? 'ok' : 'erreur');
