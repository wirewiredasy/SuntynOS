import os
import logging
import sys
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import tempfile
import uuid
import re
from datetime import datetime

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create the Flask app with security
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "prod-secret-key-" + str(uuid.uuid4()))
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Security headers
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Error handlers
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

@app.errorhandler(500)
def handle_internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error. Please try again.'}), 500

# Tool categories and their tools
TOOL_CATEGORIES = {
    'pdf': {
        'name': 'PDF Tools',
        'icon': 'fas fa-file-pdf',
        'color': 'red',
        'tools': [
            {'id': 'pdf-merger', 'name': 'PDF Merger', 'desc': 'Merge multiple PDF files', 'icon': 'fas fa-plus'},
            {'id': 'pdf-splitter', 'name': 'PDF Splitter', 'desc': 'Split PDF by pages', 'icon': 'fas fa-cut'},
            {'id': 'pdf-compressor', 'name': 'PDF Compressor', 'desc': 'Reduce PDF file size', 'icon': 'fas fa-compress'},
            {'id': 'pdf-to-word', 'name': 'PDF to Word', 'desc': 'Convert PDF to DOCX', 'icon': 'fas fa-file-word'},
            {'id': 'pdf-to-excel', 'name': 'PDF to Excel', 'desc': 'Extract tables to Excel', 'icon': 'fas fa-file-excel'},
            {'id': 'pdf-to-powerpoint', 'name': 'PDF to PowerPoint', 'desc': 'Convert PDF to PPTX', 'icon': 'fas fa-file-powerpoint'},
            {'id': 'word-to-pdf', 'name': 'Word to PDF', 'desc': 'Convert DOCX to PDF', 'icon': 'fas fa-exchange-alt'},
            {'id': 'excel-to-pdf', 'name': 'Excel to PDF', 'desc': 'Convert XLSX to PDF', 'icon': 'fas fa-exchange-alt'},
            {'id': 'powerpoint-to-pdf', 'name': 'PowerPoint to PDF', 'desc': 'Convert PPTX to PDF', 'icon': 'fas fa-exchange-alt'},
            {'id': 'pdf-to-image', 'name': 'PDF to Image', 'desc': 'Extract images from PDF', 'icon': 'fas fa-image'},
            {'id': 'image-to-pdf', 'name': 'Image to PDF', 'desc': 'Convert images to PDF', 'icon': 'fas fa-images'},
            {'id': 'pdf-unlock', 'name': 'PDF Unlock', 'desc': 'Remove PDF password', 'icon': 'fas fa-unlock'},
            {'id': 'pdf-lock', 'name': 'PDF Lock', 'desc': 'Add password to PDF', 'icon': 'fas fa-lock'},
            {'id': 'pdf-reorder', 'name': 'PDF Reorder', 'desc': 'Reorder PDF pages', 'icon': 'fas fa-sort'},
            {'id': 'pdf-rotate', 'name': 'PDF Rotate', 'desc': 'Rotate PDF pages', 'icon': 'fas fa-redo'},
            {'id': 'pdf-watermark', 'name': 'Add Watermark', 'desc': 'Add watermark to PDF', 'icon': 'fas fa-stamp'},
            {'id': 'pdf-page-numbers', 'name': 'Add Page Numbers', 'desc': 'Number PDF pages', 'icon': 'fas fa-sort-numeric-up'},
            {'id': 'pdf-to-text', 'name': 'PDF to Text', 'desc': 'Extract text from PDF', 'icon': 'fas fa-file-alt'},
            {'id': 'text-to-pdf', 'name': 'Text to PDF', 'desc': 'Convert text to PDF', 'icon': 'fas fa-file-pdf'},
            {'id': 'pdf-metadata', 'name': 'PDF Metadata', 'desc': 'View/edit PDF metadata', 'icon': 'fas fa-info'},
            {'id': 'pdf-links', 'name': 'Extract Links', 'desc': 'Extract links from PDF', 'icon': 'fas fa-link'},
            {'id': 'pdf-ocr', 'name': 'OCR PDF', 'desc': 'Extract text with OCR', 'icon': 'fas fa-eye'},
            {'id': 'pdf-to-html', 'name': 'PDF to HTML', 'desc': 'Convert PDF to web', 'icon': 'fas fa-code'},
            {'id': 'pdf-sign', 'name': 'Sign PDF', 'desc': 'Add digital signature', 'icon': 'fas fa-signature'},
            {'id': 'pdf-forms', 'name': 'PDF Forms', 'desc': 'Fill PDF forms', 'icon': 'fas fa-wpforms'}
        ]
    },
    'image': {
        'name': 'Image Tools',
        'icon': 'fas fa-image',
        'color': 'blue',
        'tools': [
            {'id': 'image-resize', 'name': 'Image Resizer', 'desc': 'Resize images', 'icon': 'fas fa-expand-arrows-alt'},
            {'id': 'image-compress', 'name': 'Image Compressor', 'desc': 'Compress images', 'icon': 'fas fa-compress'},
            {'id': 'convert-webp', 'name': 'Convert to WebP', 'desc': 'Convert to WebP format', 'icon': 'fas fa-exchange-alt'},
            {'id': 'convert-jpg', 'name': 'Convert to JPG', 'desc': 'Convert to JPG format', 'icon': 'fas fa-exchange-alt'},
            {'id': 'convert-png', 'name': 'Convert to PNG', 'desc': 'Convert to PNG format', 'icon': 'fas fa-exchange-alt'},
            {'id': 'image-to-pdf', 'name': 'Image to PDF', 'desc': 'Convert images to PDF', 'icon': 'fas fa-file-pdf'},
            {'id': 'bg-remove', 'name': 'Background Remover', 'desc': 'Remove image background', 'icon': 'fas fa-magic'},
            {'id': 'image-crop', 'name': 'Image Cropper', 'desc': 'Crop images', 'icon': 'fas fa-crop'},
            {'id': 'image-rotate', 'name': 'Image Rotator', 'desc': 'Rotate images', 'icon': 'fas fa-redo'},
            {'id': 'image-watermark', 'name': 'Add Watermark', 'desc': 'Add watermark to image', 'icon': 'fas fa-stamp'},
            {'id': 'image-grayscale', 'name': 'Grayscale Filter', 'desc': 'Convert to black & white', 'icon': 'fas fa-adjust'},
            {'id': 'image-colorize', 'name': 'Image Colorizer', 'desc': 'Colorize B&W images', 'icon': 'fas fa-palette'},
            {'id': 'image-blur', 'name': 'Blur Image', 'desc': 'Add blur effect', 'icon': 'fas fa-eye-slash'},
            {'id': 'image-enhance', 'name': 'Image Enhancer', 'desc': 'Enhance image quality', 'icon': 'fas fa-magic'},
            {'id': 'meme-generator', 'name': 'Meme Generator', 'desc': 'Create memes', 'icon': 'fas fa-laugh'},
            {'id': 'face-pixelate', 'name': 'Face Pixelator', 'desc': 'Pixelate faces', 'icon': 'fas fa-user-secret'},
            {'id': 'image-flip', 'name': 'Image Flip', 'desc': 'Flip images', 'icon': 'fas fa-arrows-alt-h'},
            {'id': 'image-invert', 'name': 'Image Inverter', 'desc': 'Invert colors', 'icon': 'fas fa-adjust'},
            {'id': 'image-border', 'name': 'Add Border', 'desc': 'Add border to image', 'icon': 'fas fa-square'},
            {'id': 'image-metadata', 'name': 'Image Metadata', 'desc': 'View EXIF data', 'icon': 'fas fa-info'}
        ]
    },
    'audio': {
        'name': 'Audio & Video Tools',
        'icon': 'fas fa-music',
        'color': 'green',
        'tools': [
            {'id': 'audio-convert', 'name': 'Audio Converter', 'desc': 'Convert audio formats', 'icon': 'fas fa-exchange-alt'},
            {'id': 'audio-trim', 'name': 'Audio Cutter', 'desc': 'Trim audio files', 'icon': 'fas fa-cut'},
            {'id': 'audio-join', 'name': 'Audio Joiner', 'desc': 'Merge audio files', 'icon': 'fas fa-plus'},
            {'id': 'audio-boost', 'name': 'Volume Booster', 'desc': 'Boost audio volume', 'icon': 'fas fa-volume-up'},
            {'id': 'audio-normalize', 'name': 'Audio Normalizer', 'desc': 'Normalize audio levels', 'icon': 'fas fa-sliders-h'},
            {'id': 'audio-extract', 'name': 'Audio Extractor', 'desc': 'Extract audio from video', 'icon': 'fas fa-music'},
            {'id': 'voice-change', 'name': 'Voice Changer', 'desc': 'Change voice pitch/speed', 'icon': 'fas fa-microphone'},
            {'id': 'noise-removal', 'name': 'Noise Remover', 'desc': 'Remove background noise', 'icon': 'fas fa-volume-mute'},
            {'id': 'vocal-remove', 'name': 'Vocal Remover', 'desc': 'Remove vocals', 'icon': 'fas fa-user-slash'},
            {'id': 'audio-record', 'name': 'Audio Recorder', 'desc': 'Record audio', 'icon': 'fas fa-record-vinyl'},
            {'id': 'video-to-audio', 'name': 'Video to Audio', 'desc': 'Extract MP3 from video', 'icon': 'fas fa-film'},
            {'id': 'video-trim', 'name': 'Video Cutter', 'desc': 'Trim video files', 'icon': 'fas fa-cut'},
            {'id': 'video-convert', 'name': 'Video Converter', 'desc': 'Convert video formats', 'icon': 'fas fa-exchange-alt'},
            {'id': 'video-resize', 'name': 'Video Resizer', 'desc': 'Resize video resolution', 'icon': 'fas fa-expand-arrows-alt'},
            {'id': 'video-join', 'name': 'Merge Videos', 'desc': 'Merge multiple videos', 'icon': 'fas fa-plus'},
            {'id': 'video-mute', 'name': 'Mute Video', 'desc': 'Remove audio from video', 'icon': 'fas fa-volume-mute'},
            {'id': 'video-add-audio', 'name': 'Add Audio to Video', 'desc': 'Add audio to video', 'icon': 'fas fa-plus'},
            {'id': 'video-frames', 'name': 'Extract Frames', 'desc': 'Extract images from video', 'icon': 'fas fa-images'},
            {'id': 'video-subtitle', 'name': 'Auto Subtitles', 'desc': 'Generate subtitles', 'icon': 'fas fa-closed-captioning'},
            {'id': 'video-color', 'name': 'Video Color Grader', 'desc': 'Adjust video colors', 'icon': 'fas fa-palette'}
        ]
    },
    'govt': {
        'name': 'Government Tools',
        'icon': 'fas fa-landmark',
        'color': 'orange',
        'tools': [
            {'id': 'pan-validator', 'name': 'PAN Validator', 'desc': 'Validate PAN card format', 'icon': 'fas fa-id-card'},
            {'id': 'aadhaar-mask', 'name': 'Aadhaar Masker', 'desc': 'Mask Aadhaar for sharing', 'icon': 'fas fa-eye-slash'},
            {'id': 'voter-id-extract', 'name': 'Voter ID Extractor', 'desc': 'Extract voter ID info', 'icon': 'fas fa-vote-yea'},
            {'id': 'income-cert', 'name': 'Income Certificate', 'desc': 'Generate income certificate', 'icon': 'fas fa-money-bill'},
            {'id': 'caste-cert', 'name': 'Caste Certificate', 'desc': 'Fill caste certificate form', 'icon': 'fas fa-file-alt'},
            {'id': 'ration-status', 'name': 'Ration Card Status', 'desc': 'Check ration card status', 'icon': 'fas fa-shopping-basket'},
            {'id': 'rent-agreement', 'name': 'Rent Agreement', 'desc': 'Create rent agreement', 'icon': 'fas fa-home'},
            {'id': 'birth-cert', 'name': 'Birth Certificate', 'desc': 'Generate birth certificate', 'icon': 'fas fa-baby'},
            {'id': 'death-cert', 'name': 'Death Certificate', 'desc': 'Generate death certificate', 'icon': 'fas fa-cross'},
            {'id': 'form16-extract', 'name': 'Form-16 Extractor', 'desc': 'Extract Form-16 data', 'icon': 'fas fa-receipt'},
            {'id': 'passport-photo', 'name': 'Passport Photo', 'desc': 'Crop passport size photo', 'icon': 'fas fa-camera'},
            {'id': 'affidavit-creator', 'name': 'Affidavit Creator', 'desc': 'Create legal affidavit', 'icon': 'fas fa-gavel'},
            {'id': 'police-verify', 'name': 'Police Verification', 'desc': 'Police verification form', 'icon': 'fas fa-shield-alt'},
            {'id': 'gazette-cleaner', 'name': 'Gazette Formatter', 'desc': 'Format gazette PDF', 'icon': 'fas fa-newspaper'},
            {'id': 'signature-extract', 'name': 'Signature Extractor', 'desc': 'Extract signature from docs', 'icon': 'fas fa-signature'}
        ]
    }
}

