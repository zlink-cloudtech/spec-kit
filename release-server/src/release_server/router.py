from enum import Enum
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query, status, Request, BackgroundTasks, Header
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel
from release_server.services.package_service import PackageService
from release_server.auth import verify_token
from release_server.dependencies import get_package_service
from release_server.storage import PackageMetadata

router = APIRouter()

class ResponseFormat(str, Enum):
    JSON = "json"
    HTML = "html"

class Asset(BaseModel):
    name: str
    size: int
    browser_download_url: str

class Release(BaseModel):
    tag_name: str = "latest"
    assets: List[Asset]

@router.get(
    "/latest",
    response_model=Release,
    status_code=status.HTTP_200_OK
)
async def get_latest_release(
    request: Request,
    package_service: PackageService = Depends(get_package_service)
) -> Release:
    """
    Get latest release metadata in GitHub-compatible format.
    """
    packages = await package_service.list_packages()
    
    # Base URL for download links
    base_url = str(request.base_url).rstrip("/")
    
    assets = [
        Asset(
            name=p.name,
            size=p.size,
            browser_download_url=f"{base_url}/assets/{p.name}"
        ) for p in packages
    ]
    
    return Release(assets=assets)

@router.get(
    "/assets/{filename}",
    status_code=status.HTTP_200_OK
)
async def download_asset(
    filename: str,
    package_service: PackageService = Depends(get_package_service)
):
    """
    Download a package asset.
    """
    path = await package_service.get_package_path(filename)
    return FileResponse(path, media_type="application/octet-stream", filename=filename)

@router.delete(
    "/assets/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_token)]
)
async def delete_package(
    filename: str,
    package_service: PackageService = Depends(get_package_service)
):
    """
    Delete a package.
    """
    await package_service.delete_package(filename)

@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    response_model=PackageMetadata,
    dependencies=[Depends(verify_token)]
)
async def upload_package(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    overwrite: bool = Query(False, description="Overwrite valid file if it exists"),
    package_service: PackageService = Depends(get_package_service)
) -> PackageMetadata:
    """
    Upload a new package file.
    """
    result = await package_service.upload_package(file, overwrite=overwrite)
    background_tasks.add_task(package_service.cleanup_old_packages)
    return result

@router.get("/packages", response_model=List[PackageMetadata], responses={200: {"content": {"text/html": {}}}})
async def list_packages_negotiated(
    request: Request,
    accept: Optional[str] = Header(default="application/json"),
    format: Optional[ResponseFormat] = Query(None),
    package_service: PackageService = Depends(get_package_service)
):
    """
    List available packages. 
    Supports Content Negotiation:
    - Query param ?format=json/html takes precedence
    - Accept: text/html -> Returns simple HTML list
    - Accept: application/json -> Returns JSON list
    """
    packages = await package_service.list_packages()
    
    # Determine if HTML is requested
    want_html = False
    
    if format == ResponseFormat.HTML:
        want_html = True
    elif format == ResponseFormat.JSON:
        want_html = False
    elif accept and "text/html" in accept:
        want_html = True
        
    if want_html:
        html_content = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Release Server Packages</title>
                <style>
                    body { font-family: sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
                    ul { list-style: none; padding: 0; }
                    li { padding: 0.5rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
                    a { text-decoration: none; color: #0366d6; font-weight: bold; }
                    .meta { color: #666; font-size: 0.9em; }
                </style>
            </head>
            <body>
                <h1>📦 Available Packages</h1>
                <ul>
        """
        
        base_url = str(request.base_url).rstrip("/")
        
        if not packages:
            html_content += "<li>No packages found.</li>"
        
        for pkg in packages:
             download_url = f"{base_url}/assets/{pkg.name}"
             date_str = pkg.created_at.strftime("%Y-%m-%d %H:%M:%S")
             html_content += f"""
                <li>
                    <a href="{download_url}">{pkg.name}</a> 
                    <span class="meta">{pkg.size} bytes | {date_str}</span>
                </li>
             """
             
        html_content += """
                </ul>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    return packages

@router.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    """Liveness check"""
    return "OK"

@router.get("/readyz", response_class=PlainTextResponse)
async def readyz(package_service: PackageService = Depends(get_package_service)):
    """Readiness check"""
    # Simple check: Try to list packages to verify storage access
    try:
        await package_service.list_packages()
        return "OK"
    except Exception:
        return PlainTextResponse("Service Unavailable", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
