#!/bin/bash
# Re-analyze all Instagram users with new primary_category logic

echo "=========================================="
echo "Re-analyzing all Instagram creators"
echo "=========================================="

users=("herfirst100k" "doobydobap" "jackinvestment" "madfitig" "rainn" "theholisticpsychologist" "ramit" "adventuresofnik" "nabela" "tinx" "mondaypunday")

for user in "${users[@]}"; do
    echo ""
    echo "Processing: $user"
    python3 pipeline.py --user "$user"
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Failed: $user"
    else
        echo "✅ Complete: $user"
    fi
done

echo ""
echo "=========================================="
echo "All users re-analyzed!"
echo "=========================================="
