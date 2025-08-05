# import os
# import json
# import asyncio
# from typing import List, Dict, Any, Optional
# import logging
# from datetime import datetime
# from pathlib import Path

# import uvicorn
# from fastapi import FastAPI, HTTPException, Request, Query
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, Field
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

# # ==============================================================================
# # LOGGING CONFIGURATION
# # ==============================================================================
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # ==============================================================================
# # PYDANTIC MODELS
# # ==============================================================================

# class FileNode(BaseModel):
#     name: str
#     type: str  # 'file' or 'folder'
#     path: str
#     children: Optional[List['FileNode']] = None

# class ProjectDocumentation(BaseModel):
#     overview: str
#     techStack: List[str]

# class Project(BaseModel):
#     id: str
#     name: str
#     description: str
#     fileStructure: List[FileNode]
#     documentation: Optional[ProjectDocumentation] = None
#     codeFiles: Optional[Dict[str, str]] = None

# class ProjectUpdateRequest(BaseModel):
#     name: Optional[str] = None
#     description: Optional[str] = None
#     documentation: Optional[ProjectDocumentation] = None

# class CodeFileRequest(BaseModel):
#     path: str
#     content: str

# class ErrorResponse(BaseModel):
#     error: str
#     details: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.now)

# # ==============================================================================
# # DATA MANAGEMENT SERVICE
# # ==============================================================================

# class ProjectService:
#     def __init__(self):
#         self.projects: Dict[str, Project] = {}
#         self._initialize_mock_data()
    
#     def _initialize_mock_data(self):
#         """Initialize with mock project data that matches the frontend"""
#         mock_project = Project(
#             id="1",
#             name="E-commerce Platform",
#             description="Modern React-based e-commerce solution",
#             fileStructure=[
#                 FileNode(
#                     name="src",
#                     type="folder",
#                     path="src",
#                     children=[
#                         FileNode(
#                             name="components",
#                             type="folder",
#                             path="src/components",
#                             children=[
#                                 FileNode(name="Header.tsx", type="file", path="src/components/Header.tsx"),
#                                 FileNode(name="Footer.tsx", type="file", path="src/components/Footer.tsx"),
#                                 FileNode(name="ProductCard.tsx", type="file", path="src/components/ProductCard.tsx"),
#                                 FileNode(name="Navigation.tsx", type="file", path="src/components/Navigation.tsx")
#                             ]
#                         ),
#                         FileNode(
#                             name="pages",
#                             type="folder",
#                             path="src/pages",
#                             children=[
#                                 FileNode(name="Home.tsx", type="file", path="src/pages/Home.tsx"),
#                                 FileNode(name="Product.tsx", type="file", path="src/pages/Product.tsx"),
#                                 FileNode(name="Cart.tsx", type="file", path="src/pages/Cart.tsx"),
#                                 FileNode(name="Checkout.tsx", type="file", path="src/pages/Checkout.tsx")
#                             ]
#                         ),
#                         FileNode(
#                             name="hooks",
#                             type="folder",
#                             path="src/hooks",
#                             children=[
#                                 FileNode(name="useCart.ts", type="file", path="src/hooks/useCart.ts"),
#                                 FileNode(name="useAuth.ts", type="file", path="src/hooks/useAuth.ts")
#                             ]
#                         ),
#                         FileNode(
#                             name="utils",
#                             type="folder",
#                             path="src/utils",
#                             children=[
#                                 FileNode(name="api.ts", type="file", path="src/utils/api.ts"),
#                                 FileNode(name="helpers.ts", type="file", path="src/utils/helpers.ts")
#                             ]
#                         ),
#                         FileNode(name="App.tsx", type="file", path="src/App.tsx"),
#                         FileNode(name="index.tsx", type="file", path="src/index.tsx"),
#                         FileNode(name="App.css", type="file", path="src/App.css")
#                     ]
#                 ),
#                 FileNode(name="package.json", type="file", path="package.json"),
#                 FileNode(name="tsconfig.json", type="file", path="tsconfig.json"),
#                 FileNode(name="README.md", type="file", path="README.md"),
#                 FileNode(name=".gitignore", type="file", path=".gitignore")
#             ],
#             documentation=ProjectDocumentation(
#                 overview="A comprehensive e-commerce platform built with modern React patterns, featuring responsive design, state management with Zustand, and robust API integration for a seamless user experience. The platform includes user authentication, product catalog, shopping cart functionality, and secure checkout process.",
#                 techStack=["React", "TypeScript", "Tailwind CSS", "Zustand", "React Router", "Vite", "React Flow", "Axios", "Jest", "React Testing Library"]
#             ),
#             codeFiles={
#                 "src/App.tsx": '''import React from 'react';
# import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
# import { Header } from './components/Header';
# import { Footer } from './components/Footer';
# import { Home } from './pages/Home';
# import { Product } from './pages/Product';
# import { Cart } from './pages/Cart';
# import { Checkout } from './pages/Checkout';
# import './App.css';

# function App() {
#   return (
#     <Router>
#       <div className="min-h-screen flex flex-col">
#         <Header />
#         <main className="flex-1">
#           <Routes>
#             <Route path="/" element={<Home />} />
#             <Route path="/product/:id" element={<Product />} />
#             <Route path="/cart" element={<Cart />} />
#             <Route path="/checkout" element={<Checkout />} />
#           </Routes>
#         </main>
#         <Footer />
#       </div>
#     </Router>
#   );
# }

# export default App;''',

#                 "src/components/Header.tsx": '''import React from 'react';
# import { Link } from 'react-router-dom';
# import { ShoppingCart, User, Search } from 'lucide-react';
# import { useCart } from '../hooks/useCart';

# export const Header: React.FC = () => {
#   const { itemCount } = useCart();

#   return (
#     <header className="bg-white shadow-md">
#       <div className="container mx-auto px-4 py-4">
#         <div className="flex items-center justify-between">
#           <Link to="/" className="text-2xl font-bold text-gray-800">
#             ShopHub
#           </Link>
          
#           <div className="flex-1 max-w-md mx-8">
#             <div className="relative">
#               <input
#                 type="text"
#                 placeholder="Search products..."
#                 className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
#               />
#               <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
#             </div>
#           </div>
          
