# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for AWS account creation automation. After evaluating multiple approaches, we have identified working browser automation solutions. The project uses `uv` for dependency management and `just` for task running.

## Common Commands

### Setup and Installation
- `just install` - Install project dependencies
- `uv sync` - Sync dependencies

### Testing and Validation
- `just test` - Run browser automation tests (in claude_spikes/)
- `just validate [config_file]` - Validate JSON configuration file format
- `just status` - Show project status and next steps

### Cleanup
- `just clean` - Remove generated result files

## Architecture

### Core Files
- `sample_account_details.json` - Template configuration file with required account details
- `main.py` - Simple entry point (currently minimal)
- `SKYVERN_DECISION.md` - Explanation of why Skyvern was rejected

### Working Approaches (in claude_spikes/)
- **Selenium**: Browser automation with JavaScript form detection (2.95s)
- **Playwright**: Modern browser automation with async support (4.56s)
- **Requests + BeautifulSoup**: Fast HTTP analysis for static content (0.30s)

### Configuration
The application expects a JSON configuration file with the following required fields:
- email, password, account_name, full_name, phone_number
- address, city, state, postal_code, country
- company_name (optional)

### Output
- Results are saved to timestamped JSON files: `aws_account_creation_result_<timestamp>.json`
- Test files and experiments are located in `claude_spikes/` directory

## Development Notes

- Uses Python 3.12+ as specified in pyproject.toml
- Dependencies managed via uv.lock
- Browser automation targets AWS signup page: https://portal.aws.amazon.com/billing/signup
- AWS registration page is JavaScript-heavy SPA requiring browser automation

## Code Organization Rules

- **Project root and application code**: Must remain clean and production-ready. No experimental or temporary code.
- **Main justfile**: Contains only stable, human-usable commands. No experimental commands or spikes.
- **claude_spikes/ directory**: Designated area for experiments, prototypes, and temporary code. Allowed to be messy during development.
- **claude_spikes/justfile**: Contains experimental commands and testing utilities specific to spike work.
- All experiments and prototyping should be contained within claude_spikes/ to maintain project cleanliness.

## Development Process - Feedback Loop

**CRITICAL**: Always complete the feedback loop when working on tasks. Never stop until you've either:
1. Achieved the goal with verified working code, OR
2. Reached a blocker that requires human intervention

**The feedback loop is**: Plan → Write → Test → Evaluate → Iterate
- **Plan**: Understand the task, break it down if complex
- **Write**: Create or modify code/configs
- **Test**: Actually run the code to verify it works  
- **Evaluate**: Check results, identify what worked/failed
- **Iterate**: Fix issues and repeat until goal is achieved

**Do not stop after writing code** - you must test it to verify it works. Creating untested experiments is incomplete work.

## When to Stop for Human Intervention

**CRITICAL**: The following situations require stopping the feedback loop and requesting human intervention:

### System Safety Concerns
- **Resource exhaustion**: Operations that could cause severe lag, memory exhaustion, or system instability
- **File system modifications outside project**: Any writes, deletions, or modifications outside the project directory
- **System-level changes**: Installing system packages, modifying system configs, changing user permissions
- **Network flooding**: Operations that could overwhelm network resources or cause rate limiting

### External Service Risks
- **Account bans/violations**: Actions that could get accounts banned from AWS, GitHub, or other services
- **Rate limiting triggers**: Rapid repeated requests that could trigger service protections
- **Terms of service violations**: Automation that violates platform terms (e.g., aggressive scraping)
- **Financial consequences**: Operations that could incur unexpected costs (cloud resources, API usage)

### Infrastructure Safety
- **Global system changes**: Modifying PATH, environment variables, or system-wide configurations
- **Process management**: Starting/stopping system services or long-running processes
- **Security implications**: Operations involving credentials, keys, or authentication outside project scope
- **Data loss risks**: Bulk deletions, destructive operations on important files

