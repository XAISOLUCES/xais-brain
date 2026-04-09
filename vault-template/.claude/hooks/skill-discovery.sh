#!/bin/bash
# Hook UserPromptSubmit — liste les skills dispos quand l'user le demande
# Non-bloquant : exit 0 toujours

PROMPT=$(cat)

# Déclencheurs FR + EN minimal
if echo "$PROMPT" | grep -iqE '\b(skills?|commandes?|que peux[- ]tu|aide[ -]moi|quoi faire|slash)\b'; then
    echo ""
    echo "Skills disponibles (tape /nom pour lancer) :"
    echo ""
    SKILLS_DIR="$(pwd)/.claude/skills"
    if [ -d "$SKILLS_DIR" ]; then
        for dir in "$SKILLS_DIR"/*/; do
            [ -f "$dir/SKILL.md" ] || continue
            name=$(basename "$dir")

            # Parse frontmatter YAML entre les deux lignes "---"
            # awk plus portable que sed BSD/GNU pour les blocs multi-lignes
            desc=$(awk '
                /^---[[:space:]]*$/ { fm++; next }
                fm == 1 && /^description:/ {
                    sub(/^description:[[:space:]]*/, "")
                    print
                    exit
                }
            ' "$dir/SKILL.md")
            invocable=$(awk '
                /^---[[:space:]]*$/ { fm++; next }
                fm == 1 && /^user-invocable:/ {
                    sub(/^user-invocable:[[:space:]]*/, "")
                    print
                    exit
                }
            ' "$dir/SKILL.md")

            if [ "$invocable" = "true" ]; then
                printf "  /%-15s — %s\n" "$name" "$desc"
            fi
        done
    fi
    echo ""
fi
exit 0