#           <div className="flex items-center space-x-4">
#             <button className="p-2 text-gray-600 hover:text-blue-600">
#               <User className="h-6 w-6" />
#             </button>
#             <Link to="/cart" className="relative p-2 text-gray-600 hover:text-blue-600">
#               <ShoppingCart className="h-6 w-6" />
#               {itemCount > 0 && (
#                 <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
#                   {itemCount}
#                 </span>
#               )}
#             </Link>
#           </div>
#         </div>
#       </div>
#     </header>
#   );
# };''',

#                 "src/components/Footer.tsx": '''import React from 'react';
# import { Link } from 'react-router-dom';

# export const Footer: React.FC = () => {
#   return (
#     <footer className="bg-gray-800 text-white">
#       <div className="container mx-auto px-4 py-8">
#         <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
#           <div>
#             <h3 className="text-lg font-semibold mb-4">ShopHub</h3>
#             <p className="text-gray-400">
#               Your one-stop destination for quality products and exceptional service.
#             </p>
#           </div>
          
#           <div>
#             <h4 className="text-md font-semibold mb-4">Quick Links</h4>
#             <ul className="space-y-2">
#               <li><Link to="/" className="text-gray-400 hover:text-white">Home</Link></li>
#               <li><Link to="/products" className="text-gray-400 hover:text-white">Products</Link></li>
#               <li><Link to="/about" className="text-gray-400 hover:text-white">About</Link></li>
#               <li><Link to="/contact" className="text-gray-400 hover:text-white">Contact</Link></li>
#             </ul>
#           </div>
          
#           <div>
#             <h4 className="text-md font-semibold mb-4">Customer Service</h4>
#             <ul className="space-y-2">
#               <li><Link to="/help" className="text-gray-400 hover:text-white">Help Center</Link></li>
#               <li><Link to="/returns" className="text-gray-400 hover:text-white">Returns</Link></li>
#               <li><Link to="/shipping" className="text-gray-400 hover:text-white">Shipping Info</Link></li>
#             </ul>
#           </div>
          
#           <div>
#             <h4 className="text-md font-semibold mb-4">Connect</h4>
#             <ul className="space-y-2">
#               <li><a href="#" className="text-gray-400 hover:text-white">Facebook</a></li>
#               <li><a href="#" className="text-gray-400 hover:text-white">Twitter</a></li>
#               <li><a href="#" className="text-gray-400 hover:text-white">Instagram</a></li>
#             </ul>
#           </div>
#         </div>
        
#         <div className="border-t border-gray-700 mt-8 pt-6 text-center text-gray-400">
#           <p>&copy; 2024 ShopHub. All rights reserved.</p>
#         </div>
#       </div>
#     </footer>
#   );
# };''',

#                 "src/pages/Home.tsx": '''import React, { useEffect, useState } from 'react';
# import { ProductCard } from '../components/ProductCard';
# import { Product } from '../types';
# import { api } from '../utils/api';

# export const Home: React.FC = () => {
#   const [products, setProducts] = useState<Product[]>([]);
#   const [loading, setLoading] = useState(true);

#   useEffect(() => {
#     const fetchProducts = async () => {
#       try {
#         const response = await api.get('/products');
#         setProducts(response.data);
#       } catch (error) {
#         console.error('Failed to fetch products:', error);
#       } finally {
#         setLoading(false);
#       }
#     };

#     fetchProducts();
#   }, []);

#   if (loading) {
#     return (
#       <div className="container mx-auto px-4 py-8">
#         <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
#           {[...Array(8)].map((_, i) => (
#             <div key={i} className="bg-gray-200 animate-pulse rounded-lg h-64"></div>
#           ))}
#         </div>
#       </div>
#     );
#   }

#   return (
#     <div className="container mx-auto px-4 py-8">
#       <section className="mb-12">
#         <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8 text-center">
#           <h1 className="text-4xl font-bold mb-4">Welcome to ShopHub</h1>
#           <p className="text-xl">Discover amazing products at unbeatable prices</p>
#         </div>
#       </section>

#       <section>
#         <h2 className="text-2xl font-bold mb-6">Featured Products</h2>
#         <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
#           {products.map((product) => (
#             <ProductCard key={product.id} product={product} />
#           ))}
#         </div>
#       </section>
#     </div>
#   );
# };''',

#                 "src/hooks/useCart.ts": '''import { create } from 'zustand';
# import { persist } from 'zustand/middleware';

# interface CartItem {
#   id: string;
#   name: string;
#   price: number;
#   quantity: number;
#   image: string;
# }

# interface CartStore {
#   items: CartItem[];
#   itemCount: number;
#   total: number;
#   addItem: (item: Omit<CartItem, 'quantity'>) => void;
#   removeItem: (id: string) => void;
#   updateQuantity: (id: string, quantity: number) => void;
#   clearCart: () => void;
# }

# export const useCart = create<CartStore>()(
#   persist(
#     (set, get) => ({
#       items: [],
#       itemCount: 0,
#       total: 0,
      
#       addItem: (item) => {
#         const { items } = get();
#         const existingItem = items.find(i => i.id === item.id);
        
#         if (existingItem) {
#           set({
#             items: items.map(i => 
#               i.id === item.id 
#                 ? { ...i, quantity: i.quantity + 1 }
#                 : i
#             )
#           });
#         } else {
#           set({
#             items: [...items, { ...item, quantity: 1 }]
#           });
#         }
        
#         // Update derived state
#         const newItems = get().items;
#         set({
#           itemCount: newItems.reduce((sum, item) => sum + item.quantity, 0),
#           total: newItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
#         });
#       },
      
#       removeItem: (id) => {
#         const { items } = get();
#         const newItems = items.filter(item => item.id !== id);
        
#         set({
#           items: newItems,
#           itemCount: newItems.reduce((sum, item) => sum + item.quantity, 0),
#           total: newItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
#         });
#       },
      
#       updateQuantity: (id, quantity) => {
#         if (quantity <= 0) {
#           get().removeItem(id);
#           return;
#         }
        
#         const { items } = get();
#         const newItems = items.map(item => 
#           item.id === id ? { ...item, quantity } : item
#         );
        
