# barnomz-backend

**Barnomz** is a web application tailored for students at Sharif University. It offers a platform to create, share, and
discuss semester plans and schedules. Additionally, it facilitates an interactive space where students can add comments
and ratings about professors and courses. This feature aids future students in making informed decisions based on the
shared experiences and insights of their peers.

## Introduction

**Barnomz** is a web application tailored for students at Sharif University. It offers a platform to create, share, and
discuss semester plans and schedules. Additionally, it facilitates an interactive space where students can add comments
and ratings about professors and courses. This feature aids future students in making informed decisions based on the
shared experiences and insights of their peers. This application is built using a powerful combination of technologies
including Next.js for the frontend, Django for the backend, and Docker for easy deployment and containerization. you can
simply check barnomz.ir to see our website but if you want to have a local copy of our website you can follow the
instructions below.

## Technology Stack

- **Frontend:** Developed with Next.js, our frontend delivers a fast, user-friendly interface that is responsive and
  optimized for performance.
- **Backend:** Our backend is powered by Django, offering a robust framework for building high-level, secure web
  applications.
- **Deployment:** Utilizing Docker, we ensure our application can be easily deployed and scaled across any environment,
  guaranteeing consistency across development, staging, and production setups.

## Getting Started

### Prerequisites

Before you begin, ensure you have Docker and Docker Compose installed on your system. If not, you can download them
from [Docker's official website](https://www.docker.com/get-started).

### Running the Project

1. **Clone the repository**
   git clone <repository-url>
2. **Navigate to the project directory**
   cd barnomz-backend
3. **Build and run the containers**
   docker-compose up --build This command builds the images for the frontend, backend, and database if they don't exist
   and starts the containers.

### Accessing the Application

- The frontend can be accessed at `http://localhost:3000`
- The backend is available at `http://localhost:8000`
- Adminer for database management is accessible at `http://localhost:8080` (if you choose to include it in your
  docker-compose for DB management)

### Stopping the Project

To stop the running containers, you can use the following command:

### Accessing the Application

- The frontend can be accessed at `http://localhost:3000`
- The backend is available at `http://localhost:8000`
- Adminer for database management is accessible at `http://localhost:8080` (if you choose to include it in your
  docker-compose for DB management)

### Stopping the Project

To stop the running containers, you can use the following command:
docker-compose down

## Project Structure

- **Frontend (`/barnomz-frontend`):** Contains all the source code for the Next.js frontend application.
- **Backend (`/barnomz-backend`):** Houses the Django backend application, including models, views, and serializers for
  API development.
- **Docker:** The `docker-compose.yml` file at the root defines the services, networks, and volumes for container
  orchestration.

## Contributing

We welcome contributions! Please feel free to fork the repository and submit pull requests with any enhancements, bug
fixes, or improvements.
