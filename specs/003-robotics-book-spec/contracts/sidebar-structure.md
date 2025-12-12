# Sidebar Structure Contract

**Version**: 1.0.0  
**Date**: 2025-12-07  
**Feature**: Physical and Humanoid Robotics Book

## Required Sidebar Structure

### Top-Level Categories
```javascript
module.exports = {
  bookSidebar: [
    {
      type: 'category',
      label: '1. Introduction',
      collapsible: true,
      collapsed: false,
      items: [
        'introduction/01-history-and-evolution',
        'introduction/02-types-of-robots',
        'introduction/03-why-humanoid-robotics',
        'introduction/04-book-overview',
      ],
    },
    {
      type: 'category',
      label: '2. Physical Robotics Fundamentals',
      collapsible: true,
      collapsed: false,
      items: [
        'physical-fundamentals/01-kinematics-dynamics',
        'physical-fundamentals/02-actuators-motors',
        'physical-fundamentals/03-sensors',
        'physical-fundamentals/04-power-systems',
        'physical-fundamentals/05-control-theory',
      ],
    },
    {
      type: 'category',
      label: '3. Humanoid Robot Design',
      collapsible: true,
      collapsed: false,
      items: [
        'humanoid-design/01-anthropomorphic-design',
        'humanoid-design/02-degrees-freedom',
        'humanoid-design/03-bipedal-locomotion',
        'humanoid-design/04-balance-gait',
        'humanoid-design/05-hands-grippers',
      ],
    },
    {
      type: 'category',
      label: '4. Perception and AI Integration',
      collapsible: true,
      collapsed: false,
      items: [
        'perception-ai/01-computer-vision',
        'perception-ai/02-sensor-fusion',
        'perception-ai/03-slam-navigation',
        'perception-ai/04-machine-learning',
        'perception-ai/05-natural-language',
      ],
    },
    {
      type: 'category',
      label: '5. Real-World Case Studies',
      collapsible: true,
      collapsed: false,
      items: [
        'case-studies/01-boston-dynamics',
        'case-studies/02-tesla-optimus',
        'case-studies/03-honda-asimo',
        'case-studies/04-open-source',
        'case-studies/05-lessons-learned',
      ],
    },
    {
      type: 'category',
      label: '6. Advanced and Emerging Topics',
      collapsible: true,
      collapsed: false,
      items: [
        'advanced-topics/01-soft-robotics',
        'advanced-topics/02-swarm-robotics',
        'advanced-topics/03-ethics-safety',
        'advanced-topics/04-general-purpose',
      ],
    },
    {
      type: 'category',
      label: '7. Hands-On and Resources',
      collapsible: true,
      collapsed: false,
      items: [
        'hands-on/01-simulation-tools',
        'hands-on/02-ros2-crash-course',
        'hands-on/03-diy-humanoid',
        'hands-on/04-glossary-resources',
      ],
    },
  ],
};
```

## File Path Mapping

### Chapter 1 - Introduction
- `introduction/01-history-and-evolution` → `/docs/01-introduction/01-history-and-evolution.mdx`
- `introduction/02-types-of-robots` → `/docs/01-introduction/02-types-of-robots.mdx`
- `introduction/03-why-humanoid-robotics` → `/docs/01-introduction/03-why-humanoid-robotics.mdx`
- `introduction/04-book-overview` → `/docs/01-introduction/04-book-overview.mdx`

### Chapter 2 - Physical Fundamentals
- `physical-fundamentals/01-kinematics-dynamics` → `/docs/02-physical-fundamentals/01-kinematics-dynamics.mdx`
- `physical-fundamentals/02-actuators-motors` → `/docs/02-physical-fundamentals/02-actuators-motors.mdx`
- `physical-fundamentals/03-sensors` → `/docs/02-physical-fundamentals/03-sensors.mdx`
- `physical-fundamentals/04-power-systems` → `/docs/02-physical-fundamentals/04-power-systems.mdx`
- `physical-fundamentals/05-control-theory` → `/docs/02-physical-fundamentals/05-control-theory.mdx`

