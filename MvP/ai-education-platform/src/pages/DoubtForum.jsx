import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ChatBubbleLeftRightIcon,
  FireIcon,
  ClockIcon,
  UserCircleIcon,
  PaperAirplaneIcon,
} from '@heroicons/react/24/outline';

const questions = [
  {
    id: 1,
    title: 'How does gradient descent work in machine learning?',
    content:
      'I'm having trouble understanding the concept of gradient descent. Could someone explain it in simple terms?',
    author: 'John Doe',
    timestamp: '2 hours ago',
    votes: 15,
    answers: 3,
    tags: ['Machine Learning', 'AI'],
  },
  {
    id: 2,
    title: 'Best practices for React state management',
    content:
      'What are the recommended approaches for managing state in a large React application?',
    author: 'Jane Smith',
    timestamp: '5 hours ago',
    votes: 8,
    answers: 2,
    tags: ['React', 'Web Development'],
  },
  {
    id: 3,
    title: 'Understanding neural networks',
    content:
      'Can someone explain the basic structure and components of a neural network?',
    author: 'Mike Johnson',
    timestamp: '1 day ago',
    votes: 12,
    answers: 4,
    tags: ['AI', 'Deep Learning'],
  },
];

const DoubtForum = () => {
  const [newQuestion, setNewQuestion] = useState({
    title: '',
    content: '',
    tags: '',
  });
  const [isAsking, setIsAsking] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle question submission
    console.log('New question:', newQuestion);
    setIsAsking(false);
    setNewQuestion({ title: '', content: '', tags: '' });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Doubt Forum
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            Ask questions and get help from the community
          </p>
        </motion.div>

        {/* Ask Question Button */}
        <div className="mb-8">
          <button
            onClick={() => setIsAsking(true)}
            className="btn-primary flex items-center"
          >
            <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
            Ask a Question
          </button>
        </div>

        {/* Ask Question Form */}
        {isAsking && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-effect p-6 rounded-2xl mb-8"
          >
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              Ask Your Question
            </h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label
                  htmlFor="title"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >
                  Title
                </label>
                <input
                  type="text"
                  id="title"
                  value={newQuestion.title}
                  onChange={(e) =>
                    setNewQuestion({ ...newQuestion, title: e.target.value })
                  }
                  className="w-full px-4 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-primary focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label
                  htmlFor="content"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >
                  Content
                </label>
                <textarea
                  id="content"
                  value={newQuestion.content}
                  onChange={(e) =>
                    setNewQuestion({ ...newQuestion, content: e.target.value })
                  }
                  rows={4}
                  className="w-full px-4 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-primary focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label
                  htmlFor="tags"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  id="tags"
                  value={newQuestion.tags}
                  onChange={(e) =>
                    setNewQuestion({ ...newQuestion, tags: e.target.value })
                  }
                  className="w-full px-4 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="e.g., Machine Learning, AI"
                />
              </div>
              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => setIsAsking(false)}
                  className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary flex items-center"
                >
                  <PaperAirplaneIcon className="w-5 h-5 mr-2" />
                  Post Question
                </button>
              </div>
            </form>
          </motion.div>
        )}

        {/* Questions List */}
        <div className="space-y-6">
          {questions.map((question) => (
            <motion.div
              key={question.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-effect p-6 rounded-2xl"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <UserCircleIcon className="w-10 h-10 text-gray-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                    {question.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    {question.content}
                  </p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {question.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center space-x-6 text-sm text-gray-600 dark:text-gray-400">
                    <div className="flex items-center">
                      <FireIcon className="w-4 h-4 mr-1" />
                      {question.votes} votes
                    </div>
                    <div className="flex items-center">
                      <ChatBubbleLeftRightIcon className="w-4 h-4 mr-1" />
                      {question.answers} answers
                    </div>
                    <div className="flex items-center">
                      <ClockIcon className="w-4 h-4 mr-1" />
                      {question.timestamp}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DoubtForum; 