#         set({
#           items: newItems,
#           itemCount: newItems.reduce((sum, item) => sum + item.quantity, 0),
#           total: newItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
#         });
#       },
      
#       clearCart: () => {
#         set({
#           items: [],
#           itemCount: 0,
#           total: 0
#         });
#       }
#     }),
#     {
#       name: 'cart-storage'
#     }
#   )
# );''',

#                 "package.json": '''{
#   "name": "ecommerce-platform",
#   "private": true,
#   "version": "0.0.0",
#   "type": "module",
#   "scripts": {
#     "dev": "vite",
#     "build": "tsc && vite build",
#     "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
#     "preview": "vite preview",
#     "test": "jest"
#   },
#   "dependencies": {
#     "react": "^18.2.0",
#     "react-dom": "^18.2.0",
#     "react-router-dom": "^6.8.1",
#     "zustand": "^4.3.6",
#     "axios": "^1.3.4",
#     "lucide-react": "^0.263.1",
#     "reactflow": "^11.7.0"
#   },
#   "devDependencies": {
#     "@types/react": "^18.0.28",
#     "@types/react-dom": "^18.0.11",
#     "@typescript-eslint/eslint-plugin": "^5.57.1",
#     "@typescript-eslint/parser": "^5.57.1",
#     "@vitejs/plugin-react": "^4.0.0",
#     "autoprefixer": "^10.4.14",
#     "eslint": "^8.38.0",
#     "eslint-plugin-react-hooks": "^4.6.0",
#     "eslint-plugin-react-refresh": "^0.3.4",
#     "postcss": "^8.4.21",
#     "tailwindcss": "^3.2.7",
#     "typescript": "^5.0.2",
#     "vite": "^4.3.2",
#     "jest": "^29.5.0",
#     "@testing-library/react": "^14.0.0",
#     "@testing-library/jest-dom": "^5.16.5"
#   }
# }''',

#                 "README.md": '''# E-commerce Platform

# A modern, responsive e-commerce platform built with React, TypeScript, and Tailwind CSS.

# ## Features

# - 🛍️ Product catalog with search and filtering
# - 🛒 Shopping cart with persistent storage
# - 👤 User authentication and profiles
# - 💳 Secure checkout process
# - 📱 Fully responsive design
# - ⚡ Fast performance with Vite
# - 🧪 Comprehensive testing suite

# ## Tech Stack

# - **Frontend**: React 18, TypeScript, Tailwind CSS
# - **State Management**: Zustand
# - **Routing**: React Router
# - **Icons**: Lucide React
# - **Build Tool**: Vite
# - **Testing**: Jest, React Testing Library

# ## Getting Started

# 1. Clone the repository
# 2. Install dependencies: `npm install`
# 3. Start development server: `npm run dev`
# 4. Open http://localhost:3000

# ## Project Structure

# ```
# src/
# ├── components/     # Reusable UI components
# ├── pages/         # Route components
# ├── hooks/         # Custom React hooks
# ├── utils/         # Utility functions
# ├── types/         # TypeScript type definitions
# ├── App.tsx        # Main application component
# └── index.tsx      # Application entry point
# ```

# ## Available Scripts

# - `npm run dev` - Start development server
# - `npm run build` - Build for production
# - `npm run test` - Run test suite
# - `npm run lint` - Run ESLint

# ## Contributing

# 1. Fork the repository
# 2. Create a feature branch
# 3. Make your changes
# 4. Add tests
# 5. Submit a pull request
# '''
#             }
#         )
        
#         self.projects["1"] = mock_project

#     def get_project(self, project_id: str) -> Optional[Project]:
#         """Get project by ID"""
#         return self.projects.get(project_id)

#     def get_all_projects(self) -> List[Project]:
#         """Get all projects"""
#         return list(self.projects.values())

#     def update_project(self, project_id: str, updates: ProjectUpdateRequest) -> Optional[Project]:
#         """Update project details"""
#         if project_id not in self.projects:
#             return None
        
#         project = self.projects[project_id]
        
#         if updates.name:
#             project.name = updates.name
#         if updates.description:
#             project.description = updates.description
#         if updates.documentation:
#             project.documentation = updates.documentation
        
#         return project

#     def get_file_content(self, project_id: str, file_path: str) -> Optional[str]:
#         """Get file content by path"""
#         project = self.get_project(project_id)
#         if not project or not project.codeFiles:
#             return None
        
#         return project.codeFiles.get(file_path)

#     def update_file_content(self, project_id: str, file_path: str, content: str) -> bool:
#         """Update file content"""
#         project = self.get_project(project_id)
#         if not project:
#             return False
        
#         if not project.codeFiles:
#             project.codeFiles = {}
        
#         project.codeFiles[file_path] = content
#         return True

#     def get_file_explanation(self, project_id: str, file_path: str) -> str:
#         """Generate explanation for a file"""
#         explanations = {
#             "src/App.tsx": "Main application component that sets up routing and layout structure with header, main content area, and footer.",
#             "src/components/Header.tsx": "Navigation header component featuring search functionality, user account access, and shopping cart with item count indicator.",
#             "src/components/Footer.tsx": "Footer component with organized links for navigation, customer service, and social media connections.",
#             "src/pages/Home.tsx": "Home page component displaying featured products with loading states and responsive grid layout for optimal user experience.",
#             "src/hooks/useCart.ts": "Custom Zustand hook managing shopping cart state with persistent storage, including add/remove items and quantity updates.",
#             "package.json": "Project configuration file defining dependencies, scripts, and metadata for the React-based e-commerce platform.",
#             "README.md": "Project documentation providing setup instructions, feature overview, and development guidelines for contributors."
#         }
        
#         return explanations.get(file_path, f"This file contains the implementation for {file_path}. It's part of the e-commerce platform's architecture and contributes to the overall functionality of the application.")

# # ==============================================================================
# # FASTAPI APPLICATION
# # ==============================================================================

# app = FastAPI(
#     title="Workspace Backend API",
#     description="Backend API for the workspace frontend application",
#     version="1.0.0"
# )

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize services
# project_service = ProjectService()

# # ==============================================================================
# # API ENDPOINTS
# # ==============================================================================

