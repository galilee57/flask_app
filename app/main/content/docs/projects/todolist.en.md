---
title: 📝 Project – Todo App (Local Storage)
summary: English Version
---

**This project is a task management application (Todo App) designed to be simple, fast, and self-contained.**

The data is stored in a local file, without relying on an external database, allowing for lightweight and independent management.

⚙️ **How it works**

The application is built around three main components:

→ Data structure : Each task is represented as a structured object.
→ Local persistence : Tasks are saved in a local file. Every modification (creation, deletion, completion) updates the file to preserve the current state.
→ Interface ↔ file synchronization. On startup, data is read from the file and injected into the interface. User interactions then update both the UI and the underlying storage.

💡 **Why this project matters**

Although intentionally simple in appearance, this project reinforces fundamental concepts:
→ state management  
→ CRUD operations (Create, Read, Update, Delete)  
→ data serialization / deserialization  
→ separation between business logic and interface  
→ persistence without external dependencies

It provides a solid foundation for evolving toward more complex architectures (database integration, API layer, authentication, remote synchronization, etc.).
