import React, { useState, useEffect, useCallback, useRef } from 'react';

// Import UI and Icon libraries
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState, addEdge, Handle, Position, BackgroundVariant, useReactFlow, ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';
import { 
    FileText, Folder, Bot, Send, Layers, ChevronRight, ChevronDown, Info, GitBranch, 
    Database, Sparkles, Code2, ArrowLeft, LoaderCircle, AlertCircle, RefreshCw, 
    Search, Download, Copy, Check, X, Settings, FileCode, FileJson, Globe,
    Maximize2, Minimize2, Monitor, Smartphone, Tablet
} from 'lucide-react';

// API Configuration
const API_BASE = 'http://localhost:8000/api/v1';

// --- ENHANCED UTILITIES ---
const getFileExtension = (filename) => filename.split('.').pop()?.toLowerCase() || '';

const getFileIcon = (filename) => {
    const ext = getFileExtension(filename);
    const iconMap = {
        'js': FileCode, 'jsx': FileCode, 'ts': FileCode, 'tsx': FileCode,
        'py': FileCode, 'html': Globe, 'css': FileCode, 'json': FileJson,
        'md': FileText, 'yml': FileCode, 'yaml': FileCode
    };
    return iconMap[ext] || FileText;
};

const formatFileSize = (content) => {
    const size = new Blob([content]).size;
    return size < 1024 ? `${size} B` : size < 1048576 ? `${(size/1024).toFixed(1)} KB` : `${(size/1048576).toFixed(1)} MB`;
};

// --- STYLED ICON COMPONENT ---
const Icon = ({ icon: IconComponent, className = "", size = 16 }) => 
    <IconComponent className={`w-${size/4} h-${size/4} ${className}`} />;

// --- ENHANCED ERROR HANDLING ---
const ErrorBoundary = ({ children, fallback }) => {
    const [hasError, setHasError] = useState(false);
    
    useEffect(() => {
        const handleError = () => setHasError(true);
        window.addEventListener('error', handleError);
        return () => window.removeEventListener('error', handleError);
    }, []);
    
    if (hasError) return fallback || <div className="p-4 text-red-400">Something went wrong</div>;
    return children;
};

