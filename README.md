---
title: Glory Furniture Hub
emoji: 👑
colorFrom: yellow
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---

# Glory Furniture Hub — Handcrafted Solid Burma Teak E-Commerce Platform

A production-grade Django web application for artisanal luxury furniture:
- **Hero Showcase**: 60% viewport carousel with rich teak luxury theme.
- **Masterpiece Catalog**: Filterable collections of beds, dining tables, sofas, and pooja mandirs.
- **Real Database Persistence**: SQLite database (`db.sqlite3`) with full product CRUD.
- **Studio Admin Portal**: Manage orders, customer directory, verified UPI transactions, and catalog inventory with live Add/Edit/Delete modals.
- **Patron Portal**: "My Future Orders" tracking, Saved Wishlist with "Move to Cart", and doorstep delivery management.

## Run Locally
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Hugging Face Spaces Deployment
Configured with Docker SDK on port `7860` with Gunicorn and WhiteNoise.
