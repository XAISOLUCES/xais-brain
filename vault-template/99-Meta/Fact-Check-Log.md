# Fact-Check Log

Log append-only des sources utilisées par les skills xais-brain.
Alimenté par `/clip` et `/file-intel`. Ne PAS éditer à la main — utiliser
`/vault-audit` pour nettoyer.

## Format d'une entrée

Chaque entrée suit le format suivant :

```markdown
## YYYY-MM-DD — [[titre-de-la-note]]

- **Source** : web | pdf | docx | txt | md | manual
- **URL / fichier** : `https://...` ou `./path/to/file.pdf`
- **Skill** : /clip | /file-intel | /inbox-zero | manual
- **Statut** : draft | verified | to-verify | archived
- **Notes** : (optionnel — commentaire libre sur la fiabilité de la source)
```

Les entrées sont ajoutées en append-only à la fin du fichier, dans l'ordre
chronologique (la plus récente en bas). Pour rechercher une source :
`Ctrl+F` sur l'URL ou le nom de fichier.

---
