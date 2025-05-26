import { motion } from 'framer-motion';
import { ChartBarIcon, UserGroupIcon, GlobeAltIcon } from '@heroicons/react/24/outline';

const stats = [
  {
    title: 'Success Rate',
    value: '95%',
    description: 'of students achieve their learning goals',
    icon: ChartBarIcon,
  },
  {
    title: 'Global Community',
    value: '50K+',
    description: 'learners from around the world',
    icon: UserGroupIcon,
  },
  {
    title: 'Languages',
    value: '20+',
    description: 'supported languages',
    icon: GlobeAltIcon,
  },
];

const About = () => {
  return (
    <section id="about" className="section-padding">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold font-display mb-6">
              Transforming Education with{' '}
              <span className="gradient-text">AI Technology</span>
            </h2>
            
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
              We're on a mission to revolutionize education by making personalized learning
              accessible to everyone. Our AI-powered platform adapts to your unique learning
              style, pace, and goals.
            </p>

            <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
              With cutting-edge technology and a passionate team of educators, we're
              creating a future where quality education knows no boundaries.
            </p>

            <div className="space-y-4">
              {[
                'Personalized Learning Paths',
                'AI-Powered Progress Tracking',
                'Interactive Learning Experience',
                'Global Community Support',
              ].map((feature) => (
                <div key={feature} className="flex items-center gap-3">
                  <svg
                    className="w-5 h-5 text-primary"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Right Column - Stats */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="space-y-6"
          >
            {stats.map((stat, index) => (
              <motion.div
                key={stat.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.2 }}
                className="glass-effect p-6 rounded-2xl"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                    <stat.icon className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold gradient-text">{stat.value}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {stat.title}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-500">
                      {stat.description}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default About; 