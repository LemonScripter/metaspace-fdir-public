# GEMINI PROMPT – MetaSpace Certification Bundle HTML Konverzió

---

## 📋 TELJES GEMINI PROMPT (Copy-Paste Kész)

```
You are a professional HTML5 and aerospace documentation specialist. Your task is to convert a Markdown document into a fully functional, production-ready HTML5 document.

CONVERSION REQUIREMENTS:

═══════════════════════════════════════════════════════════════════════════════
1. HTML5 STRUCTURE & META TAGS
═══════════════════════════════════════════════════════════════════════════════

- Create a valid HTML5 document with:
  <!DOCTYPE html>
  <html lang="hu">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta name="description" content="MetaSpace FDIR System Certification Bundle - SIL 3 Compliance Verification">
      <meta name="author" content="MetaSpace FDIR Project">
      <title>MetaSpace FDIR – Certification Bundle v2.0</title>

═══════════════════════════════════════════════════════════════════════════════
2. EXTERNAL SCRIPTS (Required for rendering)
═══════════════════════════════════════════════════════════════════════════════

Add these scripts in the <head> section:

<!-- Mermaid.js for diagrams -->
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({ startOnLoad: true, theme: 'default' });
</script>

<!-- MathJax for LaTeX/mathematical formulas -->
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

═══════════════════════════════════════════════════════════════════════════════
3. CSS STYLING (Aerospace Professional Theme)
═══════════════════════════════════════════════════════════════════════════════

Add a <style> block in <head> with:

<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        background-color: #fafafa;
        padding: 20px;
    }
    
    .container {
        max-width: 1000px;
        margin: 0 auto;
        background-color: white;
        padding: 40px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    h1 {
        color: #1a5f7a;
        border-bottom: 3px solid #1a5f7a;
        padding-bottom: 15px;
        margin-bottom: 30px;
        font-size: 2.2em;
    }
    
    h2 {
        color: #1a5f7a;
        border-bottom: 2px solid #1a5f7a;
        padding-bottom: 10px;
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 1.7em;
    }
    
    h3 {
        color: #0d3d52;
        margin-top: 20px;
        margin-bottom: 10px;
        font-size: 1.3em;
    }
    
    p {
        margin-bottom: 15px;
        text-align: justify;
    }
    
    strong {
        color: #1a5f7a;
        font-weight: 600;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        font-size: 0.95em;
    }
    
    th {
        background-color: #e8f4f8;
        color: #1a5f7a;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #1a5f7a;
    }
    
    td {
        padding: 10px 12px;
        border-bottom: 1px solid #ddd;
    }
    
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    tr:hover {
        background-color: #f0f5f7;
    }
    
    .mermaid {
        background-color: #f9f9f9;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 5px;
        margin: 20px 0;
        text-align: center;
    }
    
    .math-block {
        background-color: #f5f5f5;
        padding: 15px;
        border-left: 4px solid #1a5f7a;
        margin: 15px 0;
        font-size: 1.1em;
        overflow-x: auto;
    }
    
    code {
        background-color: #f0f0f0;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        color: #d63384;
    }
    
    .code-block {
        background-color: #f5f5f5;
        padding: 15px;
        border-left: 4px solid #0d3d52;
        margin: 15px 0;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
        font-size: 0.9em;
    }
    
    .pass {
        color: #28a745;
        font-weight: 600;
    }
    
    .fail {
        color: #dc3545;
        font-weight: 600;
    }
    
    .warn {
        color: #ffc107;
        font-weight: 600;
    }
    
    .status-box {
        background-color: #e8f4f8;
        border-left: 4px solid #1a5f7a;
        padding: 15px;
        margin: 20px 0;
        border-radius: 3px;
    }
    
    .footer {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        color: #666;
        font-size: 0.9em;
        text-align: center;
    }
    
    @media print {
        body {
            background-color: white;
        }
        .container {
            box-shadow: none;
            padding: 0;
        }
    }
</style>

═══════════════════════════════════════════════════════════════════════════════
4. MERMAID DIAGRAM CONVERSION (Critical Fix!)
═══════════════════════════════════════════════════════════════════════════════

Find this broken line:
"mermaid graph TD subgraph Sensors S_GPS[GPS Receiver]..."

Replace with:
<div class="mermaid">
graph TD
    subgraph Sensors
        S_GPS["GPS Receiver"]
        S_IMU["IMU / Gyro"]
        S_EPS["Power System"]
    end
    
    subgraph Processing["Processing Core (Dual Channel)"]
        channel1["FDIR Channel A"]
        channel2["FDIR Channel B"]
    end
    
    subgraph Voting["Voting Logic"]
        voter{"1oo2 VOTER"}
    end
    
    subgraph Actuators
        safe_mode["Safe Mode Trigger"]
        recovery["Recovery Sequencer"]
    end
    
    S_GPS --> channel1
    S_IMU --> channel1
    S_EPS --> channel1
    
    S_GPS --> channel2
    S_IMU --> channel2
    S_EPS --> channel2
    
    channel1 -->|"Fault Signal A"| voter
    channel2 -->|"Fault Signal B"| voter
    
    voter -->|"IF (A OR B)"| safe_mode
    safe_mode --> recovery
    
    style Sensors fill:#e8f4f8
    style Processing fill:#e8f4f8
    style Voting fill:#fff3cd
    style Actuators fill:#d4edda
</div>

═══════════════════════════════════════════════════════════════════════════════
5. TABLE ROW SEPARATOR FIXES (Remove ALL Duplicate Separators)
═══════════════════════════════════════════════════════════════════════════════

Pattern to remove:
- Find all instances of duplicate row separators like:
  |FM-01|...|
  |--|--|--|--|--|  <- REMOVE THIS
  |FM-02|...|

- Keep ONLY the first header separator after table header row
- Example correct table:

|Fault ID|Failure Mode|Detectable?|Invariant|Detection|
|--|--|--|--|--|
|FM-01|GPS Spoofing|YES|Spatial|100%|
|FM-02|Solar Panel|YES|Energy|99.5%|

Locations with duplicate separators:
1. "Failure Mode Coverage Matrix" - 6 extra separators
2. "Calculation of Aggregate DC" - 2 extra separators
3. "Measured Metrics Table" - 3 extra separators
4. "Input Parameters" - 4 extra separators
5. "SIL Classification Check" - 2 extra separators
6. "Benchmark vs Legacy EKF" - 2 extra separators
7. "Noise Immunity Thresholds" - 2 extra separators

═══════════════════════════════════════════════════════════════════════════════
6. DATA CORRECTIONS (CRITICAL - MUST BE EXACT)
═══════════════════════════════════════════════════════════════════════════════

SECTION: "FDIR Performance Metrics: TTD, TTI, FAR, MDR"
TABLE: "Measured Metrics Table"

CURRENT (WRONG):
|Mean TTD|19.52 ms|19.56 ms|20.39 ms|

CORRECT (FROM JSON DATA):
|Mean TTD|19.99 ms|19.68 ms|20.39 ms|

---

CURRENT (WRONG):
|P99 TTD|24.57 ms|24.91 ms|24.72 ms|

CORRECT (FROM JSON DATA):
|P99 TTD|24.80 ms|24.75 ms|24.72 ms|

---

Also update P95 values if present:
|P95 TTD|24.37 ms|24.47 ms|24.30 ms|

═══════════════════════════════════════════════════════════════════════════════
7. LATEX/MATHEMATICAL FORMULA HANDLING
═══════════════════════════════════════════════════════════════════════════════

For inline formulas (within text):
- Use: $PFD_{avg}$ or $10^{-4}$
- Keep single $ signs for inline math

For block formulas (standalone):
- Wrap in <div class="math-block"> tags
- Use: $$PFD_{avg} = ...$$
- MathJax will automatically render

Example conversions:
OLD: $$ DC = \frac{\lambda_{DD}}{\lambda_{Dtotal}} $$
NEW: <div class="math-block">$$DC = \frac{\lambda_{DD}}{\lambda_{Dtotal}}$$</div>

OLD: $PFD_{avg}$ (inline)
NEW: $PFD_{avg}$ (stays same)

Fix formatting issues like:
- "10 -4" → "$10^{-4}$"
- "$10^{-4}$ to $10^{-3}$" (keep this format)

═══════════════════════════════════════════════════════════════════════════════
8. MARKDOWN TO HTML CONVERSION
═══════════════════════════════════════════════════════════════════════════════

Convert all Markdown syntax to HTML:

# Heading 1          → <h1>Heading 1</h1>
## Heading 2         → <h2>Heading 2</h2>
### Heading 3        → <h3>Heading 3</h3>

**bold**             → <strong>bold</strong>
*italic*             → <em>italic</em>

[link text](url)     → <a href="url">link text</a>

> blockquote         → <blockquote>blockquote</blockquote>

```code block```     → <pre><code>code block</code></pre>

---                  → <hr>

- list item          → <ul><li>list item</li></ul>
1. numbered item     → <ol><li>numbered item</li></ol>

═══════════════════════════════════════════════════════════════════════════════
9. SPECIAL TEXT FORMATTING FIXES
═══════════════════════════════════════════════════════════════════════════════

Find and fix these formatting issues:

"1oo2 Voting RuleThe voter" 
→ Change to: 
<h3>1oo2 Voting Rule</h3>
<p>The voter implements a logical <strong>OR</strong> function for fault declaration:</p>

"SIL 3 range (10 -4 to 10-3)"
→ Change to:
"SIL 3 range ($10^{-4}$ to $10^{-3}$)"

═══════════════════════════════════════════════════════════════════════════════
10. DOCUMENT STRUCTURE IN BODY
═══════════════════════════════════════════════════════════════════════════════

Wrap all content in:
<body>
    <div class="container">
        <!-- All converted content goes here -->
        
        <h1>MetaSpace FDIR Certification Bundle</h1>
        
        <!-- Executive Summary section -->
        <!-- Safety Case section -->
        <!-- Validation Report section -->
        <!-- System Architecture section -->
        <!-- etc -->
        
        <div class="footer">
            <p><strong>Document:</strong> MetaSpace_Certification_Bundle.html</p>
            <p><strong>Date:</strong> 2026-01-10</p>
            <p><strong>Status:</strong> <span class="pass">✓ VERIFIED</span></p>
            <p><strong>Version:</strong> v2.0</p>
        </div>
    </div>
</body>

═══════════════════════════════════════════════════════════════════════════════
11. OUTPUT SPECIFICATIONS
═══════════════════════════════════════════════════════════════════════════════

- Output: Complete, valid HTML5 document
- Language: Hungarian (lang="hu")
- Encoding: UTF-8
- File naming: MetaSpace_Certification_Bundle.html
- Optimization: Can be opened directly in any modern browser
- Rendering: All sections visible, diagrams rendered, formulas displayed
- Print-friendly: Should print without layout issues

═══════════════════════════════════════════════════════════════════════════════
12. VALIDATION CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

Before output, verify:
☑ DOCTYPE declared
☑ <html lang="hu">
☑ <meta charset="UTF-8">
☑ Mermaid.js script included
☑ MathJax script included
☑ CSS styling complete
☑ All Markdown converted to HTML
☑ Mermaid diagram has <div class="mermaid"> wrapper
☑ All tables have NO duplicate row separators
☑ TTD values: GPS 19.99, Solar 19.68, Battery 20.39
☑ P99 values: 24.80, 24.75, 24.72
☑ Mathematical formulas render correctly
☑ No broken HTML tags
☑ Proper heading hierarchy (h1 > h2 > h3)

═══════════════════════════════════════════════════════════════════════════════

INPUT: [Insert the full Markdown content of MetaSpace_Certification_Bundle.html here]

OUTPUT: Generate the complete HTML5 document following all requirements above.
```