const Toast = ({ message, type = 'info', onClose }) => (
    <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 flex items-center gap-3 ${
        type === 'error' ? 'bg-red-900 border border-red-700 text-red-100' :
        type === 'success' ? 'bg-green-900 border border-green-700 text-green-100' :
        'bg-blue-900 border border-blue-700 text-blue-100'
    }`}>
        {type === 'error' && <AlertCircle size={20} />}
        {type === 'success' && <Check size={20} />}
        <span className="text-sm">{message}</span>
        <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">
            <X size={16} />
        </button>
    </div>
);

// --- ENHANCED CHATBOT COMPONENTS ---
const TypingIndicator = () => (
    <div className="flex items-center space-x-1.5 p-3">
        <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce"></div>
    </div>
);

const MessageBubble = ({ message }) => {
    const isUser = message.sender === 'user';
    const [copied, setCopied] = useState(false);
    
    const handleCopy = async () => {
        await navigator.clipboard.writeText(message.text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };
    
    return (
        <div className={`flex items-start gap-3 group ${isUser ? 'justify-end' : 'justify-start'}`}>
            {!isUser && (
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0">
                    <Bot size={20} className="text-white" />
                </div>
            )}
            <div className={`max-w-md rounded-2xl px-4 py-3 text-sm relative ${
                isUser ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-zinc-800 text-zinc-200 rounded-bl-none'
            }`}>
                {message.text}
                <button
                    onClick={handleCopy}
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-black/20"
                    title="Copy message"
                >
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                </button>
            </div>
        </div>
    );
};

const EnhancedLoaderCard = ({ status, progress = 0, onCancel }) => (
    <div className="flex items-start gap-3 justify-start">
        <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0">
            <Bot size={20} className="text-white" />
        </div>
        <div className="max-w-md rounded-2xl px-4 py-3 bg-zinc-800 text-zinc-200 rounded-bl-none">
            <div className="flex items-center gap-3 mb-2">
                <LoaderCircle size={20} className="animate-spin text-indigo-400" />
                <div className="flex flex-col flex-1">
                    <span className="font-medium text-zinc-100">Generating Blueprint...</span>
                    <span className="text-xs text-zinc-400">{status}</span>
                </div>
                {onCancel && (
                    <button 
                        onClick={onCancel}
                        className="text-zinc-500 hover:text-zinc-300 p-1"
                        title="Cancel generation"
                    >
                        <X size={16} />
                    </button>
                )}
            </div>
            {progress > 0 && (
                <div className="w-full bg-zinc-700 rounded-full h-2">
                    <div 
                        className="bg-indigo-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                    />
                </div>
            )}
        </div>
    </div>
);

const ResultCard = ({ onShowWorkspace, projectData }) => (
    <div className="flex items-start gap-3 justify-start">
        <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0">
            <Bot size={20} className="text-white" />
        </div>
        <div className="max-w-md rounded-2xl p-4 bg-zinc-800 border border-zinc-700 text-zinc-200 rounded-bl-none space-y-3">
            <h3 className="font-bold text-lg text-white flex items-center gap-2">
                <Sparkles className="text-yellow-400" size={20} />
                Your Blueprint is Ready!
            </h3>
            <div className="text-sm space-y-1">
                <p className="text-zinc-400">Generated successfully with:</p>
                <ul className="text-xs text-zinc-500 space-y-0.5">
                    <li>• {projectData?.files?.length || 0} code files</li>
                    <li>• Complete project structure</li>
                    <li>• Architecture diagram</li>
                    <li>• Technical documentation</li>
                </ul>
            </div>
            <div className="flex gap-2">
                <button
                    onClick={onShowWorkspace}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                    <Monitor size={16} />
                    Open Workspace
                </button>
                <button 
                    className="p-2 bg-zinc-700 hover:bg-zinc-600 text-zinc-300 rounded-lg transition-colors"
                    title="Download project"
                >
                    <Download size={16} />
                </button>
            </div>
        </div>
    </div>
);

// --- ENHANCED WORKSPACE COMPONENTS ---
const WorkspaceHeader = ({ projectName, onClose, viewMode, setViewMode }) => (
    <header className="h-16 bg-zinc-900 border-b border-zinc-800 px-4 flex items-center justify-between flex-shrink-0 z-40">
        <div className="flex items-center gap-4">
            <button 
                onClick={onClose} 
                className="flex items-center gap-2 p-2 rounded-md hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
            >
                <ArrowLeft size={16} />
                Back to Chat
            </button>
            <div className="h-6 w-px bg-zinc-700" />
            <h1 className="text-lg font-medium text-zinc-200">{projectName}</h1>
        </div>
        
        <div className="flex items-center gap-2">
            <div className="flex bg-zinc-800 rounded-lg p-1">
                <button
                    onClick={() => setViewMode('desktop')}
                    className={`p-2 rounded transition-colors ${viewMode === 'desktop' ? 'bg-zinc-700 text-white' : 'text-zinc-400 hover:text-white'}`}
                    title="Desktop view"
                >
                    <Monitor size={16} />
                </button>
                <button
                    onClick={() => setViewMode('tablet')}
                    className={`p-2 rounded transition-colors ${viewMode === 'tablet' ? 'bg-zinc-700 text-white' : 'text-zinc-400 hover:text-white'}`}
                    title="Tablet view"
                >
                    <Tablet size={16} />
                </button>
                <button
                    onClick={() => setViewMode('mobile')}
                    className={`p-2 rounded transition-colors ${viewMode === 'mobile' ? 'bg-zinc-700 text-white' : 'text-zinc-400 hover:text-white'}`}
                    title="Mobile view"
                >
                    <Smartphone size={16} />
                </button>
            </div>
            <button className="p-2 text-zinc-400 hover:text-white rounded-md hover:bg-zinc-800 transition-colors">
                <Settings size={16} />
            </button>
        </div>
    </header>
);

const SearchableFileTree = ({ nodes, selectedFile, onFileSelect, expandedFolders, onToggleFolder, depth = 0 }) => {
    const [searchTerm, setSearchTerm] = useState('');
    
    const filterNodes = (nodes, term) => {
        if (!term) return nodes;
        return nodes.filter(node => {
            if (node.name.toLowerCase().includes(term.toLowerCase())) return true;
            if (node.children) {
                const filteredChildren = filterNodes(node.children, term);
                return filteredChildren.length > 0;
            }
            return false;
        }).map(node => ({
            ...node,
            children: node.children ? filterNodes(node.children, term) : undefined
        }));
    };
    
    const filteredNodes = filterNodes(nodes, searchTerm);
    
    return (
        <div className="space-y-2">
            <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-500" size={16} />
                <input
                    type="text"
                    placeholder="Search files..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                />
            </div>
            <FileTree 
                nodes={filteredNodes} 
                selectedFile={selectedFile} 
                onFileSelect={onFileSelect} 
                expandedFolders={expandedFolders} 
                onToggleFolder={onToggleFolder} 
                depth={depth} 
            />
        </div>
    );
};

const FileTree = ({ nodes, selectedFile, onFileSelect, expandedFolders, onToggleFolder, depth = 0 }) => (
    <>
        {nodes.map((node) => {
            const isExpanded = expandedFolders.has(node.path);
            const hasChildren = node.children && node.children.length > 0;
            const FileIcon = node.type === 'folder' ? Folder : getFileIcon(node.name);
            
            return (
                <div key={node.path} style={{ paddingLeft: `${depth * 16}px` }}>
                    <div
                        className={`flex items-center gap-2 px-2 py-1.5 rounded text-sm cursor-pointer transition-colors group ${
                            selectedFile === node.path ? 'bg-indigo-900/40 text-white' : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200'
                        }`}
                        onClick={() => node.type === 'file' ? onFileSelect(node) : onToggleFolder(node.path)}
                    >
                        {hasChildren ? (
                            isExpanded ? <ChevronDown className="w-4 h-4 text-zinc-500" /> : <ChevronRight className="w-4 h-4 text-zinc-500" />
                        ) : (
                            <div className="w-4" />
                        )}
                        <Icon 
                            icon={FileIcon} 
                            className={node.type === 'folder' ? 'text-sky-400' : 'text-zinc-500'} 
                        />
                        <span className="truncate flex-1">{node.name}</span>
                        {node.type === 'file' && (
                            <span className="opacity-0 group-hover:opacity-100 text-xs text-zinc-600 transition-opacity">
                                {getFileExtension(node.name)}
                            </span>
                        )}
                    </div>
                    {hasChildren && isExpanded && (
                        <div className="mt-0.5">
                            <FileTree 
                                nodes={node.children} 
                                selectedFile={selectedFile} 
                                onFileSelect={onFileSelect} 
                                expandedFolders={expandedFolders} 
                                onToggleFolder={onToggleFolder} 
                                depth={depth + 1} 
                            />
                        </div>
                    )}
                </div>
            );
        })}
    </>
);

const EnhancedProjectOverview = ({ documentation, project }) => {
    if (!documentation && !project) {
        return <p className="text-zinc-500 text-sm p-4">No documentation available.</p>;
    }
    
    const stats = {
        totalFiles: project?.files?.length || 0,
        codeFiles: Object.keys(project?.codeFiles || {}).length,
        totalLines: Object.values(project?.codeFiles || {}).reduce((acc, code) => acc + code.split('\n').length, 0)
    };
    
    return (
        <div className="text-zinc-300 space-y-6 p-4">
            <div className="grid grid-cols-3 gap-4">
                <div className="bg-zinc-800 rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-indigo-400">{stats.totalFiles}</div>
                    <div className="text-xs text-zinc-500">Total Files</div>
                </div>
                <div className="bg-zinc-800 rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-green-400">{stats.codeFiles}</div>
                    <div className="text-xs text-zinc-500">Code Files</div>
                </div>
                <div className="bg-zinc-800 rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-yellow-400">{stats.totalLines}</div>
                    <div className="text-xs text-zinc-500">Lines of Code</div>
                </div>
            </div>
            
            {documentation?.readme && (
                <div>
                    <h3 className="font-semibold text-zinc-100 text-base mb-2">Project Description</h3>
                    <p className="text-sm text-zinc-400 leading-relaxed">{documentation.readme.description}</p>
                </div>
            )}
            
            {documentation?.readme?.features && (
                <div>
                    <h3 className="font-semibold text-zinc-100 text-base mb-3">Key Features</h3>
                    <ul className="space-y-1">
                        {documentation.readme.features.map((feature, index) => (
                            <li key={index} className="text-sm text-zinc-400 flex items-start gap-2">
                                <span className="text-indigo-400 mt-1">•</span>
                                {feature}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            
            {documentation?.api_docs?.endpoints && (
                <div>
                    <h3 className="font-semibold text-zinc-100 text-base mb-3">API Endpoints</h3>
                    <div className="space-y-2">
                        {documentation.api_docs.endpoints.map((endpoint, index) => (
                            <div key={index} className="bg-zinc-800 rounded p-2 text-xs">
                                <span className={`font-mono px-2 py-1 rounded ${
                                    endpoint.method === 'GET' ? 'bg-green-900 text-green-300' :
                                    endpoint.method === 'POST' ? 'bg-blue-900 text-blue-300' :
                                    'bg-gray-900 text-gray-300'
                                }`}>
                                    {endpoint.method}
                                </span>
                                <span className="ml-2 text-zinc-300">{endpoint.path}</span>
                                <p className="text-zinc-500 mt-1">{endpoint.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

const LeftSidebar = ({ project, selectedFile, onFileSelect }) => {
    const [expandedFolders, setExpandedFolders] = useState(new Set(['/', '/src', '/src/components', '/src/pages']));
    const [activeTab, setActiveTab] = useState('overview'); // Changed default to overview
    
    const toggleFolder = (path) => {
        setExpandedFolders(prev => {
            const newSet = new Set(prev);
            newSet.has(path) ? newSet.delete(path) : newSet.add(path);
            return newSet;
        });
    };
    
    const fileStructure = project?.fileStructure?.[0]?.children || [];
    
    // Debug logging to see what data we have
    console.log('LeftSidebar project data:', project);
    console.log('File structure:', fileStructure);
    
    return (
        <div className="w-full h-full flex flex-col bg-zinc-900 border-r border-zinc-800 overflow-hidden">
            <div className='p-4'>
                <h2 className="text-base font-semibold text-zinc-200">Project Explorer</h2>
            </div>
            
            <div className="px-2 border-y border-zinc-800">
                <nav className="flex space-x-2">
                    <button 
                        onClick={() => setActiveTab('overview')} 
                        className={`flex items-center gap-2 px-3 py-2 text-sm font-medium transition-colors rounded-t-md ${
                            activeTab === 'overview' ? 'text-white bg-zinc-800' : 'text-zinc-400 hover:text-white'
                        }`}
                    >
                        <Icon icon={Info} /> Overview
                    </button>
                    <button 
                        onClick={() => setActiveTab('files')} 
                        className={`flex items-center gap-2 px-3 py-2 text-sm font-medium transition-colors rounded-t-md ${
                            activeTab === 'files' ? 'text-white bg-zinc-800' : 'text-zinc-400 hover:text-white'
                        }`}
                    >
                        <Icon icon={Folder} /> Files
                    </button>
                </nav>
            </div>
            
            <div className="flex-1 overflow-y-auto">
                {activeTab === 'overview' ? (
                    <EnhancedProjectOverview documentation={project.documentation} project={project} />
                ) : (
                    <div className="p-4">
                        {fileStructure.length > 0 ? (
                            <SearchableFileTree 
                                nodes={fileStructure} 
                                selectedFile={selectedFile} 
                                onFileSelect={onFileSelect} 
                                expandedFolders={expandedFolders} 
                                onToggleFolder={toggleFolder} 
                            />
                        ) : (
                            <div className="text-center text-zinc-600 py-8">
                                <Folder className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                <p className="text-xs">No file structure available</p>
                                <p className="text-xs text-zinc-700 mt-1">Project files are being generated...</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

const CodeEditor = ({ content, filename }) => {
    const [copied, setCopied] = useState(false);
    
    const handleCopy = async () => {
        await navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };
    
    const getLanguageFromFilename = (filename) => {
        const ext = getFileExtension(filename);
        const langMap = {
            'js': 'javascript', 'jsx': 'javascript', 'ts': 'typescript', 'tsx': 'typescript',
            'py': 'python', 'html': 'html', 'css': 'css', 'json': 'json',
            'md': 'markdown', 'yml': 'yaml', 'yaml': 'yaml'
        };
        return langMap[ext] || 'text';
    };
    
    return (
        <div className="h-full flex flex-col">
            <div className="flex items-center justify-between p-3 border-b border-zinc-800">
                <div className="flex items-center gap-2">
                    <Icon icon={getFileIcon(filename)} className="text-zinc-400" />
                    <span className="text-sm font-medium text-zinc-200">{filename?.split('/').pop()}</span>
                    <span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">
                        {getLanguageFromFilename(filename)}
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-500">{formatFileSize(content)}</span>
                    <button
                        onClick={handleCopy}
                        className="p-1.5 text-zinc-400 hover:text-white rounded transition-colors"
                        title="Copy to clipboard"
                    >
                        {copied ? <Check size={14} /> : <Copy size={14} />}
                    </button>
                </div>
            </div>
            <div className="flex-1 overflow-auto">
                <pre className="text-xs bg-zinc-950 text-zinc-300 p-4 h-full overflow-auto">
                    <code className={`language-${getLanguageFromFilename(filename)}`}>
                        {content}
                    </code>
                </pre>
            </div>
        </div>
    );
};

const RightSidebar = ({ selectedFile, project }) => {
    const codeContent = selectedFile && project.codeFiles?.[selectedFile];
    const fileData = selectedFile && project.files?.find(f => f.fileName === selectedFile);
    const explanation = fileData?.explanation;

    return (
        <div className="w-full h-full flex flex-col bg-zinc-900 border-l border-zinc-800 overflow-hidden">
            <div className='p-4'>
                <h2 className="text-base font-semibold text-zinc-200">File Inspector</h2>
            </div>
            <div className="border-t border-zinc-800 mx-4"></div>
            
            <div className="flex-1 flex flex-col overflow-hidden">
                <PanelGroup direction="vertical">
                    <Panel defaultSize={65} minSize={20}>
                        {codeContent ? (
                            <CodeEditor content={codeContent} filename={selectedFile} />
                        ) : (
                            <div className="h-full flex items-center justify-center text-center text-zinc-600">
                                <div>
                                    <Code2 className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                    <p className="text-sm">Select a file to view its content</p>
                                    <p className="text-xs text-zinc-700 mt-1">Click on any file in the explorer</p>
                                </div>
                            </div>
                        )}
                    </Panel>
                    
                    <PanelResizeHandle className="h-px bg-zinc-800 hover:h-1 hover:bg-indigo-500 transition-all" />
                    
                    <Panel defaultSize={35} minSize={15}>
                        <div className="h-full p-4 overflow-y-auto">
                            <h3 className="text-xs font-semibold text-zinc-500 mb-3 uppercase tracking-wider flex items-center gap-2">
                                <Sparkles size={12} />
                                AI Analysis
                            </h3>
                            {explanation ? (
                                <div className="prose prose-sm prose-invert max-w-none">
                                    <p className="text-sm text-zinc-400 leading-relaxed">{explanation}</p>
                                    {selectedFile && (
                                        <div className="mt-4 p-3 bg-zinc-800 rounded-lg">
                                            <h4 className="text-xs font-semibold text-zinc-300 mb-2">File Details</h4>
                                            <div className="space-y-1 text-xs text-zinc-500">
                                                <div>Path: <span className="text-zinc-400">{selectedFile}</span></div>
                                                <div>Type: <span className="text-zinc-400">{getFileExtension(selectedFile).toUpperCase()}</span></div>
                                                <div>Size: <span className="text-zinc-400">{formatFileSize(codeContent || '')}</span></div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="text-center text-zinc-600 py-8">
                                    <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                    <p className="text-xs">Select a file to see AI-generated explanation</p>
                                </div>
                            )}
                        </div>
                    </Panel>
                </PanelGroup>
            </div>
        </div>
    );
};

// Enhanced React Flow Node Types
const enhancedNodeTypes = {
    ui: ({ data, selected }) => (
        <div className={`p-4 rounded-lg border w-64 bg-gradient-to-br from-zinc-800 to-zinc-900 transition-all duration-300 shadow-lg ${
            selected ? 'border-sky-500 shadow-[0_0_20px] shadow-sky-500/30 scale-105' : 'border-zinc-700 hover:border-zinc-600'
        }`}>
            <Handle type="target" position={Position.Top} className="!bg-zinc-600 !border-2 !border-zinc-500" />
            <div className="font-semibold text-sky-300 flex items-center gap-2 mb-2">
                <Icon icon={FileText} className="text-sky-400" />
                {data.label}
            </div>
            <p className="text-xs text-zinc-400 mb-2">{data.type}</p>
            {data.description && <p className="text-xs text-zinc-500">{data.description}</p>}
            <Handle type="source" position={Position.Bottom} className="!bg-zinc-600 !border-2 !border-zinc-500" />
        </div>
    ),
    logic: ({ data, selected }) => (
        <div className={`p-4 rounded-lg border w-64 bg-gradient-to-br from-zinc-800 to-zinc-900 transition-all duration-300 shadow-lg ${
            selected ? 'border-teal-500 shadow-[0_0_20px] shadow-teal-500/30 scale-105' : 'border-zinc-700 hover:border-zinc-600'
        }`}>
            <Handle type="target" position={Position.Top} className="!bg-zinc-600 !border-2 !border-zinc-500" />
            <div className="font-semibold text-teal-300 flex items-center gap-2 mb-2">
                <Icon icon={Layers} className="text-teal-400" />
                {data.label}
            </div>
            <p className="text-xs text-zinc-400 mb-2">{data.purpose}</p>
            {data.technologies && (
                <div className="flex flex-wrap gap-1 mb-2">
                    {data.technologies.map(tech => (
                        <span key={tech} className="text-xs bg-teal-900/50 text-teal-300 px-2 py-0.5 rounded">
                            {tech}
                        </span>
                    ))}
                </div>
            )}
            <Handle type="source" position={Position.Bottom} className="!bg-zinc-600 !border-2 !border-zinc-500" />
        </div>
    ),
    data: ({ data, selected }) => (
        <div className={`p-4 rounded-lg border w-64 bg-gradient-to-br from-zinc-800 to-zinc-900 transition-all duration-300 shadow-lg ${
            selected ? 'border-amber-500 shadow-[0_0_20px] shadow-amber-500/30 scale-105' : 'border-zinc-700 hover:border-zinc-600'
        }`}>
            <Handle type="target" position={Position.Top} className="!bg-zinc-600 !border-2 !border-zinc-500" />
            <div className="font-semibold text-amber-300 flex items-center gap-2 mb-2">
                <Icon icon={Database} className="text-amber-400" />
                {data.label}
            </div>
            <p className="text-xs text-zinc-400">{data.dataType}</p>
            <Handle type="source" position={Position.Bottom} className="!bg-zinc-600 !border-2 !border-zinc-500" />
        </div>
    ),
    external: ({ data, selected }) => (
        <div className={`p-4 rounded-lg border w-64 bg-gradient-to-br from-zinc-800 to-zinc-900 transition-all duration-300 shadow-lg ${
            selected ? 'border-purple-500 shadow-[0_0_20px] shadow-purple-500/30 scale-105' : 'border-zinc-700 hover:border-zinc-600'
        }`}>
            <Handle type="target" position={Position.Top} className="!bg-zinc-600 !border-2 !border-zinc-500" />
            <div className="font-semibold text-purple-300 flex items-center gap-2 mb-2">
                <Icon icon={Send} className="text-purple-400" />
                {data.label}
            </div>
            <p className="text-xs text-zinc-400">{data.provider}</p>
            <Handle type="source" position={Position.Bottom} className="!bg-zinc-600 !border-2 !border-zinc-500" />
        </div>
    ),
    state: ({ data, selected }) => (
        <div className={`p-4 rounded-lg border w-64 bg-gradient-to-br from-zinc-800 to-zinc-900 transition-all duration-300 shadow-lg ${
            selected ? 'border-rose-500 shadow-[0_0_20px] shadow-rose-500/30 scale-105' : 'border-zinc-700 hover:border-zinc-600'
        }`}>
            <Handle type="target" position={Position.Top} className="!bg-zinc-600 !border-2 !border-zinc-500" />
            <div className="font-semibold text-rose-300 flex items-center gap-2 mb-2">
                <Icon icon={GitBranch} className="text-rose-400" />
                {data.label}
            </div>
            <p className="text-xs text-zinc-400">{data.library}</p>
            <Handle type="source" position={Position.Bottom} className="!bg-zinc-600 !border-2 !border-zinc-500" />
        </div>
    )
};

const EnhancedArchitectureCanvas = ({ flowchart }) => {
    // Transform flowchart data to ensure ReactFlow compatibility
    const transformFlowchartData = (flowchart) => {
        if (!flowchart) return { nodes: [], edges: [] };
        
        let nodes = flowchart.nodes || [];
        let edges = flowchart.edges || [];
        
        // Transform nodes to ensure they have proper ReactFlow format
        nodes = nodes.map((node, index) => {
            // If node doesn't have position, add default positions
            if (!node.position) {
                const x = 200 + (index % 3) * 300;
                const y = 100 + Math.floor(index / 3) * 200;
                return {
                    ...node,
                    position: { x, y },
                    data: node.data || { label: node.label || `Node ${index + 1}` }
                };
            }
            return node;
        });
        
        // Transform edges to ensure they have proper ReactFlow format
        edges = edges.map((edge, index) => ({
            id: edge.id || `e${index + 1}`,
            source: edge.source || edge.from,
            target: edge.target || edge.to,
            label: edge.label,
            animated: true,
            style: { stroke: '#6366f1', strokeWidth: 2 }
        }));
        
        return { nodes, edges };
    };
    
    const { nodes: transformedNodes, edges: transformedEdges } = transformFlowchartData(flowchart);
    const [nodes, setNodes, onNodesChange] = useNodesState(transformedNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(transformedEdges);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const { fitView, zoomIn, zoomOut, zoomTo } = useReactFlow();

    const onConnect = useCallback((params) => 
        setEdges((eds) => addEdge({ 
            ...params, 
            animated: true, 
            style: { stroke: '#6366f1', strokeWidth: 2 } 
        }, eds)), []
    );

    useEffect(() => {
        const { nodes: newNodes, edges: newEdges } = transformFlowchartData(flowchart);
        setNodes(newNodes);
        setEdges(newEdges);
        const timer = setTimeout(() => {
            if (fitView) fitView({ duration: 800, padding: 0.1 });
        }, 100);
        return () => clearTimeout(timer);
    }, [flowchart, setNodes, setEdges, fitView]);

    return (
        <div className={`${isFullscreen ? 'fixed inset-0 z-50' : 'h-full'} bg-zinc-950 relative`}>
            {transformedNodes.length === 0 ? (
                <div className="h-full flex items-center justify-center text-center text-zinc-600">
                    <div>
                        <Layers className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p className="text-sm">Architecture diagram is being generated...</p>
                        <p className="text-xs text-zinc-700 mt-1">This may take a moment</p>
                    </div>
                </div>
            ) : (
                <>
                    {/* Fullscreen toggle button - top right */}
                    <button
                        onClick={() => setIsFullscreen(!isFullscreen)}
                        className="absolute top-4 right-4 z-20 bg-zinc-800 rounded-lg p-2 text-zinc-400 hover:text-white transition-colors"
                        title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
                    >
                        {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                    </button>

                    {/* Custom controls - bottom left corner */}
                    <div className="absolute bottom-4 left-4 z-20 bg-zinc-800 rounded-lg p-2 flex items-center gap-2">
                        <button
                            onClick={() => zoomIn()}
                            className="p-1 text-zinc-400 hover:text-white transition-colors"
                            title="Zoom in"
                        >
                            <span className="text-lg font-bold">+</span>
                        </button>
                        <button
                            onClick={() => zoomOut()}
                            className="p-1 text-zinc-400 hover:text-white transition-colors"
                            title="Zoom out"
                        >
                            <span className="text-lg font-bold">−</span>
                        </button>
                        <button
                            onClick={() => fitView({ duration: 500 })}
                            className="px-2 py-1 text-zinc-400 hover:text-white transition-colors text-xs font-semibold"
                            title="Fit to view"
                        >
                            FIT
                        </button>
                    </div>
                    
                    <ReactFlow 
                        nodes={nodes} 
                        edges={edges} 
                        onNodesChange={onNodesChange} 
                        onEdgesChange={onEdgesChange} 
                        onConnect={onConnect} 
                        nodeTypes={enhancedNodeTypes} 
                        className="bg-zinc-950 w-full h-full"
                        defaultEdgeOptions={{ animated: true }}
                        fitView
                        fitViewOptions={{ padding: 0.2 }}
                    >
                        {/* Hide default controls since we have custom ones */}
                        <MiniMap 
                            className="!bg-zinc-900 !border !border-zinc-700"
                            position="top-right"
                            nodeColor={(node) => {
                                const colorMap = {
                                    ui: '#0ea5e9', logic: '#14b8a6', data: '#f59e0b',
                                    external: '#a855f7', state: '#ef4444'
                                };
                                return colorMap[node.type] || '#6b7280';
                            }}
                        />
                        <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#27272a" />
                    </ReactFlow>
                </>
            )}
        </div>
    );
};

const WorkspaceView = ({ blueprintData, onClose }) => {
    const [selectedFile, setSelectedFile] = useState('');
    const [viewMode, setViewMode] = useState('desktop');
    
    const handleFileSelect = (file) => {
        setSelectedFile(file.path);
    };
    
    const getPanelSizes = () => {
        switch (viewMode) {
            case 'mobile': return { left: 15, main: 70, right: 15 };
            case 'tablet': return { left: 18, main: 60, right: 22 };
            default: return { left: 25, main: 50, right: 25 }; // Better default distribution
        }
    };
    
    const sizes = getPanelSizes();
    
    return (
        <ErrorBoundary>
            <div className="h-screen w-screen bg-zinc-950 text-zinc-300 flex flex-col font-sans overflow-hidden">
                <WorkspaceHeader 
                    projectName={blueprintData.project.name} 
                    onClose={onClose}
                    viewMode={viewMode}
                    setViewMode={setViewMode}
                />
                
                <div className="flex-1 overflow-hidden">
                    <PanelGroup direction="horizontal">
                        <Panel defaultSize={40} minSize={20}>
                            <LeftSidebar 
                                project={blueprintData.project} 
                                selectedFile={selectedFile} 
                                onFileSelect={handleFileSelect} 
                            />
                        </Panel>
                        
                        <PanelResizeHandle className="w-1 bg-zinc-800 hover:bg-indigo-500" />
                        
                        <Panel defaultSize={35} minSize={25}>
                            <ReactFlowProvider>
                                <EnhancedArchitectureCanvas flowchart={blueprintData.flowchart} />
                            </ReactFlowProvider>
                        </Panel>
                        
                        <PanelResizeHandle className="w-1 bg-zinc-800 hover:bg-indigo-500" />
                        
                        <Panel defaultSize={25} minSize={15}>
                            <RightSidebar selectedFile={selectedFile} project={blueprintData.project} />
                        </Panel>
                    </PanelGroup>
                </div>
            </div>
        </ErrorBoundary>
    );
};

// Enhanced Main App Component
export default function App() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [conversationState, setConversationState] = useState('AWAITING_IDEA');
    const [isBotTyping, setIsBotTyping] = useState(false);
    
    // Data stores
    const [projectIdea, setProjectIdea] = useState('');
    const [clarifyingQuestions, setClarifyingQuestions] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [userAnswers, setUserAnswers] = useState([]);
    const [generationProgress, setGenerationProgress] = useState(0);
    
    // Result state
    const [isWorkspaceVisible, setIsWorkspaceVisible] = useState(false);
    const [finalBlueprintData, setFinalBlueprintData] = useState(null);
    
    // UI state
    const [toast, setToast] = useState(null);
    const [generationController, setGenerationController] = useState(null);
    
    const chatEndRef = useRef(null);

    // Auto-scroll chat
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isBotTyping]);
    
    // Initial greeting
    useEffect(() => {
        setMessages([{
            id: 1,
            sender: 'bot',
            text: '👋 Hello! I\'m your AI architect. I can help you generate a complete project blueprint with architecture diagrams, file structures, and boilerplate code. What amazing project do you want to build today?'
        }]);
    }, []);

    const showToast = (message, type = 'info') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 5000);
    };

    const addMessage = (sender, text, type = 'text', data = {}) => {
        setMessages(prev => [...prev, { id: Date.now(), sender, text, type, data }]);
    };
    
    const askNextQuestion = () => {
        if (currentQuestionIndex < clarifyingQuestions.length) {
            setIsBotTyping(false);
            addMessage('bot', `${currentQuestionIndex + 1}/${clarifyingQuestions.length}: ${clarifyingQuestions[currentQuestionIndex]}`);
        } else {
            setConversationState('GENERATING');
            setIsBotTyping(false);
            addMessage('bot', null, 'enhanced_loader', { 
                status: 'Initializing blueprint generation...', 
                progress: 0 
            });
            triggerBlueprintGeneration();
        }
    };
    
    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const newUserMessage = inputValue;
        addMessage('user', newUserMessage);
        setInputValue('');

        if (conversationState === 'AWAITING_IDEA') {
            setProjectIdea(newUserMessage);
            setConversationState('FETCHING_QUESTIONS');
            setIsBotTyping(true);
            
            try {
                const response = await fetch(`${API_BASE}/generate-questions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        initial_idea: newUserMessage, 
                        user_profile: { name: 'User', experience: 'Intermediate' }
                    })
                });
                
                if (!response.ok) throw new Error(`Server error: ${response.status}`);
                
                const data = await response.json();
                setClarifyingQuestions(data.questions);
                setUserAnswers(new Array(data.questions.length).fill(''));
                setCurrentQuestionIndex(0);
                setConversationState('AWAITING_CLARIFICATIONS');
                showToast('Questions generated successfully!', 'success');
                
            } catch (err) {
                addMessage('bot', `❌ I encountered an error: ${err.message}. Please try again.`);
                setConversationState('AWAITING_IDEA');
                setIsBotTyping(false);
                showToast('Failed to generate questions', 'error');
            }
            
        } else if (conversationState === 'AWAITING_CLARIFICATIONS') {
            const updatedAnswers = [...userAnswers];
            updatedAnswers[currentQuestionIndex] = newUserMessage;
            setUserAnswers(updatedAnswers);
            setCurrentQuestionIndex(prev => prev + 1);
            setIsBotTyping(true);
        }
    };

    // Handle question progression
    useEffect(() => {
        if (conversationState === 'AWAITING_CLARIFICATIONS' && clarifyingQuestions.length > 0) {
            setTimeout(() => askNextQuestion(), 500);
        }
    }, [currentQuestionIndex, conversationState, clarifyingQuestions]);

    const cancelGeneration = () => {
        if (generationController) {
            generationController.abort();
            setGenerationController(null);
        }
        setConversationState('AWAITING_IDEA');
        setGenerationProgress(0);
        // Remove the loader message and add cancellation message
        setMessages(prev => prev.filter(msg => msg.type !== 'enhanced_loader'));
        addMessage('bot', '⚠️ Blueprint generation was cancelled. Feel free to start over with a new idea!');
        showToast('Generation cancelled', 'info');
    };

    const triggerBlueprintGeneration = async () => {
        const controller = new AbortController();
        setGenerationController(controller);
        
        try {
            const response = await fetch(`${API_BASE}/generate-blueprint`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    initial_idea: projectIdea,
                    user_profile: { name: 'User', experience: 'Intermediate' },
                    user_answers: userAnswers
                }),
                signal: controller.signal
            });

            if (!response.ok) throw new Error(`Server error: ${response.status}`);
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let stepCount = 0;
            const totalSteps = 4; // Architect, Designer, Structure, Code_Generator

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const jsonString = line.substring(6);
                        if (!jsonString) continue;
                        
                        const data = JSON.parse(jsonString);
                        
                        if (data.error) throw new Error(data.details || 'Generation failed');
                        
                        if (data.agent === 'ERROR') {
                            // Remove the loader message and add error message
                            setMessages(prev => prev.filter(msg => msg.type !== 'enhanced_loader'));
                            addMessage('bot', `❌ ${data.output?.error || 'Blueprint generation failed'}: ${data.output?.details || 'Unknown error'}`);
                            setConversationState('AWAITING_IDEA');
                            setGenerationProgress(0);
                            showToast('Blueprint generation failed', 'error');
                            return;
                        }
                        
                        if (data.agent === 'COMPLETE') {
                            setFinalBlueprintData(data.output);
                            setGenerationProgress(100);
                            
                            // Remove the loader and add the result card immediately
                            setMessages(prev => prev.filter(msg => msg.type !== 'enhanced_loader'));
                            addMessage('bot', null, 'result_card', { projectData: data.output });
                            setConversationState('COMPLETE');
                            showToast('Blueprint generated successfully!', 'success');
                            
                            return;
                        } else {
                            stepCount++;
                            const progress = Math.round((stepCount / totalSteps) * 90); // Max 90% until complete
                            setGenerationProgress(progress);
                            
                            setMessages(prev =>
                                 prev.map(msg => 
                                msg.type === 'enhanced_loader' 
                                ? { ...msg, data: { 
                                    status: `✅ ${data.agent.replace(/_/g, ' ')} completed`, 
                                    progress 
                                }} 
                                : msg
                            ));         
                        }                           
                    }
                }
            }
        } catch (err) {
            if (err.name === 'AbortError') return; // User cancelled
            
            // Remove the loader message and add error message
            setMessages(prev => prev.filter(msg => msg.type !== 'enhanced_loader'));
            addMessage('bot', `❌ Blueprint generation failed: ${err.message}`);
            setConversationState('AWAITING_IDEA');
            setGenerationProgress(0);
            showToast('Blueprint generation failed', 'error');
        } finally {
            setGenerationController(null);
        }
    };
    
    if (isWorkspaceVisible && finalBlueprintData) {
        return <WorkspaceView blueprintData={finalBlueprintData} onClose={() => setIsWorkspaceVisible(false)} />;
    }

    const isInputDisabled = conversationState !== 'AWAITING_IDEA' && conversationState !== 'AWAITING_CLARIFICATIONS';

    return (
        <ErrorBoundary>
            <div className="h-screen w-screen bg-zinc-900 flex flex-col font-sans">
                {toast && (
                    <Toast 
                        message={toast.message} 
                        type={toast.type} 
                        onClose={() => setToast(null)} 
                    />
                )}
                
                <header className="h-16 bg-zinc-900 border-b border-zinc-800 px-6 flex items-center justify-center flex-shrink-0 z-10">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <Sparkles className="text-white" size={20} />
                        </div>
                        <h1 className="text-lg font-medium text-zinc-200">The Agentic Architect</h1>
                    </div>
                </header>
                
                <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
                    {messages.map((msg) => {
                        if (msg.type === 'enhanced_loader') {
                            return (
                                <EnhancedLoaderCard 
                                    key={msg.id} 
                                    status={msg.data.status} 
                                    progress={msg.data.progress}
                                    onCancel={generationController ? cancelGeneration : null}
                                />
                            );
                        }
                        if (msg.type === 'result_card') {
                            return (
                                <ResultCard 
                                    key={msg.id} 
                                    onShowWorkspace={() => setIsWorkspaceVisible(true)}
                                    projectData={msg.data.projectData}
                                />
                            );
                        }
                        return <MessageBubble key={msg.id} message={msg} />;
                    })}
                    {isBotTyping && <TypingIndicator />}
                    <div ref={chatEndRef} />
                </div>
                
                <div className="p-4 bg-zinc-900 border-t border-zinc-800">
                    <div className="max-w-4xl mx-auto">
                        <div className="flex items-center gap-3 bg-zinc-800 border border-zinc-700 rounded-xl p-3 focus-within:border-indigo-500 transition-colors">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && !isInputDisabled && handleSendMessage()}
                                placeholder={isInputDisabled ? "AI is working..." : "Describe your project idea or answer the question..."}
                                disabled={isInputDisabled}
                                className="flex-1 bg-transparent text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none disabled:cursor-not-allowed"
                            />
                            <div className="flex items-center gap-2">
                                {conversationState === 'AWAITING_CLARIFICATIONS' && (
                                    <span className="text-xs text-zinc-500 bg-zinc-700 px-2 py-1 rounded">
                                        {currentQuestionIndex + 1}/{clarifyingQuestions.length}
                                    </span>
                                )}
                                <button 
                                    onClick={handleSendMessage}
                                    disabled={isInputDisabled || !inputValue.trim()}
                                    className="p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-zinc-700 disabled:text-zinc-500 transition-all duration-200 hover:scale-105 active:scale-95"
                                >
                                    <Send className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                        
                        {conversationState === 'AWAITING_CLARIFICATIONS' && (
                            <div className="mt-2 text-center">
                                <p className="text-xs text-zinc-500">
                                    Answer {clarifyingQuestions.length} questions to get a personalized blueprint
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </ErrorBoundary>
    );
}