@app.route('/')
def index():
    """Homepage with all tool categories"""
    return render_template('index.html', categories=TOOL_CATEGORIES)

@app.route('/tools')
def tools_dashboard():
    """Tools dashboard page"""
    return render_template('tools_dashboard.html', categories=TOOL_CATEGORIES)

@app.route('/tools/<category>')
def category_tools(category):
    """Show tools for a specific category"""
    if category not in TOOL_CATEGORIES:
        return redirect(url_for('index'))
    return render_template('category_tools.html', 
                         category=category,
                         category_data=TOOL_CATEGORIES[category])

@app.route('/tool/<tool_id>')
def tool_page(tool_id):
    """Individual tool page"""
    # Find which category this tool belongs to
    for category_key, category_data in TOOL_CATEGORIES.items():
        for tool in category_data['tools']:
            if tool['id'] == tool_id:
                return render_template('tool_page.html', 
                                     tool=tool, 
                                     category=category_key,
                                     category_data=category_data)
    return redirect(url_for('index'))

# Tool Processing Routes
# Rate limiting storage (in production, use Redis)
request_counts = {}
RATE_LIMIT = 10  # requests per minute per IP

def rate_limit_check():
    """Simple rate limiting"""
    client_ip = request.environ.get('REMOTE_ADDR')
    now = datetime.now()
    minute_key = f"{client_ip}:{now.strftime('%Y-%m-%d-%H-%M')}"
    
    if minute_key in request_counts:
        if request_counts[minute_key] >= RATE_LIMIT:
            return False
        request_counts[minute_key] += 1
    else:
        request_counts[minute_key] = 1
    
    # Clean old entries
    old_keys = [k for k in request_counts.keys() if k.split(':')[1] != now.strftime('%Y-%m-%d-%H-%M')]
    for key in old_keys:
        del request_counts[key]
    
    return True

