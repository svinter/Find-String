#!/bin/zsh
# Script: Find String
# Version: 3.8 (Silent)
# Arguments: $1=MyFindPath, $2=MyStringFilter, $3=MyStringName
# Created using gemini

/usr/bin/python3 - "$KMVAR_MyFindPath" "$KMVAR_MyStringFilter" "$KMVAR_MyStringName" <<'PY'
import json, sys, os, html

# 1. SETUP
VERSION = "3.8"
SCRIPT_NAME = "Find String"
path_dir = sys.argv[1]
filters_raw = sys.argv[2]
name = sys.argv[3]

config_file = os.path.join(path_dir, f"{name}.txt")
html_path = os.path.join(path_dir, f"{name}.html")

# 2. DATA PROCESSING
mapping = {}
entry_count = 0
filter_list = [f.strip().lower() for f in filters_raw.split(',')] if filters_raw.strip() else []

if os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            clean = line.strip()
            if not clean or clean.startswith('#'): continue

            parts = [p.strip() for p in clean.split('|')]
            if len(parts) < 5: continue

            line_filter = parts[0].lower()
            abbrev = parts[1]
            example = parts[2]
            val_type = parts[3]
            val_actual = parts[4]
            label = parts[5] if len(parts) > 5 else ""
            # New Color Field (Field 7)
            color = parts[6] if len(parts) > 6 else "gray"

            if not filter_list or line_filter in filter_list:
                mapping[abbrev] = {
                    "val": val_actual,
                    "type": val_type,
                    "ex": example,
                    "lbl": label,
                    "clr": color if color else "gray"
                }
                entry_count += 1

# 3. GENERATE HTML
html_out = f"""<!doctype html><html><head><meta charset="utf-8">
<style>
    body {{ font-family: -apple-system, system-ui; background: #f2f2f2; padding: 15px; margin: 0; overflow: hidden; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }}
    #q {{ width: 100%; padding: 10px; font-size: 18px; border-radius: 8px; border: 1px solid #ccc; text-align: center; outline: none; box-sizing: border-box; -webkit-appearance: none; }}
    #q:focus {{ border-color: #1f6feb; box-shadow: 0 0 0 3px rgba(31,111,235,0.2); }}
    #result-container {{ flex-grow: 1; margin-top: 5px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
    #abbrev-text {{ font-size: 11px; color: #000; font-weight: 400; margin-bottom: 2px; height: 1.2em; }}
    #display-text {{ font-size: 18px; color: #1f6feb; font-weight: 600; line-height: 1.2; }}
    #example-text {{ font-size: 13px; color: #666; font-style: italic; margin-top: 4px; min-height: 1.2em; }}
    /* Updated opt class to allow dynamic border colors */
    .opt {{ font-size: 11px; color: #444; background: #fff; border-radius: 4px; padding: 2px 8px; margin: 2px; display: inline-block; border: 2px solid gray; }}
    #footer {{ font-size: 10px; color: #888; border-top: 1px solid #ddd; padding-top: 8px; display: flex; justify-content: space-between; opacity: 0.8; }}
</style></head>
<body data-kmwindow="SCREENVISIBLE(Main,MidX)-200,SCREENVISIBLE(Main,MidY)-120,400,240">
    <input type="search" id="q" placeholder="Type abbreviation..." autofocus autocomplete="off" spellcheck="false">
    <div id="result-container">
        <div id="abbrev-text"></div>
        <div id="display-text"></div>
        <div id="example-text"></div>
        <div id="options" style="margin-top:10px;"></div>
    </div>
    <div id="footer">
        <span>{SCRIPT_NAME} v{VERSION} | Filters: {html.escape(filters_raw or "All")}</span>
        <span>Entries: {entry_count}</span>
    </div>
    <script>
        const mapping = {json.dumps(mapping)};
        const input = document.getElementById('q'),
              abrDiv = document.getElementById('abbrev-text'),
              valDiv = document.getElementById('display-text'),
              exDiv = document.getElementById('example-text'),
              optDiv = document.getElementById('options');

        let currentActiveKey = null;

        input.addEventListener('input', () => {{
            const typed = input.value;
            abrDiv.textContent = ""; valDiv.textContent = ""; exDiv.textContent = ""; optDiv.innerHTML = "";
            currentActiveKey = null;

            if (typed.length > 0) {{
                let matches = Object.keys(mapping).filter(k => k.startsWith(typed));
                if (matches.length >= 1) {{
                    matches.sort((a, b) => a.length - b.length);
                    currentActiveKey = mapping[typed] ? typed : matches[0];
                    const entry = mapping[currentActiveKey];

                    abrDiv.textContent = currentActiveKey;
                    valDiv.textContent = (entry.lbl && entry.lbl.trim() !== "") ? entry.lbl : entry.val;
                    if (entry.ex && entry.ex.trim() !== "") exDiv.textContent = entry.ex;

                    // Show other options with their specific colored outlines
                    matches.forEach(m => {{
                        const matchEntry = mapping[m];
                        const s = document.createElement('span');
                        s.className = 'opt';
                        s.textContent = m;
                        // Apply the color to the border
                        s.style.borderColor = matchEntry.clr;
                        // Bold the currently active one
                        if (m === currentActiveKey) {{
                            s.style.fontWeight = "bold";
                            s.style.boxShadow = "0 0 2px " + matchEntry.clr;
                        }}
                        optDiv.appendChild(s);
                    }});
                }}
            }}
        }});

        window.addEventListener('keydown', (e) => {{
            if (e.key === "Enter") {{
                if (currentActiveKey && mapping[currentActiveKey]) {{
                    const activeMatch = mapping[currentActiveKey];
                    input.blur();
                    window.KeyboardMaestro.SetVariable("MyFindResults", activeMatch.val);
                    window.KeyboardMaestro.SetVariable("MyFindType", activeMatch.type);
                    window.KeyboardMaestro.Submit("OK");
                }}
            }}
            if (e.key === "Escape") {{
                window.KeyboardMaestro.SetVariable("MyFindResults", "");
                window.KeyboardMaestro.SetVariable("MyFindType", "");
                window.KeyboardMaestro.Cancel("User Cancelled Prompt");
            }}
        }});
    </script>
</body></html>"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_out)
PY