### Chapter 3 - Humanoid Design
- `humanoid-design/01-anthropomorphic-design` → `/docs/03-humanoid-design/01-anthropomorphic-design.mdx`
- `humanoid-design/02-degrees-freedom` → `/docs/03-humanoid-design/02-degrees-freedom.mdx`
- `humanoid-design/03-bipedal-locomotion` → `/docs/03-humanoid-design/03-bipedal-locomotion.mdx`
- `humanoid-design/04-balance-gait` → `/docs/03-humanoid-design/04-balance-gait.mdx`
- `humanoid-design/05-hands-grippers` → `/docs/03-humanoid-design/05-hands-grippers.mdx`

### Chapter 4 - Perception and AI
- `perception-ai/01-computer-vision` → `/docs/04-perception-ai/01-computer-vision.mdx`
- `perception-ai/02-sensor-fusion` → `/docs/04-perception-ai/02-sensor-fusion.mdx`
- `perception-ai/03-slam-navigation` → `/docs/04-perception-ai/03-slam-navigation.mdx`
- `perception-ai/04-machine-learning` → `/docs/04-perception-ai/04-machine-learning.mdx`
- `perception-ai/05-natural-language` → `/docs/04-perception-ai/05-natural-language.mdx`

### Chapter 5 - Case Studies
- `case-studies/01-boston-dynamics` → `/docs/05-case-studies/01-boston-dynamics.mdx`
- `case-studies/02-tesla-optimus` → `/docs/05-case-studies/02-tesla-optimus.mdx`
- `case-studies/03-honda-asimo` → `/docs/05-case-studies/03-honda-asimo.mdx`
- `case-studies/04-open-source` → `/docs/05-case-studies/04-open-source.mdx`
- `case-studies/05-lessons-learned` → `/docs/05-case-studies/05-lessons-learned.mdx`

### Chapter 6 - Advanced Topics
- `advanced-topics/01-soft-robotics` → `/docs/06-advanced-topics/01-soft-robotics.mdx`
- `advanced-topics/02-swarm-robotics` → `/docs/06-advanced-topics/02-swarm-robotics.mdx`
- `advanced-topics/03-ethics-safety` → `/docs/06-advanced-topics/03-ethics-safety.mdx`
- `advanced-topics/04-general-purpose` → `/docs/06-advanced-topics/04-general-purpose.mdx`

### Chapter 7 - Hands-On
- `hands-on/01-simulation-tools` → `/docs/07-hands-on/01-simulation-tools.mdx`
- `hands-on/02-ros2-crash-course` → `/docs/07-hands-on/02-ros2-crash-course.mdx`
- `hands-on/03-diy-humanoid` → `/docs/07-hands-on/03-diy-humanoid.mdx`
- `hands-on/04-glossary-resources` → `/docs/07-hands-on/04-glossary-resources.mdx`

## Validation Rules

### Structure Requirements
- All 7 chapters must be present
- Each chapter must have exactly 4-5 modules
- Total modules must be 28
- All paths must be valid and accessible

### Navigation Requirements
- Categories must be collapsible with collapsed: false
- Items must be in correct order
- Labels must match chapter titles exactly
- No broken links allowed

### Accessibility Requirements
- Proper heading hierarchy (h1 > h2 > h3)
- Keyboard navigation support
- Screen reader compatibility
- ARIA labels for interactive elements

### Performance Requirements
- Sidebar must load instantly
- No JavaScript errors in navigation
- Mobile-responsive design
- Touch-friendly interface

## Customization Options

### Theme Integration
- Custom colors for active items
- Icons for chapter categories
- Progress indicators
- Search integration

### User Experience
- Breadcrumb navigation
- Reading progress indicator
- Chapter completion tracking
- Quick navigation shortcuts

## Testing Requirements

### Automated Tests
- Link validation for all sidebar items
- Structure validation against file system
- Accessibility testing with axe-core
- Performance testing with Lighthouse

### Manual Testing
- Cross-browser compatibility
- Mobile device testing
- Screen reader testing
- User interaction testing

## Maintenance Requirements

### Content Updates
- Automatic sidebar regeneration on file changes
- Validation of new content structure
- Broken link detection and reporting
- Version compatibility checking

### Performance Monitoring
- Sidebar loading time tracking
- User interaction analytics
- Error reporting and monitoring
- Usage pattern analysis