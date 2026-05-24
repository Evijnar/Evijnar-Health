/* Lightweight framer-motion shim
   Tries to require 'framer-motion'. If unavailable, exports minimal fallbacks
   so the app can build without the dependency. This file is intentionally
   CommonJS-friendly to avoid bundler errors when the package is missing.
*/

import React from 'react';

let motion: any;
let AnimatePresence: any;
let useReducedMotion: any;

try {
  // Use require to avoid static ESM import causing build failure when package missing
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const fm = require('framer-motion');
  motion = fm.motion;
  AnimatePresence = fm.AnimatePresence || (({ children }: any) => children);
  useReducedMotion = fm.useReducedMotion || (() => false);
} catch (err) {
  // Fallback implementations
  const passthrough = (el: string) => (
    ({ children, ...props }: any) => React.createElement(el, props, children)
  );

  motion = new Proxy({}, {
    get: (_target, prop) => passthrough('div'),
  });

  AnimatePresence = ({ children }: any) => children;
  useReducedMotion = () => true;
}

export { motion, AnimatePresence, useReducedMotion };
