import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  PlayIcon,
  PauseIcon,
  ForwardIcon,
  BackwardIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  QuestionMarkCircleIcon,
} from '@heroicons/react/24/outline';
import DoubtSidebar from './DoubtSidebar';

const lessons = [
  {
    id: 1,
    title: 'Introduction to Python',
    duration: '15:00',
    completed: true,
  },
  {
    id: 2,
    title: 'Variables and Data Types',
    duration: '20:00',
    completed: true,
  },
  {
    id: 3,
    title: 'Control Structures',
    duration: '25:00',
    completed: false,
  },
  {
    id: 4,
    title: 'Functions and Modules',
    duration: '30:00',
    completed: false,
  },
  {
    id: 5,
    title: 'Object-Oriented Programming',
    duration: '35:00',
    completed: false,
  },
];

const CourseLearning = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentLesson, setCurrentLesson] = useState(3);
  const [isDoubtSidebarOpen, setIsDoubtSidebarOpen] = useState(false);

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Main Content */}
      <div className="flex-1">
        {/* Video Player */}
        <div className="relative aspect-video bg-black rounded-xl overflow-hidden mb-6">
          <video
            className="w-full h-full"
            poster="https://images.unsplash.com/photo-1526378800650-7d2c5f5b3d3a?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
          >
            <source src="video.mp4" type="video/mp4" />
          </video>

          {/* Video Controls */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors duration-200"
                >
                  {isPlaying ? (
                    <PauseIcon className="w-6 h-6 text-white" />
                  ) : (
                    <PlayIcon className="w-6 h-6 text-white" />
                  )}
                </button>
                <button className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors duration-200">
                  <BackwardIcon className="w-6 h-6 text-white" />
                </button>
                <button className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors duration-200">
                  <ForwardIcon className="w-6 h-6 text-white" />
                </button>
                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors duration-200"
                >
                  {isMuted ? (
                    <SpeakerXMarkIcon className="w-6 h-6 text-white" />
                  ) : (
                    <SpeakerWaveIcon className="w-6 h-6 text-white" />
                  )}
                </button>
              </div>
              <div className="text-white text-sm">
                {lessons[currentLesson - 1].duration}
              </div>
            </div>
          </div>
        </div>

        {/* Lesson Content */}
        <div className="glass-effect rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {lessons[currentLesson - 1].title}
            </h2>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsDoubtSidebarOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors duration-200"
            >
              <QuestionMarkCircleIcon className="w-5 h-5" />
              <span>Ask Doubt</span>
            </motion.button>
          </div>
          <div className="prose dark:prose-invert max-w-none">
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
              eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
              ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
              aliquip ex ea commodo consequat.
            </p>
            <h3>Key Points</h3>
            <ul>
              <li>First key point about the lesson</li>
              <li>Second key point about the lesson</li>
              <li>Third key point about the lesson</li>
            </ul>
            <h3>Code Example</h3>
            <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
              <code>
                {`def example_function():
    print("Hello, World!")
    return True`}
              </code>
            </pre>
          </div>
        </div>
      </div>

      {/* Lesson Navigation */}
      <div className="lg:w-80">
        <div className="glass-effect rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Course Content
          </h3>
          <div className="space-y-2">
            {lessons.map((lesson, index) => (
              <motion.button
                key={lesson.id}
                onClick={() => setCurrentLesson(lesson.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors duration-200 ${
                  currentLesson === lesson.id
                    ? 'bg-primary text-white'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
                whileHover={{ x: 4 }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center ${
                        lesson.completed
                          ? 'bg-green-500 text-white'
                          : 'bg-gray-200 dark:bg-gray-700'
                      }`}
                    >
                      {lesson.completed ? '✓' : index + 1}
                    </div>
                    <span className="font-medium">{lesson.title}</span>
                  </div>
                  <span className="text-sm">{lesson.duration}</span>
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Course Progress */}
        <div className="glass-effect rounded-xl p-6 mt-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Course Progress
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Overall Progress
                </span>
                <span className="text-sm font-medium text-primary">40%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: '40%' }}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Current Module
                </span>
                <span className="text-sm font-medium text-primary">60%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: '60%' }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Doubt Sidebar */}
      <DoubtSidebar
        isOpen={isDoubtSidebarOpen}
        onClose={() => setIsDoubtSidebarOpen(false)}
      />
    </div>
  );
};

export default CourseLearning; 