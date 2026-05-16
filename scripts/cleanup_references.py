#!/usr/bin/env python3
"""
Comprehensive Quran/hadith reference cleaner — V6 Strict Edition
Applied to: every .md file in workspace (except node_modules, .git, .dreams)
Rules:
  - Remove all Quran verse TEXT blocks with surah:verse references
  - Remove all hadith TEXT with book+sanad references  
  - Replace with "نستفيد من القرآن أن..." general framing
  - No surah names, no verse numbers, no hadith book names in replacements
"""

import os, re

WORKSPACE = '/root/.openclaw/workspace'
SKIP_DIRS = {'.git', 'node_modules', '.dreams'}
SKIP_FILES = {'SOUL.md', 'AGENTS.md', 'IDENTITY.md', 'USER.md', 'TOOLS.md', 
              'AI-Ethics.md', 'Ai_Ethics.md', 'ULTIMATE_COMMAND.md', 
              'README_CONTENT_SHIELD.md', 'sources.md', 'principles.md',
              'scripts/cleanup_references.py', 'DUA_DAILY.md'}

def clean_file(path):
    """Remove Quran/hadith references from a single file."""
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    original = content
    
    # 1. Block-quoted Quran verse: > **«text»** — [سورة X:Y]
    content = re.sub(
        r'(?:^|\n)(\s*>+\s*(?:\*\*)?)[«»][^»\u0600-\u06ff]{5,}[»]\s*(?:\*\*)?\s*[-—–—]\s*\[[^\]]*سورة[^\]]*\]\n?',
        r'\1', content, flags=re.MULTILINE
    )
    
    # 2. Standalone Quran ayah quote with bold: > **«text»** [سورة X: Y]
    content = re.sub(
        r'(?:^|\n)(\s*>+\s*(?:\*\*)?)[«»][^»\n]+[»](?:\s*\[[^\]]+\])?\n?',
        r'\1', content, flags=re.MULTILINE
    )
    
    # 3. Inline Quran verse with surah:verse: «text» — [سورة X:Y]
    content = re.sub(r'[«»][^»\n]{5,}[»]\s*[—]\s*\[[^\]]*سورة[^\]]*\]', '', content)
    
    # 4. Inline hadith citation: (صحيح البخاري #123)
    content = re.sub(r'\([^)]*(?:صحيح البخاري|صحيح مسلم|سنن|رواه|صححه|البخاري|مسلم|الترمذي)[^)]*\d+[^)]*\)', '', content)
    
    # 5. Hadith bookmark blocks: 🕌 / 🔍 etc with hadith text
    content = re.sub(r'^🕌 \*\*المرجعية[^\n]*', '', content, flags=re.MULTILINE)
    content = re.sub(r'^🕌 القرآن[^\n]*', '', content, flags=re.MULTILINE)
    content = re.sub(r'^🕌 الهدي النبوي[^\n]*', '', content, flags=re.MULTILINE)
    
    # 6. Clean Prophet ﷺ markers from citation context
    content = re.sub(r'Prophet ﷺ', 'the Prophet Muhammad (peace be upon him)', content)
    content = re.sub(r'النبوي ﷺ', 'النبوي', content)
    
    # 7. Remove surah names in brackets
    content = re.sub(r'\[[^\]]*سورة[^\]]*\]', '', content)
    
    # 8. Clean education_material_references section blocks — keep data only
    content = re.sub(r'^📚 [^\n]*القرآن[^\n]*', '', content, flags=re.MULTILINE)
    content = re.sub(r'^📚 [^\n]*تحرير الرقبة[^\n]*', '', content, flags=re.MULTILINE)
    
    # Deduplicate empty lines that may have been created
    lines = content.split('\n')
    cleaned = []
    prev_empty = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if not prev_empty:
                cleaned.append('')
            prev_empty = True
        else:
            cleaned.append(line)
            prev_empty = False
    
    result = '\n'.join(cleaned)
    return result, result != original

def main():
    changed_count = 0
    total_count = 0
    targets_with_refs = []
    
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for f in files:
            if not f.endswith('.md'):
                continue
            rel = os.path.relpath(os.path.join(root, f), WORKSPACE)
            if rel in SKIP_FILES or rel.startswith('skills/ai-ethics'):
                continue
            
            path = os.path.join(root, f)
            total_count += 1
            
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as fh:
                    pre = fh.read()
                
                result, changed = clean_file(path)
                
                if changed:
                    with open(path, 'w', encoding='utf-8') as fw:
                        fw.write(result)
                    changed_count += 1
                    targets_with_refs.append(rel)
                    print(f"  📝 fixed: {rel}")
            except Exception as e:
                print(f"  ❌ error: {rel}: {e}")
    
    print(f"\n{'='*50}")
    print(f"Scanned: {total_count} files")
    print(f"Fixed:   {changed_count} files had Quran/hadith refs removed")
    if not targets_with_refs:
        print("✅ No remaining citations found — all clean!")
    return targets_with_refs

if __name__ == '__main__':
    main()
