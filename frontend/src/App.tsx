/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { 
  Search,
  User as UserIcon,
  Home as HomeIcon,
  History,
  Film,
  Star,
  Plus
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

// --- Types ---

interface Movie {
  id: number;
  title: string;
  genre: string;
  rating: number;
  year: number;
  description: string;
}

// --- Mock Data ---

const MOVIES: Movie[] = [
  { id: 101, title: "Inception", genre: "Sci-Fi", rating: 4.8, year: 2010, description: "A thief who steals corporate secrets through dream-sharing." },
  { id: 102, title: "The Dark Knight", genre: "Action", rating: 4.9, year: 2008, description: "Batman faces the Joker in Gotham City." },
  { id: 103, title: "Interstellar", genre: "Sci-Fi", rating: 4.7, year: 2014, description: "Explorers travel through a wormhole to save humanity." },
  { id: 104, title: "Pulp Fiction", genre: "Crime", rating: 4.9, year: 1994, description: "Intertwining lives of mob hitmen and criminals." },
  { id: 105, title: "The Matrix", genre: "Sci-Fi", rating: 4.7, year: 1999, description: "A hacker discovers the true nature of reality." },
  { id: 106, title: "Parasite", genre: "Thriller", rating: 4.6, year: 2019, description: "Class discrimination in a symbiotic relationship." },
  { id: 107, title: "Joker", genre: "Drama", rating: 4.4, year: 2019, description: "A troubled comedian is mistreated by society." },
  { id: 108, title: "The Godfather", genre: "Crime", rating: 4.9, year: 1972, description: "The patriarch of a crime dynasty transfers control." },
];

// --- Components ---

const Header = ({ setView }: { setView: (v: string) => void }) => (
  <header className="fixed top-0 left-0 right-0 h-14 bg-[#0f0f0f] flex items-center justify-between px-2 sm:px-4 z-50">
    <div className="flex items-center gap-1 sm:gap-4">
      <div className="flex items-center gap-2 cursor-pointer p-2" onClick={() => setView('home')}>
        <div className="bg-yt-red p-1.5 rounded-lg">
          <Film className="w-5 h-5 text-white" />
        </div>
        <span className="font-bold text-base sm:text-lg tracking-tight">Movie Recommender</span>
      </div>
    </div>

    <div className="hidden md:flex items-center flex-1 max-w-2xl mx-10">
      <div className="flex flex-1 items-center bg-[#121212] border border-zinc-800 rounded-l-full px-4 py-1.5 focus-within:border-blue-500">
        <input 
          type="text" 
          placeholder="Search movies..." 
          className="bg-transparent w-full outline-none text-sm placeholder:text-zinc-500"
        />
      </div>
      <button className="bg-zinc-800 border border-l-0 border-zinc-800 px-5 py-1.5 rounded-r-full hover:bg-zinc-700 transition-colors">
        <Search className="w-5 h-5" />
      </button>
    </div>

    <div className="flex items-center gap-2">
      <button className="p-2 hover:bg-white/10 rounded-full transition-colors md:hidden">
        <Search className="w-6 h-6" />
      </button>
      <button
        onClick={() => setView('login')}
        className="px-3 py-1.5 rounded-full border border-white/20 text-xs font-semibold hover:bg-white/10 transition-colors"
      >
        Sign In
      </button>
    </div>
  </header>
);

const BottomNav = ({ currentView, setView }: { currentView: string, setView: (v: string) => void }) => (
  <nav className="fixed bottom-0 left-0 right-0 h-14 bg-[#0f0f0f] border-t border-zinc-800 flex items-center justify-around sm:hidden z-50">
    <button onClick={() => setView('home')} className={`flex flex-col items-center gap-1 ${currentView === 'home' ? 'text-white' : 'text-zinc-400'}`}>
      <HomeIcon className="w-6 h-6" />
      <span className="text-[10px]">Home</span>
    </button>
    <button onClick={() => setView('rate')} className={`flex flex-col items-center gap-1 ${currentView === 'rate' ? 'text-white' : 'text-zinc-400'}`}>
      <Star className="w-6 h-6" />
      <span className="text-[10px]">Rate</span>
    </button>
    <button onClick={() => setView('dashboard')} className={`flex flex-col items-center gap-1 ${currentView === 'dashboard' ? 'text-white' : 'text-zinc-400'}`}>
      <History className="w-6 h-6" />
      <span className="text-[10px]">Dashboard</span>
    </button>
  </nav>
);

const Sidebar = ({ currentView, setView }: { currentView: string, setView: (v: string) => void }) => (
  <aside className="fixed left-0 top-14 bottom-0 w-[72px] lg:w-60 bg-[#0f0f0f] overflow-y-auto no-scrollbar hidden sm:flex flex-col py-2 z-40">
    <div className="px-1 lg:px-3 space-y-1">
      {[
        { id: 'home', label: 'Home', icon: HomeIcon },
        { id: 'rate', label: 'Rate Movies', icon: Star },
        { id: 'dashboard', label: 'Dashboard', icon: History },
      ].map((item) => (
        <button 
          key={item.id}
          onClick={() => setView(item.id)}
          className={`w-full flex flex-col lg:flex-row items-center gap-1 lg:gap-6 p-2 lg:px-4 lg:py-2.5 rounded-xl transition-colors ${currentView === item.id ? 'bg-white/10 font-bold' : 'hover:bg-white/10'}`}
        >
          <item.icon className="w-6 h-6" />
          <span className="text-[10px] lg:text-sm text-center lg:text-left">{item.label}</span>
        </button>
      ))}
    </div>
  </aside>
);

const MovieCard = ({ movie, setView }: { movie: Movie, setView: (v: string) => void, key?: React.Key }) => (
  <div className="group cursor-pointer" onClick={() => setView('rate')}>
    <div className="aspect-video bg-zinc-800 rounded-xl overflow-hidden relative mb-3">
      <img 
        src={`https://picsum.photos/seed/${movie.title}/640/360`} 
        alt={movie.title} 
        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        referrerPolicy="no-referrer"
      />
      <div className="absolute bottom-2 right-2 bg-black/80 px-1.5 py-0.5 rounded text-[10px] font-bold">
        2:14:05
      </div>
    </div>
    <div className="flex gap-3">
      <div className="w-9 h-9 bg-zinc-700 rounded-full flex-shrink-0 flex items-center justify-center overflow-hidden">
        <img src={`https://picsum.photos/seed/${movie.genre}/100/100`} alt="channel" referrerPolicy="no-referrer" />
      </div>
      <div className="flex-1">
        <h3 className="text-sm font-bold line-clamp-2 mb-1 leading-tight">{movie.title}</h3>
        <p className="text-xs text-zinc-400 hover:text-white transition-colors">
          {movie.genre} • {movie.year}
        </p>
        <p className="text-xs text-zinc-400 mt-0.5">Rating {movie.rating.toFixed(1)}</p>
      </div>
    </div>
  </div>
);

const HomeView = ({ setView }: { setView: (v: string) => void }) => (
  <div className="p-4 lg:p-6">
    <div className="flex gap-3 overflow-x-auto no-scrollbar mb-6">
      {['All', 'Sci-Fi', 'Action', 'Crime', 'Thriller', 'Drama', 'Recently uploaded', 'Watched', 'New to you'].map((tag) => (
        <button 
          key={tag} 
          className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${tag === 'All' ? 'bg-white text-black' : 'bg-white/10 hover:bg-white/20'}`}
        >
          {tag}
        </button>
      ))}
    </div>

    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-4 gap-y-10">
      {MOVIES.map((movie) => (
        <MovieCard key={movie.id} movie={movie} setView={setView} />
      ))}
    </div>
  </div>
);

const SignupView = () => (
  <div className="min-h-[calc(100vh-112px)] sm:min-h-[calc(100vh-56px)] flex items-center justify-center px-4">
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-md bg-[#0f0f0f] p-6 sm:p-10 rounded-3xl border border-zinc-800 shadow-2xl"
    >
      <div className="text-center mb-8">
        <Film className="w-12 h-12 text-yt-red mx-auto mb-4" />
        <h2 className="text-2xl font-bold">Create Account</h2>
        <p className="text-sm text-zinc-400 mt-2">Start your movie journey</p>
      </div>
      <form action="/signup" method="POST" className="space-y-4">
        <input 
          type="text" 
          name="username" 
          required 
          className="w-full px-4 py-3 bg-[#121212] border border-zinc-700 rounded-xl focus:border-blue-500 outline-none transition-all"
          placeholder="Username"
        />
        <input 
          type="password" 
          name="password" 
          required 
          className="w-full px-4 py-3 bg-[#121212] border border-zinc-700 rounded-xl focus:border-blue-500 outline-none transition-all"
          placeholder="Password"
        />
        <button type="submit" className="w-full py-3 bg-blue-600 text-white font-bold rounded-full hover:bg-blue-700 transition-colors mt-4">
          Sign Up
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-zinc-400">
        Already have an account? <a href="/login" className="text-blue-400 hover:underline">Sign in</a>
      </p>
    </motion.div>
  </div>
);

const LoginView = () => (
  <div className="min-h-[calc(100vh-112px)] sm:min-h-[calc(100vh-56px)] flex items-center justify-center px-4">
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-md bg-[#0f0f0f] p-6 sm:p-10 rounded-3xl border border-zinc-800 shadow-2xl"
    >
      <div className="text-center mb-8">
        <Film className="w-12 h-12 text-yt-red mx-auto mb-4" />
        <h2 className="text-2xl font-bold">Sign In</h2>
        <p className="text-sm text-zinc-400 mt-2">Welcome back to Movie Recommender</p>
      </div>
      <form action="/login" method="POST" className="space-y-4">
        <input 
          type="text" 
          name="username" 
          required 
          className="w-full px-4 py-3 bg-[#121212] border border-zinc-700 rounded-xl focus:border-blue-500 outline-none transition-all"
          placeholder="Username"
        />
        <input 
          type="password" 
          name="password" 
          required 
          className="w-full px-4 py-3 bg-[#121212] border border-zinc-700 rounded-xl focus:border-blue-500 outline-none transition-all"
          placeholder="Password"
        />
        <button type="submit" className="w-full py-3 bg-blue-600 text-white font-bold rounded-full hover:bg-blue-700 transition-colors mt-4">
          Sign In
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-zinc-400">
        New to Movie Recommender? <a href="/signup" className="text-blue-400 hover:underline">Create account</a>
      </p>
    </motion.div>
  </div>
);

const DashboardView = ({ setView }: { setView: (v: string) => void }) => (
  <div className="p-4 lg:p-8">
      <div className="flex flex-col sm:flex-row justify-between items-center sm:items-center gap-6 mb-10 text-center sm:text-left">
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <div className="w-20 h-20 bg-indigo-600 rounded-full flex items-center justify-center">
            <UserIcon className="w-10 h-10 text-white" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Your Dashboard</h1>
            <p className="text-sm text-zinc-400">@movie_fan • 42 ratings • Active profile</p>
          </div>
        </div>
        <button 
          onClick={() => setView('rate')}
        className="w-full sm:w-auto px-6 py-2 bg-white text-black font-bold rounded-full hover:bg-zinc-200 transition-colors flex items-center justify-center gap-2"
      >
        <Plus className="w-5 h-5" /> Rate Movie
      </button>
    </div>

    <div className="border-b border-zinc-800 mb-8 overflow-x-auto no-scrollbar">
      <div className="flex gap-6 sm:gap-8 min-w-max">
        {['Overview', 'Ratings', 'Recommendations'].map((tab) => (
          <button key={tab} className={`pb-3 text-sm font-bold border-b-2 transition-colors ${tab === 'Overview' ? 'border-white text-white' : 'border-transparent text-zinc-400 hover:text-white'}`}>
            {tab}
          </button>
        ))}
      </div>
    </div>

    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-4 gap-y-10">
      <div className="col-span-full mb-4">
        <h2 className="text-xl font-bold">Recommended for You</h2>
      </div>
      {MOVIES.slice(0, 4).map((movie) => (
        <MovieCard key={movie.id} movie={movie} setView={setView} />
      ))}
    </div>
  </div>
);

const RateView = () => (
  <div className="min-h-[calc(100vh-112px)] sm:min-h-[calc(100vh-56px)] flex items-center justify-center px-4">
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-md bg-[#0f0f0f] p-6 sm:p-10 rounded-3xl border border-zinc-800 shadow-2xl"
    >
      <h2 className="text-2xl font-bold mb-8">Rate Movie</h2>
      <form action="/rate" method="POST" className="space-y-6">
        <div>
          <label className="block text-sm font-bold text-zinc-400 mb-2">Movie ID</label>
          <input 
            type="number" 
            name="movie_id" 
            required 
            className="w-full px-4 py-3 bg-[#121212] border border-zinc-700 rounded-xl focus:border-blue-500 outline-none"
            placeholder="e.g. 101"
          />
        </div>
        <div>
          <label className="block text-sm font-bold text-zinc-400 mb-2">Rating (0-5)</label>
          <input 
            type="number" 
            step="0.1" 
            min="0" 
            max="5" 
            name="rating" 
            required 
            className="w-full px-4 py-3 bg-[#121212] border border-zinc-700 rounded-xl focus:border-blue-500 outline-none"
            placeholder="e.g. 4.5"
          />
        </div>
        <button type="submit" className="w-full py-3 bg-blue-600 text-white font-bold rounded-full hover:bg-blue-700 transition-colors">
          Submit Rating
        </button>
      </form>
    </motion.div>
  </div>
);

// --- Main App ---

export default function App() {
  const [view, setView] = useState('home');

  return (
    <div className="min-h-screen bg-[#0f0f0f] text-white selection:bg-blue-500/30 selection:text-white pb-14 sm:pb-0">
      <Header setView={setView} />
      
      <div className="flex pt-14">
        <Sidebar currentView={view} setView={setView} />
        
        <main className="flex-1 sm:ml-[72px] lg:ml-60 min-h-[calc(100vh-56px)] w-full overflow-x-hidden">
          <AnimatePresence mode="wait">
            <motion.div
              key={view}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {view === 'home' && <HomeView setView={setView} />}
              {view === 'signup' && <SignupView />}
              {view === 'login' && <LoginView />}
              {view === 'dashboard' && <DashboardView setView={setView} />}
              {view === 'rate' && <RateView />}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      <BottomNav currentView={view} setView={setView} />

    </div>
  );
}
