---
title: Viewer 360 with Marzipano
summary: English version
---

About this project

This application allows users to explore 360° panoramic images interactively using the Marzipano JavaScript library.

Marzipano is a high-performance panoramic viewer based on WebGL, designed to display high-resolution panoramas directly in the browser. It uses a multi-resolution tiling system, which loads only the portions of the image required for the current zoom level and viewing direction, significantly improving performance and responsiveness.

Project architecture
The application combines several technologies:
• Flask to serve the web application and static resources.
• JavaScript to manage the loading and display of panoramas.
• Marzipano to render interactive panoramas in the browser.
• Tailwind CSS for the user interface styling.

How it works 1. Panoramas are stored as multi-resolution tiled images. 2. When a panorama is selected, the application initializes a Marzipano scene in the display container. 3. The rendering engine dynamically loads the required tiles depending on:
• the camera orientation,
• the zoom level,
• the size of the display window. 4. Users can navigate within the panorama using mouse or touch interactions.

Objective
This project demonstrates how to integrate a high-performance 360° panoramic viewer into a web application, with a simple interface for selecting and browsing multiple panoramas.
