#!/usr/bin/env python3
"""
Add celebrity Instagram accounts
"""
import subprocess
import sys

# Famous celebrities for demo purposes
celebrities = [
    "therock",        # Dwayne "The Rock" Johnson
    "kimkardashian"   # Kim Kardashian
]

def run_command(cmd, desc):
    """Run a command and return success status"""
    print(f"  {desc}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ❌ Error: {result.stderr[:200]}")
        print(f"    Output: {result.stdout[:200]}")
        return False
    return True

def process_account(username, num, total):
    """Process a single celebrity account through the full pipeline"""
    print(f"\n{'='*70}")
    print(f"[{num}/{total}] Processing Celebrity: @{username}")
    print('='*70)
    
    # Step 1: Collect data
    print("\n📥 Step 1: Collecting Instagram data...")
    if not run_command(
        f"python3 test_single_user.py --username {username}",
        "Fetching user info, posts, and reels"
    ):
        print(f"⚠️  Warning: Data collection failed for {username}")
        print("   This might be due to:")
        print("   - API rate limits")
        print("   - Private account")
        print("   - Invalid username")
        return False
    
    # Step 2: Analyze with GPT (will auto-categorize as Celebrity)
    print("\n🤖 Step 2: Analyzing with GPT-4...")
    if not run_command(
        f"python3 pipeline.py --user {username}",
        "Analyzing profile and posts with AI"
    ):
        print(f"⚠️  Warning: GPT analysis failed for {username}")
        return False
    
    # Step 3: Generate embeddings
    print("\n🔢 Step 3: Generating embeddings...")
    if not run_command(
        f"python3 generate_embeddings.py --username {username}",
        "Creating content embeddings"
    ):
        print(f"⚠️  Warning: Embedding generation failed for {username}")
        return False
    
    print(f"\n✅ Successfully added: @{username}")
    return True

def main():
    """Process all celebrity accounts"""
    print("\n" + "="*70)
    print("🌟 ADDING CELEBRITY INSTAGRAM ACCOUNTS")
    print("="*70)
    print(f"\nAccounts to add: {len(celebrities)}")
    for i, username in enumerate(celebrities, 1):
        print(f"  {i}. @{username}")
    print()
    
    success_count = 0
    failed = []
    
    for i, username in enumerate(celebrities, 1):
        if process_account(username, i, len(celebrities)):
            success_count += 1
        else:
            failed.append(username)
    
    # Final summary
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    print(f"✅ Successfully added: {success_count}/{len(celebrities)}")
    
    if failed:
        print(f"❌ Failed: {len(failed)}")
        for username in failed:
            print(f"   - @{username}")
    
    print("\n🎉 Celebrity accounts ready for demo!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
