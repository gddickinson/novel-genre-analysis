// Entry point: registers the page modules (loaded on first visit), sets the mode line, draws the background, starts
// the router.
import { start, route, lazy, app, $, isStatic } from './core.js';
import { background } from './background.js';

const PAGES = {
  'home.js': ['home', 'about'], 'genres.js': ['genres', 'genre'], 'traits.js': ['traits'], 'tree.js': ['tree'],
  'distance.js': ['distance'], 'timeline.js': ['timeline'], 'analysis.js': ['analysis'], 'guides.js': ['guides', 'guide'],
};
lazy(Object.fromEntries(Object.entries(PAGES).flatMap(([file, names]) => names.map(n => [n, () => import('./' + file)]))));

route('notfound', () => { app().innerHTML = '<h1>Not found</h1><p><a href="#/">Back to the start</a></p>'; });

$('#mode').textContent = isStatic() ? 'static site (tree and distances computed in your browser)' : 'local app';
background($('#bg'));
start();