# @app.get("/")
# async def read_root():
#     return {
#         "status": "Workspace Backend API is running",
#         "version": "1.0.0",
#         "timestamp": datetime.now().isoformat()
#     }

# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy", 
#         "timestamp": datetime.now().isoformat(),
#         "projects_count": len(project_service.projects)
#     }

# @app.get("/api/projects", response_model=List[Project])
# async def get_projects():
#     """Get all projects"""
#     try:
#         projects = project_service.get_all_projects()
#         return projects
#     except Exception as e:
#         logger.error(f"Error fetching projects: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/projects/{project_id}", response_model=Project)
# async def get_project(project_id: str):
#     """Get specific project by ID"""
#     try:
#         project = project_service.get_project(project_id)
#         if not project:
#             raise HTTPException(status_code=404, detail="Project not found")
#         return project
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching project {project_id}: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.put("/api/projects/{project_id}", response_model=Project)
# async def update_project(project_id: str, updates: ProjectUpdateRequest):
#     """Update project details"""
#     try:
#         project = project_service.update_project(project_id, updates)
#         if not project:
#             raise HTTPException(status_code=404, detail="Project not found")
#         return project
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error updating project {project_id}: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/projects/{project_id}/files/{file_path:path}")
# async def get_file_content(project_id: str, file_path: str):
#     """Get file content by path"""
#     try:
#         content = project_service.get_file_content(project_id, file_path)
#         if content is None:
#             raise HTTPException(status_code=404, detail="File not found")
        
#         explanation = project_service.get_file_explanation(project_id, file_path)
        
#         return {
#             "file_path": file_path,
#             "content": content,
#             "explanation": explanation,
#             "last_modified": datetime.now().isoformat()
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching file {file_path} from project {project_id}: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.put("/api/projects/{project_id}/files/{file_path:path}")
# async def update_file_content(project_id: str, file_path: str, request: CodeFileRequest):
#     """Update file content"""
#     try:
#         success = project_service.update_file_content(project_id, file_path, request.content)
#         if not success:
#             raise HTTPException(status_code=404, detail="Project not found")
        
#         return {
#             "message": "File updated successfully",
#             "file_path": file_path,
#             "timestamp": datetime.now().isoformat()
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error updating file {file_path} in project {project_id}: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/projects/{project_id}/file-tree")
# async def get_file_tree(project_id: str):
#     """Get project file tree structure"""
#     try:
#         project = project_service.get_project(project_id)
#         if not project:
#             raise HTTPException(status_code=404, detail="Project not found")
        
#         return {
#             "project_id": project_id,
#             "file_structure": project.fileStructure,
#             "timestamp": datetime.now().isoformat()
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching file tree for project {project_id}: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/projects/{project_id}/documentation")
# async def get_project_documentation(project_id: str):
#     """Get project documentation"""
#     try:
#         project = project_service.get_project(project_id)
#         if not project:
#             raise HTTPException(status_code=404, detail="Project not found")
        
#         return {
#             "project_id": project_id,
#             "documentation": project.documentation,
#             "timestamp": datetime.now().isoformat()
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching documentation for project {project_id}: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/projects/{project_id}/stats")
# async def get_project_stats(project_id: str):
#     """Get project statistics"""
#     try:
#         project = project_service.get_project(project_id)
#         if not project:
#             raise HTTPException(status_code=404, detail="Project not found")
        
#         def count_files(nodes: List[FileNode]) -> Dict[str, int]:
#             stats = {"files": 0, "folders": 0}
#             for node in nodes:
#                 if node.type == "file":
#                     stats["files"] += 1
#                 else:
#                     stats["folders"] += 1
#                     if node.children:
#                         child_stats = count_files(node.children)
#                         stats["files"] += child_stats["files"]
#                         stats["folders"] += child_stats["folders"]
#             return stats
        
#         file_stats = count_files(project.fileStructure)
#         code_files_count = len(project.codeFiles) if project.codeFiles else 0
#         tech_stack_count = len(project.documentation.techStack) if project.documentation else 0
        
#         return {
#             "project_id": project_id,
#             "stats": {
#                 "total_files": file_stats["files"],
#                 "total_folders": file_stats["folders"],
#                 "code_files_with_content": code_files_count,
#                 "tech_stack_items": tech_stack_count,
#                 "has_documentation": project.documentation is not None
#             },
#             "timestamp": datetime.now().isoformat()
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching stats for project {project_id}: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# # ==============================================================================
# # ERROR HANDLERS
# # ==============================================================================

# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "error": exc.detail,
#             "status_code": exc.status_code,
#             "timestamp": datetime.now().isoformat()
#         }
#     )

# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     logger.error(f"Unhandled exception: {exc}")
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "Internal server error",
#             "details": str(exc),
#             "timestamp": datetime.now().isoformat()
#         }
#     )

# if __name__ == "__main__":
#     uvicorn.run(
#         app, 
#         host="0.0.0.0", 
#         port=8000,
#         log_level="info",
# #         reload=True
# import os
# import json
# import asyncio
# import re
# from typing import List, Dict, Any, TypedDict, Optional
# import logging
# from datetime import datetime

# import uvicorn
# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException, Request
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel, Field
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware

# from langchain.tools import tool
# from langchain_core.messages import HumanMessage, BaseMessage
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langgraph.graph import StateGraph, END

# # ==============================================================================
# # 1. LOGGING CONFIGURATION
# # ==============================================================================
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # ==============================================================================
# # 2. INITIAL SETUP & CONFIGURATION
# # ==============================================================================
# load_dotenv()

# # --- Enhanced Pydantic Models ---
# class UserProfile(BaseModel):
#     name: str = Field(default="Default User", description="User's name")
#     experience: str = Field(default="Intermediate", description="Programming experience level")
#     preferences: Dict[str, Any] = Field(default_factory=dict, description="Additional preferences")

# class BlueprintRequest(BaseModel):
#     initial_idea: str = Field(..., min_length=10, description="The initial project idea")
#     user_profile: UserProfile = Field(default_factory=UserProfile)
#     user_answers: List[str] = Field(default_factory=list, description="Answers to clarifying questions")

# class ErrorResponse(BaseModel):
#     error: str
#     details: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.now)