### Uncertainty Boundaries
- **Unclear requirements**: When task specifications are ambiguous and could be interpreted multiple ways
- **Missing permissions**: When unsure if an operation requires elevated privileges
- **External dependencies**: When success depends on external services or configurations not under project control
- **Irreversible actions**: Operations that cannot be easily undone (account creation, permanent deletions)

### Safe Operations (Continue Feedback Loop)
- ✅ Reading files within project directory
- ✅ Writing/modifying files within project directory  
- ✅ Installing project dependencies via uv/pip within virtual environment
- ✅ Running tests and scripts within project scope
- ✅ Making HTTP requests for testing/analysis (with reasonable rate limits)
- ✅ Browser automation for testing purposes (non-production)

**Rule of thumb**: If there's any doubt about safety or reversibility, stop and ask for guidance.

## Software Engineering Principles

### Operational Simplicity
- **Prefer fewer dependencies** over feature-rich but complex solutions
- **Minimize external service dependencies** to reduce failure modes
- **Choose mature, well-documented tools** over bleeding-edge alternatives
- **Optimize for debugging ease** - direct control beats abstraction layers

### Tight Feedback Cycles
- **Test early and often** - every code change should be immediately testable
- **Fail fast** - identify issues within seconds, not minutes
- **Enable rapid iteration** - minimize setup time between test runs
- **Provide clear error messages** - debugging should be straightforward

### Reliability & Maintainability
- **Fewer moving parts** = higher reliability
- **Battle-tested solutions** over novel approaches for critical paths
- **Community support** matters for long-term maintenance
- **Performance vs complexity trade-offs** - favor simplicity unless performance is critical

### Implementation Quality
- **Complete the feedback loop** - don't stop until you have working, tested code
- **Systematic evaluation** - test multiple approaches before committing
- **Document decisions** - explain why you chose one approach over alternatives
- **Clean separation** - keep experiments separate from production code

## Concrete Practices

### Testing Strategy
- **Write pytest tests first** - Define expected behavior before implementation
- **Test the interface, not internals** - Focus on public APIs and user-facing behavior
- **Avoid testing implementation details** - Don't test private methods or internal state
- **Integration tests over unit tests** - Test complete workflows rather than isolated functions
- **Real browser tests** - Use actual Selenium/Playwright instead of mocking browser interactions

### Code Quality
- **Prefer duplication over bad abstraction** - Copy-paste clear code rather than create fragile abstractions
- **Optimize for readability** - Code is read 10x more than written
- **Avoid premature optimization** - Make it work first, then make it fast if needed
- **Simple functions** - One responsibility, clear inputs/outputs, minimal side effects
- **Explicit over implicit** - Be clear about dependencies, configurations, and expectations

### Debugging Practices
- **Use pdb for interactive debugging** - `import pdb; pdb.set_trace()` for step-through debugging
- **Add strategic print statements** - Temporary logging to understand execution flow
- **Test with real data** - Use actual AWS pages, not mocked responses
- **Fail fast with clear messages** - Better to crash with useful error than fail silently
- **Isolate problems** - Create minimal reproduction cases when debugging

### Development Workflow
- **Start with the simplest thing that works** - Avoid complexity until proven necessary
- **Build incrementally** - Small, testable changes rather than big rewrites
- **Test manually first** - Understand the problem by hand before automating
- **Document as you go** - Update CLAUDE.md and comments during development
- **Clean up experiments** - Move working code from claude_spikes/ to production

### Example Application
```python
# GOOD: Simple, testable, readable
def fill_aws_form(driver, account_details):
    """Fill AWS registration form with account details"""
    email_field = driver.find_element(By.ID, "emailAddress")
    email_field.send_keys(account_details.email)
    
    # Test: assert email_field.get_attribute("value") == account_details.email

# BAD: Over-abstracted, hard to debug
class FormFieldManager:
    def __init__(self, driver, locator_strategy="id"):
        self.driver = driver
        self.strategy = locator_strategy
    
    def fill_field(self, locator, value, validation_fn=None):
        # Complex abstraction that breaks in edge cases
```

