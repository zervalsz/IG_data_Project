#!/usr/bin/env python3
"""
Batch add Instagram accounts
"""
import subprocess
import sys

accounts = [
    "humphreytalks",
    "wishbonekitchen",
    "justinesnacks",
    "blogilates",
    "wisdm",
    "greceghanem",
    "mkbhd",
    "unboxtherapy",
    "ijustine",
    "nedratawwab",
    "carolinagelen"
]

def run_command(cmd, desc):
    """Run a command and return success status"""
    print(f"  {desc}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ❌ Error: {result.stderr[:200]}")
        return False
    return True

def process_account(username, num, total):
    """Process a single account through the full pipeline"""
    print(f"\n{'='*70}")
    print(f"[{num}/{total}] Processing: {username}")
    print('='*70)
    
    # Step 1: Collect data
    if not run_command(
        f"python3 test_single_user.py --username {username}",
        "📥 Collecting data"
    ):
        return False
    
    # Step 2: Analyze with GPT
    if not run_command(
        f"python3 pipeline.py --user {username}",
        "🤖 Analyzing with GPT"
    ):
        return False
    
    # Step 3: Generate embeddings
    if not run_command(
        f"python3 generate_embeddings.py --username {username}",
        "🔢 Generating embeddings"
    ):
        return False
    
    print(f"✅ Completed: {username}")
    return True

def main():
    print("="*70)
    print("🎯 Batch Adding Instagram Accounts")
    print("="*70)
    
    total = len(accounts)
    success = 0
    failed = []
    
    for i, account in enumerate(accounts, 1):
        if process_account(account, i, total):
            success += 1
        else:
            failed.append(account)
    
    print(f"\n{'='*70}")
    print("📊 BATCH PROCESSING COMPLETE")
    print('='*70)
    print(f"✅ Success: {success}/{total}")
    if failed:
        print(f"❌ Failed: {len(failed)}")
        for acc in failed:
            print(f"   - {acc}")

if __name__ == "__main__":
    main()
