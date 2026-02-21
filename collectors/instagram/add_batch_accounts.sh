#!/bin/bash
# Batch add multiple Instagram accounts

echo "========================================================================"
echo "🎯 Batch Adding Instagram Accounts"
echo "========================================================================"

accounts=(
    "humphreytalks"
    "wishbonekitchen"
    "justinesnacks"
    "blogilates"
    "wisdm"
    "greceghanem"
    "mkbhd"
    "unboxtherapy"
    "ijustine"
    "nedratawwab"
    "carolinagelen"
)

total=${#accounts[@]}
success=0
failed=0

for i in "${!accounts[@]}"; do
    account="${accounts[$i]}"
    num=$((i + 1))
    
    echo ""
    echo "========================================================================"
    echo "[$num/$total] Processing: $account"
    echo "========================================================================"
    
    # Step 1: Collect data
    echo "📥 Step 1/3: Collecting data..."
    python3 test_single_user.py --username "$account"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to collect data for $account"
        ((failed++))
        continue
    fi
    
    # Step 2: Analyze with GPT
    echo "🤖 Step 2/3: Analyzing with GPT..."
    python3 pipeline.py --user "$account"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to analyze $account"
        ((failed++))
        continue
    fi
    
    # Step 3: Generate embeddings
    echo "🔢 Step 3/3: Generating embeddings..."
    python3 generate_embeddings.py --username "$account"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate embeddings for $account"
        ((failed++))
        continue
    fi
    
    echo "✅ Completed: $account"
    ((success++))
done

echo ""
echo "========================================================================"
echo "📊 BATCH PROCESSING COMPLETE"
echo "========================================================================"
echo "✅ Success: $success"
echo "❌ Failed: $failed"
echo "📁 Total: $total"
echo ""
