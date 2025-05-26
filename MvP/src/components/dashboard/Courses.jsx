import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
} from '@heroicons/react/24/outline';

const courses = [
  {
    id: 1,
    title: 'Python Programming Fundamentals',
    description: 'Learn the basics of Python programming language',
    level: 'Beginner',
    duration: '8 weeks',
    lessons: 24,
    image: 'https://images.unsplash.com/photo-1526378800650-7d2c5f5b3d3a?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
    category: 'Programming',
    price: '$49.99',
    rating: 4.8,
    students: 1234,
  },
  {
    id: 2,
    title: 'Web Development with React',
    description: 'Master modern web development with React.js',
    level: 'Intermediate',
    duration: '10 weeks',
    lessons: 32,
    image: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
    category: 'Web Development',
    price: '$59.99',
    rating: 4.9,
    students: 2156,
  },
  {
    id: 3,
    title: 'Machine Learning Basics',
    description: 'Introduction to machine learning concepts and algorithms',
    level: 'Advanced',
    duration: '12 weeks',
    lessons: 36,
    image: 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
    category: 'AI & ML',
    price: '$79.99',
    rating: 4.7,
    students: 987,
  },
  // Add more courses as needed
];

const categories = [
  'All',
  'Programming',
  'Web Development',
  'AI & ML',
  'Data Science',
  'Mobile Development',
];

const Courses = () => {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCourses = courses.filter((course) => {
    const matchesCategory = selectedCategory === 'All' || course.category === selectedCategory;
    const matchesSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         course.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Available Courses
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Explore our collection of AI-powered courses.
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="block w-full rounded-lg border-0 py-3 pl-10 pr-4 text-gray-900 dark:text-white bg-white dark:bg-dark-light shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-700 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
            placeholder="Search courses..."
          />
        </div>
        <div className="flex items-center gap-2">
          <AdjustmentsHorizontalIcon className="h-5 w-5 text-gray-400" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="block rounded-lg border-0 py-3 pl-3 pr-10 text-gray-900 dark:text-white bg-white dark:bg-dark-light shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-700 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
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
        {filteredCourses.map((course) => (
          <motion.div
            key={course.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -5 }}
            className="bg-white dark:bg-dark-light rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200"
          >
            <div className="relative h-48">
              <img
                src={course.image}
                alt={course.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 right-4">
                <span className="bg-primary text-white px-3 py-1 rounded-full text-sm font-medium">
                  {course.price}
                </span>
              </div>
            </div>
            <div className="p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-primary">
                  {course.category}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {course.level}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {course.title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                {course.description}
              </p>
              <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
                <span>{course.duration}</span>
                <span>{course.lessons} lessons</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex items-center">
                    {[...Array(5)].map((_, i) => (
                      <svg
                        key={i}
                        className={`h-4 w-4 ${
                          i < Math.floor(course.rating)
                            ? 'text-yellow-400'
                            : 'text-gray-300 dark:text-gray-600'
                        }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <span className="ml-2">{course.rating}</span>
                </div>
                <span>{course.students} students</span>
              </div>
              <button className="mt-4 w-full btn-primary">
                Enroll Now
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Courses; 