# # --- Enhanced Agent State Definition ---
# class AgentState(TypedDict):
#     initial_idea: str
#     user_profile: Dict[str, Any]
#     user_answers: List[str]
#     full_context: str
#     clarifying_questions: List[str]
#     tech_stack: Dict[str, Any]
#     flowchart: Dict[str, Any]
#     project_overview: str
#     files: List[Dict[str, str]]
#     processing_status: str
#     error_count: int

# # ==============================================================================
# # 3. ENHANCED LLM SERVICE WITH BETTER ERROR HANDLING
# # ==============================================================================
# class LLMService:
#     _models_cache = {}
#     _api_keys = [
#         "GEMINI_API_KEY_1", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3",
#         "GEMINI_API_KEY_4", "GEMINI_API_KEY_5", "GEMINI_API_KEY_6"
#     ]
    
#     @classmethod
#     def get_model(cls, api_key_name: str, retry_count: int = 0) -> ChatGoogleGenerativeAI:
#         """Get model with fallback to other API keys if one fails"""
#         if api_key_name in cls._models_cache:
#             return cls._models_cache[api_key_name]
        
#         # Try primary key first, then fallback to others
#         keys_to_try = [api_key_name] + [k for k in cls._api_keys if k != api_key_name]
        
#         for key in keys_to_try:
#             api_key = os.getenv(key)
#             if not api_key:
#                 continue
                
#             try:
#                 model = ChatGoogleGenerativeAI(
#                     model="gemini-1.5-flash",
#                     google_api_key=api_key,
#                     temperature=0.1,
#                     timeout=120,
#                     max_retries=2
#                 )
#                 cls._models_cache[api_key_name] = model
#                 logger.info(f"Successfully initialized model with {key}")
#                 return model
#             except Exception as e:
#                 logger.warning(f"Failed to initialize model with {key}: {e}")
#                 continue
        
#         raise ValueError(f"No valid API keys found. Please check your .env file.")
    
#     @classmethod
#     def extract_json(cls, text: str) -> str:
#         """Enhanced JSON extraction with better error handling"""
#         try:
#             # First try to find JSON in code blocks
#             json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
#             if json_match:
#                 return json_match.group(1)
            
#             # Then try to find any JSON object
#             json_match = re.search(r'\{.*\}', text, re.DOTALL)
#             if json_match:
#                 # Validate it's proper JSON
#                 json.loads(json_match.group(0))
#                 return json_match.group(0)
            
#             logger.warning("No valid JSON found in response")
#             return "{}"
#         except json.JSONDecodeError as e:
#             logger.error(f"JSON decode error: {e}")
#             return "{}"
#         except Exception as e:
#             logger.error(f"Unexpected error in JSON extraction: {e}")
#             return "{}"

# # ==============================================================================
# # 4. ENHANCED GENERATION FUNCTIONS
# # ==============================================================================
# class BlueprintGenerator:
    
#     @staticmethod
#     async def generate_clarifying_questions(initial_idea: str, user_profile: dict) -> List[str]:
#         """Generate clarifying questions with better prompting"""
#         try:
#             model = LLMService.get_model("GEMINI_API_KEY_1")
            
#             prompt = f"""
#             You are an expert requirements analyst. Based on this project idea: "{initial_idea}"
#             and user profile: {json.dumps(user_profile)}, generate exactly 3 concise, specific clarifying questions.
            
#             Focus on:
#             1. Core functionality and features
#             2. Target audience and use cases
#             3. Technical constraints or preferences
            
#             Respond with ONLY a valid JSON array of strings. Example format:
#             ["What specific features should the app include?", "Who is your target audience?", "Do you have any preferred technologies?"]
#             """
            
#             response = model.invoke(prompt).content
#             questions_json = LLMService.extract_json(response)
#             questions = json.loads(questions_json)
            
#             # Validate and provide fallback
#             if not isinstance(questions, list) or len(questions) != 3:
#                 return [
#                     "What are the main features you want in your application?",
#                     "Who is your target audience for this project?",
#                     "Do you have any specific technical requirements or constraints?"
#                 ]
            
#             return questions
            
#         except Exception as e:
#             logger.error(f"Error generating questions: {e}")
#             return [
#                 "What are the core functionalities you need?",
#                 "What type of users will use this application?", 
#                 "Are there any specific technologies you prefer?"
#             ]
    
#     @staticmethod
#     async def generate_tech_stack(full_context: str) -> Dict[str, Any]:
#         """Generate tech stack with enhanced reasoning"""
#         try:
#             model = LLMService.get_model("GEMINI_API_KEY_2")
            
#             prompt = f"""
#             You are a senior software architect. Analyze this project context and recommend an optimal tech stack:
            
#             Context: {full_context}
            
#             Consider:
#             - Project requirements and complexity
#             - Scalability needs
#             - Development speed vs performance
#             - Team experience level
#             - Modern best practices
            
#             Respond with ONLY a valid JSON object with this exact structure:
#             {{
#                 "stack": {{
#                     "frontend": "technology name",
#                     "backend": "technology name", 
#                     "database": "technology name",
#                     "deployment": "platform name",
#                     "additional_tools": ["tool1", "tool2"]
#                 }},
#                 "justification": "detailed explanation of choices",
#                 "alternatives": {{
#                     "frontend": ["alternative1", "alternative2"],
#                     "backend": ["alternative1", "alternative2"]
#                 }}
#             }}
#             """
            
#             response = model.invoke(prompt).content
#             tech_stack_json = LLMService.extract_json(response)
#             tech_stack = json.loads(tech_stack_json)
            
#             # Validate structure
#             if "stack" not in tech_stack:
#                 tech_stack = {
#                     "stack": {
#                         "frontend": "React",
#                         "backend": "Node.js",
#                         "database": "PostgreSQL",
#                         "deployment": "Vercel/Heroku"
#                     },
#                     "justification": "Default modern web stack for rapid development",
#                     "alternatives": {"frontend": ["Vue.js", "Angular"], "backend": ["Python", "Java"]}
#                 }
            
#             return tech_stack
            
#         except Exception as e:
#             logger.error(f"Error generating tech stack: {e}")
#             return {
#                 "stack": {"frontend": "React", "backend": "Node.js", "database": "MongoDB"},
#                 "justification": f"Error occurred during generation: {e}",
#                 "alternatives": {}
#             }
    
