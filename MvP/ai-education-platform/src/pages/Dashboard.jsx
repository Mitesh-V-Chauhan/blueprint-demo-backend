import { motion } from 'framer-motion';
import {
  BookOpenIcon,
  ClockIcon,
  ChartBarIcon,
  TrophyIcon,
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const stats = [
    {
      label: 'Courses in Progress',
      value: '3',
      icon: BookOpenIcon,
      color: 'text-blue-500',
    },
    {
      label: 'Hours Learned',
      value: '24',
      icon: ClockIcon,
      color: 'text-green-500',
    },
    {
      label: 'Completion Rate',
      value: '75%',
      icon: ChartBarIcon,
      color: 'text-purple-500',
    },
    {
      label: 'Achievements',
      value: '8',
      icon: TrophyIcon,
      color: 'text-yellow-500',
    },
  ];

  const recentCourses = [
    {
      title: 'Introduction to AI',
      progress: 75,
      lastAccessed: '2 hours ago',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80',
    },
    {
      title: 'Machine Learning Basics',
      progress: 45,
      lastAccessed: '1 day ago',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80',
    },
    {
      title: 'Data Science Fundamentals',
      progress: 30,
      lastAccessed: '3 days ago',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=80',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, John!
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            Here's your learning progress overview
          </p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="glass-effect p-6 rounded-2xl"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <span className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stat.value}
                </span>
              </div>
              <p className="text-gray-600 dark:text-gray-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Recent Courses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="glass-effect p-6 rounded-2xl"
        >
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            Continue Learning
          </h2>
          <div className="space-y-6">
            {recentCourses.map((course) => (
              <div
                key={course.title}
                className="flex items-center space-x-4 p-4 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200"
              >
                <img
                  src={course.image}
                  alt={course.title}
                  className="w-16 h-16 rounded-lg object-cover"
                />
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {course.title}
                  </h3>
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full"
                        style={{ width: `${course.progress}%` }}
                      />
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {course.progress}% Complete
                      </span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Last accessed {course.lastAccessed}
                      </span>
                    </div>
                  </div>
                </div>
                <button className="btn-primary px-4 py-2">
                  Continue
                </button>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Learning Streak */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-8 glass-effect p-6 rounded-2xl"
        >
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            Learning Streak
          </h2>
          <div className="flex space-x-2">
            {[...Array(7)].map((_, i) => (
              <div
                key={i}
                className="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center"
              >
                <span className="text-primary font-bold">{i + 1}</span>
              </div>
            ))}
          </div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            Keep up the great work! You're on a 7-day learning streak.
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard; 