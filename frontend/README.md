# Hotel Management System - Frontend

React + TypeScript frontend built with Vite, featuring a modern, responsive UI.

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment (Optional)
```bash
# Create .env file if backend is on different URL
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
```

### 3. Run Development Server
```bash
npm run dev
```

Application runs on `http://localhost:5173`

## Build for Production

```bash
npm run build
```

Built files will be in `dist/` directory.

## Features

- 🎨 **Modern UI**: Clean, responsive design with Tailwind CSS
- 📱 **Mobile-Friendly**: Works great on all screen sizes
- ⚡ **Fast**: Vite for lightning-fast development
- 🔒 **Secure**: JWT authentication with automatic token handling
- 🖼️ **Image Upload**: Drag-and-drop image uploads to Cloudinary
- 🎯 **Type-Safe**: Full TypeScript coverage
- 📊 **State Management**: Zustand for simple, efficient state
- 🔔 **Notifications**: Toast notifications for user feedback

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API client and HTTP calls
│   ├── components/       # Reusable UI components
│   │   └── ui/          # Base UI components
│   ├── pages/           # Page components
│   ├── store/           # State management
│   ├── types/           # TypeScript type definitions
│   ├── App.tsx          # Main application
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── index.html           # HTML template
└── package.json         # Dependencies
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Login Credentials

Use these credentials to login:
- Username: `admin`
- Password: `admin123`

## Environment Variables

Optional variables:
- `VITE_API_URL`: Backend API URL (default: proxied to localhost:8000)
