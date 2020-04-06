# DGVOST

A crisis event management system for DGVOST built with Flask as the backend and Vue as the frontend.

# Instructions

### Production

Rename `.env.docker-example` to `.env` and fill in the appropriate details. Then use `docker build -t web:latest .` to build the docker image and use `docker run -e "PORT=8765" -p 8007:8765 --env-file .env  web:latest` to run it. This will run the frontend within the Docker container on port 8765 and will bind it to port 8007 which is where you can access it.

If you wish to run a multi-container with the database then use `docker-compose up` instead.

### Development

Rename `.env.development-example` in the backend folder to `.env` and `.env.local.development-example` in the frontend folder to `.env.local` and fill in the appropriate details for both. Then in the backend folder run `python3.6 dgvost.py` and run `npm run serve` in the frontend folder. This will run the backend API at `http://localhost:5000/api` and the frontend at `http://localhost:8080/`.


### Default login details
Email: `admin@admin.com`\
Password: `admin`

Make sure you change both the email and password for this login.