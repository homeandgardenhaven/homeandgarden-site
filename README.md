# Home and Garden Haven Website

A Hugo-based gardening and home improvement blog featuring practical tips, DIY projects, and seasonal guides.

## Development Guidelines

### Internal Linking

**CRITICAL**: All internal links between blog posts must use Hugo's `ref` shortcode for validation and proper URL generation.

✅ **Correct format:**
```markdown
[Link Text]({{< ref "filename.md" >}})
```

❌ **Incorrect format:**
```markdown
[Link Text](/slug-name/)
```

### Benefits of using `ref`:
- Hugo validates that referenced files exist during build
- Generates correct URLs regardless of site structure
- Automatic broken link detection
- Better maintainability when files are renamed

### Examples:
```markdown
See our [companion planting]({{< ref "companion-planting.md" >}}) article.
Learn about [watering tips]({{< ref "watering-tips-hot-weather.md" >}}).
```

## Content Structure

- Blog posts: `/content/posts/`
- Pages: `/content/pages/`
- Images: `/static/images/`
- Scripts: `/scripts/`

## Development Tools

- Link validator script: `/scripts/link_validator.py`
- Python virtual environment: `/scripts/.venv`
- Full development guidelines: `/.github/instructions/agent_readme.md`

## Local Development

1. Install Hugo
2. Clone the repository
3. Run `hugo server -D` for development
4. Access site at `http://localhost:1313`

For detailed content guidelines and agent instructions, see `/.github/instructions/agent_readme.md`.
