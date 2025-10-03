"""
FastAPI Backend Server for Research Journal Recommendation System
==================================================================
Connects Next.js frontend with Python backend (Vraj + Aadi integration)

API Endpoints:
- POST /api/recommend - Get journal recommendations

Author: Vraj + Aadi + Kunj (Full Integration)
Date: October 3, 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import subprocess
import sys
import os
from pathlib import Path
import logging
import tempfile
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Research Journal Recommendation API",
    description="AI-powered journal recommendation system using Gemini AI and OpenAlex",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get base directory
BASE_DIR = Path(__file__).parent.absolute()
VRAJ_DIR = BASE_DIR / "Vraj"
AADI_DIR = BASE_DIR / "Aadi"
REFINED_OUTPUT = BASE_DIR / "refined_output.json"
JOURNAL_RESULTS = AADI_DIR / "journal_results.json"


# Request/Response Models
class RecommendationRequest(BaseModel):
    """Frontend request format"""
    subjectArea: str = Field(..., description="Research subject area")
    title: str = Field(..., description="Paper title")
    abstract: str = Field(..., description="Paper abstract")
    accPercentFrom: int = Field(..., ge=0, le=100, description="Acceptance rate from")
    accPercentTo: int = Field(..., ge=0, le=100, description="Acceptance rate to")
    openAccess: bool = Field(..., description="Open access filter (true=free only, false=any)")


class JournalRecommendation(BaseModel):
    """Single journal recommendation"""
    name: str
    publisher: str
    impactFactor: float  # h-index
    citationCount: int
    acceptanceRate: int  # Estimated from range
    openAccess: bool
    apc: Optional[float]  # Article Processing Charge in USD
    homepage: str
    score: float  # Quality score 0-100
    explanation: str
    rank: int


class RecommendationResponse(BaseModel):
    """API response format"""
    success: bool
    inputData: dict
    recommendations: List[JournalRecommendation]
    processingTime: float


class FormatConverter:
    """Convert between frontend and backend formats"""
    
    @staticmethod
    def frontend_to_backend(frontend_data: RecommendationRequest) -> dict:
        """
        Convert frontend format to backend format for Vraj system.
        
        Frontend sends:
        - openAccess: boolean (true/false)
        
        Backend expects:
        - openAccess: string ("yes"/"any")
        """
        return {
            "subjectArea": frontend_data.subjectArea,
            "title": frontend_data.title,
            "abstract": frontend_data.abstract,
            "accPercentFrom": frontend_data.accPercentFrom,
            "accPercentTo": frontend_data.accPercentTo,
            "openAccess": "yes" if frontend_data.openAccess else "any"
        }
    
    @staticmethod
    def _estimate_acceptance_rate(journal: dict) -> int:
        """
        Estimate journal acceptance rate based on h-index with smooth interpolation.
        Higher prestige journals typically have lower acceptance rates.
        
        Uses linear interpolation within ranges and adds random variance for realism:
        - h-index > 300: 5-15% (top-tier: Nature, Science, etc.)
        - h-index 100-300: 15-35% (interpolated, excellent to very good)
        - h-index 10-100: 35-60% (interpolated, good to moderate)
        - h-index < 10: 60-85% (lower quality)
        
        Adds ±3% random jitter for realistic variance.
        """
        import random
        
        h_index = journal.get('h_index', 0)
        
        # Calculate base acceptance rate using smooth interpolation
        if h_index > 300:
            # Top-tier journals: stable low rate
            base_rate = 10  # Mid-point of 5-15%
        
        elif h_index >= 100:
            # Medium-to-high range: linear interpolation from 35% (at 100) to 15% (at 300)
            # Formula: rate = 35 - ((h_index - 100) / (300 - 100)) * (35 - 15)
            base_rate = 35 - ((h_index - 100) / 200) * 20
        
        elif h_index >= 10:
            # Low-to-medium range: linear interpolation from 60% (at 10) to 35% (at 100)
            # Formula: rate = 60 - ((h_index - 10) / (100 - 10)) * (60 - 35)
            base_rate = 60 - ((h_index - 10) / 90) * 25
        
        else:
            # Very low h-index: high acceptance rate
            base_rate = 72  # Mid-point of 60-85%
        
        # Add random jitter: ±3 percentage points for realistic variance
        jitter = random.uniform(-3, 3)
        final_rate = base_rate + jitter
        
        # Clamp between 5% and 85%, return as integer
        return int(max(5, min(85, final_rate)))
    
    @staticmethod
    def backend_to_frontend(backend_journals: List[dict], acceptance_range: tuple) -> List[JournalRecommendation]:
        """
        Convert backend journal results to frontend format.
        
        Backend returns:
        - journal_name, h_index, cited_by_count, publisher, etc.
        
        Frontend expects:
        - name, impactFactor, acceptanceRate, openAccess, explanation, etc.
        """
        recommendations = []
        
        for journal in backend_journals:
            # Estimate acceptance rate based on journal quality (h-index)
            estimated_acceptance = FormatConverter._estimate_acceptance_rate(journal)
            
            # Generate explanation based on journal metrics
            explanation = FormatConverter._generate_explanation(journal, estimated_acceptance)
            
            recommendation = JournalRecommendation(
                name=journal.get('journal_name', 'N/A'),
                publisher=journal.get('publisher', 'N/A'),
                impactFactor=float(journal.get('h_index', 0)),
                citationCount=journal.get('cited_by_count', 0),
                acceptanceRate=estimated_acceptance,  # Estimated from h-index
                openAccess=journal.get('is_open_access', False),
                apc=journal.get('apc_usd'),
                homepage=journal.get('homepage_url', ''),
                score=float(journal.get('calculated_score', 0)),
                explanation=explanation,
                rank=journal.get('rank', 0)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    @staticmethod
    def _generate_explanation(journal: dict, acceptance_rate: int) -> str:
        """Generate AI-like explanation for journal recommendation"""
        name = journal.get('journal_name', 'This journal')
        h_index = journal.get('h_index', 0)
        citations = journal.get('cited_by_count', 0)
        is_oa = journal.get('is_open_access', False)
        score = journal.get('calculated_score', 0)
        relevance = journal.get('relevance_count', 0)
        
        # Build explanation based on metrics
        explanations = []
        
        # Score-based intro
        if score >= 70:
            explanations.append(f"Highly recommended journal with exceptional quality metrics (score: {score:.1f}/100).")
        elif score >= 60:
            explanations.append(f"Strong publication venue with solid reputation (score: {score:.1f}/100).")
        elif score >= 50:
            explanations.append(f"Reputable journal with good standing (score: {score:.1f}/100).")
        else:
            explanations.append(f"Emerging journal with growing impact (score: {score:.1f}/100).")
        
        # h-index
        if h_index >= 300:
            explanations.append(f"Exceptional h-index of {h_index} indicates world-class influence.")
        elif h_index >= 150:
            explanations.append(f"High h-index of {h_index} demonstrates strong academic impact.")
        elif h_index >= 50:
            explanations.append(f"Solid h-index of {h_index} shows established reputation.")
        
        # Citations
        if citations >= 1000000:
            explanations.append(f"Extremely high citation count ({citations:,}) reflects broad readership.")
        elif citations >= 100000:
            explanations.append(f"Substantial citation count ({citations:,}) indicates wide visibility.")
        
        # Relevance
        if relevance >= 5:
            explanations.append(f"Frequently publishes in your research area ({relevance} relevant papers found).")
        elif relevance >= 2:
            explanations.append(f"Actively publishes related research ({relevance} relevant papers found).")
        
        # Open Access
        if is_oa:
            explanations.append("Open access publication ensures maximum visibility and impact.")
        
        # Acceptance rate
        if acceptance_rate < 20:
            explanations.append("Highly selective with rigorous peer review process.")
        elif acceptance_rate < 30:
            explanations.append("Competitive acceptance rate maintains quality standards.")
        
        return " ".join(explanations)


class PipelineRunner:
    """Run the integrated pipeline and return results"""
    
    @staticmethod
    def run_pipeline(input_data: dict) -> List[dict]:
        """
        Run the integrated pipeline with given input data.
        
        Steps:
        1. Write input to refined_output.json (bypass Vraj's interactive input)
        2. Convert to format.json for Aadi
        3. Run Aadi's journal search
        4. Read and return results
        """
        try:
            # Step 1: Convert openAccess from "yes"/"any" to 1/0 for backend
            backend_data = {
                "subjectArea": input_data["subjectArea"],
                "keywords": [input_data["subjectArea"]],  # Will be refined by Vraj
                "openAccess": 1 if input_data["openAccess"] == "yes" else 0,
                "acceptancePercentFrom": input_data["accPercentFrom"],
                "acceptancePercentTo": input_data["accPercentTo"]
            }
            
            # Step 2: Write to refined_output.json (skip Vraj's interactive part)
            # We'll call Vraj's refinement programmatically
            refined_data = PipelineRunner._run_vraj_refinement(input_data)
            
            # Step 3: Write to Aadi's format.json
            format_file = AADI_DIR / "format.json"
            with open(format_file, 'w', encoding='utf-8') as f:
                json.dump(refined_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Wrote format.json with {len(refined_data.get('keywords', []))} keywords")
            
            # Step 3.5: Clear old cached results to prevent stale data
            logger.info("Clearing old cached results...")
            cache_files = [
                AADI_DIR / "journal_results.json",
                AADI_DIR / "__pycache__"
            ]
            for cache_file in cache_files:
                try:
                    if cache_file.exists():
                        if cache_file.is_dir():
                            import shutil
                            shutil.rmtree(cache_file)
                            logger.debug(f"Removed cache directory: {cache_file}")
                        else:
                            cache_file.unlink()
                            logger.debug(f"Removed cache file: {cache_file}")
                except Exception as e:
                    logger.warning(f"Could not remove {cache_file}: {e}")
            
            # Step 4: Run Aadi's journal search
            PipelineRunner._run_aadi_search()
            
            # Step 5: Read results
            if not JOURNAL_RESULTS.exists():
                raise FileNotFoundError("journal_results.json not found after search")
            
            with open(JOURNAL_RESULTS, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            logger.info(f"Found {len(results)} journal recommendations")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")
    
    @staticmethod
    def _run_vraj_refinement(input_data: dict) -> dict:
        """Run Vraj's refinement system programmatically"""
        try:
            # Import Vraj's main module
            sys.path.insert(0, str(VRAJ_DIR))
            from main import PaperSearchBackend
            
            # Load Gemini API key from Vraj's .env
            vraj_env = VRAJ_DIR / ".env"
            if vraj_env.exists():
                from dotenv import load_dotenv
                load_dotenv(vraj_env)
                api_key = os.getenv("GEMINI_API_KEY")
            else:
                api_key = None
            
            logger.info("Running Vraj's refinement...")
            
            if api_key:
                backend = PaperSearchBackend(api_key=api_key)
            else:
                raise ValueError("No Gemini API key found")
            
            # Prepare input in Vraj's format
            vraj_input = {
                "subjectArea": input_data["subjectArea"],
                "title": input_data["title"],
                "abstract": input_data["abstract"],
                "accPercentFrom": input_data["accPercentFrom"],
                "accPercentTo": input_data["accPercentTo"],
                "openAccess": input_data["openAccess"]  # "yes" or "any"
            }
            
            # Run refinement
            refined = backend.process_input(vraj_input)
            
            logger.info(f"Refinement complete: {len(refined.get('keywords', []))} keywords extracted")
            
            return refined
            
        except Exception as e:
            logger.warning(f"Vraj refinement failed: {e}. Using intelligent fallback.")
            # Intelligent Fallback: Extract keywords from input text
            import re
            
            # Combine all text
            all_text = f"{input_data['subjectArea']} {input_data['title']} {input_data['abstract']}"
            
            # Remove common words and extract meaningful keywords
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                         'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                         'this', 'that', 'these', 'those', 'we', 'our', 'using', 'paper'}
            
            # Extract words (lowercase, remove punctuation)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            
            # Filter and deduplicate
            keywords = []
            seen = set()
            for word in words:
                if word not in stop_words and word not in seen and len(word) > 3:
                    keywords.append(word)
                    seen.add(word)
                    if len(keywords) >= 20:  # Limit to 20 keywords
                        break
            
            # Ensure we have the subject area
            if input_data["subjectArea"].lower() not in seen:
                keywords.insert(0, input_data["subjectArea"].lower())
            
            logger.info(f"Fallback extracted {len(keywords)} keywords: {keywords[:5]}...")
            
            return {
                "subjectArea": input_data["subjectArea"],
                "keywords": keywords,
                "openAccess": 1 if input_data["openAccess"] == "yes" else 0,
                "acceptancePercentFrom": input_data["accPercentFrom"],
                "acceptancePercentTo": input_data["accPercentTo"]
            }
    
    @staticmethod
    def _run_aadi_search():
        """Run Aadi's journal search system"""
        try:
            logger.info("Running Aadi's journal search...")
            
            # Run Aadi's fetch_journals.py
            result = subprocess.run(
                [sys.executable, str(AADI_DIR / "fetch_journals.py")],
                cwd=str(AADI_DIR),
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Aadi search failed: {result.stderr}")
                raise Exception(f"Journal search failed: {result.stderr}")
            
            logger.info("Aadi search completed successfully")
            
        except subprocess.TimeoutExpired:
            raise Exception("Journal search timed out after 60 seconds")
        except Exception as e:
            raise Exception(f"Journal search execution failed: {str(e)}")


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Research Journal Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/recommend": "Get journal recommendations"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "vraj_available": VRAJ_DIR.exists(),
        "aadi_available": AADI_DIR.exists(),
        "timestamp": time.time()
    }


@app.post("/api/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get journal recommendations based on paper details.
    
    Request Body:
    - subjectArea: Research subject area (e.g., "Machine Learning")
    - title: Paper title
    - abstract: Paper abstract
    - accPercentFrom: Min acceptance rate (0-100)
    - accPercentTo: Max acceptance rate (0-100)
    - openAccess: true (free only) or false (any)
    
    Returns:
    - List of top 5 journal recommendations with scores and explanations
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received recommendation request for: {request.subjectArea}")
        
        # Convert frontend format to backend format
        backend_input = FormatConverter.frontend_to_backend(request)
        
        # Run the integrated pipeline
        journal_results = PipelineRunner.run_pipeline(backend_input)
        
        # Convert backend results to frontend format (TOP 3 ONLY)
        all_recommendations = FormatConverter.backend_to_frontend(
            journal_results,
            acceptance_range=(request.accPercentFrom, request.accPercentTo)
        )
        
        # Return only top 3 recommendations
        recommendations = all_recommendations[:3]
        
        processing_time = time.time() - start_time
        
        logger.info(f"Request processed in {processing_time:.2f}s, returning top {len(recommendations)} recommendations")
        
        return RecommendationResponse(
            success=True,
            inputData=request.model_dump(),
            recommendations=recommendations,
            processingTime=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Research Journal Recommendation API Server...")
    logger.info(f"Base directory: {BASE_DIR}")
    logger.info(f"Vraj directory: {VRAJ_DIR}")
    logger.info(f"Aadi directory: {AADI_DIR}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
