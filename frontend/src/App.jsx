import React, { useState, useRef } from 'react';
import { 
  Upload, 
  Search, 
  FileText, 
  Clock, 
  DollarSign, 
  Loader2, 
  CheckCircle2, 
  AlertCircle,
  BookOpen,
  Trash2,
  ChevronDown,
  ChevronUp,
  ExternalLink
} from 'lucide-react';
import { Analytics } from '@vercel/analytics/react';

// API base URL - update for production
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  // State
  const [activeTab, setActiveTab] = useState('query'); // 'ingest' or 'query'
  const [text, setText] = useState('');
  const [title, setTitle] = useState('');
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [queryResult, setQueryResult] = useState(null);
  const [expandedCitation, setExpandedCitation] = useState(null);
  const fileInputRef = useRef(null);

  // Ingest text
  const handleIngestText = async () => {
    if (!text.trim()) {
      setMessage({ type: 'error', text: 'Please enter some text to ingest' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await fetch(`${API_BASE}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          title: title || 'Untitled Document',
          source: 'user_input'
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: `✓ ${data.message} (${data.processing_time_ms}ms)` 
        });
        setText('');
        setTitle('');
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to ingest text' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` });
    } finally {
      setIsLoading(false);
    }
  };

  // Ingest file
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsLoading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);

    try {
      const response = await fetch(`${API_BASE}/ingest/file`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: `✓ ${data.message} (${data.processing_time_ms}ms)` 
        });
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to upload file' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` });
    } finally {
      setIsLoading(false);
      fileInputRef.current.value = '';
    }
  };

  // Query
  const handleQuery = async () => {
    if (!query.trim()) {
      setMessage({ type: 'error', text: 'Please enter a query' });
      return;
    }

    setIsLoading(true);
    setMessage(null);
    setQueryResult(null);

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          top_k: 10,
          rerank_top_k: 5
        })
      });

      const data = await response.json();

      if (response.ok) {
        setQueryResult(data);
      } else {
        setMessage({ type: 'error', text: data.detail || 'Query failed' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` });
    } finally {
      setIsLoading(false);
    }
  };

  // Clear index
  const handleClearIndex = async () => {
    if (!confirm('Are you sure you want to clear all documents from the knowledge base?')) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/clear`, { method: 'DELETE' });
      const data = await response.json();
      
      if (response.ok) {
        setMessage({ type: 'success', text: 'Knowledge base cleared successfully' });
        setQueryResult(null);
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to clear' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` });
    } finally {
      setIsLoading(false);
    }
  };

  // Render answer with citation highlights
  const renderAnswerWithCitations = (answer) => {
    if (!answer) return null;
    
    // Replace [1], [2], etc. with clickable spans
    const parts = answer.split(/(\[\d+\])/g);
    
    return parts.map((part, index) => {
      const match = part.match(/\[(\d+)\]/);
      if (match) {
        const citationNum = parseInt(match[1]);
        return (
          <button
            key={index}
            className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-blue-500 rounded hover:bg-blue-600 mx-0.5"
            onClick={() => setExpandedCitation(expandedCitation === citationNum ? null : citationNum)}
            title={`View source ${citationNum}`}
          >
            {citationNum}
          </button>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <BookOpen className="w-8 h-8 text-blue-500" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">RAG Knowledge Assistant</h1>
                <p className="text-sm text-gray-500">Retrieval-Augmented Generation with Citations</p>
              </div>
            </div>
            <button
              onClick={handleClearIndex}
              className="flex items-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear Knowledge Base
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6 w-fit">
          <button
            onClick={() => setActiveTab('ingest')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'ingest' 
                ? 'bg-white text-blue-600 shadow' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Upload className="w-4 h-4 inline mr-2" />
            Add Documents
          </button>
          <button
            onClick={() => setActiveTab('query')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'query' 
                ? 'bg-white text-blue-600 shadow' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Search className="w-4 h-4 inline mr-2" />
            Ask Questions
          </button>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center ${
            message.type === 'success' 
              ? 'bg-green-50 text-green-700 border border-green-200' 
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5 mr-2 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
            )}
            {message.text}
          </div>
        )}

        {/* Ingest Tab */}
        {activeTab === 'ingest' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Text Input */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-blue-500" />
                Paste Text
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Document Title (optional)
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g., Company Handbook"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Content
                  </label>
                  <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Paste your document content here..."
                    rows={12}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  />
                </div>

                <button
                  onClick={handleIngestText}
                  disabled={isLoading || !text.trim()}
                  className="w-full py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5 mr-2" />
                      Add to Knowledge Base
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* File Upload */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Upload className="w-5 h-5 mr-2 text-blue-500" />
                Upload File
              </h2>

              <div 
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.md,.csv"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 mb-2">
                  Click to upload or drag and drop
                </p>
                <p className="text-sm text-gray-400">
                  Supported: .txt, .md, .csv
                </p>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h3 className="font-medium text-blue-900 mb-2">Chunking Strategy</h3>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Chunk size: 1,000 tokens</li>
                  <li>• Overlap: 100 tokens (10%)</li>
                  <li>• Sentence-aware splitting</li>
                  <li>• Metadata preserved for citations</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Query Tab */}
        {activeTab === 'query' && (
          <div className="space-y-6">
            {/* Query Input */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Search className="w-5 h-5 mr-2 text-blue-500" />
                Ask a Question
              </h2>

              <div className="flex space-x-4">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                  placeholder="What would you like to know?"
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
                />
                <button
                  onClick={handleQuery}
                  disabled={isLoading || !query.trim()}
                  className="px-8 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="w-5 h-5 mr-2" />
                      Search
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Loading State */}
            {isLoading && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
                <div className="flex justify-center mb-4">
                  <div className="loading-dot w-3 h-3 bg-blue-500 rounded-full mx-1"></div>
                  <div className="loading-dot w-3 h-3 bg-blue-500 rounded-full mx-1"></div>
                  <div className="loading-dot w-3 h-3 bg-blue-500 rounded-full mx-1"></div>
                </div>
                <p className="text-gray-600">Searching knowledge base and generating answer...</p>
              </div>
            )}

            {/* Query Results */}
            {queryResult && !isLoading && (
              <div className="space-y-6">
                {/* Answer */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Answer</h2>
                  <div className="prose prose-blue max-w-none text-gray-700 leading-relaxed">
                    {renderAnswerWithCitations(queryResult.answer)}
                  </div>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                    <div className="flex items-center text-gray-500 mb-1">
                      <Clock className="w-4 h-4 mr-2" />
                      <span className="text-sm">Total Time</span>
                    </div>
                    <p className="text-xl font-semibold text-gray-900">
                      {queryResult.processing_time_ms}ms
                    </p>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                    <div className="flex items-center text-gray-500 mb-1">
                      <Search className="w-4 h-4 mr-2" />
                      <span className="text-sm">Retrieval</span>
                    </div>
                    <p className="text-xl font-semibold text-gray-900">
                      {queryResult.retrieval_time_ms}ms
                    </p>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                    <div className="flex items-center text-gray-500 mb-1">
                      <FileText className="w-4 h-4 mr-2" />
                      <span className="text-sm">Tokens Used</span>
                    </div>
                    <p className="text-xl font-semibold text-gray-900">
                      {queryResult.tokens_used?.total_tokens || 0}
                    </p>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                    <div className="flex items-center text-gray-500 mb-1">
                      <DollarSign className="w-4 h-4 mr-2" />
                      <span className="text-sm">Est. Cost</span>
                    </div>
                    <p className="text-xl font-semibold text-gray-900">
                      ${queryResult.cost_estimate?.toFixed(5) || '0.00000'}
                    </p>
                  </div>
                </div>

                {/* Citations */}
                {queryResult.citations && queryResult.citations.length > 0 && (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">
                      Sources ({queryResult.citations.length})
                    </h2>
                    
                    <div className="space-y-3">
                      {queryResult.citations.map((citation, index) => (
                        <div 
                          key={index}
                          className={`border rounded-lg transition-all ${
                            expandedCitation === citation.id 
                              ? 'border-blue-300 bg-blue-50' 
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <button
                            onClick={() => setExpandedCitation(
                              expandedCitation === citation.id ? null : citation.id
                            )}
                            className="w-full p-4 text-left flex items-start justify-between"
                          >
                            <div className="flex items-start space-x-3">
                              <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded text-sm font-bold flex items-center justify-center">
                                {citation.id}
                              </span>
                              <div>
                                <p className="font-medium text-gray-900">{citation.title}</p>
                                <p className="text-sm text-gray-500">
                                  Source: {citation.source} • 
                                  Relevance: {(citation.relevance_score * 100).toFixed(1)}%
                                </p>
                              </div>
                            </div>
                            {expandedCitation === citation.id ? (
                              <ChevronUp className="w-5 h-5 text-gray-400" />
                            ) : (
                              <ChevronDown className="w-5 h-5 text-gray-400" />
                            )}
                          </button>
                          
                          {expandedCitation === citation.id && (
                            <div className="px-4 pb-4 pt-0">
                              <div className="ml-9 p-3 bg-white rounded border border-gray-200">
                                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                                  {citation.text}
                                </p>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {!queryResult && !isLoading && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                <Search className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Search</h3>
                <p className="text-gray-500 max-w-md mx-auto">
                  Enter a question above to search through your knowledge base. 
                  Make sure you've added some documents first!
                </p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 mt-12 py-6 text-center text-sm text-gray-500">
        <p>Mini RAG • Powered by Gemini Embeddings, Cohere Rerank, and Groq LLM</p>
        <p className="mt-1">Vector DB: Pinecone • Chunking: 1000 tokens with 10% overlap</p>
        <p className="mt-1">Created by <a className='text-blue-500 hover:underline' href="https://github.com/shubhankitsingh" target="_blank" rel="noopener noreferrer">Shubhankit</a></p>
      </footer>
      <Analytics />
    </div>
  );
}

export default App;