#     @staticmethod
#     async def generate_flowchart(full_context: str, tech_stack: dict) -> Dict[str, Any]:
#         """Generate enhanced flowchart with proper React Flow format"""
#         try:
#             model = LLMService.get_model("GEMINI_API_KEY_3")
            
#             prompt = f"""
# You are an expert UI/UX designer specializing in modern system architecture diagrams. 
# Create a visually stunning, React Flow compatible flowchart for this project:

# Context: {full_context}
# Tech Stack: {json.dumps(tech_stack)}

# DESIGN REQUIREMENTS:
# 1. Use a modern, clean aesthetic with proper spacing and alignment
# 2. Implement a logical flow from left to right or top to bottom
# 3. Use appropriate node types:
#    - 'input': User entry points, data sources (style with blue/green theme)
#    - 'output': Final results, displays, notifications (style with purple/pink theme)
#    - 'default': Processing, logic, APIs, databases (style with gray/blue theme)
#    - 'group': Use for grouping related components

# 4. MODERN STYLING for each node:
#    - Add gradient backgrounds
#    - Use rounded corners (borderRadius: 12)
#    - Add subtle shadows
#    - Use modern color palette
#    - Include proper padding and typography

# 5. EDGE STYLING:
#    - Use 'smoothstep' or 'step' edges for clean connections
#    - All edges must be animated: "animated": true
#    - Use different colors for different types of data flow
#    - Add labels to edges where helpful

# 6. LAYOUT OPTIMIZATION:
#    - Ensure proper spacing between nodes (minimum 150px)
#    - Create logical groupings
#    - Use hierarchical positioning
#    - Consider mobile responsiveness

# 7. ADVANCED FEATURES:
#    - Add meaningful icons or emojis in labels
#    - Use descriptive, concise labels
#    - Include data flow indicators
#    - Add connection points for complex flows

# EXAMPLE MODERN STYLING:
# {{
#   "nodes": [
#     {{
#       "id": "user-input",
#       "type": "input",
#       "position": {{"x": 50, "y": 100}},
#       "data": {{
#         "label": "👤 User Interface"
#       }},
#       "style": {{
#         "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
#         "color": "white",
#         "border": "none",
#         "borderRadius": 12,
#         "padding": "10px 15px",
#         "fontSize": "14px",
#         "fontWeight": "600",
#         "boxShadow": "0 4px 15px rgba(102, 126, 234, 0.3)",
#         "minWidth": "120px",
#         "textAlign": "center"
#       }}
#     }},
#     {{
#       "id": "api-process",
#       "type": "default",
#       "position": {{"x": 300, "y": 100}},
#       "data": {{
#         "label": "⚡ API Processing"
#       }},
#       "style": {{
#         "background": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
#         "color": "white",
#         "border": "none",
#         "borderRadius": 12,
#         "padding": "10px 15px",
#         "fontSize": "14px",
#         "fontWeight": "600",
#         "boxShadow": "0 4px 15px rgba(240, 147, 251, 0.3)",
#         "minWidth": "140px",
#         "textAlign": "center"
#       }}
#     }},
#     {{
#       "id": "data-output",
#       "type": "output", 
#       "position": {{"x": 550, "y": 100}},
#       "data": {{
#         "label": "📊 Results Display"
#       }},
#       "style": {{
#         "background": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
#         "color": "white",
#         "border": "none",
#         "borderRadius": 12,
#         "padding": "10px 15px",
#         "fontSize": "14px",
#         "fontWeight": "600",
#         "boxShadow": "0 4px 15px rgba(79, 172, 254, 0.3)",
#         "minWidth": "130px",
#         "textAlign": "center"
#       }}
#     }}
#   ],
#   "edges": [
#     {{
#       "id": "edge-input-api",
#       "source": "user-input",
#       "target": "api-process",
#       "type": "smoothstep",
#       "animated": true,
#       "style": {{
#         "stroke": "#667eea",
#         "strokeWidth": 3
#       }},
#       "label": "Request",
#       "labelStyle": {{
#         "fontSize": "12px",
#         "fontWeight": "500",
#         "color": "#4a5568"
#       }}
#     }},
#     {{
#       "id": "edge-api-output",
#       "source": "api-process",
#       "target": "data-output", 
#       "type": "smoothstep",
#       "animated": true,
#       "style": {{
#         "stroke": "#f093fb",
#         "strokeWidth": 3
#       }},
#       "label": "Response",
#       "labelStyle": {{
#         "fontSize": "12px",
#         "fontWeight": "500",
#         "color": "#4a5568"
#       }}
#     }}
#   ]
# }}

# Create a comprehensive flowchart that represents the entire system architecture with modern styling.
# Respond with ONLY a valid JSON object in the exact React Flow format shown above.
# """
            
#             response = model.invoke(prompt).content
#             flowchart_json = LLMService.extract_json(response)
#             flowchart = json.loads(flowchart_json)
            
#             # Validate and ensure proper structure
#             if "nodes" not in flowchart or "edges" not in flowchart:
#                 flowchart = {
#                     "nodes": [
#                         {"id": "1", "position": {"x": 100, "y": 100}, "data": {"label": "User Interface"}},
#                         {"id": "2", "position": {"x": 300, "y": 100}, "data": {"label": "Backend API"}},
#                         {"id": "3", "position": {"x": 500, "y": 100}, "data": {"label": "Database"}}
#                     ],
#                     "edges": [
#                         {"id": "e1-2", "source": "1", "target": "2", "type": "smoothstep"},
#                         {"id": "e2-3", "source": "2", "target": "3", "type": "smoothstep"}
#                     ]
#                 }
            
#             return flowchart
            
#         except Exception as e:
#             logger.error(f"Error generating flowchart: {e}")
#             return {
#                 "nodes": [{"id": "error", "position": {"x": 100, "y": 100}, "data": {"label": f"Error: {e}"}}],
#                 "edges": []
#             }
    
#     @staticmethod
#     async def generate_project_overview(full_context: str, tech_stack: dict, flowchart: dict) -> str:
#         """Generate comprehensive project overview"""
#         try:
#             model = LLMService.get_model("GEMINI_API_KEY_4")
            
