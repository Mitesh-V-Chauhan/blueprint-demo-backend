import { motion } from 'framer-motion';
import {
  AcademicCapIcon,
  CodeBracketIcon,
  BriefcaseIcon,
} from '@heroicons/react/24/outline';

const features = [
  {
    title: 'AI-Powered Personalized Learning',
    description: 'Tailored lessons and interactive AI chat that adapts to your learning style and pace.',
    icon: AcademicCapIcon,
  },
  {
    title: 'Hands-On Projects & AI-Graded Assignments',
    description: 'Real-world learning with instant feedback and personalized guidance from AI.',
    icon: CodeBracketIcon,
  },
  {
    title: 'Career Pathways & AI-Verified Certifications',
    description: 'Build in-demand skills and get job-ready with industry-recognized certifications.',
    icon: BriefcaseIcon,
  },
];

const Features = () => {
  return (
    <section id="features" className="section-padding">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold font-display mb-4">
            Why Choose Our{' '}
            <span className="gradient-text">AI-Powered Platform</span>
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Experience the future of education with our cutting-edge AI technology
            that adapts to your learning journey.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              whileHover={{ y: -10 }}
              className="glass-effect p-8 rounded-2xl"
            >
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6">
                <feature.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-4">{feature.title}</h3>
              <p className="text-gray-600 dark:text-gray-300">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Additional Features Grid */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            '24/7 AI Support',
            'Interactive Learning',
            'Progress Tracking',
            'Mobile Access',
            'Community Forums',
            'Resource Library',
            'Practice Tests',
            'Career Guidance',
          ].map((feature) => (
            <motion.div
              key={feature}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3 }}
              className="glass-effect p-4 rounded-xl text-center"
            >
              <span className="text-sm font-medium">{feature}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features; 