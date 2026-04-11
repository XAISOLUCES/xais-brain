---
name: client
description: Charge le contexte complet d'un client en prod. Lit le dossier client, surface les specs, décisions, historique des échanges et tickets ouverts. Utiliser quand on bosse sur un projet client ou qu'il y a une demande entrante.
user-invocable: true
disable-model-invocation: false
model: haiku
---

# client

Use when the user runs `/client [name]` or mentions working for/on a client.

## What to do

1. **Find the client**
   - Look for `clients/[name]/` (fuzzy match if needed)
   - If multiple matches → list them
   - If no match → list all clients in `clients/` and ask, or propose to onboard a new one

2. **Load the context**
   Read in this order:
   - `clients/[name]/README.md` — contexte, statut, contrat, stack, contacts
   - `clients/[name]/SPECS.md` ou `clients/[name]/specs/` — specs en cours
   - `clients/[name]/DECISIONS.md` — décisions techniques et produits
   - `clients/[name]/notes/` — les 3 notes les plus récentes
   - `clients/[name]/tickets/` — tickets ouverts si présent

3. **Surface the briefing**
   ```
   👤 [Client name]

   Statut: [active / maintenance / paused / churned]
   Stack: [...]
   Contact principal: [...]

   Dernière activité: [date]

   Décisions récentes:
   - ...

   Tickets ouverts / en cours:
   - [ ] ...

   Qu'est-ce qui t'amène ?
   ```

4. **Wait for direction**
   Ne rien faire avant que l'utilisateur dise ce qu'il veut faire. Juste charger et présenter.

## If the client doesn't exist yet

Propose to bootstrap:
```
clients/[name]/
├── README.md        ← Contexte, contrat, stack, contacts
├── SPECS.md         ← Specs en cours
├── DECISIONS.md     ← Log des décisions tech & produit
├── notes/           ← Sessions notes (YYYY-MM-DD-slug.md)
└── tickets/         ← Tickets / demandes en cours
```

Ask for confirmation.

## README template for new clients

```markdown
# [Client name]

**Statut:** active | maintenance | paused | churned
**Démarré:** YYYY-MM-DD
**Stack:** [...]
**Repo:** [url]
**Contact principal:** [nom + canal]

## Contexte
[Qui c'est, quoi ils font, pourquoi on bosse avec eux]

## Contrat / scope
[Ce qui est dans le scope, ce qui ne l'est pas, fréquence des interventions]

## Accès
[Liens vers dashboards, Notion, repos, etc. — pas de credentials ici]
```

## Rules
- Français par défaut
- **JAMAIS de credentials, clés API, passwords dans ces fichiers** — juste des pointeurs vers les vraies sources (1Password, etc.)
- Client en prod = attention particulière, toujours rappeler l'impact potentiel avant de suggérer un changement
- Si le client est `churned`, flagger immédiatement avant toute action
