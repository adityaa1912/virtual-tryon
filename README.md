# AI Virtual Jewellery Try-On

A full-stack AI application that allows users to virtually try jewellery before purchasing it. Users can upload a face or hand image, select a jewellery item from the catalogue (or upload their own), and generate a realistic try-on image using Google's Gemini image generation model. The generated image can also be converted into a short video using Google Veo.

This project was developed as part of the **Backend Intern Assignment** for **Sixth Dimension Labs**.

---

## Demo


# Project Overview

The application follows a simple workflow.

1. Upload a face image or a hand image.
2. Choose a jewellery item from the built-in catalogue or upload your own jewellery image.
3. The backend validates both images.
4. Google Gemini (Nano Banana Pro) generates a realistic try-on image.
5. The generated image is stored locally.
6. Google Veo generates a short animation from the generated image.
7. The frontend displays both the final image and the generated video.

The project was designed to keep the backend modular so that AI providers can be replaced without changing the API or frontend.

---

# Features

### Image Upload

- Upload face images for:
  - Necklaces
  - Earrings

- Upload hand images for:
  - Rings
  - Bracelets
  - Watches

- Upload custom jewellery images.

---

### Jewellery Catalogue

The application includes a small jewellery catalogue containing multiple sample products.

Current catalogue includes:

- Diamond Ring
- Gold Necklace
- Pearl Earrings
- Silver Bracelet
- Classic Watch
- Diamond Pendant

---

### AI Image Generation

Uses **Google Gemini Nano Banana Pro** to:

- Preserve facial identity
- Preserve hand structure
- Preserve lighting
- Preserve skin tone
- Keep jewellery design unchanged
- Blend jewellery naturally with the uploaded image

---

### AI Video Generation

Uses **Google Veo** to generate a short animation from the final try-on image.

The generated video is stored locally and displayed directly in the frontend.

---

### Validation

Before any AI request is sent:

- Image format is validated.
- File size is checked.
- Image dimensions are verified.
- Invalid or corrupted images are rejected.

---

### Local Storage

Everything is stored locally.

This includes:

- Uploaded images
- Generated try-on images
- Generated videos

No cloud storage is required.

---

# Tech Stack

## Backend

- Python
- FastAPI
- Pydantic
- Google GenAI SDK
- Pillow
- AnyIO
- HTTPX

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Axios

## AI Models

### Image Generation

Google Gemini

Model used:

```

models/nano-banana-pro-preview

```

### Video Generation

Google Veo

Model used:

```

models/veo-3.1-fast-generate-preview

```

---

# Project Structure

```

virtual-tryon/

├── backend/
│
├── app/
│ ├── api/
│ ├── core/
│ ├── models/
│ ├── prompts/
│ ├── schemas/
│ ├── services/
│ └── utils/
│
├── storage/
│ ├── uploads/
│ ├── outputs/
│ └── videos/
│
├── tests/
│
├── requirements.txt
└── .env.example

frontend/

├── public/
│ └── jewellery/
│
├── src/
│ ├── api/
│ ├── components/
│ ├── hooks/
│ ├── data/
│ └── pages/
│
└── package.json

docs/
README.md

```

---

# System Architecture

```

                 React Frontend
                        │
                        │
                Upload Images
                        │
                        ▼
              FastAPI Backend API
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
 Validation      Prompt Builder    Storage Service
        │               │
        └───────────────┼───────────────┘
                        ▼
              Gemini Image Provider
                        │
                        ▼
             Generated Try-On Image
                        │
                        ▼
                Google Veo Provider
                        │
                        ▼
               Generated Video (MP4)
                        │
                        ▼
                  Frontend Display

```

---

# Why this architecture?

Instead of placing all AI logic inside the API routes, the project separates each responsibility into independent services.

This makes it easier to:

- replace AI providers
- test the application without calling external APIs
- maintain the codebase
- add new providers in the future

The frontend never communicates directly with Gemini or Veo. Every request goes through the backend, which handles validation, prompt generation, storage and error handling.

---
# Installation

## Prerequisites

Before running the project, make sure the following are installed:

