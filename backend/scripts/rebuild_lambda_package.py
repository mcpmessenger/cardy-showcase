#!/usr/bin/env python3
"""Rebuild Lambda deployment package excluding Windows binaries and including updated code."""
import zipfile
import os
import sys

def rebuild_lambda_package():
    # Find source zip (backup or original)
    source_zips = ['lambda_prev.zip', 'lambda_win.zip']
    source_zip = None
    for sz in source_zips:
        if os.path.exists(sz):
            source_zip = sz
            break
    
    if not source_zip:
        print("ERROR: No source zip found. Expected lambda_prev.zip or lambda_win.zip")
        sys.exit(1)
    
    # Directories/files to exclude (Windows binaries)
    exclude_prefixes = ('pydantic_core/', 'pydantic_core-', 'charset_normalizer/', 
                       'charset_normalizer-', 'jiter/', 'jiter-')
    exclude_suffixes = ('.pyd', '__pycache__/', '.pyc')
    
    output_zip = 'lambda.zip'
    
    print(f"Rebuilding {output_zip} from {source_zip}...")
    print("Excluding Windows binaries and Python cache files...")
    
    with zipfile.ZipFile(source_zip, 'r') as zin:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zout:
            included = 0
            excluded = 0
            
            for item in zin.infolist():
                filename = item.filename
                
                # Skip if matches exclusion patterns
                if any(filename.startswith(prefix) for prefix in exclude_prefixes):
                    excluded += 1
                    continue
                
                if any(filename.endswith(suffix) for suffix in exclude_suffixes):
                    excluded += 1
                    continue
                
                # Include the file
                zout.writestr(item, zin.read(filename))
                included += 1
            
            print(f"Created {output_zip}")
            print(f"   Included: {included} files")
            print(f"   Excluded: {excluded} files")
    
    # Verify app/services/llm.py is in the zip
    with zipfile.ZipFile(output_zip, 'r') as z:
        if 'app/services/llm.py' in z.namelist():
            print("Verified: app/services/llm.py is included")
        else:
            print("WARNING: app/services/llm.py not found in package!")
            print("   Make sure you're running this from the backend/ directory")

if __name__ == '__main__':
    rebuild_lambda_package()

