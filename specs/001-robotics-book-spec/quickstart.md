# Quick Start Guide

**Feature**: Physical and Humanoid Robotics Book  
**Date**: 2025-12-07  
**Purpose**: Rapid setup and deployment guide

## Prerequisites

### Development Environment
- Node.js 18+ (required for Docusaurus)
- npm or yarn package manager
- Git for version control
- GitHub account for Pages deployment
- Code editor (VS Code recommended)

### Required Knowledge
- Basic JavaScript/React knowledge
- Markdown familiarity
- Git workflow understanding
- Command line comfort

## Setup Instructions

### 1. Repository Setup
```bash
# Clone the repository
git clone https://github.com/[username]/robotics-book.git
cd robotics-book

# Switch to development branch
git checkout opencode-ai

# Install dependencies
npm install
```

### 2. Local Development
```bash
# Start development server
npm start

# Open browser to http://localhost:3000
# Site will auto-reload on changes
```

### 3. Content Creation
```bash
# Create new module in appropriate chapter folder
# Example: docs/01-introduction/05-new-module.mdx

# Add frontmatter
---
title: "New Module Title"
sidebar_label: "New Module"
description: "Module description"
hide_table_of_contents: false
---

# Module Title
Content goes here...
```

### 4. Build and Test
```bash
# Build production version
npm run build

# Test locally
npm run serve

# Check build output
ls build/
```

## Configuration

### Docusaurus Configuration
Edit `docusaurus.config.js`:
```javascript
const config = {
  title: "Physical and Humanoid Robotics",
  tagline: "From Fundamentals to Advanced Applications",
  url: "https://[username].github.io",
  baseUrl: "/robotics-book/",
  // ... other config
}
```

### Sidebar Configuration
Edit `sidebars.js`:
```javascript
module.exports = {
  bookSidebar: [
    // Chapter structure defined here
  ],
}
```

### Custom Styling
Edit `src/css/custom.css`:
```css
:root {
  --ifm-color-primary: #0066cc;
  --ifm-color-primary-dark: #0052a3;
  --ifm-color-primary-light: #1a7dff;
}
```

## Content Guidelines

### Module Structure
Each MDX file should follow this structure:
```markdown
---
title: "Module Title"
sidebar_label: "Module Display Name"
---

# Module Title

## Learning Objectives
- [ ] Objective 1
- [ ] Objective 2

## Introduction
Brief overview...

## Main Content
Detailed explanation...

## Code Examples
```python
# Code here
```

## Exercises
Practice activities...

## Summary
Key takeaways...

## References
[1] Citation format
```

### Constitution Compliance
- **No Visual Diagrams**: Use text descriptions only
- **Educational Clarity**: Define technical terms on first use
- **Technical Accuracy**: Include citations for all claims
- **Modular Structure**: Each module independently consumable

## Development Workflow

### 1. Content Creation
```bash
# Create feature branch for new content
git checkout -b feature/new-module

# Add content
# Edit/create MDX files

# Test locally
npm start
```

### 2. Quality Assurance
```bash
# Check build
npm run build

# Run accessibility tests
npm run test:a11y

# Check links
npm run test:links
```

### 3. Review Process
1. **Technical Review**: Verify accuracy and citations
2. **Editorial Review**: Check clarity and accessibility
3. **Ethics Review**: Ensure inclusive language
4. **Constitution Check**: Verify compliance

### 4. Deployment
```bash
# Commit changes
git add .
git commit -m "Add new module: [title]"
git push origin feature/new-module

# Create pull request
# Review and merge to main branch
```

## Deployment

### GitHub Pages Setup
1. **Repository Settings**:
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: main / (root)
   - Save

2. **Automatic Deployment**:
   - Push to main branch triggers build
   - GitHub Actions builds and deploys
   - Site available at `https://[username].github.io/robotics-book`

### Custom Domain (Optional)
```bash
# Add CNAME file
echo "yourdomain.com" > static/CNAME

# Commit and push
git add static/CNAME
git commit -m "Add custom domain"
git push origin main
```

## Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clear cache
npm run clear

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### Styling Issues
```bash
# Check custom CSS
npm run start

# Inspect elements in browser
# Verify CSS variables are set correctly
```

#### Navigation Problems
```bash
# Check sidebar.js syntax
npm run build

# Verify file paths exist
ls docs/chapter-folder/
```

### Performance Issues
```bash
# Optimize images
npm run optimize:images

# Check bundle size
npm run analyze

# Test loading speed
npm run test:performance
```

## Best Practices

### Content Development
- Write in clear, accessible language
- Include practical examples and code
- Add proper citations and references
- Test all code examples
- Follow constitution principles

### File Organization
- Use consistent naming conventions
- Keep modules focused and concise
- Organize assets in appropriate folders
- Maintain clean directory structure

### Version Control
- Commit frequently with descriptive messages
- Use feature branches for new content
- Tag releases for major milestones
- Keep main branch stable

## Resources

### Documentation
- [Docusaurus Documentation](https://docusaurus.io/docs)
- [MDX Documentation](https://mdxjs.com/docs)
- [React Documentation](https://reactjs.org/docs)

### Tools and Extensions
- VS Code extensions for MDX
- Markdown preview tools
- Accessibility testing tools
- Performance analysis tools

### Community Support
- [Docusaurus Discord](https://discord.gg/docusaurus)
- [GitHub Discussions](https://github.com/facebook/docusaurus/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/docusaurus)

## Next Steps

1. **Set up development environment**
2. **Create first module following guidelines**
3. **Test build and deployment process**
4. **Review content for constitution compliance**
5. **Iterate based on feedback**

For detailed specifications and requirements, see:
- `spec.md` - Feature specification
- `data-model.md` - Content structure
- `contracts/` - Technical contracts
- `constitution.md` - Governance principles