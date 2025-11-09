#!/usr/bin/env python3
"""Package current app code for Lambda deployment."""
import zipfile
import os
import sys
from pathlib import Path

def package_lambda_code():
    backend_dir = Path(__file__).parent.parent
    app_dir = backend_dir / 'app'
    output_zip = backend_dir / 'lambda.zip'
    
    if not app_dir.exists():
        print(f"ERROR: app directory not found at {app_dir}")
        sys.exit(1)
    
    print(f"Packaging Lambda code from {app_dir}...")
    
    # Files/directories to exclude
    exclude_dirs = {'__pycache__', '.pyc', '.pyd', '.pyo'}
    exclude_patterns = ('test_', '.test.', '_test.py')
    
    included = 0
    excluded = 0
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zout:
        # Walk through app directory
        for root, dirs, files in os.walk(app_dir):
            # Remove excluded directories from dirs list (modify in-place)
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip excluded files
                if any(pattern in file for pattern in exclude_patterns):
                    excluded += 1
                    continue
                
                if file.endswith(('.pyc', '.pyd', '.pyo')):
                    excluded += 1
                    continue
                
                # Calculate relative path for zip
                rel_path = file_path.relative_to(backend_dir)
                arcname = str(rel_path).replace('\\', '/')
                
                # Add file to zip
                zout.write(file_path, arcname=arcname)
                included += 1
    
    print(f"Created {output_zip}")
    print(f"   Included: {included} files")
    print(f"   Excluded: {excluded} files")
    
    # Verify key files
    with zipfile.ZipFile(output_zip, 'r') as z:
        required_files = ['app/main.py', 'app/services/llm.py', 'app/config.py']
        for req_file in required_files:
            if req_file in z.namelist():
                print(f"Verified: {req_file} is included")
            else:
                print(f"WARNING: {req_file} not found in package!")

if __name__ == '__main__':
    package_lambda_code()

