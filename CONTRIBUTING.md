# Contributing to opendesk

## Setup
```bash
git clone https://github.com/YOUR_USERNAME/opendesk
cd opendesk
pip install -e ".[dev]"
```

## Running Tests
```bash
pytest tests/test_universal.py          # platform-agnostic
pytest tests/test_mac.py -v             # Mac only
pytest --cov=opendesk tests/         # with coverage
```

## Adding a New Tool

1. Create function in appropriate tools/ file
2. Add to tool registry in tools/__init__.py
3. Add to MCP server handlers in server.py
4. Add tests in tests/
5. Document in docs/tools.md
6. Submit PR

## PR Checklist
- [ ] Works on at least one platform
- [ ] Has tests
- [ ] Documented
- [ ] No new required dependencies without discussion
- [ ] Follows security model (destructive = off by default)