import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Comprehensive Coverage',
    icon: '📚',
    description: (
      <>
        From fundamental kinematics to advanced AI integration, explore the complete
        spectrum of physical and humanoid robotics through 7 detailed chapters.
      </>
    ),
  },
  {
    title: 'Hands-On Learning',
    icon: '🛠️',
    description: (
      <>
        Master practical skills with real code examples, simulation tools, and
        step-by-step tutorials for building your own humanoid robots.
      </>
    ),
  },
  {
    title: 'Expert Knowledge',
    icon: '🎯',
    description: (
      <>
        Learn from industry case studies, cutting-edge research, and
        ethical considerations in modern robotics development.
      </>
    ),
  },
];

function Feature({icon, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className={styles.featureCard}>
        <div className={styles.featureIcon}>
          <span className={styles.icon}>{icon}</span>
        </div>
        <div className={styles.featureContent}>
          <Heading as="h3" className={styles.featureTitle}>{title}</Heading>
          <p className={styles.featureDescription}>{description}</p>
        </div>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
