# AWS Account Automation

Automated AWS root account creation with minimal human intervention.

## Quick Start

```bash
# Install dependencies
just install

# Create account with config
just create-account sample_account_details.json

# Test browser automation
just test
```

## Status

-  Browser automation (Selenium, Playwright) 
- = Production implementation
- = Email service integration

## Commands

- `just install` - Install dependencies
- `just test` - Run automation tests  
- `just validate config.json` - Validate config
- `just status` - Show project status
- `just clean` - Clean generated files

---
*Generated with [Claude Code](https://claude.ai/code)*