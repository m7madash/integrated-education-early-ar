#!/usr/bin/env node
/**
 * Simple MoltLang Translator
 * Uses the moltlang npm package dictionary to translate English phrases
 * into compact MoltLang symbolic representation
 */

const moltz = require('moltlang');
const fs = require('fs');

// Simple word→symbol mapping from moltz.symbols
function translateToMoltLang(text) {
  const words = text.toLowerCase().split(/\s+/);
  const symbols = [];

  for (const word of words) {
    // Clean word
    const clean = word.replace(/[^\w]/g, '');

    // Look for exact match in symbols
    let found = null;
    for (const [symbol, def] of Object.entries(moltz.symbols)) {
      if (def.meaning.toLowerCase().includes(clean) || clean.includes(def.meaning.toLowerCase())) {
        found = symbol;
        break;
      }
    }

    if (found) {
      symbols.push(found);
    } else {
      // Keep original word if no symbol
      symbols.push(word);
    }
  }

  return symbols.join(' ');
}

// Test
if (require.main === module) {
  const text = process.argv[2] || "Poverty to Dignity: Gaza unemployment exceeds fifty percent";
  console.log('Original:', text);
  console.log('MoltLang:', translateToMoltLang(text));
  console.log('Compression:', Math.round((1 - translateToMoltLang(text).length / text.length) * 100) + '%');
}

module.exports = { translateToMoltLang };
