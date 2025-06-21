# Decision: Why Skyvern Was Rejected for AWS Account Automation

## Summary

After evaluation, Skyvern was removed from this project in favor of **Selenium** as the recommended automation tool.

## Issues with Skyvern

1. **Complex Setup Requirements**: Requires separate server infrastructure and API key management
2. **Environment Dependencies**: Needs local Skyvern server running on localhost:8000 and Ollama on localhost:11434  
3. **Over-engineered**: Too much overhead for simple form automation tasks
4. **Reliability Concerns**: Additional failure points due to external service dependencies
5. **Poor Feedback Cycles**: Long debugging cycles due to external service dependencies

## Alternative Approaches Tested

Testing revealed that simpler tools work better for AWS registration:

- **Selenium**: Successfully identified form fields, 2.95s execution time ✅
- **Playwright**: Successfully identified form fields, 4.56s execution time ✅  
- **Requests + BeautifulSoup**: Fast (0.30s) but limited to static HTML ⚠️

## Recommended Choice: Selenium

**Selected based on software engineering principles:**

### Operational Simplicity
- Single dependency installation (`pip install selenium`)
- No external service requirements
- Well-documented, mature ecosystem
- Straightforward debugging with browser DevTools

### Tight Feedback Cycles
- Fast test-debug-iterate cycles (2.95s execution)
- Direct browser control for immediate feedback
- Easy to add breakpoints and step through code
- Clear error messages and stack traces

### Reliability & Maintainability
- Stable API with 15+ years of development
- Large community support and documentation
- Fewer moving parts = fewer failure modes
- Battle-tested in production environments

### Performance vs Complexity Trade-off
- Playwright is only 1.6s slower but adds complexity
- Selenium's maturity outweighs the minor performance difference
- Easier onboarding for team members

## Implementation Path

1. Use Selenium WebDriver with Chrome/ChromeDriver
2. Implement retry logic and error handling
3. Add configuration management for different environments
4. Build comprehensive test suite

See `claude_spikes/test_selenium_aws.py` for working implementation.