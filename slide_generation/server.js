import express from 'express';
import multer from 'multer';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';
import cors from 'cors';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const execAsync = promisify(exec);
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Configure multer for file uploads
const upload = multer({
    dest: 'temp/',
    limits: {
        fileSize: 10 * 1024 * 1024, // 10MB limit
    },
});

// Utility function to generate unique filename
function generateUniqueFilename(prefix = 'presentation') {
    const timestamp = Date.now();
    const randomString = crypto.randomBytes(4).toString('hex');
    return `${prefix}-${timestamp}-${randomString}`;
}

// Utility function to create temporary markdown file
async function createTempMarkdownFile(content, filename) {
    const tempDir = path.join(__dirname, 'temp', generateUniqueFilename());
    await fs.ensureDir(tempDir);

    const markdownPath = path.join(tempDir, `${filename}.md`);
    await fs.writeFile(markdownPath, content, 'utf8');

    return { tempDir, markdownPath };
}

// Utility function to convert markdown to PDF using Slidev
async function convertToPDF(markdownPath, outputDir) {
    try {
        // Run slidev export command using pnpm
        console.log('markdownPath', markdownPath);
        console.log('outputDir', outputDir);
        const outputFile = path.join(outputDir, 'output.pdf');
        const command = `pnpm slidev export "${markdownPath}" --output "${outputFile}" --format pdf`;
        const { stdout, stderr } = await execAsync(command, { cwd: __dirname });

        // Check for Playwright installation error
        if (stderr && stderr.includes('playwright-chromium')) {
            throw new Error('Playwright is required for PDF export. Please run: pnpm install playwright-chromium');
        }

        if (stderr && !stderr.includes('Warning') && !stderr.includes('info')) {
            throw new Error(`Slidev export error: ${stderr}`);
        }

        // Find the generated PDF file
        const files = await fs.readdir(outputDir);
        const pdfFile = files.find(file => file.endsWith('.pdf'));

        if (!pdfFile) {
            throw new Error('PDF file not generated');
        }

        return path.join(outputDir, pdfFile);
    } catch (error) {
        throw new Error(`Conversion failed: ${error.message}`);
    }
}

// Utility function to cleanup temporary files
async function cleanupTempFiles(tempDir) {
    try {
        await fs.remove(tempDir);
    } catch (error) {
        console.error('Cleanup error:', error);
    }
}

// Endpoint 1: Convert markdown text (JSON)
app.post('/convert-text', async (req, res) => {
    try {
        const { content, filename = 'presentation' } = req.body;

        if (!content) {
            return res.status(400).json({ error: 'Content is required' });
        }

        // Create temporary directory and markdown file
        const { tempDir, markdownPath } = await createTempMarkdownFile(content, filename);

        try {
            // Convert to PDF
            const pdfPath = await convertToPDF(markdownPath, tempDir);

            // Read the PDF file
            const pdfBuffer = await fs.readFile(pdfPath);

            // Set response headers
            res.setHeader('Content-Type', 'application/pdf');
            res.setHeader('Content-Disposition', `attachment; filename="${filename}.pdf"`);
            res.setHeader('Content-Length', pdfBuffer.length);

            // Send the PDF
            res.send(pdfBuffer);

        } finally {
            // Cleanup temporary files
            console.log('cleaning tempDir', tempDir);

            await cleanupTempFiles(tempDir);
        }

    } catch (error) {
        console.error('Error in /convert-text:', error);
        res.status(500).json({ error: error.message });
    }
});

// Endpoint 2: Convert markdown file upload
app.post('/convert', upload.single('markdown'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'Markdown file is required' });
        }

        const uploadedFile = req.file;
        const filename = path.parse(uploadedFile.originalname).name;

        // Read the uploaded file content
        const content = await fs.readFile(uploadedFile.path, 'utf8');

        // Create temporary directory and markdown file
        const { tempDir, markdownPath } = await createTempMarkdownFile(content, filename);

        try {
            // Convert to PDF
            const pdfPath = await convertToPDF(markdownPath, tempDir);

            // Read the PDF file
            const pdfBuffer = await fs.readFile(pdfPath);

            // Set response headers
            res.setHeader('Content-Type', 'application/pdf');
            res.setHeader('Content-Disposition', `attachment; filename="${filename}.pdf"`);
            res.setHeader('Content-Length', pdfBuffer.length);

            // Send the PDF
            res.send(pdfBuffer);

        } finally {
            // Cleanup temporary files
            await cleanupTempFiles(tempDir);
            await fs.remove(uploadedFile.path); // Remove uploaded file
        }

    } catch (error) {
        console.error('Error in /convert:', error);
        res.status(500).json({ error: error.message });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'OK', message: 'Slidev PDF conversion server is running' });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Unhandled error:', error);
    res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Slidev PDF conversion server running on port ${PORT}`);
    console.log(`📝 POST /convert-text - Convert markdown text to PDF`);
    console.log(`📁 POST /convert - Convert markdown file to PDF`);
    console.log(`❤️  GET /health - Health check`);
});

export default app; 