- Python 3.11 or later
- Node.js 18 or later
- npm
- Git

You will also need:

- A Google AI Studio API key (Gemini)
- A Google AI Studio API key with access to Veo

---

# Clone the Repository

```bash
git clone https://github.com/<your-username>/virtual-tryon.git

cd virtual-tryon
```

---

# Backend Setup

Move into the backend directory.

```bash
cd backend
```

Create a virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

Create a `.env` file by copying the example.

```bash
cp .env.example .env
```

Now start the backend server.

```bash
uvicorn app.main:app --reload
```

The backend will run at:

```
http://127.0.0.1:8000
```

Swagger documentation:

```
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

Open another terminal.

```bash
cd frontend
```

Install dependencies.

```bash
npm install
```

Run the development server.

```bash
npm run dev
```

The frontend will start on

```
http://localhost:5173
```

---

# Environment Variables

The application is configured entirely through environment variables.

Below are the most important ones.

| Variable | Description |
|------------|------------|
| GEMINI_PROVIDER | AI provider for image generation |
| GEMINI_API_KEY | Google AI Studio API key |
| GEMINI_MODEL | Gemini image generation model |
| VIDEO_PROVIDER | Video generation provider |
| VEO_MODEL | Google Veo model |
| VEO_PROMPT | Default animation prompt |
| STORAGE_DIR | Local storage directory |

The repository already contains a `.env.example` file with all available options.

---

# APIs Used

## 1. Google Gemini

Used for generating the jewellery try-on image.

Model used:

```
models/nano-banana-pro-preview
```

API Key:

Google AI Studio

https://aistudio.google.com/

Generate an API key and add it to:

```
backend/.env
```

Example:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

---

## 2. Google Veo

Used for converting the generated image into a short animation.

Model used:

```
models/veo-3.1-fast-generate-preview
```

The project reuses the same Google AI Studio API key.

No additional authentication is required.

---

# Running the Application

Start both backend and frontend.

1. Upload a face image or hand image.
2. Choose a jewellery item.
3. Click **Generate Try-On**.
4. Wait for Gemini to generate the result.
5. Click **Generate Video**.
6. Wait for Veo to finish processing.
7. View or download the final image and video.

---

# API Endpoints

## Upload Image

```
POST /api/v1/uploads
```

Uploads and validates a user or jewellery image.

---

## Generate Try-On

```
POST /api/v1/try-on
```

Uses Gemini to generate a realistic jewellery try-on.

---

## Generate Video

```
POST /api/v1/videos
```

Uses Google Veo to animate the generated image.

---

## Download Image

```
GET /api/v1/results/{result_id}
```

Returns the generated image.

---

## Download Video

```
GET /api/v1/videos/{video_id}/content
```

Returns the generated MP4.

---

# Gemini Prompt Design

One of the main goals while designing the prompt was to make the generated jewellery look natural without changing the user's identity.
The prompt first determines the jewellery category and automatically chooses the correct user image. Face images are used for necklaces and earrings, while hand images are used for rings, bracelets, and watches.
Special attention was given to preserving the user's facial features, hand shape, skin tone, lighting, and background. The prompt also instructs Gemini to keep the jewellery's original colour, material, and design unchanged so that the output closely matches the catalogue image.
Instead of using one generic prompt, the application uses category-specific instructions to improve placement and realism. This approach produced more consistent and visually accurate results during testing.

---

# Screenshots



## Home Page



---

## Jewellery Catalogue



---

## Generated Try-On



---

## Generated Video



---

## Demo Video


---

# Limitations

- Image quality depends on the quality of the uploaded image.
- Google Gemini preview models may occasionally return temporary `503 UNAVAILABLE` errors during periods of high demand. Retrying the request usually resolves the issue.
- Video generation takes longer than image generation 
- All generated files are stored locally. 

---

# Future Improvements

Some improvements that could be added in future versions include:

- Clothing try-on support (Part 2 of the assignment)
- User authentication

---

# Author

**Aditya Mengawade**

Backend Intern Assignment

Sixth Dimension Labs
