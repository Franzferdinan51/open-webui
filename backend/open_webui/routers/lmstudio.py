from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
import httpx
import asyncio

from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.config import get_config

router = APIRouter()

class ModelLoadRequest(BaseModel):
    model: str

class LMStudioModel(BaseModel):
    id: str
    name: str
    path: Optional[str] = None
    size: Optional[int] = None
    loaded: Optional[bool] = False
    provider: str = "lmstudio"

@router.get("/models", response_model=List[LMStudioModel])
async def get_lmstudio_models(request: Request, user=Depends(get_verified_user)):
    """
    Get available LM Studio models
    """
    try:
        # Get LM Studio configuration (we'll need to implement getting the actual URL from config)
        lm_studio_url = "http://localhost:1234"  # Default, should come from config
        
        # Make request to LM Studio API
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{lm_studio_url}/v1/models", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                models = []
                
                for model in data.get("data", []):
                    models.append(LMStudioModel(
                        id=model.get("id", ""),
                        name=model.get("id", ""),
                        path=model.get("root", ""),
                        loaded=True,  # If it's returned by /v1/models, it's likely loaded
                        provider="lmstudio"
                    ))
                
                return models
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"LM Studio API error: {response.text}"
                )
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to LM Studio: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching LM Studio models: {str(e)}"
        )

@router.post("/models/load")
async def load_lmstudio_model(
    request: Request,
    form_data: ModelLoadRequest,
    user=Depends(get_admin_user)
):
    """
    Load a model in LM Studio
    """
    try:
        lm_studio_url = "http://localhost:1234"  # Default, should come from config
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{lm_studio_url}/v1/models/load",
                json={"model": form_data.model},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return {"status": "success", "message": f"Model {form_data.model} loaded successfully"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to load model: {response.text}"
                )
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to LM Studio: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading model: {str(e)}"
        )

@router.post("/models/unload")
async def unload_lmstudio_model(
    request: Request,
    form_data: ModelLoadRequest,
    user=Depends(get_admin_user)
):
    """
    Unload a model in LM Studio
    """
    try:
        lm_studio_url = "http://localhost:1234"  # Default, should come from config
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{lm_studio_url}/v1/models/unload",
                json={"model": form_data.model},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return {"status": "success", "message": f"Model {form_data.model} unloaded successfully"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to unload model: {response.text}"
                )
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to LM Studio: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error unloading model: {str(e)}"
        )

@router.get("/models/{model_id}")
async def get_lmstudio_model_info(
    request: Request,
    model_id: str,
    user=Depends(get_verified_user)
):
    """
    Get information about a specific LM Studio model
    """
    try:
        lm_studio_url = "http://localhost:1234"  # Default, should come from config
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{lm_studio_url}/v1/models/{model_id}", timeout=10.0)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Model not found: {response.text}"
                )
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to LM Studio: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching model info: {str(e)}"
        )