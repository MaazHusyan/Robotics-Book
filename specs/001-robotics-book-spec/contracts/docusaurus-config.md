# Docusaurus Configuration Contract

**Version**: 1.0.0  
**Date**: 2025-12-07  
**Feature**: Physical and Humanoid Robotics Book

## Required Configuration

### Site Metadata
```javascript
const config = {
  title: "Physical and Humanoid Robotics",
  tagline: "From Fundamentals to Advanced Applications",
  url: "https://[username].github.io",
  baseUrl: "/robotics-book/",
  organizationName: "[username]",
  projectName: "robotics-book",
}
```

### Preset Configuration
```javascript
const presets = [
  [
    '@docusaurus/preset-classic',
    {
      docs: {
        sidebarPath: './sidebars.js',
        routeBasePath: 'docs',
        editUrl: 'https://github.com/[username]/robotics-book/tree/main/',
      },
      blog: false, // Explicitly disabled
      theme: {
        customCss: ['./src/css/custom.css'],
      },
    },
  ],
]
```

### Theme Configuration
```javascript
const themeConfig = {
  colorMode: {
    defaultMode: 'dark',
    respectPrefersColorScheme: false,
  },
  navbar: {
    title: "Physical and Humanoid Robotics",
    logo: {
      alt: "Robotics Book Logo",
      src: "img/logo.svg",
    },
    items: [
      {
        type: 'doc',
        docId: 'introduction/01-history-and-evolution',
        position: 'left',
        label: 'Book',
      },
      {
        href: 'https://github.com/[username]/robotics-book',
        label: 'GitHub',
        position: 'right',
      },
    ],
  },
  footer: {
    style: 'dark',
    links: [
      {
        title: 'Book',
        items: [
          {
            label: 'GitHub Repository',
            href: 'https://github.com/[username]/robotics-book',
          },
        ],
      },
    ],
    copyright: `Copyright © ${new Date().getFullYear()} Physical and Humanoid Robotics Book.`,
  },
  prism: {
    theme: require('prism-react-renderer/themes/vsDark'),
    additionalLanguages: ['python', 'cpp', 'bash'],
  },
}
```

### Plugin Configuration
```javascript
const plugins = [
  [
    '@docusaurus/plugin-content-docs',
    {
      id: 'book',
      path: 'docs',
      routeBasePath: 'docs',
      sidebarPath: './sidebars.js',
      editUrl: 'https://github.com/[username]/robotics-book/tree/main/',
      include: ['**/*.mdx'],
    },
  ],
  [
    '@docusaurus/plugin-ideal-image',
    {
      quality: 70,
      max: 1030,
      min: 640,
      steps: 2,
      disableInDev: false,
    },
  ],
  [
    '@docusaurus/plugin-pwa',
    {
      debug: true,
      offlineMode: true,
      register: true,
      strategies: ['networkFirst'],
    },
  ],
]
```

## Validation Rules

### Site Performance
- Page load time must be <3 seconds
- Google PageSpeed score must be >90
- All images must be optimized
- Code splitting must be implemented

### Accessibility Compliance
- WCAG 2.1 AA compliance required
- Semantic HTML structure mandatory
- ARIA labels for interactive elements
- Keyboard navigation support

### Content Structure
- All content must be in /docs/ folder
- MDX format required for all files
- Frontmatter must include title and sidebar_label
- No blog functionality allowed

### Theme Requirements
- Dark mode must be default
- Custom colors: primary #0066cc, accent #00d4ff
- Responsive design mandatory
- Mobile-first approach required

## Deployment Configuration

### GitHub Pages Setup
```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
```

### Build Requirements
- Build must complete without errors
- All links must be valid
- No console errors in production
- Sitemap must be generated

## Testing Requirements

### Automated Tests
- Build validation on every commit
- Link checking for all internal links
- Accessibility testing with axe-core
- Performance testing with Lighthouse

### Manual Testing
- Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Mobile device testing (iOS, Android)
- Screen reader compatibility
- Print stylesheet validation

## Security Requirements

### Content Security
- All external links must use HTTPS
- No inline scripts in MDX content
- Subresource Integrity checking for external resources
- XSS prevention in user input handling

### Dependency Security
- Regular dependency updates
- Security scanning with npm audit
- No known vulnerabilities in production
- Minimal external dependencies

## Maintenance Requirements

### Content Updates
- Version control for all content changes
- Automated testing for content validation
- Review process for all updates
- Backup and recovery procedures

### Technical Maintenance
- Regular dependency updates
- Performance monitoring
- Error tracking and reporting
- User feedback collection system