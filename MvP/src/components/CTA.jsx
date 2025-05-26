import { motion } from 'framer-motion';

const CTA = () => {
  return (
    <section className="section-padding bg-primary relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-dark to-primary opacity-90" />
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />
      </div>

      <div className="relative max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center lg:text-left"
          >
            <h2 className="text-3xl sm:text-4xl font-bold font-display mb-6 text-white">
              Ready to Transform Your{' '}
              <span className="text-white/90">Learning Journey?</span>
            </h2>
            
            <p className="text-lg text-white/80 mb-8 max-w-xl mx-auto lg:mx-0">
              Join thousands of learners who are already experiencing the future of
              education with our AI-powered platform.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-white text-primary hover:bg-white/90 text-lg px-8 py-4 rounded-lg font-medium transition-colors duration-200"
              >
                Start Free Trial
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="border-2 border-white text-white hover:bg-white/10 text-lg px-8 py-4 rounded-lg font-medium transition-colors duration-200"
              >
                Schedule Demo
              </motion.button>
            </div>
          </motion.div>

          {/* Right Column - Features */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="grid grid-cols-2 gap-4"
          >
            {[
              {
                title: 'Free Trial',
                description: '14-day free access to all features',
              },
              {
                title: 'No Credit Card',
                description: 'Start learning without commitment',
              },
              {
                title: 'Cancel Anytime',
                description: 'Flexible subscription options',
              },
              {
                title: 'Full Access',
                description: 'All courses and AI features included',
              },
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white/10 backdrop-blur-lg p-6 rounded-2xl"
              >
                <h3 className="text-lg font-bold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-white/70 text-sm">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default CTA; 