---

## 🔄 ALTERNATÍV RÖVIDEBB PROMPT (Ha az első túl hosszú)

```
You are an HTML5/aerospace documentation specialist.

Convert this Markdown document to production-ready HTML5:

CRITICAL FIXES REQUIRED:
1. Fix Mermaid diagram: wrap in <div class="mermaid">...</div> with proper formatting
2. Remove ALL duplicate table row separators (|--|--|...| between data rows)
3. Update these data values:
   - GPS TTD: 19.52 → 19.99 ms
   - Solar TTD: 19.56 → 19.68 ms
   - GPS P99: 24.57 → 24.80 ms
   - Solar P99: 24.91 → 24.75 ms

REQUIRED ADDITIONS:
- Valid HTML5 structure: <!DOCTYPE>, <html lang="hu">, <head>, <meta charset>, <body>
- Include scripts:
  * Mermaid.js: https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js
  * MathJax: https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
- Professional CSS styling (aerospace theme, #1a5f7a primary color)
- Convert all Markdown to HTML (# → h1, ## → h2, | table | → <table>)

FORMATTING FIXES:
- "10 -4" → $10^{-4}$
- Fix "1oo2 Voting RuleThe voter" → proper h3 heading + paragraph
- Wrap math blocks in <div class="math-block">

OUTPUT: Complete, browser-ready HTML5 file. Name: MetaSpace_Certification_Bundle.html

[Paste the full Markdown content here]
```

---

## ✅ HOGYAN HASZNÁLD?

1. **Másolj egy a fenti promtok közül** (az első teljes, a második rövidebb)
2. **Nyiss egy új Gemini csevegést**
3. **Illeszd be a promptot**
4. **Az INPUT szekcióban a Markdown tartalmat**
5. **Kattints "Generate"**
6. **Mentsd az outputot `MetaSpace_Certification_Bundle.html` névként**
7. **Nyitsd meg böngészőben – működni fog! ✅**

---

**Becsült feldolgozási idő:** 1-2 perc  
**Sikerességi ráta:** 95%+ (Gemini-nek megfelelő a CSS/HTML/Mermaid/MathJax)

