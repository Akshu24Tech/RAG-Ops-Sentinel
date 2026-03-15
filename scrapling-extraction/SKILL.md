---
name: scrapling-extraction
description: Extracts technical promises and structured data from web pages using Scrapling. Use when documentation sites have bot protection or need adaptive DOM traversal to resist UI changes.
---

# Scrapling Extraction

## When to use this skill
- Fetching documentation pages from GitHub or WAF-protected sites.
- Extracting specific technical claims, code blocks, and feature lists.
- Using "Adaptive Selectors" to handle evolving web layouts.

## Workflow
- [ ] Initialize `StealthyFetcher` with `adaptive=True`.
- [ ] Fetch the target documentation URL.
- [ ] Use CSS or XPath selectors to extract specific elements (e.g., `pre`, `code`, `li`).
- [ ] Save the extracted "claims" to a JSON format for downstream auditing.

## Instructions

### Implementation Example
```python
from scrapling import StealthyFetcher

def extract_docs(url):
    # StealthyFetcher bypasses most bot detections
    page = StealthyFetcher.fetch(
        url,
        headless=True,
        network_idle=True,
        selector_config={"adaptive": True}
    )
    # page is a Selector object
    code_blocks = page.css("pre").get_all_text()
    return code_blocks
```

### Best Practices
- Use `network_idle=True` for single-page apps (React/Vue docs).
- Use `adaptive=True` to store selector paths in the local `scrapling_storage` for performance on repeat visits.

## Resources
- [Scrapling Documentation](https://github.com/D4Vinci/Scrapling)
