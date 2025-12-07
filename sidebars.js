// @ts-check

/**
 * Creating a sidebar enables you to:
 * - create an ordered group of docs
 * - render a sidebar for each doc of that group
 * - provide next/previous navigation
 * 
 * The sidebars can be generated from the filesystem, or explicitly defined here.
 * 
 * Create as many sidebars as you want.
 * 
 * @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
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

export default sidebars;