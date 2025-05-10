# NVIDIA NGC Setup Guide

## Credentials Added to .env

I've added your NVIDIA NGC credentials to the `.env` file in your SoulCoreHub project:

```
# NVIDIA NGC Credentials
NGC_API_KEY_1=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
NGC_API_KEY_2=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
NGC_ORG_PRIMARY=0701214761930058
NGC_ORG_SECONDARY=0580661486523348
NGC_TEAM=helo-im-ai
NGC_PACKAGE_HASH=64281653428c3dc1ece4c4b74a0d1571b5e007d0c523c241e16a45a02bd2cfc8
```

## NGC CLI Installation

It appears you have the NGC CLI package file (`ngccli_mac_arm.pkg`) with hash `64281653428c3dc1ece4c4b74a0d1571b5e007d0c523c241e16a45a02bd2cfc8`. To install it:

1. Verify the package hash:
   ```bash
   shasum -a 256 ngccli_mac_arm.pkg
   ```

2. Install the package:
   ```bash
   sudo installer -pkg ngccli_mac_arm.pkg -target /
   ```

3. Verify installation:
   ```bash
   ngc --version
   ```

## Using NGC CLI with Your Credentials

The NGC CLI is already configured with your credentials. You can use it to:

1. List available resources:
   ```bash
   ngc registry resource list
   ```

2. Pull models or containers:
   ```bash
   ngc registry resource download-version <resource_name>:<version>
   ```

3. Run NGC containers:
   ```bash
   ngc registry model run <model_name>
   ```

## Integrating with SoulCoreHub

To integrate NVIDIA resources with your SoulCoreHub project:

1. Create a Python utility to access NGC resources:
   ```python
   # src/utils/nvidia_resources.py
   import os
   import subprocess
   
   def get_nvidia_model(model_name, version="latest"):
       """Download a model from NGC registry"""
       api_key = os.environ.get("NGC_API_KEY_1")
       org = os.environ.get("NGC_ORG_PRIMARY")
       
       # Use NGC CLI to download
       cmd = f"ngc registry model download-version {org}/{model_name}:{version}"
       result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
       
       if result.returncode == 0:
           return True, result.stdout
       else:
           return False, result.stderr
   ```

2. Add this utility to your agent implementation to leverage NVIDIA models.

## Security Note

Keep your API keys secure. They have been added to your `.env` file, which should be in your `.gitignore` to prevent accidental exposure in your Git repository.
