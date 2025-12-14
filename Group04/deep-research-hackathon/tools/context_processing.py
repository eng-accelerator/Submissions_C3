import io
import requests
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def process_uploaded_file(uploaded_file) -> str:
    """Extracts text from an uploaded file (PDF or Text)."""
    if uploaded_file is None:
        return ""
    
    try:
        # PDF
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return f"\n[File: {uploaded_file.name}]\n{text[:10000]}..." # Limit to 10k chars for now
        
        # Text/Markdown
        elif uploaded_file.type in ["text/plain", "text/markdown"]:
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            content = stringio.read()
            return f"\n[File: {uploaded_file.name}]\n{content[:10000]}..."
            
    except Exception as e:
        return f"\n[Error processing file {uploaded_file.name}: {str(e)}]"
    
    return ""

def get_youtube_id(url):
    """Extracts video ID from YouTube URL."""
    try:
        query = urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
    except:
        return None
    return None

def process_youtube_url(url: str) -> str:
    """Fetches transcript from a YouTube URL."""
    if not url: return ""
    
    video_id = get_youtube_id(url)
    if not video_id:
        return f"\n[Error: Invalid YouTube URL: {url}]"
        
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([t['text'] for t in transcript_list])
        return f"\n[YouTube Video: {url}]\n{transcript_text[:10000]}..."
    except Exception as e:
        return f"\n[Error fetching transcript for {url}: {str(e)}]"

def process_context(uploaded_files, video_url: str) -> str:
    """Aggregates context from files and video."""
    context = []
    
    if uploaded_files:
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]
        for f in uploaded_files:
            context.append(process_uploaded_file(f))
            
    if video_url:
        context.append(process_youtube_url(video_url))
        
    return "\n".join(context)
