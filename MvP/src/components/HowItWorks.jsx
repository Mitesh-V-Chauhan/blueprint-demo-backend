import { motion } from 'framer-motion';
import {
  UserCircleIcon,
  ChatBubbleLeftRightIcon,
  DocumentCheckIcon,
  RocketLaunchIcon,
} from '@heroicons/react/24/outline';

const steps = [
  {
    title: 'Create Your Profile',
    description: 'Sign up and tell us about your learning goals and preferences.',
    icon: UserCircleIcon,
  },
  {
    title: 'AI Tutor Matching',
    description: 'Our AI analyzes your needs and matches you with the perfect learning path.',
    icon: ChatBubbleLeftRightIcon,
  },
  {
    title: 'Interactive Learning',
    description: 'Engage with personalized lessons, projects, and real-time AI feedback.',
    icon: DocumentCheckIcon,
  },
  {
    title: 'Track Progress',
    description: 'Monitor your achievements and get AI-powered recommendations.',
    icon: RocketLaunchIcon,
  },
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="section-padding bg-gray-50 dark:bg-dark-light">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold font-display mb-4">
            How Our <span className="gradient-text">AI Platform</span> Works
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Experience a personalized learning journey powered by cutting-edge AI technology.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="relative">
          {/* Connecting Line */}
          <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-primary/20 hidden md:block" />

          <div className="space-y-12">
            {steps.map((step, index) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.2 }}
                className="relative"
              >
                <div className={`flex flex-col md:flex-row items-center gap-8 ${
                  index % 2 === 0 ? 'md:flex-row-reverse' : ''
                }`}>
                  {/* Content */}
                  <div className="flex-1 text-center md:text-left">
                    <div className="inline-block p-3 bg-primary/10 rounded-xl mb-4">
                      <step.icon className="w-6 h-6 text-primary" />
                    </div>
                    <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      {step.description}
                    </p>
                  </div>

                  {/* Step Number */}
                  <div className="flex-shrink-0 w-16 h-16 rounded-full bg-primary text-white flex items-center justify-center text-xl font-bold">
                    {index + 1}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.8 }}
          className="mt-16 text-center"
        >
          <button className="btn-primary text-lg px-8 py-4">
            Start Your Learning Journey
          </button>
        </motion.div>
      </div>
    </section>
  );
};

export default HowItWorks; 