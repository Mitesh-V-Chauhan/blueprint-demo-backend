import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
} from '@heroicons/react/24/outline';

const Courses = () => {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    'All',
    'AI & Machine Learning',
    'Data Science',
    'Programming',
    'Web Development',
    'Mobile Development',
  ];

  const courses = [
    {
      id: 1,
      title: 'Introduction to Artificial Intelligence',
      description: 'Learn the fundamentals of AI and its applications in modern technology.',
      category: 'AI & Machine Learning',
      instructor: 'Dr. Sarah Johnson',
      rating: 4.8,
      students: 1200,
      duration: '8 weeks',
      level: 'Beginner',
      price: '$49.99',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995',
    },
    {
      id: 2,
      title: 'Data Science Fundamentals',
      description: 'Master the basics of data analysis and visualization.',
      category: 'Data Science',
      instructor: 'Prof. Michael Chen',
      rating: 4.6,
      students: 850,
      duration: '10 weeks',
      level: 'Intermediate',
      price: '$59.99',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995',
    },
    {
      id: 3,
      title: 'Web Development with React',
      description: 'Build modern web applications using React and best practices.',
      category: 'Web Development',
      instructor: 'Alex Thompson',
      rating: 4.9,
      students: 1500,
      duration: '12 weeks',
      level: 'Intermediate',
      price: '$69.99',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995',
    },
  ];

  const filteredCourses = courses.filter((course) => {
    const matchesCategory =
      selectedCategory === 'All' || course.category === selectedCategory;
    const matchesSearch = course.title
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-effect p-6 rounded-2xl"
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Available Courses
        </h1>
        <p className="text-gray-600 dark:text-gray-300 mt-2">
          Explore our collection of AI-powered learning courses
        </p>
      </motion.div>

      {/* Search and Filter */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search courses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <AdjustmentsHorizontalIcon className="h-5 w-5 text-gray-400" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Course Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCourses.map((course, index) => (
          <motion.div
            key={course.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-effect rounded-2xl overflow-hidden"
          >
            <img
              src={course.image}
              alt={course.title}
              className="w-full h-48 object-cover"
            />
            <div className="p-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {course.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                {course.description}
              </p>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {course.instructor}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    • {course.rating} ⭐
                  </span>
                </div>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {course.students} students
                </span>
              </div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {course.duration}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    • {course.level}
                  </span>
                </div>
                <span className="text-lg font-bold text-primary">
                  {course.price}
                </span>
              </div>
              <button className="w-full btn-primary">Enroll Now</button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Courses; 