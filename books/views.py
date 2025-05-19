import tempfile
import os
from django.http import FileResponse

from django import forms
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub

from .models import Book, Part, Chapter, Chunk, Glossary
from .yandex_translate import YandexTranslateClient

# Create your views here.

class BookUploadForm(forms.Form):
    epub_file = forms.FileField(label='EPUB file')

class ChunkForm(forms.ModelForm):
    class Meta:
        model = Chunk
        fields = ['original_text', 'translated_text', 'translated']

class GlossaryForm(forms.ModelForm):
    class Meta:
        model = Glossary
        fields = ['word', 'translation']

def load_book(request):
    """Handle the upload and processing of an EPUB file."""
    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            epub_file = form.cleaned_data['epub_file']
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in epub_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            book_obj = epub.read_epub(tmp_path)
            # Extract metadata
            title = book_obj.get_metadata('DC', 'title')[0][0] if book_obj.get_metadata('DC', 'title') else 'Untitled'
            author = book_obj.get_metadata('DC', 'creator')[0][0] if book_obj.get_metadata('DC', 'creator') else ''
            language = book_obj.get_metadata('DC', 'language')[0][0] if book_obj.get_metadata('DC', 'language') else 'en'
            metadata = {k: v for k, v in book_obj.metadata.items()}
            # Save Book
            book = Book.objects.create(title=title, author=author, language=language, metadata=metadata)
            # Parse spine and split into parts/chapters/chunks
            part = Part.objects.create(book=book, title=None, order=1)
            chapter_order = 1
            for item in book_obj.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                chapter_title = item.get_name()
                chapter = Chapter.objects.create(part=part, title=chapter_title, order=chapter_order)
                chapter_order += 1
                # Split content into chunks (for simplicity, by paragraphs)
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                paragraphs = [p.get_text() for p in soup.find_all('p') if p.get_text(strip=True)]
                for i, para in enumerate(paragraphs, 1):
                    Chunk.objects.create(chapter=chapter, original_text=para, order=i)
            messages.success(request, f'Book "{title}" loaded successfully!')
            return redirect('books:list_books')
    else:
        form = BookUploadForm()
    return render(request, 'books/load_book.html', {'form': form})

def list_books(request):
    """Display a list of all books."""
    books = Book.objects.all()
    return render(request, 'books/list_books.html', {'books': books})

def view_book(request, book_id):
    """Display the details of a specific book."""
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/view_book.html', {'book': book})

def edit_chapter(request, chapter_id):
    """Edit the chunks of a specific chapter."""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    chunks = chapter.chunks.all()
    if request.method == 'POST':
        chunk_id = request.POST.get('chunk_id')
        if chunk_id:
            chunk = get_object_or_404(Chunk, id=chunk_id)
            form = ChunkForm(request.POST, instance=chunk, prefix=f'chunk_{chunk.id}')
            if form.is_valid():
                form.save()
                messages.success(request, f'Chunk {chunk.order} updated successfully!')
        return redirect('books:edit_chapter', chapter_id=chapter_id)
    else:
        forms = [ChunkForm(instance=chunk, prefix=f'chunk_{chunk.id}') for chunk in chunks]
    return render(request, 'books/edit_chapter.html', {'chapter': chapter, 'forms': forms})

