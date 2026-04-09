---
name: daily
description: Démarre la journée avec le contexte du vault — lit ou crée la note du jour, surface les priorités, vérifie l'inbox. Utiliser quand l'utilisateur dit daily, démarrer la journée, on commence, bonjour, ou en début de session.
user-invocable: true
disable-model-invocation: false
model: haiku
---

# daily

Démarre la journée de l'utilisateur en chargeant le contexte vault.

## Étapes

### 1. Identifier la date

Date du jour au format `YYYY-MM-DD`.

### 2. Charger le contexte

- Lire `CLAUDE.md` (si pas déjà chargé)
- Lire `MEMORY.md` pour l'index mémoire
- Lire les 3 dernières notes dans `daily/` (pour continuité)
- Lister le contenu de `inbox/` (compter les fichiers non traités)

### 3. Note du jour

**Si `daily/YYYY-MM-DD.md` existe** → la lire et résumer son contenu à l'utilisateur.

**Sinon** → la créer avec ce template :

```markdown
---
date: YYYY-MM-DD
tags: [daily]
---

# YYYY-MM-DD

## Priorités du jour

- [ ]
- [ ]
- [ ]

## Notes

## Prochaines actions
```

### 4. Surface les priorités

Présente à l'utilisateur :

1. **Continuité** : ce sur quoi il travaillait hier (dérivé des dernières notes daily)
2. **Inbox** : combien de fichiers non triés (et propose `/inbox-zero` si > 0)
3. **Projets actifs** : liste rapide des dossiers dans `projects/`
4. **Mémoire pertinente** : si `MEMORY.md` contient des entrées liées à un projet en cours

### 5. Question d'ouverture

Termine par : *"Sur quoi tu travailles aujourd'hui ?"*
