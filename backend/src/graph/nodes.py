import json
import os
import logging
import re  # <--- Added Regex for cleaning
from typing import Dict, Any, List

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

# Import the State schema .
from backend.src.graph.state import VideoAuditState, ComplianceIssue

# Import the Service
from backend.src.services.video_indexer import VideoIndexerService

# Configure Logger
logger = logging.getLogger("healthguard")
logging.basicConfig(level=logging.INFO)

# --- NODE 1: THE INDEXER ---
def index_video_node(state: VideoAuditState) -> Dict[str, Any]:
    """
    Downloads video from YouTube/TikTok, uploads to Azure VI, and extracts insights.
    """
    video_url = state.get("video_url")
    video_id_input = state.get("video_id", "vid_demo")
    
    logger.info(f"--- [Node: Indexer] Processing: {video_url} ---")
    
    local_filename = "temp_audit_video.mp4"
    
    try:
        vi_service = VideoIndexerService()
        
        # 1. DOWNLOAD (supports YouTube and TikTok)
        supported_domains = ["youtube.com", "youtu.be", "tiktok.com"]
        if any(domain in video_url for domain in supported_domains):
            local_path = vi_service.download_video(video_url, output_path=local_filename)
        else:
            raise Exception("Please provide a valid YouTube or TikTok URL.")

        # 2. UPLOAD
        azure_video_id = vi_service.upload_video(local_path, video_name=video_id_input)
        logger.info(f"Upload Success. Azure ID: {azure_video_id}")
        
        # 3. CLEANUP
        if os.path.exists(local_path):
            os.remove(local_path)

        # 4. WAIT
        raw_insights = vi_service.wait_for_processing(azure_video_id)
        
        # 5. EXTRACT
        clean_data = vi_service.extract_data(raw_insights)
        
        logger.info("--- [Node: Indexer] Extraction Complete ---")
        return clean_data

    except Exception as e:
        logger.error(f"Video Indexer Failed: {e}")
        return {
            "errors": [str(e)],
            "final_status": "FAIL",
            "transcript": "", 
            "ocr_text": []
        }

# --- NODE 1B: THE INDEXER (LOCAL FILE UPLOAD) ---
def index_uploaded_video_node(state: VideoAuditState) -> Dict[str, Any]:
    """
    Uploads a local video file directly to Azure VI (skips yt-dlp download).
    """
    local_path = state.get("local_file_path")
    video_id_input = state.get("video_id", "vid_upload")

    logger.info(f"--- [Node: Indexer-Upload] Processing local file: {local_path} ---")

    try:
        vi_service = VideoIndexerService()

        # 1. UPLOAD directly (no download needed)
        azure_video_id = vi_service.upload_video(local_path, video_name=video_id_input)
        logger.info(f"Upload Success. Azure ID: {azure_video_id}")

        # 2. CLEANUP
        if os.path.exists(local_path):
            os.remove(local_path)

        # 3. WAIT
        raw_insights = vi_service.wait_for_processing(azure_video_id)

        # 4. EXTRACT
        clean_data = vi_service.extract_data(raw_insights)
        # Mark platform as "upload" since there's no source URL
        if "video_metadata" in clean_data:
            clean_data["video_metadata"]["platform"] = "upload"

        logger.info("--- [Node: Indexer-Upload] Extraction Complete ---")
        return clean_data

    except Exception as e:
        logger.error(f"Video Indexer (Upload) Failed: {e}")
        return {
            "errors": [str(e)],
            "final_status": "FAIL",
            "transcript": "",
            "ocr_text": []
        }


# --- NODE 2: THE COMPLIANCE AUDITOR ---
def audit_content_node(state: VideoAuditState) -> Dict[str, Any]:
    """
    Performs Retrieval-Augmented Generation (RAG) to audit the content.
    """
    logger.info("--- [Node: Auditor] querying Knowledge Base & LLM ---")
    
    transcript = state.get("transcript", "")
    
    if not transcript:
        prior_errors = state.get("errors", [])
        error_detail = f" Errors: {prior_errors}" if prior_errors else ""
        logger.warning(f"No transcript available. Skipping Audit.{error_detail}")
        return {
            "final_status": "FAIL",
            "final_report": f"Audit skipped — no transcript extracted.{error_detail}"
        }

    # Initialize Clients
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.0
    )

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-3-small",
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )

    vector_store = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
        embedding_function=embeddings.embed_query
    )
    
    # RAG Retrieval
    ocr_text = state.get("ocr_text", [])
    query_text = f"{transcript} {' '.join(ocr_text)}"
    docs = vector_store.similarity_search(query_text, k=3)
    
    retrieved_rules = "\n\n".join([doc.page_content for doc in docs])
    
    # --- HEALTH CLAIMS AUDIT PROMPT ---
    system_prompt = f"""
    You are a Senior Health Claims Analyst specializing in social media content.
    Your job is to analyze TikTok/YouTube video content for misleading or
    dangerous health claims based on FTC, FDA, and WHO guidelines.
    
    OFFICIAL HEALTH GUIDELINES & RULES:
    {retrieved_rules}
    
    INSTRUCTIONS:
    1. Analyze the Transcript and OCR text below.
    2. Identify ANY health misinformation, unsubstantiated claims, or guideline violations.
    3. Focus on these violation categories:
       - "Unsubstantiated Health Claim" — health benefit claims without scientific evidence
       - "Misleading Medical Advice" — content that could lead viewers to harmful actions
       - "Dangerous Recommendation" — advice that poses direct health risks
       - "Undisclosed Sponsorship" — paid health product promotion without disclosure
       - "Fake Authority" — misrepresented credentials or false expert claims
       - "Deceptive Testimonial" — anecdotal evidence presented as proof
    4. Return strictly JSON in the following format:
    
    {{
        "compliance_results": [
            {{
                "category": "Unsubstantiated Health Claim",
                "severity": "CRITICAL",
                "description": "Explanation of the violation..."
            }}
        ],
        "status": "FAIL", 
        "final_report": "Summary of findings..."
    }}

    Severity levels:
    - CRITICAL: Direct disease cure/treatment claims, dangerous substance promotion,
      advice to stop medications, targeting vulnerable populations
    - WARNING: Unsubstantiated supplement claims, undisclosed sponsorships,
      misleading before/after results, cherry-picked science

    If no violations are found, set "status" to "PASS" and "compliance_results" to [].
    """

    user_message = f"""
    VIDEO METADATA: {state.get('video_metadata', {})}
    TRANSCRIPT: {transcript}
    ON-SCREEN TEXT (OCR): {ocr_text}
    """

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        # --- FIX: Clean Markdown if present (```json ... ```) ---
        content = response.content
        if "```" in content:
            # Regex to find JSON inside code blocks
            content = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL).group(1)
            
        audit_data = json.loads(content.strip())
        
        return {
            "compliance_results": audit_data.get("compliance_results", []),
            "final_status": audit_data.get("status", "FAIL"),
            "final_report": audit_data.get("final_report", "No report generated.")
        }

    except Exception as e:
        logger.error(f"System Error in Auditor Node: {str(e)}")
        # Log the raw response to see what went wrong
        logger.error(f"Raw LLM Response: {response.content if 'response' in locals() else 'None'}")
        return {
            "errors": [str(e)],
            "final_status": "FAIL"
        }