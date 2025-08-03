#!/usr/bin/env python3
"""
Pre-publish Link Validation Workflow
Usage: python validate_and_fix.py <markdown_file_path>
"""

import sys
import os
import subprocess

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ {description} failed")
        if result.stderr:
            print(f"Error: {result.stderr}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return False

def validate_and_fix_page(file_path):
    """Complete workflow to validate and fix a page before publishing"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🚀 Starting pre-publish validation for: {os.path.basename(file_path)}")
    print("=" * 60)
    
    # Step 1: Fix obvious link issues automatically
    print(f"\n📋 STEP 1: Auto-fix broken links")
    if not run_command(f"python link_fixer.py {file_path}", "Auto-fixing broken links"):
        print("⚠️  Auto-fix had issues, but continuing...")
    
    # Step 2: Get the page URL for validation
    # Extract slug from frontmatter or use filename
    page_slug = os.path.basename(file_path).replace('.md', '')
    page_url = f"/posts/{page_slug}/"
    
    # Step 3: Validate all links on the page
    print(f"\n📋 STEP 2: Validate all links")
    validation_success = run_command(
        f"python link_validator_enhanced.py {page_url}", 
        f"Validating links on {page_url}"
    )
    
    # Step 4: Check Hugo build
    print(f"\n📋 STEP 3: Test Hugo build")
    build_success = run_command(
        "cd .. && hugo --quiet", 
        "Testing Hugo build"
    )
    
    # Summary
    print(f"\n📊 VALIDATION SUMMARY")
    print("=" * 40)
    print(f"📄 File: {file_path}")
    print(f"🔗 Links: {'✅ PASS' if validation_success else '❌ FAIL'}")
    print(f"🏗️  Build: {'✅ PASS' if build_success else '❌ FAIL'}")
    
    if validation_success and build_success:
        print(f"\n🎉 Page is ready for publishing!")
        print(f"📝 Next steps:")
        print(f"   1. Review any manual fixes suggested above")
        print(f"   2. Commit changes to git")
        print(f"   3. Push to trigger deployment")
        return True
    else:
        print(f"\n⚠️  Page needs fixes before publishing:")
        if not validation_success:
            print(f"   • Fix broken links identified above")
        if not build_success:
            print(f"   • Fix Hugo build errors")
        return False

def validate_all_posts():
    """Validate all posts in the content directory"""
    content_dir = "../content/posts"
    
    if not os.path.exists(content_dir):
        print(f"❌ Content directory not found: {content_dir}")
        return
    
    md_files = [f for f in os.listdir(content_dir) if f.endswith('.md')]
    
    print(f"🗂️  Found {len(md_files)} markdown files to validate")
    
    results = {}
    for md_file in md_files:
        file_path = os.path.join(content_dir, md_file)
        print(f"\n" + "="*80)
        success = validate_and_fix_page(file_path)
        results[md_file] = success
    
    # Final summary
    print(f"\n🏁 FINAL SUMMARY")
    print("=" * 50)
    passed = sum(results.values())
    total = len(results)
    
    for file, success in results.items():
        status = "✅ READY" if success else "❌ NEEDS WORK"
        print(f"  {status}: {file}")
    
    print(f"\n📊 Overall: {passed}/{total} posts ready for publishing")

def main():
    if len(sys.argv) < 2:
        print("📚 Pre-publish Link Validation Workflow")
        print("")
        print("Usage:")
        print("  python validate_and_fix.py <markdown_file_path>   # Validate single file")
        print("  python validate_and_fix.py --all                  # Validate all posts")
        print("")
        print("Examples:")
        print("  python validate_and_fix.py ../content/posts/indoor-herb-garden.md")
        print("  python validate_and_fix.py --all")
        sys.exit(1)
    
    if sys.argv[1] == "--all":
        validate_all_posts()
    else:
        file_path = sys.argv[1]
        validate_and_fix_page(file_path)

if __name__ == "__main__":
    main()
