# AWS Account Automation Project

# Install main project dependencies
install:
    uv sync

# Create AWS account with configuration file
create-account config_file="sample_account_details.json":
    uv run python aws_account_creator.py {{config_file}}

# Validate account configuration file
validate config_file="sample_account_details.json":
    uv run python -c "import json; json.load(open('{{config_file}}'))"

# Test working browser automation approaches (in claude_spikes)
test:
    @echo "Running browser automation tests in claude_spikes/"
    cd claude_spikes && just test-all

# Clean up generated result files
clean:
    rm -f aws_account_creation_result_*.json
    rm -f *.png *.html
    cd claude_spikes && just clean

# Show project status and next steps
status:
    @echo "=== AWS Account Automation Project Status ==="
    @echo "❌ Skyvern approach deprecated (see SKYVERN_DECISION.md)"
    @echo "✅ Working alternatives available in claude_spikes/"
    @echo "   - Selenium: Browser automation with form detection"
    @echo "   - Playwright: Modern browser automation"
    @echo "   - Requests: Fast HTTP analysis"
    @echo ""
    @echo "Next steps:"
    @echo "1. Choose automation approach from claude_spikes/"
    @echo "2. Implement production version in project root"
    @echo "3. Test with sample_account_details.json"