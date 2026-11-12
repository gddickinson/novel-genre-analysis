// Shared bits for the genre pages: date formatting, era buckets (by date only) and their colours, genre links,
// and the cached genre list.
import { api, esc } from './core.js';

export const ERAS = [
  { key: 'ancient', label: 'Before 500 CE', max: 499, color: '#c77dff' },
  { key: 'medieval', label: '500 to 1699', max: 1699, color: '#ff8fab' },
  { key: 'c18', label: '1700 to 1899', max: 1899, color: '#f5c451' },
  { key: 'c20a', label: '1900 to 1959', max: 1959, color: '#7ee081' },
  { key: 'c20b', label: '1960 to 1999', max: 1999, color: '#4cc9f0' },
  { key: 'c21', label: '2000 onward', max: Infinity, color: '#8fa8ff' },
];
export const eraOf = date => ERAS.find(e => date <= e.max);
export const fmtDate = d => (d < 0 ? `${-d} BCE` : `${d}`);
export const href = name => '#/genre/' + encodeURIComponent(name);
export const glink = name => `<a href="${href(name)}">${esc(name)}</a>`;
export const swatch = date => `<span class="sw" style="background:${eraOf(date).color}" aria-hidden="true"></span>`;
export const legend = () => `<div class="legend">${ERAS.map(e => `<span><i style="background:${e.color}"></i>${e.label}</span>`).join('')}</div>`;

export async function genreList() { return api('/genres'); }
export async function genreMap() { return Object.fromEntries((await genreList()).map(g => [g.name, g])); }

