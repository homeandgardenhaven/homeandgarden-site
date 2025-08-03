# Scripts Directory

## Virtual Environment

This project uses a Python virtual environment located at `scripts/.venv`.

### Activating the Virtual Environment

Before running any Python scripts, activate the virtual environment:

```bash
source scripts/.venv/bin/activate
```

### Installing Dependencies

To install required dependencies, ensure the virtual environment is activated and run:

```bash
pip install -r requirements.txt
```

### Link Validator Script

The `link_validator.py` script checks for broken links on the site. To run it:

1. Start the Hugo server locally:
   ```bash
   hugo server -D
   ```

2. Activate the virtual environment:
   ```bash
   source scripts/.venv/bin/activate
   ```

3. Run the script:
   ```bash
   python scripts/link_validator.py
   ```

## Content Guidelines

### Internal Links

**IMPORTANT**: All internal links between blog posts must use Hugo's `ref` shortcode for validation and proper URL generation.

✅ **Correct format:**
```markdown
[Link Text]({{< ref "filename.md" >}})
```

❌ **Incorrect format:**
```markdown
[Link Text](/slug-name/)
```

**Benefits of using `ref`:**
- Hugo validates that referenced files exist during build
- Generates correct URLs regardless of site structure
- Automatic broken link detection
- Better maintainability when files are renamed

**Examples:**
```markdown
See our [companion planting]({{< ref "companion-planting.md" >}}) article.
Learn about [watering tips]({{< ref "watering-tips-hot-weather.md" >}}).
```

### Notes
- Always use the virtual environment for Python scripts.
- Add new dependencies to `requirements.txt` and commit the changes.
- All internal links must use the `ref` shortcode format shown above.
