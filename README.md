# Burrow Shopping

Shopping list tool built using Python, SQLite and Flask/Gunicorn. 

## Purpose

Designed to be lightweight and simple for deployment to a small VPS, so I can access my shopping list from different devices.

This project is directly based on [burrow-tasks](https://github.com/lambtails/burrow-tasks).

### Implementation notes

This application doesn't have any security features, instead I'm using mTLS to restrict client access to this server on my VPS, so that only myself or anyone with the cert can access it.

This project is very much a proof of concept to see what I can achieve with a minimal server setup, and lacks most of the features you'd expect to see in a more complex shopping list app like Bring! or AnyList.  

## Getting started

This project assumes you have a basic knowledge of python and git.

1. Download the repository
2. Setup a python virtual environment `python -m venv .venv`
3. Set your source to the virtual environment `source .venv/bin/activate`
4. Install requirements `python -m pip install -r requirements.txt`
5. Run `python app.py` to start the server (this will also initialize an empty database)

By default, the application will be at http://127.0.0.1:5000

Have fun!
