import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import LocomotiveScroll from 'locomotive-scroll';

// Components
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import About from './components/About';
import CTA from './components/CTA';
import Footer from './components/Footer';
import DashboardLayout from './components/dashboard/DashboardLayout';
import Dashboard from './components/dashboard/Dashboard';
import Courses from './components/dashboard/Courses';
import CourseLearning from './components/dashboard/CourseLearning';

function App() {
  const [isDark, setIsDark] = useState(false);
  const [scroll, setScroll] = useState(null);

  useEffect(() => {
    // Initialize Locomotive Scroll
    const locomotiveScroll = new LocomotiveScroll({
      el: document.querySelector('[data-scroll-container]'),
      smooth: true,
      lerp: 0.03,
      multiplier: 0.8,
      smartphone: {
        smooth: true,
        lerp: 0.05,
        multiplier: 0.8,
      },
      tablet: {
        smooth: true,
        lerp: 0.04,
        multiplier: 0.8,
      }
    });

    setScroll(locomotiveScroll);

    // Cleanup
    return () => {
      if (locomotiveScroll) {
        locomotiveScroll.destroy();
      }
    };
  }, []);

  return (
    <div className={`${isDark ? 'dark' : ''}`}>
      <AnimatePresence mode="wait">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
          data-scroll-container
        >
          <Routes>
            {/* Public Routes */}
            <Route
              path="/"
              element={
                <>
                  <Navbar isDark={isDark} setIsDark={setIsDark} />
                  <Hero />
                  <Features />
                  <HowItWorks />
                  <About />
                  <CTA />
                  <Footer />
                </>
              }
            />

            {/* Dashboard Routes */}
            <Route path="/dashboard" element={<DashboardLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="courses" element={<Courses />} />
              <Route path="course/:id" element={<CourseLearning />} />
            </Route>
          </Routes>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export default App;