### When to Abstract vs Duplicate
- **Duplicate code when**: Logic is similar but contexts differ (different forms, different validations)
- **Abstract when**: Exact same logic used 3+ times with identical behavior
- **Prefer composition over inheritance** - Use functions and classes together, avoid deep hierarchies
- **Extract constants, not functions** - Shared values are safer to abstract than shared behavior

## Project Management Principles for Agentic Coding

### Task Parallelizability
- **Independent tasks**: Design tasks that can be worked on simultaneously without dependencies
- **Clear interfaces**: Define explicit inputs/outputs between parallel work streams
- **Minimal shared state**: Reduce coupling between parallel tasks to prevent conflicts
- **Atomic deliverables**: Each task produces a complete, testable unit of work

### Requirements Writing (Strunk & White Principles)
- **Omit needless words**: Be concise, direct, specific
- **Use active voice**: "Implement X" not "X should be implemented"
- **Concrete over abstract**: "Parse email field" not "Handle user input"
- **One idea per requirement**: Split complex requirements into focused tasks

### Spike Management
- **Spike indicators**: Flag tasks requiring research, proof-of-concept, or unknown complexity
- **Time-boxed exploration**: Set clear boundaries for spike work (2-4 hours max)
- **Decision documentation**: Record findings and rationale for approach selection
- **Transition criteria**: Define when to move from spike to production implementation

### Task Prioritization (ROI Focus)
- **High ROI**: Core functionality, user-facing features, critical path items
- **Medium ROI**: Error handling, edge cases, nice-to-have features
- **Low ROI**: Premature optimizations, over-engineering, distant future needs
- **Prune ruthlessly**: Remove tasks that don't directly serve project goals

### Stakeholder Feedback Integration
- **Feedback checkpoints**: Built-in review points for direction validation
- **Decision points**: Explicit moments requiring stakeholder input
- **Scope control**: Clear boundaries on what changes require approval
- **Progress visibility**: Regular updates on task completion and blockers

### Emergency Protocol (--dangerously-skip-permissions Mode)
- **Job completion**: Consider work finished when hitting emergency scenarios
- **Safety boundaries**: Respect all safety guidelines in CLAUDE.md
- **No system modifications**: Avoid any irreversible changes outside project scope
- **Escalation required**: Stop and request human intervention at safety boundaries

### GitHub CLI Safety Protocol
- **CRITICAL**: Only use `gh` commands within this project repository
- **FORBIDDEN**: Never access other repos, orgs, or user accounts via GH CLI
- **Verification**: Always verify current repo context before GH CLI usage
- **Emergency**: Immediately stop if any GH CLI command targets external repos

### Trunk-Based Development Workflow
- **Small PRs**: Each PR addresses single ticket or logical unit
- **Feature branches**: Short-lived branches from main (hours to 1-2 days max)
- **Continuous integration**: All changes go through main branch
- **Fast feedback**: Tight review cycles for rapid iteration
- **Branch naming**: `feature/CORE-001`, `fix/config-validation`, etc.

## Project Tickets

### Epic: Minimal Human Intervention AWS Account Creation
**Goal**: Run single command to provision new AWS root account with minimal manual steps

### Ticket Categories

#### 🚀 **CORE-001: Production Account Creation Engine** 
**Priority**: Critical | **Type**: Implementation | **Parallel**: No
- Implement production AWS account creation based on working spike approaches
- Input: JSON config file with account details
- Output: Created AWS account with confirmation
- **Dependencies**: None
- **Acceptance**: `just create-account config.json` provisions working AWS account

#### 🚀 **CORE-002: Email Service Integration**
**Priority**: Critical | **Type**: Research + Implementation | **Parallel**: Yes
- Research free email services (10minutemail, guerrilla mail, temp-mail.org)
- Integrate email service API for temporary email generation
- Handle email verification workflow automatically
- **Dependencies**: None (can work in parallel with CORE-001)
- **Acceptance**: Generate disposable email, use in AWS signup, handle verification

