import PyPDF2
from docx import Document



class ProcessDocs:
  
  def __init__(self, filename, mime_type):
    self.filename = filename
    self.mime_type = mime_type
    
 # Function to process the document based on its MIME type
  def process_document(self):
      if self.mime_type == 'application/pdf':
          return self.process_pdf(self.filename)
      elif self.mime_type == 'application/msword' or self.mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
          return self.process_word(self.filename)
      elif self.mime_type == 'text/plain':
          return self.process_text(self.filename)
      else:
          print(f"Unsupported document type: {self.mime_type}")

  # Example functions to process different document types
  def process_pdf(self):
      try:
          with open(self.filename, 'rb') as file:
              reader = PyPDF2.PdfFileReader(file)
              num_pages = reader.numPages
              content = []
              for page_num in range(num_pages):
                  page = reader.getPage(page_num)
                  content.append(page.extractText())
              full_content = "\n".join(content)
              print(f"PDF document content:\n{full_content}")
      except Exception as e:
          print(f"An error occurred while processing the PDF document: {e}")

  def process_word(self):
      try:
          doc = Document(self.filename)
          content = []
          for paragraph in doc.paragraphs:
              content.append(paragraph.text)
          full_content = "\n".join(content)
          print(f"Word document content:\n{full_content}")
      except Exception as e:
          print(f"An error occurred while processing the Word document: {e}")

  def process_text(self):
    try:
        with open(self.filename, 'r') as file:
            content = file.read()
            print(f"Text document content:\n{content}")
    except Exception as e:
        print(f"An error occurred while processing the text document: {e}")