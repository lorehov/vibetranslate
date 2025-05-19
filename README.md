# Book Translator

A Django-based web application for translating books using Yandex Translate API. The application allows users to upload EPUB books, translate them chapter by chapter, manage translations, and save the translated content back to EPUB format.

## Features

- Upload EPUB books
- View book structure (parts, chapters, chunks)
- Translate individual chapters or entire books
- Edit and review translations
- Manage glossary entries
- Save translated books as EPUB files

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Yandex Cloud account with Translate API access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd translator
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
YANDEX_TRANSLATE_API_KEY=your-api-key
YANDEX_TRANSLATE_TARGET_LANGUAGE=en  # or your target language code
```

## Yandex Cloud Setup

To use the translation functionality, you need to set up Yandex Cloud and obtain API credentials:

1. Create a Yandex Cloud account if you don't have one
2. Create a new service account
3. Assign the necessary roles (at minimum, `translate.user`)
4. Create an API key for the service account

For detailed instructions, refer to the official Yandex Cloud documentation:
- [Getting Started with Yandex Cloud](https://cloud.yandex.com/en/docs/getting-started)
- [Creating a Service Account](https://cloud.yandex.com/en/docs/iam/operations/sa/create)
- [Creating an API Key](https://cloud.yandex.com/en/docs/iam/operations/api-key/create)
- [Yandex Translate API Documentation](https://cloud.yandex.com/en/docs/translate/quickstart)

## Database Setup

1. Run migrations:
```bash
python manage.py migrate
```

2. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

## Running the Application

1. Start the development server:
```bash
python manage.py runserver
```

2. Open your browser and navigate to `http://localhost:8000`

## Usage

1. **Upload a Book**
   - Click "Load Book" in the navigation
   - Select an EPUB file
   - The book will be processed and split into chapters

2. **Translate Content**
   - View the book details
   - Use "Translate Book" to translate all chapters at once
   - Or use "Translate Chapter" to translate individual chapters
   - Edit translations as needed

3. **Manage Glossary**
   - Access the glossary from the book view
   - Add, edit, or delete glossary entries
   - Glossary entries can be used for consistent translations

4. **Save Translated Book**
   - Click "Save Book" to generate an EPUB file
   - The file will include all translated content

## Project Structure

```
translator/
├── books/                 # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View logic
│   ├── urls.py           # URL routing
│   └── templates/        # HTML templates
├── translator/           # Project settings
├── requirements.txt      # Python dependencies
└── manage.py            # Django management script
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 