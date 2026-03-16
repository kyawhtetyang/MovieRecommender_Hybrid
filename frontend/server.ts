import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import session from 'express-session';
import cookieParser from 'cookie-parser';

async function startServer() {
  const app = express();
  const PORT = 3000;

  // Middleware
  app.use(express.urlencoded({ extended: true }));
  app.use(cookieParser());
  app.use(session({
    secret: 'movie-rec-secret',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false } // Set to true if using HTTPS
  }));

  // --- Mock Backend Routes (Aligning with Flask Backend) ---

  // Helper to render a simple HTML page that looks like the UI
  const renderMockPage = (title: string, content: string) => `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${title} - MovieRec</title>
      <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-zinc-50 font-sans text-zinc-900">
      <nav class="bg-white border-b border-zinc-200 py-4">
        <div class="max-w-7xl mx-auto px-4 flex justify-between items-center">
          <a href="/" class="font-bold text-xl text-indigo-600">MovieRec</a>
          <div class="flex gap-4">
            <a href="/dashboard" class="text-sm font-medium text-zinc-600 hover:text-zinc-900">Dashboard</a>
            <a href="/logout" class="text-sm font-medium text-red-600">Logout</a>
          </div>
        </div>
      </nav>
      <main class="max-w-4xl mx-auto py-20 px-4">
        <div class="bg-white p-12 rounded-[2.5rem] shadow-xl border border-zinc-100">
          ${content}
        </div>
        <div class="mt-12 text-center">
          <a href="/" class="text-indigo-600 font-semibold hover:underline">← Back to React UI</a>
        </div>
      </main>
    </body>
    </html>
  `;

  // POST /signup
  app.post('/signup', (req, res) => {
    const { username, password } = req.body;
    console.log(`Signup attempt: ${username}`);
    // In a real app, create user here
    res.redirect('/login');
  });

  // POST /login
  app.post('/login', (req, res) => {
    const { username, password } = req.body;
    console.log(`Login attempt: ${username}`);
    if (username && password) {
      (req.session as any).user = username;
      res.redirect('/dashboard');
    } else {
      res.status(401).send('Invalid credentials');
    }
  });

  // GET /dashboard
  app.get('/dashboard', (req, res, next) => {
    if (!(req.session as any).user) {
      return res.redirect('/login');
    }
    // If it's a browser request for HTML, render mock dashboard
    if (req.headers.accept?.includes('text/html')) {
      return res.send(renderMockPage('Dashboard', `
        <h1 class="text-4xl font-black mb-4">Welcome, ${(req.session as any).user}!</h1>
        <p class="text-zinc-500 mb-8">This is a server-rendered dashboard simulating your Flask backend.</p>
        <div class="bg-indigo-50 p-6 rounded-2xl border border-indigo-100 mb-8">
          <h2 class="font-bold text-indigo-900 mb-2">Your Recommendations</h2>
          <ul class="list-disc list-inside text-indigo-700 space-y-1">
            <li>The Shawshank Redemption</li>
            <li>The Godfather</li>
            <li>Schindler's List</li>
          </ul>
        </div>
        <a href="/rate" class="inline-block px-6 py-3 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-all">Rate a Movie</a>
      `));
    }
    next();
  });

  // GET /logout
  app.get('/logout', (req, res) => {
    req.session.destroy(() => {
      res.redirect('/');
    });
  });

  // POST /rate
  app.post('/rate', (req, res) => {
    const { movie_id, rating } = req.body;
    console.log(`Rating submitted: Movie ${movie_id}, Rating ${rating}`);
    res.redirect('/dashboard');
  });

  // GET /recommend
  app.get('/recommend', (req, res) => {
    const userId = req.query.user_id;
    res.send(renderMockPage(`Recommendations for User ${userId}`, `
      <h1 class="text-4xl font-black mb-4">Recommendations for User #${userId}</h1>
      <p class="text-zinc-500 mb-8">Based on profile #${userId}, we suggest these titles:</p>
      <div class="grid grid-cols-1 gap-4">
        <div class="p-4 bg-zinc-50 rounded-xl border border-zinc-200">
          <h3 class="font-bold">Movie Alpha</h3>
          <p class="text-sm text-zinc-500">Match: 98%</p>
        </div>
        <div class="p-4 bg-zinc-50 rounded-xl border border-zinc-200">
          <h3 class="font-bold">Movie Beta</h3>
          <p class="text-sm text-zinc-500">Match: 95%</p>
        </div>
      </div>
    `));
  });

  // --- Vite Integration ---

  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