#             prompt = f"""
#             You are a technical writer. Create a comprehensive project overview in Markdown format.
            
#             Context: {full_context}
#             Tech Stack: {json.dumps(tech_stack)}
#             Architecture: {len(flowchart.get('nodes', []))} components planned
            
#             Include these sections:
#             # Project Overview
#             ## Executive Summary
#             ## Key Features
#             ## Technical Architecture
#             ## Implementation Plan
#             ## Potential Challenges
#             ## Next Steps
            
#             Write in clear, professional language suitable for developers and stakeholders.
#             """
            
#             response = model.invoke(prompt).content
#             return response
            
#         except Exception as e:
#             logger.error(f"Error generating overview: {e}")
#             return f"# Project Overview\n\nError generating overview: {e}\n\nPlease try again."
    
#     @staticmethod
#     async def generate_project_files(full_context: str, tech_stack: dict, flowchart: dict) -> List[Dict[str, str]]:
#         """Generate project files with better structure"""
#         try:
#             # Determine files based on tech stack
#             stack_info = tech_stack.get("stack", {})
#             frontend = stack_info.get("frontend", "React").lower()
#             backend = stack_info.get("backend", "Node.js").lower()
            
#             files_to_generate = []
            
#             # Frontend files
#             if "react" in frontend:
#                 files_to_generate.extend([
#                     "src/App.js", "src/components/Header.js", "src/components/MainContent.js",
#                     "package.json", "src/index.js"
#                 ])
#             elif "vue" in frontend:
#                 files_to_generate.extend([
#                     "src/App.vue", "src/components/Header.vue", "package.json"
#                 ])
            
#             # Backend files
#             if "node" in backend or "express" in backend:
#                 files_to_generate.extend([
#                     "server.js", "routes/api.js", "models/index.js"
#                 ])
#             elif "python" in backend or "flask" in backend or "django" in backend:
#                 files_to_generate.extend([
#                     "app.py", "models.py", "requirements.txt"
#                 ])
            
#             # Generate each file
#             all_files = []
#             model = LLMService.get_model("GEMINI_API_KEY_5")
            
#             for file_name in files_to_generate[:6]:  # Limit to 6 files to avoid timeout
#                 try:
#                     code_prompt = f"""
#                     Generate complete, production-ready code for: {file_name}
                    
#                     Project Context: {full_context}
#                     Tech Stack: {json.dumps(stack_info)}
                    
#                     Requirements:
#                     - Include all necessary imports
#                     - Add proper error handling
#                     - Follow best practices
#                     - Add meaningful comments
#                     - Make it functional and complete
                    
#                     Return ONLY the code, no explanations or markdown.
#                     """
                    
#                     code_response = model.invoke(code_prompt).content
#                     code = code_response.strip().replace("```javascript", "").replace("```python", "").replace("```", "")
                    
#                     # Generate explanation
#                     explanation_model = LLMService.get_model("GEMINI_API_KEY_6")
#                     explanation_prompt = f"""
#                     Explain this code file in 2-3 sentences:
#                     File: {file_name}
#                     Code: {code[:500]}...
                    
#                     Focus on:
#                     - What this file does
#                     - How it fits in the project
#                     - Next steps for development
#                     """
                    
#                     explanation = explanation_model.invoke(explanation_prompt).content
                    
#                     all_files.append({
#                         "fileName": file_name,
#                         "code": code,
#                         "explanation": explanation
#                     })
                    
#                 except Exception as file_error:
#                     logger.error(f"Error generating {file_name}: {file_error}")
#                     all_files.append({
#                         "fileName": file_name,
#                         "code": f"// Error generating {file_name}: {file_error}",
#                         "explanation": f"Failed to generate this file due to: {file_error}"
#                     })
            
#             return all_files
            
#         except Exception as e:
#             logger.error(f"Error generating files: {e}")
#             return [{
#                 "fileName": "error.txt",
#                 "code": f"Error generating project files: {e}",
#                 "explanation": "An error occurred during file generation."
#             }]

# # ==============================================================================
# # 5. ENHANCED GRAPH DEFINITION
# # ==============================================================================
# def create_enhanced_agent_graph():
#     """Create enhanced agent graph with better error handling"""
    
#     async def requirements_node(state: AgentState):
#         logger.info("--- Running Requirements Expert ---")
#         try:
#             questions = await BlueprintGenerator.generate_clarifying_questions(
#                 state["initial_idea"], 
#                 state["user_profile"]
#             )
#             return {
#                 "clarifying_questions": questions,
#                 "processing_status": "questions_generated"
#             }
#         except Exception as e:
#             logger.error(f"Requirements node error: {e}")
#             return {
#                 "clarifying_questions": [
#                     "What are the main features you want?",
#                     "Who will use this application?",
#                     "Any technical preferences?"
#                 ],
#                 "processing_status": "questions_error",
#                 "error_count": state.get("error_count", 0) + 1
#             }
    
#     async def architect_node(state: AgentState):
#         logger.info("--- Running Architect ---")
#         try:
#             tech_stack = await BlueprintGenerator.generate_tech_stack(state["full_context"])
#             return {
#                 "tech_stack": tech_stack,
#                 "processing_status": "tech_stack_generated"
#             }
#         except Exception as e:
#             logger.error(f"Architect node error: {e}")
#             return {
#                 "tech_stack": {"error": str(e)},
#                 "processing_status": "tech_stack_error",
#                 "error_count": state.get("error_count", 0) + 1
#             }
    
#     async def designer_node(state: AgentState):
#         logger.info("--- Running Designer ---")
#         try:
#             flowchart = await BlueprintGenerator.generate_flowchart(
#                 state["full_context"], 
#                 state["tech_stack"]
#             )
#             return {
#                 "flowchart": flowchart,
#                 "processing_status": "flowchart_generated"
#             }
#         except Exception as e:
#             logger.error(f"Designer node error: {e}")
#             return {
#                 "flowchart": {"error": str(e)},
#                 "processing_status": "flowchart_error",
#                 "error_count": state.get("error_count", 0) + 1
#             }
    
