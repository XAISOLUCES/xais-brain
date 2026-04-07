---
name: vault-setup
description: Personnalise le vault Obsidian en interviewant l'utilisateur sur son rôle, ses projets et ses objectifs, puis met à jour CLAUDE.md. Utiliser quand l'utilisateur dit vault-setup, personnalise mon vault, configure mon vault, ou ouvre un vault frais.
---

# vault-setup

Personnalise le vault Obsidian de l'utilisateur en générant un `CLAUDE.md` adapté à son profil.

## Étapes

### 1. Vérifier l'état actuel

- Lire `CLAUDE.md` à la racine du vault
- Si la section "Qui je suis" contient déjà du contenu personnalisé (pas le placeholder), demander à l'utilisateur s'il veut écraser ou compléter
- Si écrasement : backup l'ancien → `CLAUDE.md.backup-YYYY-MM-DD-HHMMSS`

### 2. Interview en un seul tour (4 questions)

Pose **toutes les questions en une seule fois** dans un AskUserQuestion. Ne fais pas de back-and-forth.

Les 4 questions :

1. **Que fais-tu dans la vie ?** (rôle, métier, contexte pro)
2. **Qu'est-ce qui te passe à la trappe le plus souvent — qu'aimerais-tu mieux suivre ?**
3. **Travail uniquement, ou vie perso aussi ?**
4. **As-tu des fichiers à importer ? (PDFs, docs, slides — chemin du dossier ou skip)**

Ton encourageant : *"Pas besoin d'être formel. Quelques phrases suffisent."*

### 3. Générer le CLAUDE.md personnalisé

Garde la structure standard du template, mais remplace la section "Qui je suis" par :

```markdown
## Qui je suis

[Synthèse en 3-5 phrases du rôle de l'utilisateur, ce qu'il fait, et ce qui lui passe à la trappe.]

## Mes priorités actuelles

- [3-5 bullets dérivés des réponses]

## Mon style de travail

- [Préférences déduites : pro/perso, niveau de formalisme, outils utilisés, etc.]
```

### 4. Si fichiers à importer

- Confirmer le chemin avec l'utilisateur
- Lancer `/file-intel` avec ce dossier en argument
- Sortie → `inbox/`

### 5. Confirmation finale

Affiche un résumé de ce qui a été fait :

```
✓ CLAUDE.md personnalisé
✓ Backup ancien CLAUDE.md (si applicable)
✓ X fichiers traités (si applicable)

Prochaine étape : tape /daily pour démarrer ta première journée.
```
