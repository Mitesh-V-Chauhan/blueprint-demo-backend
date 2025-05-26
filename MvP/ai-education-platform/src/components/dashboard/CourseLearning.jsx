import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  PlayIcon,
  PauseIcon,
  ForwardIcon,
  BackwardIcon,
  BookOpenIcon,
  CheckCircleIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';

const CourseLearning = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentLesson, setCurrentLesson] = useState(1);
  const [progress, setProgress] = useState(0);

  const courseContent = [
    {
      id: 1,
      title: 'Introduction to AI',
      lessons: [
        { id: 1, title: 'What is Artificial Intelligence?', duration: '15:00' },
        { id: 2, title: 'History of AI', duration: '20:00' },
        { id: 3, title: 'Types of AI', duration: '18:00' },
      ],
    },
    {
      id: 2,
      title: 'Machine Learning Basics',
      lessons: [
        { id: 4, title: 'Introduction to Machine Learning', duration: '25:00' },
        { id: 5, title: 'Supervised Learning', duration: '30:00' },
        { id: 6, title: 'Unsupervised Learning', duration: '28:00' },
      ],
    },
  ];

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Main Content Area */}
      <div className="flex-1 space-y-6">
        {/* Video Player */}
        <div className="glass-effect rounded-2xl overflow-hidden">
          <div className="aspect-video bg-gray-900 relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-4 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
              >
                {isPlaying ? (
                  <PauseIcon className="h-8 w-8 text-white" />
                ) : (
                  <PlayIcon className="h-8 w-8 text-white" />
                )}
              </button>
            </div>
          </div>
          <div className="p-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              {courseContent[0].lessons[currentLesson - 1].title}
            </h2>
            <div className="mt-2 flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
                  <BackwardIcon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                </button>
                <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
                  <ForwardIcon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                </button>
              </div>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {courseContent[0].lessons[currentLesson - 1].duration}
              </span>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="glass-effect p-4 rounded-2xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Course Progress
            </span>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {progress}%
            </span>
          </div>
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
            <div
              className="h-2 bg-primary rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Course Content Sidebar */}
      <div className="lg:w-80 space-y-4">
        <div className="glass-effect p-4 rounded-2xl">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Course Content
          </h3>
          <div className="space-y-2">
            {courseContent.map((section) => (
              <div key={section.id} className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {section.title}
                </h4>
                <div className="space-y-1">
                  {section.lessons.map((lesson) => (
                    <button
                      key={lesson.id}
                      onClick={() => setCurrentLesson(lesson.id)}
                      className={`w-full flex items-center justify-between p-2 rounded-lg transition-colors ${
                        currentLesson === lesson.id
                          ? 'bg-primary/10 text-primary'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <BookOpenIcon className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {lesson.title}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {lesson.duration}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Resources */}
        <div className="glass-effect p-4 rounded-2xl">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Resources
          </h3>
          <div className="space-y-2">
            <button className="w-full flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
              <CheckCircleIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Quiz
              </span>
            </button>
            <button className="w-full flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
              <ChatBubbleLeftRightIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Discussion Forum
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseLearning; 