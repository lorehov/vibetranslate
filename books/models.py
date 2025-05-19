from django.db import models

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=32, default='en')
    metadata = models.JSONField(default=dict, blank=True)  # Store all EPUB metadata

    def __str__(self):
        return self.title

class Part(models.Model):
    book = models.ForeignKey(Book, related_name='parts', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.title or f"Part {self.order}"

class Chapter(models.Model):
    part = models.ForeignKey(Part, related_name='chapters', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.title or f"Chapter {self.order}"

class Chunk(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='chunks', on_delete=models.CASCADE)
    original_text = models.TextField()
    translated_text = models.TextField(blank=True, null=True)
    translated = models.BooleanField(default=False)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"Chunk {self.order} (translated: {self.translated})"

class Glossary(models.Model):
    book = models.ForeignKey(Book, related_name='glossaries', on_delete=models.CASCADE)
    word = models.CharField(max_length=255)
    translation = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.word} - {self.translation}"
