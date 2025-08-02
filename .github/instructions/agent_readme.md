# AGENT_README.md

## 🧠 Agent Content Guidelines for homeandgardenhaven.com

This guide is intended for use by human collaborators, AI content agents (e.g., Claude, Copilot, GPT), and automation systems interacting with the `homeandgardenhaven.com` project.

All generation should comply with the structure and rules defined in `agent_instructions.yaml`. This document provides a simplified interface for generating compliant Markdown posts.

---

## ✅ Article Generation Guidelines

### 📚 Approved Article Types:
Choose one per post:
- DIY Gardening Projects
- Indoor Plant Guides
- Seasonal Home Decor Ideas
- Composting and Sustainability Tips
- Landscaping Techniques

### ✍️ Writing Style:
- Tone: Conversational but informative
- Readability: 8th–10th grade
- Word count: Between 600 and 1500 words

### 📄 Markdown Output Format:
Each post must be saved in `content/posts/` as a `.md` file and include this frontmatter:

```markdown
---
title: "Your Title Here"
date: YYYY-MM-DD
draft: false
featured_image: "/images/example.jpg"
alt_text: "Short, keyword-rich description of the image."
caption: "Brief caption using SEO-relevant phrasing."
categories: ["Selected Category"]
tags: ["tag1", "tag2"]
---
```

---

## 🖼️ Image Handling Requirements

### ✅ Only use sources that are:
- Free for commercial use
- Do not require payment or non-commercial-only licenses

### 🔗 Preferred Sources:
- Unsplash
- Pexels
- Pixabay

### 🧾 Metadata Requirements:
- `featured_image`: Path to image saved under `static/images/`
- `alt_text`: One-sentence functional description with relevant keywords
- `caption`: One-sentence SEO-enhancing description
- Attribution must be included where required

### 🔧 Optimization:
- Resize to max width of 1200px
- Compress images before use

---

## 🤖 Image API Support (for agents)
If using API-based agents to retrieve images, refer to:
- `content.images.image_api.enabled = true`
- Provider priority: Unsplash → Pexels → Pixabay
- API keys are available in `agent_instructions.yaml`

---

## ✅ Final Checklist Before Committing Content

- [ ] Is the article type approved?
- [ ] Is word count between 600–1500?
- [ ] Does frontmatter include all required fields?
- [ ] Is the image from an approved, licensed source?
- [ ] Does the image have appropriate alt text and caption?
- [ ] Is the filename slugified and placed in `content/posts/`?

---

This file may be updated as content strategy evolves. All agents should assume it reflects current operational policy unless stated otherwise.
