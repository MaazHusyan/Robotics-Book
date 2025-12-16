import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/Robotics-Book/__docusaurus/debug',
    component: ComponentCreator('/Robotics-Book/__docusaurus/debug', '58f'),
    exact: true
  },
  {
    path: '/Robotics-Book/__docusaurus/debug/config',
    component: ComponentCreator('/Robotics-Book/__docusaurus/debug/config', 'a2e'),
    exact: true
  },
  {
    path: '/Robotics-Book/__docusaurus/debug/content',
    component: ComponentCreator('/Robotics-Book/__docusaurus/debug/content', '43a'),
    exact: true
  },
  {
    path: '/Robotics-Book/__docusaurus/debug/globalData',
    component: ComponentCreator('/Robotics-Book/__docusaurus/debug/globalData', '545'),
    exact: true
  },
  {
    path: '/Robotics-Book/__docusaurus/debug/metadata',
    component: ComponentCreator('/Robotics-Book/__docusaurus/debug/metadata', 'e4f'),
    exact: true
  },
  {
    path: '/Robotics-Book/__docusaurus/debug/registry',
    component: ComponentCreator('/Robotics-Book/__docusaurus/debug/registry', '157'),
    exact: true
  },
  {
    path: '/Robotics-Book/__docusaurus/debug/routes',
    component: ComponentCreator('/Robotics-Book/__docusaurus/debug/routes', '4c0'),
    exact: true
  },
  {
    path: '/Robotics-Book/markdown-page',
    component: ComponentCreator('/Robotics-Book/markdown-page', 'e00'),
    exact: true
  },
  {
    path: '/Robotics-Book/docs',
    component: ComponentCreator('/Robotics-Book/docs', '477'),
    routes: [
      {
        path: '/Robotics-Book/docs',
        component: ComponentCreator('/Robotics-Book/docs', 'aa5'),
        routes: [
          {
            path: '/Robotics-Book/docs/tags',
            component: ComponentCreator('/Robotics-Book/docs/tags', '7a4'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/actuators',
            component: ComponentCreator('/Robotics-Book/docs/tags/actuators', 'f03'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/anthropomorphic-design',
            component: ComponentCreator('/Robotics-Book/docs/tags/anthropomorphic-design', 'b79'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/biomechanics',
            component: ComponentCreator('/Robotics-Book/docs/tags/biomechanics', 'af8'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/control-theory',
            component: ComponentCreator('/Robotics-Book/docs/tags/control-theory', '54b'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/degrees-of-freedom',
            component: ComponentCreator('/Robotics-Book/docs/tags/degrees-of-freedom', '4ae'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/energy-management',
            component: ComponentCreator('/Robotics-Book/docs/tags/energy-management', '929'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/feedback-systems',
            component: ComponentCreator('/Robotics-Book/docs/tags/feedback-systems', 'a39'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/humanoid-robotics',
            component: ComponentCreator('/Robotics-Book/docs/tags/humanoid-robotics', 'fb2'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/joint-configuration',
            component: ComponentCreator('/Robotics-Book/docs/tags/joint-configuration', '8eb'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/kinematic-chains',
            component: ComponentCreator('/Robotics-Book/docs/tags/kinematic-chains', 'ebe'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/kinematics',
            component: ComponentCreator('/Robotics-Book/docs/tags/kinematics', 'da3'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/motors',
            component: ComponentCreator('/Robotics-Book/docs/tags/motors', '4c4'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/perception',
            component: ComponentCreator('/Robotics-Book/docs/tags/perception', '46b'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/physical-fundamentals',
            component: ComponentCreator('/Robotics-Book/docs/tags/physical-fundamentals', '094'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/power-systems',
            component: ComponentCreator('/Robotics-Book/docs/tags/power-systems', 'b62'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/robot-design',
            component: ComponentCreator('/Robotics-Book/docs/tags/robot-design', '534'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/robotics',
            component: ComponentCreator('/Robotics-Book/docs/tags/robotics', 'b49'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs/tags/sensors',
            component: ComponentCreator('/Robotics-Book/docs/tags/sensors', 'bab'),
            exact: true
          },
          {
            path: '/Robotics-Book/docs',
            component: ComponentCreator('/Robotics-Book/docs', 'c4f'),
            routes: [
              {
                path: '/Robotics-Book/docs/humanoid-design/anthropomorphic-design',
                component: ComponentCreator('/Robotics-Book/docs/humanoid-design/anthropomorphic-design', '7b7'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/humanoid-design/balance-gait',
                component: ComponentCreator('/Robotics-Book/docs/humanoid-design/balance-gait', 'c38'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/humanoid-design/degrees-freedom',
                component: ComponentCreator('/Robotics-Book/docs/humanoid-design/degrees-freedom', '17f'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/humanoid-design/hands-grippers',
                component: ComponentCreator('/Robotics-Book/docs/humanoid-design/hands-grippers', '6c8'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/humanoid-design/kinematic-chains',
                component: ComponentCreator('/Robotics-Book/docs/humanoid-design/kinematic-chains', '75b'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/intro',
                component: ComponentCreator('/Robotics-Book/docs/intro', '90f'),
                exact: true
              },
              {
                path: '/Robotics-Book/docs/introduction/book-overview',
                component: ComponentCreator('/Robotics-Book/docs/introduction/book-overview', '7cf'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/introduction/history-and-evolution',
                component: ComponentCreator('/Robotics-Book/docs/introduction/history-and-evolution', '13b'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/introduction/types-of-robots',
                component: ComponentCreator('/Robotics-Book/docs/introduction/types-of-robots', 'faa'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/introduction/why-humanoid-robotics',
                component: ComponentCreator('/Robotics-Book/docs/introduction/why-humanoid-robotics', '07e'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/physical-fundamentals/actuators-motors',
                component: ComponentCreator('/Robotics-Book/docs/physical-fundamentals/actuators-motors', 'f8b'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/physical-fundamentals/control-theory',
                component: ComponentCreator('/Robotics-Book/docs/physical-fundamentals/control-theory', '56d'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/physical-fundamentals/kinematics-dynamics',
                component: ComponentCreator('/Robotics-Book/docs/physical-fundamentals/kinematics-dynamics', '6dc'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/physical-fundamentals/power-systems',
                component: ComponentCreator('/Robotics-Book/docs/physical-fundamentals/power-systems', '41b'),
                exact: true,
                sidebar: "bookSidebar"
              },
              {
                path: '/Robotics-Book/docs/physical-fundamentals/sensors',
                component: ComponentCreator('/Robotics-Book/docs/physical-fundamentals/sensors', 'c3a'),
                exact: true,
                sidebar: "bookSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/Robotics-Book/',
    component: ComponentCreator('/Robotics-Book/', 'a5d'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