def manage_glossary(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    glossaries = book.glossaries.all()
    if request.method == 'POST':
        form = GlossaryForm(request.POST)
        if form.is_valid():
            glossary = form.save(commit=False)
            glossary.book = book
            glossary.save()
            messages.success(request, 'Glossary entry added successfully!')
            return redirect('books:manage_glossary', book_id=book_id)
    else:
        form = GlossaryForm()
    return render(request, 'books/manage_glossary.html', {'book': book, 'glossaries': glossaries, 'form': form})

def delete_glossary(request, glossary_id):
    glossary = get_object_or_404(Glossary, id=glossary_id)
    book_id = glossary.book.id
    glossary.delete()
    messages.success(request, 'Glossary entry deleted successfully!')
    return redirect('books:manage_glossary', book_id=book_id)

def update_glossary(request, glossary_id):
    glossary = get_object_or_404(Glossary, id=glossary_id)
    if request.method == 'POST':
        form = GlossaryForm(request.POST, instance=glossary)
        if form.is_valid():
            form.save()
            messages.success(request, 'Glossary entry updated successfully!')
            return redirect('books:manage_glossary', book_id=glossary.book.id)
    else:
        form = GlossaryForm(instance=glossary)
    return render(request, 'books/update_glossary.html', {'form': form, 'glossary': glossary})

def save_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    # Create a new EPUB book
    epub_book = epub.EpubBook()
    # Set metadata
    epub_book.set_identifier(f'book_{book.id}')
    epub_book.set_title(book.title)
    epub_book.set_language(book.language)
    if book.author:
        epub_book.add_author(book.author)
    # Add parts and chapters
    for part in book.parts.all():
        for chapter in part.chapters.all():
            # Gather chunks for the chapter
            chunks = chapter.chunks.all()
            chapter_content = '<section class="" data-pdf-bookmark="{}" data-type="chapter" epub:type="chapter">'.format(chapter.title)
            chapter_content += '<h1 class="Body-TextTx">{}</h1>'.format(chapter.title)
            for chunk in chunks:
                if chunk.translated:
                    chapter_content += f'<p class="Body-TextTx">{chunk.translated_text}</p>'
                else:
                    chapter_content += f'<p class="Body-TextTx">{chunk.original_text}</p>'
            chapter_content += '</section>'
            # Create an EPUB chapter
            epub_chapter = epub.EpubHtml(
                title=chapter.title, 
                file_name=f'chapter_{chapter.id}.xhtml',
                lang=book.language,
                content=f'<html><head><title>{chapter.title}</title></head><body>{chapter_content}</body></html>'
            )
            epub_book.add_item(epub_chapter)
            # Add chapter to the spine
            epub_book.spine.append(epub_chapter)
    # Create EPUB file
    epub_path = f'book_{book.id}.epub'

    epub.write_epub(epub_path, epub_book)
    # Return the file as a response
    response = FileResponse(open(epub_path, 'rb'), as_attachment=True, filename=epub_path)
    os.remove(epub_path)  # Clean up the file after sending
    return response

def translate_chunks(chunks, source_language, target_language):
    """
    Helper function to translate chunks using Yandex Translate API.
    
    Args:
        chunks: QuerySet of Chunk objects to translate
        source_language: Source language code
        target_language: Target language code
        
    Returns:
        tuple: (number of chunks translated, list of translated chunks)
    """
    translator = YandexTranslateClient()
    chunks_translated = 0
    translated_chunks = []
    
    for chunk in chunks:
        if not chunk.translated:  # Only translate if not already translated
            translated_text = translator.translate(
                chunk.original_text,
                source_language=source_language,
                target_language=target_language
            )
            chunk.translated_text = translated_text
            chunk.save()
            chunks_translated += 1
            translated_chunks.append(chunk)
    
    return chunks_translated, translated_chunks

def translate_chapter(request, chapter_id):
    """Translate all chunks in a chapter using Yandex Translate API."""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    
    try:
        chunks_translated, _ = translate_chunks(
            chapter.chunks.all(),
            source_language=chapter.part.book.language,
            target_language=settings.YANDEX_TRANSLATE_TARGET_LANGUAGE
        )
        
        if chunks_translated > 0:
            messages.success(request, f'Successfully translated {chunks_translated} chunks in chapter "{chapter.title}"!')
        else:
            messages.info(request, f'No new content to translate in chapter "{chapter.title}".')
            
    except Exception as e:
        messages.error(request, f'Translation failed: {str(e)}')
    
    return redirect('books:edit_chapter', chapter_id=chapter_id)

def translate_book(request, book_id):
    """Translate all chapters in a book using Yandex Translate API."""
    book = get_object_or_404(Book, id=book_id)
    
    try:
        chapters_translated = 0
        total_chunks_translated = 0
        
        for part in book.parts.all():
            for chapter in part.chapters.all():
                chunks_translated, _ = translate_chunks(
                    chapter.chunks.all(),
                    source_language=book.language,
                    target_language=settings.YANDEX_TRANSLATE_TARGET_LANGUAGE
                )
                
                if chunks_translated > 0:
                    chapters_translated += 1
                    total_chunks_translated += chunks_translated
        
        if chapters_translated > 0:
            messages.success(
                request, 
                f'Successfully translated {total_chunks_translated} chunks in {chapters_translated} chapters of book "{book.title}"!'
            )
        else:
            messages.info(request, f'No new content to translate in book "{book.title}".')
            
    except Exception as e:
        messages.error(request, f'Translation failed: {str(e)}')
    
    return redirect('books:view_book', book_id=book_id)
