# DLMS

Device Lifecycle Management System

## Overview

This project provides the initial scaffold for a production-ready Windows desktop application built with Python, PySide6, SQLAlchemy, and SQLite.

## Structure

- app: application bootstrap
- core: shared abstractions
- database: connection and initialization
- models: domain models
- repositories: repository pattern
- services: service layer
- ui: Qt windows and views
- widgets: reusable UI widgets
- resources: icons and Qt resource files
- utils: helpers and logging
- config: application settings
- tests: test suite placeholder

## Development

1. Create a virtual environment:
   python -m venv .venv
2. Activate it:
   .venv\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Run the app:
   python main.py
