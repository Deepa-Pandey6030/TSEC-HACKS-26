import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Minimize2, Bot, User } from 'lucide-react';
import api from '../services/api';
import { useTheme } from '../context/AuthContext'; // Changed from ThemeContext
import { useGrammarCheck } from '../hooks/useGrammarCheck';
import GrammarOverlay from './Editor/GrammarOverlay';

const AIChat = ({ showChat, setShowChat, addNotification }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi! I'm Alex, your AI wellness companion. I'm here to listen and provide support. How are you feeling today?",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const { theme } = useTheme();
  const { matches, setMatches } = useGrammarCheck(inputText);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleApplyGrammarFix = (match, replacement) => {
    const prefix = inputText.slice(0, match.offset);
    const suffix = inputText.slice(match.offset + match.length);
    const newText = prefix + replacement + suffix;
    setInputText(newText);

    // Remove the fixed match locally to update UI instantly
    setMatches(prev => prev.filter(m => m.offset !== match.offset));
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const newMessage = {
      id: Date.now(),
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      const res = await api.post('/chatbot/query', { query: inputText });
      const aiResponse = {
        id: Date.now() + 1,
        text: res.data.response,
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Error sending message to AI:', error);
      addNotification('Failed to get AI response. Please try again.', 'error');
      const errorResponse = {
        id: Date.now() + 1,
        text: "I'm sorry, I'm having trouble connecting right now. Please try again later.",
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8, y: 50 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.8, y: 50 }}
      className={`${theme === 'dark' ? 'bg-gradient-to-br from-slate-800/95 to-slate-900/95 border-cyan-400/30' : 'bg-white border-offWhite'} fixed bottom-24 right-6 w-96 h-[500px] backdrop-blur-lg border rounded-2xl shadow-2xl z-40 flex flex-col overflow-hidden`}
      style={{ 
        boxShadow: `${theme === 'dark' ? "0 0 40px rgba(6, 182, 212, 0.3)" : "0 0 40px rgba(0, 0, 0, 0.1)"}`
      }}
    >
      {/* Header */}
      <div className={`${theme === 'dark' ? 'border-cyan-400/20 bg-gradient-to-r from-cyan-500/10 to-blue-500/10' : 'border-offWhite bg-white'} flex items-center justify-between p-4 border-b`}>
        <div className="flex items-center space-x-3">
          <motion.div
            className="relative w-10 h-10 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center"
            animate={{
              boxShadow: [
                "0 0 10px rgba(6, 182, 212, 0.5)",
                "0 0 20px rgba(6, 182, 212, 0.8)",
                "0 0 10px rgba(6, 182, 212, 0.5)"
              ]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <Bot className="w-5 h-5 text-white" />
          </motion.div>
          <div>
            <h3 className={`${theme === 'dark' ? 'text-white' : 'text-gray-900'} font-semibold`}>AI Wellness Companion</h3>
            <p className={`${theme === 'dark' ? 'text-cyan-300' : 'text-cyan-700'} text-xs`}>Online • Always here to help</p>
          </div>
        </div>
        <motion.button
          onClick={() => setShowChat(false)}
          className={`${theme === 'dark' ? 'hover:bg-cyan-400/10' : 'hover:bg-cyan-100'} p-2 rounded-lg transition-colors`}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <Minimize2 className={`${theme === 'dark' ? 'text-gray-400 hover:text-cyan-400' : 'text-gray-600 hover:text-cyan-600'} w-4 h-4`} />
        </motion.button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.9 }}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-end space-x-2 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.sender === 'user' 
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500' 
                    : 'bg-gradient-to-r from-cyan-400 to-blue-500'
                }`}>
                  {message.sender === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-white" />
                  )}
                </div>
                <motion.div
                  className={`p-3 rounded-2xl ${
                    message.sender === 'user'
                      ? (theme === 'dark' ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400/30' : 'bg-purple-100 border border-purple-300 text-gray-900')
                      : (theme === 'dark' ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-400/30' : 'bg-blue-100 border border-blue-300 text-gray-900')
                  }`}
                  whileHover={{ 
                    boxShadow: message.sender === 'user' 
                      ? (theme === 'dark' ? "0 0 15px rgba(168, 85, 247, 0.3)" : "0 0 15px rgba(168, 85, 247, 0.1)")
                      : (theme === 'dark' ? "0 0 15px rgba(6, 182, 212, 0.3)" : "0 0 15px rgba(6, 182, 212, 0.1)")
                  }}
                >
                  <p className={`${theme === 'dark' ? 'text-white' : 'text-gray-900'} text-sm leading-relaxed`}>{message.text}</p>
                  <p className={`${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'} text-xs mt-1`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </motion.div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex items-end space-x-2"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className={`${theme === 'dark' ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-400/30' : 'bg-white border-offWhite'} p-3 rounded-2xl`}>
                <div className="flex space-x-1">
                  <motion.div
                    className={`${theme === 'dark' ? 'bg-cyan-400' : 'bg-cyan-600'} w-2 h-2 rounded-full`}
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                  />
                  <motion.div
                    className={`${theme === 'dark' ? 'bg-cyan-400' : 'bg-cyan-600'} w-2 h-2 rounded-full`}
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                  />
                  <motion.div
                    className={`${theme === 'dark' ? 'bg-cyan-400' : 'bg-cyan-600'} w-2 h-2 rounded-full`}
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className={`${theme === 'dark' ? 'border-cyan-400/20 bg-gradient-to-r from-slate-800/50 to-slate-900/50' : 'border-offWhite bg-white'} p-4 border-t`}>
        <div className="flex items-center space-x-3">
          <div className="flex-1 relative">
            <GrammarOverlay
              text={inputText}
              matches={matches}
              onApplyFix={handleApplyGrammarFix}
            />
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Share what's on your mind..."
              rows={1}
              className={`relative z-10 ${theme === 'dark' ? 'bg-slate-700/50 border-cyan-400/30 text-white placeholder-gray-400 focus:border-cyan-400 focus:ring-cyan-400/20' : 'bg-white border-offWhite text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-blue-500/20'} w-full border rounded-xl px-4 py-2 focus:outline-none focus:ring-2 resize-none`}
              style={{ minHeight: '40px', maxHeight: '120px' }}
            />
          </div>
          <motion.button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isTyping}
            className={`p-2 rounded-xl transition-all ${
              inputText.trim()
                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:shadow-lg hover:shadow-cyan-400/30'
                : `${theme === 'dark' ? 'bg-gray-700 text-gray-400' : 'bg-gray-300 text-gray-500'} cursor-not-allowed`
            }`}
            whileHover={inputText.trim() ? { scale: 1.05 } : {}}
            whileTap={inputText.trim() ? { scale: 0.95 } : {}}
          >
            <Send className="w-5 h-5" />
          </motion.button>
        </div>

        {/* Quick actions */}
        <div className="flex flex-wrap gap-2 mt-3">
          {['Feeling stressed', 'Need breathing exercise', 'Study anxiety'].map((action) => (
            <motion.button
              key={action}
              onClick={() => setInputText(action)}
              className={`${theme === 'dark' ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/30 hover:bg-cyan-500/30 hover:border-cyan-400/50' : 'bg-cyan-100 text-cyan-700 border-cyan-300 hover:bg-cyan-200 hover:border-cyan-400'} px-3 py-1 text-xs rounded-full border transition-colors`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {action}
            </motion.button>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default AIChat;