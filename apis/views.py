from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse,HttpResponse
import urllib.parse
import requests
from django.contrib.auth import login, logout
from apis.models import CustomUser


def google_auth_start(request):
    # Google OAuth 2.0 authorization endpoint
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    
    # Parameters for the authorization request
    params = {
        "client_id": settings.CLIENT_ID,
        "redirect_uri": settings.REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/drive.file",
        "access_type": "offline",
        "prompt": "consent",
    }
    
    redirect_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(redirect_url)



def google_auth_callback(request):
    if "error" in request.GET:
        return redirect("/error/") 
    
    code = request.GET.get("code")
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "redirect_uri": settings.REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    response = requests.post(token_url, data=data)
    token_data = response.json()
    

    if "error" in token_data:
        return redirect("/error/") 
    
    access_token = token_data.get("access_token")
    id_token = token_data.get("id_token")
    refresh_token = token_data.get("refresh_token")
    

    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()
    
    if "error" in user_info:
        return redirect("/error/")  # Handle errors
    
    email = user_info.get("email")
    name = user_info.get("name")

    user, created = CustomUser.objects.get_or_create(email=email, defaults={"username": email, "first_name": name})
    
    user.access_token = access_token
    if refresh_token:
        user.refresh_token = refresh_token

    if created:
        user.set_unusable_password()

    user.save()
    login(request, user)

    return JsonResponse({"email": email, "name": name, "new_user": created})


def logout_view(request):
    if request.user.is_authenticated:
        
        request.user.access_token = None
        request.user.refresh_token = None
        request.user.save()

        
        logout(request)
        return JsonResponse({"message": "Logged out successfully"}, status=200)
    
    return JsonResponse({"error": "User is not logged in"}, status=400)


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def upload_to_drive(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            return JsonResponse({"error": "No file provided"}, status=400)
        
        access_token = getattr(request.user, "access_token", None)
        if not access_token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header.split(" ")[1]

        if not access_token:
            return JsonResponse({"error": "Access token is missing"}, status=403)
        
        upload_url = "https://www.googleapis.com/upload/drive/v3/files"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream",
        }
        params = {
            "uploadType": "media",
            "name": file.name,
        }
        response = requests.post(upload_url, headers=headers, params=params, data=file)
        
        if response.status_code == 200:
            return JsonResponse({"message": "File uploaded successfully", "file_id": response.json().get("id")})
        else:
            return JsonResponse({"error": "Failed to upload file"}, status=response.status_code)
        

def list_drive_files(request):
    
    access_token = getattr(request.user, "access_token", None)
    if not access_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]

    if not access_token:
        return JsonResponse({"error": "Access token is missing"}, status=403)
    
    
    files_url = "https://www.googleapis.com/drive/v3/files"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(files_url, headers=headers)
    
    if response.status_code == 200:
        files = response.json().get("files", [])
        return JsonResponse({"files": files})
    else:
        return JsonResponse({"error": "Failed to fetch files"}, status=response.status_code)
    

def download_from_drive(request, file_id):
    
    access_token = getattr(request.user, "access_token", None)
    if not access_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]

    if not access_token:
        return JsonResponse({"error": "Access token is missing"}, status=403)
    
    
    file_url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(file_url, headers=headers)
    
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch file metadata"}, status=response.status_code)
    
    
    download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    response = requests.get(download_url, headers=headers)
    
    if response.status_code == 200:
        file_content = response.content
        file_name = response.headers.get("content-disposition", "").split("filename=")[-1].strip('"')
        response = HttpResponse(file_content, content_type="application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response
    else:
        return JsonResponse({"error": "Failed to download file"}, status=response.status_code)