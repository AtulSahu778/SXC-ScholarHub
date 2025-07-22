'use client'

import { useState } from 'react'
import { BookOpen, Users, Award, MessageSquare } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <BookOpen className="h-8 w-8 text-indigo-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">ScholarHub</h1>
            </div>
            <nav className="hidden md:flex space-x-8">
              <a href="#features" className="text-gray-600 hover:text-indigo-600 transition-colors">Features</a>
              <a href="#about" className="text-gray-600 hover:text-indigo-600 transition-colors">About</a>
              <a href="#contact" className="text-gray-600 hover:text-indigo-600 transition-colors">Contact</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Your AI-Powered 
            <span className="text-indigo-600"> Academic Companion</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            Discover, learn, and excel with ScholarHub's intelligent chatbot. 
            Get instant answers to your academic questions and research queries.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-indigo-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-indigo-700 transition-colors shadow-lg">
              Get Started
            </button>
            <button className="bg-white text-indigo-600 px-8 py-4 rounded-lg font-semibold border border-indigo-200 hover:border-indigo-300 transition-colors">
              Learn More
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Powerful Features for Academic Success
            </h3>
            <p className="text-xl text-gray-600">
              Everything you need to enhance your academic journey
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-8 rounded-xl shadow-lg">
              <MessageSquare className="h-12 w-12 text-indigo-600 mb-4" />
              <h4 className="text-xl font-semibold text-gray-900 mb-3">AI Chat Assistant</h4>
              <p className="text-gray-600">
                Get instant answers to your academic questions with our advanced AI chatbot powered by Gemini 2.0 Flash.
              </p>
            </div>
            
            <div className="bg-gradient-to-br from-purple-50 to-pink-100 p-8 rounded-xl shadow-lg">
              <Users className="h-12 w-12 text-purple-600 mb-4" />
              <h4 className="text-xl font-semibold text-gray-900 mb-3">Collaborative Learning</h4>
              <p className="text-gray-600">
                Connect with fellow scholars, share insights, and learn together in our collaborative environment.
              </p>
            </div>
            
            <div className="bg-gradient-to-br from-green-50 to-emerald-100 p-8 rounded-xl shadow-lg">
              <Award className="h-12 w-12 text-emerald-600 mb-4" />
              <h4 className="text-xl font-semibold text-gray-900 mb-3">Academic Excellence</h4>
              <p className="text-gray-600">
                Track your progress, set goals, and achieve academic excellence with personalized insights.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h3 className="text-3xl font-bold text-white mb-6">
            Ready to Transform Your Academic Journey?
          </h3>
          <p className="text-xl text-indigo-100 mb-8">
            Start chatting with our AI assistant and unlock your potential today.
          </p>
          <button className="bg-white text-indigo-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-50 transition-colors shadow-lg">
            Try AI Chat Now
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center mb-4 md:mb-0">
              <BookOpen className="h-6 w-6 text-indigo-400 mr-2" />
              <span className="text-lg font-semibold">ScholarHub</span>
            </div>
            <p className="text-gray-400">
              © 2025 ScholarHub. Empowering academic excellence with AI.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}