# ShareMitra Flask Backend

This repository contains the backend for the ShareMitra application. It is built using Flask and provides endpoints for user authentication, task management, image analysis, and payment details submission with IFSC validation. Data is stored in MongoDB, and the project integrates with external services (Tesseract OCR and Razorpay IFSC API).

## Getting Started

### Prerequisites

- **Python 3.7+**
- **MongoDB:** Ensure you have a MongoDB instance running (default: `mongodb://localhost:27017`).
- **Tesseract OCR:**  
  On macOS, install via Homebrew:
  ```bash
  brew install tesseract