#     async def writer_node(state: AgentState):
#         logger.info("--- Running Writer ---")
#         try:
#             overview = await BlueprintGenerator.generate_project_overview(
#                 state["full_context"], 
#                 state["tech_stack"], 
#                 state["flowchart"]
#             )
#             return {
#                 "project_overview": overview,
#                 "processing_status": "overview_generated"
#             }
#         except Exception as e:
#             logger.error(f"Writer node error: {e}")
#             return {
#                 "project_overview": f"Error generating overview: {e}",
#                 "processing_status": "overview_error",
#                 "error_count": state.get("error_count", 0) + 1
#             }
    
#     async def coder_node(state: AgentState):
#         logger.info("--- Running Code Generator ---")
#         try:
#             files = await BlueprintGenerator.generate_project_files(
#                 state["full_context"], 
#                 state["tech_stack"], 
#                 state["flowchart"]
#             )
#             return {
#                 "files": files,
#                 "processing_status": "files_generated"
#             }
#         except Exception as e:
#             logger.error(f"Coder node error: {e}")
#             return {
#                 "files": [{"error": str(e)}],
#                 "processing_status": "files_error",
#                 "error_count": state.get("error_count", 0) + 1
#             }
    
#     def router(state: AgentState):
#         """Enhanced router with error handling"""
#         error_count = state.get("error_count", 0)
        
#         # Stop if too many errors
#         if error_count >= 3:
#             logger.error("Too many errors, stopping execution")
#             return END
        
#         if not state.get("user_answers"):
#             return "Requirements_Expert"
#         if not state.get("tech_stack") or "error" in state.get("tech_stack", {}):
#             return "Architect"
#         if not state.get("flowchart") or "error" in state.get("flowchart", {}):
#             return "Designer"
#         if not state.get("project_overview"):
#             return "Writer"
#         if not state.get("files"):
#             return "Code_Generator"
#         return END
    
#     # Build the graph
#     workflow = StateGraph(AgentState)
#     workflow.add_node("Requirements_Expert", requirements_node)
#     workflow.add_node("Architect", architect_node)
#     workflow.add_node("Designer", designer_node)
#     workflow.add_node("Writer", writer_node)
#     workflow.add_node("Code_Generator", coder_node)
    
#     workflow.set_conditional_entry_point(router)
#     workflow.add_edge("Requirements_Expert", END)
#     workflow.add_edge("Architect", "Designer")
#     workflow.add_edge("Designer", "Writer")
#     workflow.add_edge("Writer", "Code_Generator")
#     workflow.add_edge("Code_Generator", END)
    
#     return workflow.compile()

# # ==============================================================================
# # 6. ENHANCED FASTAPI APPLICATION
# # ==============================================================================
# app = FastAPI(
#     title="AI Blueprint Generator API",
#     description="Advanced AI-powered project blueprint generation",
#     version="2.0.0"
# )

# # Enhanced middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize graph
# agent_graph = create_enhanced_agent_graph()

# @app.get("/")
# async def read_root():
#     return {
#         "status": "AI Blueprint Generator API is running",
#         "version": "2.0.0",
#         "timestamp": datetime.now().isoformat()
#     }

# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     try:
#         # Test if we can initialize a model
#         LLMService.get_model("GEMINI_API_KEY_1")
#         return {"status": "healthy", "timestamp": datetime.now().isoformat()}
#     except Exception as e:
#         return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}

# @app.post("/api/v1/generate-blueprint")
# async def generate_blueprint(request: BlueprintRequest):
#     """Enhanced blueprint generation endpoint"""
#     logger.info(f"Received blueprint request for: '{request.initial_idea[:50]}...'")
    
#     try:
#         # Prepare initial state
#         initial_state = {
#             "initial_idea": request.initial_idea,
#             "user_profile": request.user_profile.dict(),
#             "user_answers": request.user_answers,
#             "full_context": "",
#             "tech_stack": {},
#             "flowchart": {},
#             "project_overview": "",
#             "files": [],
#             "clarifying_questions": [],
#             "processing_status": "starting",
#             "error_count": 0
#         }
        
#         # Build context
#         if request.user_answers:
#             qa_text = "\n".join(f"Q{i+1}: {ans}" for i, ans in enumerate(request.user_answers))
#             initial_state["full_context"] = f"""
# Project Idea: {request.initial_idea}

# User Profile:
# - Name: {request.user_profile.name}
# - Experience: {request.user_profile.experience}

# User Clarifications:
# {qa_text}
#             """.strip()
#         else:
#             initial_state["full_context"] = f"""
# Project Idea: {request.initial_idea}
# User Profile: {request.user_profile.name} ({request.user_profile.experience})
#             """.strip()
        
#         async def stream_generator():
#             config = {"recursion_limit": 10}
            
#             try:
#                 async for chunk in agent_graph.astream(initial_state, config=config):
#                     node_name = list(chunk.keys())[0]
                    
#                     if node_name != "__end__":
#                         logger.info(f"Streaming from node: {node_name}")
                        
#                         payload = {
#                             'agent': node_name,
#                             'output': chunk[node_name],
#                             'timestamp': datetime.now().isoformat()
#                         }
                        
#                         yield f"data: {json.dumps(payload)}\n\n"
#                         await asyncio.sleep(0.1)
                
#                 # Send completion signal
#                 completion_payload = {
#                     'agent': 'COMPLETE',
#                     'output': {'status': 'Blueprint generation completed successfully'},
#                     'timestamp': datetime.now().isoformat()
#                 }
#                 yield f"data: {json.dumps(completion_payload)}\n\n"
                
#             except Exception as e:
#                 logger.error(f"Stream generation error: {e}")
#                 error_payload = {
#                     "error": "Blueprint generation failed",
#                     "details": str(e),
#                     "timestamp": datetime.now().isoformat()
#                 }
#                 yield f"data: {json.dumps(error_payload)}\n\n"
        
#         return StreamingResponse(
#             stream_generator(),
#             media_type="text/event-stream",
#             headers={
#                 "Cache-Control": "no-cache",
#                 "Connection": "keep-alive",
#                 "Access-Control-Allow-Origin": "*",
#             }
#         )
        
#     except Exception as e:
#         logger.error(f"Request processing error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     uvicorn.run(
#         app, 
#         host="0.0.0.0", 
#         port=8000,
#         log_level="info"
#     )