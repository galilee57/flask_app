---
title: 🌍 Project – Flags Game (Countries API)
summary: English Version
---

**This project is an interactive game where the player matches flags with their corresponding country names.**  
The objective is simple: drag each flag to the correct target area.

The key feature of this project is the use of an external API to dynamically retrieve country data (name, flag, region, capital, etc.).

⚙️ **Technical Overview**

Data retrieval via API
→ Country information is fetched dynamically from a public API (such as REST Countries).  
→ This avoids static local storage and ensures structured, normalized data.

Dynamic element generation
→ Flags are generated from the retrieved data (using the flag image URLs).  
→ Target areas correspond to regions or categories defined in the API response.

Drag & Drop interaction
→ The player drags flags into a target zone.  
→ A validation logic checks whether the country’s actual region matches the selected zone.

Validation & feedback
→ If the match is correct → visual confirmation and/or score update.  
→ Otherwise → user feedback (error indication, repositioning, retry).

💡 **Why this project matters**

This project highlights:
→ REST API integration  
→ JSON data handling  
→ dynamic UI generation  
→ event handling (drag & drop)  
→ separation between external data and application logic

It combines educational gameplay, user interaction, and real-time data usage in a cohesive and practical implementation.
