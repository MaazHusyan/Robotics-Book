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
        'introduction/history-and-evolution',
        'introduction/types-of-robots',
        'introduction/why-humanoid-robotics',
        'introduction/book-overview',
      ],
    },
    {
      type: 'category',
      label: '2. Physical Robotics Fundamentals',
      collapsible: true,
      collapsed: false,
      items: [
        'physical-fundamentals/kinematics-dynamics',
        'physical-fundamentals/actuators-motors',
        'physical-fundamentals/sensors',
        'physical-fundamentals/power-systems',
        'physical-fundamentals/control-theory',
      ],
    },
    {
      type: 'category',
      label: '3. Humanoid Robot Design',
      collapsible: true,
      collapsed: false,
      items: [
        'humanoid-design/anthropomorphic-design',
        'humanoid-design/degrees-freedom',
        'humanoid-design/balance-gait',
        'humanoid-design/hands-grippers',
      ],
    },
    
  ],
};

export default sidebars;