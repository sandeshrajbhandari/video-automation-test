## **1. Send Markdown Text (JSON)**

```bash
curl -X POST http://localhost:3000/convert-text \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Welcome to Slidev\n\nPresentation slides for developers.\n\n---\n\n# What is Slidev?\n\n- **Slides** based on Markdown\n- **Hot** reload support\n- **Vue** components\n- **Themes** and customization\n- **Code** highlighting\n\n---\n\n# Code Example\n\n```ts\nconsole.log(\"Hello, Slidev!\")\n```",
    "filename": "my-presentation"
  }' \
  --output my-presentation.pdf
```

## **2. Send Markdown File**

```bash
curl -X POST http://localhost:3000/convert \
  -F "markdown=@slides.md" \
  --output slides.pdf
```

## **3. Simple Text Example**
```bash
curl -X POST http://localhost:3000/convert-text \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Hello World\n\nThis is a simple slide.\n\n---\n\n# Second Slide\n\n- Point 1\n- Point 2\n- Point 3"
  }' \
  --output output.pdf
```

## **Notes:**

- Replace localhost:3000 with your actual server URL if different
- The --output flag saves the PDF to a file (remove it if you want to see the binary data in terminal)
- For the file upload version, make sure slides.md exists in your current directory
- The server will return the PDF as a binary response with appropriate headers for download