#### 🔧 **INFRA-001: Configuration Management**
**Priority**: High | **Type**: Implementation | **Parallel**: Yes
- Enhance JSON schema validation for account details
- Add configuration templates for different use cases
- Support environment variable overrides
- **Dependencies**: None
- **Acceptance**: Robust config validation with clear error messages

#### 🔧 **INFRA-002: Error Recovery System**
**Priority**: High | **Type**: Implementation | **Parallel**: Yes
- Implement retry logic for transient failures
- Handle common AWS signup errors (rate limiting, validation)
- Save progress state for interrupted workflows
- **Dependencies**: CORE-001 (for error scenarios)
- **Acceptance**: Graceful handling of 90% of common failure cases

#### 🧪 **TEST-001: End-to-End Testing Suite**
**Priority**: High | **Type**: Implementation | **Parallel**: Yes
- Create test environment with mock AWS endpoints
- Implement integration tests for full workflow
- Add performance benchmarking
- **Dependencies**: CORE-001, CORE-002
- **Acceptance**: Comprehensive test coverage with CI integration

#### 📊 **MONITOR-001: Workflow Observability**
**Priority**: Medium | **Type**: Implementation | **Parallel**: Yes
- Add structured logging throughout workflow
- Implement progress reporting and status updates
- Create debugging utilities for troubleshooting
- **Dependencies**: CORE-001
- **Acceptance**: Clear visibility into workflow progress and failures

#### 🔒 **SEC-001: Security Hardening** 
**Priority**: Medium | **Type**: Implementation | **Parallel**: Yes
- Secure credential handling and storage
- Implement browser fingerprint randomization
- Add user-agent rotation and stealth techniques
- **Dependencies**: CORE-001
- **Acceptance**: Reduced detection risk, secure credential management

#### 🚢 **DEPLOY-001: Deployment Packaging**
**Priority**: Low | **Type**: Implementation | **Parallel**: Yes
- Create portable deployment package
- Add Docker containerization option
- Implement easy installation script
- **Dependencies**: All core functionality
- **Acceptance**: One-command deployment on fresh systems

### Spike Tasks (Research Required)
- **SPIKE-EMAIL**: Evaluate free email service reliability and API capabilities (2 hours)
- **SPIKE-CAPTCHA**: Research CAPTCHA solving services and integration (2 hours)  
- **SPIKE-SCALING**: Investigate parallel account creation feasibility (1 hour)

### Pruned Tasks (Low ROI)
- ~~Custom browser engine development~~ (Use existing solutions)
- ~~AWS CLI integration~~ (Not needed for account creation)
- ~~GUI interface~~ (CLI-first approach sufficient)
- ~~Multi-cloud support~~ (AWS-focused scope)

## Current Status

### Completed
- [✅] Browser automation approaches evaluated (Selenium, Playwright, Requests)
- [✅] AWS registration page analysis (JavaScript SPA with form detection)
- [✅] Working proof-of-concept implementations in claude_spikes/

### In Progress  
- [🔄] Production implementation architecture
- [🔄] Project cleanup and ticket creation

### Pending
- [ ] **CORE-001**: Production account creation engine
- [ ] **CORE-002**: Email service integration  
- [ ] **INFRA-001**: Configuration management
- [ ] **INFRA-002**: Error recovery system
- [ ] **TEST-001**: End-to-end testing suite

### Stakeholder Decisions Made
- **Email service**: mail.tm (free, unrestricted, OpenAPI spec)  
- **Risk tolerance**: Initial manual email verification acceptable, iterate to full automation
- **Deployment target**: Local development only (no containerization needed)

### Next Steps
1. Implement CORE-001 (Production account creation engine)
2. Integrate mail.tm API for CORE-002  
3. Small PRs via trunk-based development workflow