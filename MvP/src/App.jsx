import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import LocomotiveScroll from 'locomotive-scroll';
import 'locomotive-scroll/dist/locomotive-scroll.css';

// Components
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import About from './components/About';
import CTA from './components/CTA';
import Footer from './components/Footer';

function App() {
  const [isDark, setIsDark] = useState(true);
  const [scroll, setScroll] = useState(null);

  useEffect(() => {
    // Initialize Locomotive Scroll
    const locomotiveScroll = new LocomotiveScroll({
      el: document.querySelector('[data-scroll-container]'),
      smooth: true,
      lerp: 0.05,
      multiplier: 0.5,
      smartphone: {
        smooth: true,
        lerp: 0.05,
        multiplier: 0.5,
      },
    });

    setScroll(locomotiveScroll);

    // Cleanup
    return () => {
      locomotiveScroll.destroy();
    };
  }, []);

  return (
    <div className={`min-h-screen ${isDark ? 'dark' : ''}`}>
      <div data-scroll-container className="relative">
        <Navbar isDark={isDark} setIsDark={setIsDark} />
        
        <AnimatePresence mode="wait">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Hero />
            <Features />
            <HowItWorks />
            <About />
            <CTA />
            <Footer />
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App; 