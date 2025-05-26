import { motion } from 'framer-motion';
import {
  AcademicCapIcon,
  SparklesIcon,
  ChartBarIcon,
  UserGroupIcon,
  ClockIcon,
  GlobeAltIcon,
} from '@heroicons/react/24/outline';

const features = [
  {
    title: 'AI-Powered Learning',
    description: 'Personalized learning paths adapted to your pace and style using advanced AI algorithms.',
    icon: SparklesIcon,
  },
  {
    title: 'Interactive Content',
    description: 'Engage with dynamic content, quizzes, and real-world projects for hands-on learning.',
    icon: AcademicCapIcon,
  },
  {
    title: 'Progress Tracking',
    description: 'Monitor your learning journey with detailed analytics and achievement milestones.',
    icon: ChartBarIcon,
  },
  {
    title: 'Community Learning',
    description: 'Connect with peers, share knowledge, and learn together in a supportive environment.',
    icon: UserGroupIcon,
  },
  {
    title: 'Flexible Schedule',
    description: 'Learn at your own pace with 24/7 access to course materials and resources.',
    icon: ClockIcon,
  },
  {
    title: 'Global Access',
    description: 'Access world-class education from anywhere, anytime, on any device.',
    icon: GlobeAltIcon,
  },
];

const Features = () => {
  return (
    <section id="features" className="py-24 bg-gradient">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-bold text-gradient mb-4">
            Why Choose Our Platform?
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Experience the future of education with our cutting-edge features designed to enhance your learning journey.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="glass-effect p-8 rounded-2xl hover:scale-105 transform transition-all duration-300"
            >
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 rounded-xl bg-primary/10">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {feature.title}
                </h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Decorative Elements */}
        <motion.div
          className="absolute top-1/4 right-1/4 w-64 h-64 bg-primary/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            repeatType: 'reverse',
          }}
        />
        <motion.div
          className="absolute bottom-1/4 left-1/4 w-64 h-64 bg-secondary/10 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.5, 0.3, 0.5],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            repeatType: 'reverse',
          }}
        />
      </div>
    </section>
  );
};

export default Features; 