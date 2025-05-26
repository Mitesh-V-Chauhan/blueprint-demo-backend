import { motion } from 'framer-motion';
import {
  BookOpenIcon,
  ClockIcon,
  ChartBarIcon,
  TrophyIcon,
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const stats = [
    { name: 'Courses in Progress', value: '3', icon: BookOpenIcon },
    { name: 'Hours Learned', value: '24', icon: ClockIcon },
    { name: 'Completion Rate', value: '75%', icon: ChartBarIcon },
    { name: 'Achievements', value: '8', icon: TrophyIcon },
  ];

  const recentCourses = [
    {
      id: 1,
      title: 'Introduction to AI',
      progress: 75,
      lastAccessed: '2 hours ago',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995',
    },
    {
      id: 2,
      title: 'Machine Learning Basics',
      progress: 45,
      lastAccessed: '1 day ago',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995',
    },
    {
      id: 3,
      title: 'Deep Learning Fundamentals',
      progress: 30,
      lastAccessed: '3 days ago',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-effect p-6 rounded-2xl"
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Welcome back, John!
        </h1>
        <p className="text-gray-600 dark:text-gray-300 mt-2">
          Continue your learning journey
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-effect p-6 rounded-2xl"
          >
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-primary/10">
                <stat.icon className="h-6 w-6 text-primary" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-300">
                  {stat.name}
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stat.value}
                </p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Recent Courses */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-effect p-6 rounded-2xl"
      >
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
          Recent Courses
        </h2>
        <div className="space-y-4">
          {recentCourses.map((course) => (
            <div
              key={course.id}
              className="flex items-center space-x-4 p-4 rounded-lg bg-white dark:bg-gray-800"
            >
              <img
                src={course.image}
                alt={course.title}
                className="w-16 h-16 rounded-lg object-cover"
              />
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 dark:text-white">
                  {course.title}
                </h3>
                <div className="mt-1">
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                    <div
                      className="h-2 bg-primary rounded-full"
                      style={{ width: `${course.progress}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-1">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {course.progress}% Complete
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      Last accessed {course.lastAccessed}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard; 