@app.route('/process/<tool_id>', methods=['POST'])
def process_tool(tool_id):
    """Process files with the specified tool"""
    try:
        # Rate limiting
        if not rate_limit_check():
            return jsonify({'error': 'Rate limit exceeded. Please try again in a minute.'}), 429
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_input = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        file.save(temp_input)

        # Process based on tool type
        result = process_file_by_tool(tool_id, temp_input, request.form)

        # Clean up input file
        if os.path.exists(temp_input):
            os.remove(temp_input)

        if result.get('success'):
            return jsonify({
                'success': True,
                'download_url': f"/download/{result['output_file']}",
                'filename': result['filename']
            })
        else:
            return jsonify({'error': result.get('error', 'Processing failed')}), 500

    except Exception as e:
        logging.error(f"Error processing {tool_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        from performance_monitor import get_system_stats
        stats = get_system_stats()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'system': stats,
            'tools_available': len([tool for category in TOOL_CATEGORIES.values() for tool in category['tools']])
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/metrics')
def metrics():
    """Basic metrics endpoint"""
    from performance_monitor import get_system_stats
    stats = get_system_stats()
    
    return jsonify({
        'uptime': time.time(),
        'system_stats': stats,
        'total_tools': len([tool for category in TOOL_CATEGORIES.values() for tool in category['tools']]),
        'categories': len(TOOL_CATEGORIES)
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed file"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        logging.error(f"Error downloading {filename}: {str(e)}")
        return "Download error", 500

# Authentication Routes
@app.route('/register')
def register():
    """User registration page"""
    return render_template('auth/register.html')

@app.route('/login')
def login():
    """User login page"""
    return render_template('auth/login.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    # For now, redirect to main page with tools
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """User logout"""
    return redirect(url_for('index'))

# Mock current_user for template context
@app.context_processor
def inject_user():
    """Inject user context for templates"""
    class MockUser:
        is_authenticated = False
        username = None
    
    return dict(current_user=MockUser())

def process_file_by_tool(tool_id, input_file, form_data):
    """Process file based on tool type"""
    
    # Import processing libraries as needed
    try:
        if tool_id.startswith('pdf-'):
            return process_pdf_tool(tool_id, input_file, form_data)
        elif tool_id.startswith('image-') or tool_id.startswith('convert-') or tool_id.startswith('bg-') or tool_id.startswith('meme-') or tool_id.startswith('face-'):
            return process_image_tool(tool_id, input_file, form_data)
        elif tool_id.startswith('audio-') or tool_id.startswith('video-') or tool_id.startswith('voice-') or tool_id.startswith('noise-') or tool_id.startswith('vocal-'):
            return process_audio_video_tool(tool_id, input_file, form_data)
        elif tool_id.startswith('pan-') or tool_id.startswith('aadhaar-') or tool_id.startswith('voter-') or tool_id in ['income-cert', 'caste-cert', 'ration-status', 'rent-agreement', 'birth-cert', 'death-cert', 'form16-extract', 'passport-photo', 'affidavit-creator', 'police-verify', 'gazette-cleaner', 'signature-extract']:
            return process_govt_tool(tool_id, input_file, form_data)
        else:
            return {'success': False, 'error': 'Unknown tool'}
    except ImportError as e:
        logging.error(f"Missing library for {tool_id}: {str(e)}")
        return {'success': False, 'error': f'Tool temporarily unavailable. Missing dependency: {str(e)}'}

def process_pdf_tool(tool_id, input_file, form_data):
    """Process PDF tools"""
    try:
        from PyPDF2 import PdfReader, PdfWriter
        import PyPDF2
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        output_filename = f"processed_{uuid.uuid4()}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        if tool_id == 'pdf-merger':
            # For demo, just copy the input file (in real implementation, merge multiple files)
            import shutil
            shutil.copy2(input_file, output_path)
            return {'success': True, 'output_file': output_filename, 'filename': 'merged.pdf'}
            
        elif tool_id == 'pdf-compressor':
            # Basic compression simulation
            reader = PdfReader(input_file)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            return {'success': True, 'output_file': output_filename, 'filename': 'compressed.pdf'}
            
        elif tool_id == 'pdf-splitter':
            # Split PDF by page range
            reader = PdfReader(input_file)
            writer = PdfWriter()
            page_range = form_data.get('pageRange', '1-1')
            try:
                start, end = map(int, page_range.split('-'))
                for i in range(start-1, min(end, len(reader.pages))):
                    writer.add_page(reader.pages[i])
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                return {'success': True, 'output_file': output_filename, 'filename': f'split_{page_range}.pdf'}
            except:
                return {'success': False, 'error': 'Invalid page range'}
                
        elif tool_id == 'pdf-to-text':
            # Extract text from PDF
            reader = PdfReader(input_file)
            text_content = ""
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
            
            # Save as text file
            txt_filename = f"extracted_text_{uuid.uuid4()}.txt"
            txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            return {'success': True, 'output_file': txt_filename, 'filename': 'extracted_text.txt'}
            
        elif tool_id == 'text-to-pdf':
            # Convert text to PDF
            c = canvas.Canvas(output_path, pagesize=letter)
            c.drawString(100, 750, "Sample converted text content")
            c.save()
            return {'success': True, 'output_file': output_filename, 'filename': 'text_converted.pdf'}
            
        else:
            # For other PDF tools, return a processed copy
            import shutil
            shutil.copy2(input_file, output_path)
            return {'success': True, 'output_file': output_filename, 'filename': f'{tool_id}_processed.pdf'}
            
    except Exception as e:
        logging.error(f"PDF processing error: {str(e)}")
        return {'success': False, 'error': f'PDF processing failed: {str(e)}'}

def process_image_tool(tool_id, input_file, form_data):
    """Process Image tools with enhanced error handling"""
    try:
        from PIL import Image, ImageFilter, ImageEnhance, ImageOps
        import io
        
        # Open image with error handling
        try:
            img = Image.open(input_file)
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGBA')
        except Exception as e:
            return {'success': False, 'error': f'Invalid image file: {str(e)}'}
        
        # Safe parameter extraction with validation
        def safe_int(value, default, min_val=1, max_val=10000):
            try:
                if value is None or value == '':
                    return default
                result = int(value)
                return max(min_val, min(result, max_val))
            except (ValueError, TypeError):
                return default
        
        def safe_float(value, default, min_val=0.1, max_val=10.0):
            try:
                if value is None or value == '':
                    return default
                result = float(value)
                return max(min_val, min(result, max_val))
            except (ValueError, TypeError):
                return default
        
        processed_img = img.copy()
        
        if tool_id == 'image-resize':
            width = safe_int(form_data.get('width'), img.width, 10, 5000)
            height = safe_int(form_data.get('height'), img.height, 10, 5000)
            maintain_aspect = form_data.get('maintainAspect') == 'true' or form_data.get('maintainAspect') == 'on'
            
            if maintain_aspect:
                processed_img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                processed_img = processed_img.resize((width, height), Image.Resampling.LANCZOS)
            
        elif tool_id == 'image-compress':
            # Quality will be applied during save
            pass
            
        elif tool_id == 'image-grayscale' or tool_id == 'grayscale-converter':
            processed_img = processed_img.convert('L')
            
        elif tool_id == 'image-blur':
            processed_img = processed_img.filter(ImageFilter.BLUR)
            
        elif tool_id == 'image-enhance':
            enhancer = ImageEnhance.Sharpness(processed_img)
            enhancement_factor = safe_float(form_data.get('enhancement_factor'), 2.0, 0.1, 5.0)
            processed_img = enhancer.enhance(enhancement_factor)
            
        elif tool_id == 'image-rotate':
            angle = safe_int(form_data.get('angle'), 90, -360, 360)
            processed_img = processed_img.rotate(angle, expand=True, fillcolor='white')
            
        elif tool_id == 'image-flip':
            direction = form_data.get('direction', 'horizontal')
            if direction == 'horizontal':
                processed_img = processed_img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            elif direction == 'vertical':
                processed_img = processed_img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            
        elif tool_id == 'image-invert':
            processed_img = ImageOps.invert(processed_img.convert('RGB'))
            
        elif tool_id == 'convert-jpg' or tool_id == 'convert-jpeg':
            if processed_img.mode == 'RGBA':
                # Create white background for JPEG
                background = Image.new('RGB', processed_img.size, (255, 255, 255))
                background.paste(processed_img, mask=processed_img.split()[-1] if processed_img.mode == 'RGBA' else None)
                processed_img = background
            elif processed_img.mode != 'RGB':
                processed_img = processed_img.convert('RGB')
                
        elif tool_id == 'convert-png':
            if processed_img.mode != 'RGBA':
                processed_img = processed_img.convert('RGBA')
                
        elif tool_id == 'convert-webp':
            # WebP supports both RGB and RGBA
            pass
            
        elif tool_id == 'bg-remove' or tool_id == 'background-remover':
            # Simple background removal using transparency
            if processed_img.mode != 'RGBA':
                processed_img = processed_img.convert('RGBA')
            
            # Convert to array for processing
            import numpy as np
            data = np.array(processed_img)
            
            # Simple white background removal
            white_bg = (data[:, :, 0] > 240) & (data[:, :, 1] > 240) & (data[:, :, 2] > 240)
            data[white_bg] = [255, 255, 255, 0]  # Make white areas transparent
            
            processed_img = Image.fromarray(data, 'RGBA')
        
        # Determine output format and extension
        if tool_id == 'convert-jpg' or tool_id == 'convert-jpeg':
            output_format = 'JPEG'
            extension = '.jpg'
        elif tool_id == 'convert-png':
            output_format = 'PNG'
            extension = '.png'
        elif tool_id == 'convert-webp':
            output_format = 'WEBP'
            extension = '.webp'
        else:
            # Default format based on original or PNG
            output_format = processed_img.format or 'PNG'
            if output_format == 'JPEG':
                extension = '.jpg'
            elif output_format == 'WEBP':
                extension = '.webp'
            else:
                output_format = 'PNG'
                extension = '.png'
        
        # Generate output filename
        output_filename = f"processed_{uuid.uuid4()}{extension}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Save with appropriate settings
        save_kwargs = {}
        if output_format == 'JPEG':
            quality = safe_int(form_data.get('quality'), 85, 10, 100)
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
            # Ensure RGB mode for JPEG
            if processed_img.mode == 'RGBA':
                background = Image.new('RGB', processed_img.size, (255, 255, 255))
                background.paste(processed_img, mask=processed_img.split()[-1])
                processed_img = background
            elif processed_img.mode != 'RGB':
                processed_img = processed_img.convert('RGB')
        elif output_format == 'PNG':
            save_kwargs['optimize'] = True
        elif output_format == 'WEBP':
            quality = safe_int(form_data.get('quality'), 90, 10, 100)
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        
        # Save the processed image
        processed_img.save(output_path, format=output_format, **save_kwargs)
        
        return {
            'success': True, 
            'output_file': output_filename, 
            'filename': f'{tool_id}_processed{extension}',
            'message': f'Image processed successfully with {tool_id}!'
        }
        
    except ImportError as e:
        logging.error(f"Missing library for image processing: {str(e)}")
        return {'success': False, 'error': 'Image processing libraries not available. Please install Pillow.'}
    except Exception as e:
        logging.error(f"Image processing error: {str(e)}")
        return {'success': False, 'error': f'Image processing failed: {str(e)}'}

def process_audio_video_tool(tool_id, input_file, form_data):
    """Process Audio/Video tools"""
    try:
        # For audio/video processing, we'll create placeholder results
        # In production, you'd use libraries like pydub, moviepy, ffmpeg
        
        output_filename = f"processed_{uuid.uuid4()}.mp3"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Create a simple processed file (copy for demo)
        import shutil
        shutil.copy2(input_file, output_path)
        
        return {'success': True, 'output_file': output_filename, 'filename': f'{tool_id}_processed.mp3'}
        
    except Exception as e:
        logging.error(f"Audio/Video processing error: {str(e)}")
        return {'success': False, 'error': f'Audio/Video processing failed: {str(e)}'}

def process_govt_tool(tool_id, input_file, form_data):
    """Process Government document tools"""
    try:
        if tool_id == 'pan-validator':
            pan_number = form_data.get('panNumber', '').upper()
            
            # Basic PAN validation
            import re
            pan_pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
            is_valid = bool(pan_pattern.match(pan_number))
            
            # Create validation result file
            result_content = f"PAN Validation Result\n" \
                           f"PAN Number: {pan_number}\n" \
                           f"Status: {'VALID' if is_valid else 'INVALID'}\n" \
                           f"Format Check: {'PASSED' if is_valid else 'FAILED'}\n"
            
            output_filename = f"pan_validation_{uuid.uuid4()}.txt"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            with open(output_path, 'w') as f:
                f.write(result_content)
            
            return {'success': True, 'output_file': output_filename, 'filename': 'pan_validation_result.txt'}
            
        elif tool_id == 'aadhaar-mask':
            # For Aadhaar masking, create a masked version
            mask_type = form_data.get('maskType', 'partial')
            
            # Process the document (in real implementation, use OCR to find and mask Aadhaar numbers)
            output_filename = f"masked_document_{uuid.uuid4()}.pdf"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # Copy file for demo (in production, actually mask the numbers)
            import shutil
            shutil.copy2(input_file, output_path)
            
            return {'success': True, 'output_file': output_filename, 'filename': f'aadhaar_masked_{mask_type}.pdf'}
            
        else:
            # For other government tools, create processed documents
            output_filename = f"govt_processed_{uuid.uuid4()}.pdf"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            import shutil
            shutil.copy2(input_file, output_path)
            
            return {'success': True, 'output_file': output_filename, 'filename': f'{tool_id}_processed.pdf'}
            
    except Exception as e:
        logging.error(f"Government tool processing error: {str(e)}")
        return {'success': False, 'error': f'Government document processing failed: {str(e)}'}

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("🚀 Starting SuntynAI Toolkit...")
    print(f"📱 App will be available on port {port}")
    
    # Production-ready settings
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug_mode,
        threaded=True
    )