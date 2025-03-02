import os
import httpx
from fastapi import HTTPException
from datetime import datetime, timedelta
import jwt


from load_env import load_vars

load_vars()

BACKEND_URL = os.getenv("BACKEND_URL")
SERVICE_EMAIL = os.getenv("SERVICE_EMAIL")
SERVICE_PASSWORD = os.getenv("SERVICE_PASSWORD")

class TokenManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._access_token = None
            cls._instance._refresh_token = None
            cls._instance._token_expiry = None
        return cls._instance
    
    async def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        if self._is_token_valid():
            return self._access_token
            
        if self._refresh_token:
            success = await self._refresh_access_token()
            if success:
                return self._access_token
                
        # If we get here, we need to login again
        success = await self._login()
        if success:
            return self._access_token
        raise HTTPException(status_code=401, detail="Could not authenticate with service credentials")
    
    def _is_token_valid(self) -> bool:
        """Check if current access token is valid"""
        if not self._access_token or not self._token_expiry:
            return False
        return datetime.now() < self._token_expiry - timedelta(minutes=1)  # 1 min buffer
    
    async def _refresh_access_token(self) -> bool:
        """Attempt to refresh the access token"""
        url = f"{BACKEND_URL}auth/refresh/"
        data = {"refresh": self._refresh_token}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data)
                if response.status_code == 200:
                    self._update_tokens(
                        response.json()["access"],
                        self._refresh_token  # Keep existing refresh token
                    )
                    return True
            except Exception as e:
                print(f"Token refresh error: {e}")
            return False
    
    async def _login(self) -> bool:
        """Login to get new access and refresh tokens"""
        url = f"{BACKEND_URL}auth/login/"
        data = {
            "email": SERVICE_EMAIL.strip(),
            "password": SERVICE_PASSWORD
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        print("Attempting login with:", {
            "email": SERVICE_EMAIL.strip(),
            "password": "***" # Masked for security
        })
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self._update_tokens(data["access"], data["refresh"])
                    return True
                else:
                    print(f"Login failed with status {response.status_code}")
                    print(f"Response body: {response.text}")
                    print(f"Request URL: {url}")
                    print(f"Request headers: {headers}")
            except Exception as e:
                print(f"Login error: {str(e)}")
            return False
    
    def _update_tokens(self, access_token: str, refresh_token: str):
        """Update stored tokens and calculate expiry"""
        self._access_token = access_token
        self._refresh_token = refresh_token
        
        # Decode JWT to get expiry (without verification)
        try:
            payload = jwt.decode(access_token, options={"verify_signature": False})
            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                self._token_expiry = datetime.fromtimestamp(exp_timestamp)
        except Exception as e:
            print(f"Error decoding token: {e}")
            self._token_expiry = datetime.now() + timedelta(minutes=55)  # Fallback expiry



class DjangoInteract():
    def __init__(self, access_token, basemodel_id, model_id, phone_number, user_name, business_id, thread_id):
        self.access_token = access_token
        self.basemodel_id = basemodel_id
        self.model_id = model_id
        self.phone_number = phone_number
        self.user_name = user_name
        self.business_id = business_id
        self.thread_id = thread_id

    async def save_messages(self, user_message, assistant_message, output_type, double_message):
        url = f"{BACKEND_URL}basemodel/wa/save_message/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        
        data = {
            "business_id": self.business_id,
            "user_message": user_message,
            "assistant_message": assistant_message, 
            "user_name": self.user_name,
            "thread_id": self.thread_id,
            "basemodel_id": self.basemodel_id,
            "phone_number": self.phone_number,
            "model_id": self.model_id,
            "output_type": output_type,
            "double_message": double_message
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            return response



class Getters:
    def __init__(self, access_token, business_id, phone_number_id):
        self.access_token = access_token
        self.business_id = business_id
        self.phone_number_id = phone_number_id

    async def get_product(self, ai_output):
        url = f"{BACKEND_URL}basemodel/wa/get-product-info/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "phone_number_id": self.phone_number_id,
            "business_id": self.business_id,
            "ai_output": ai_output,
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return (
                        result["image_url"],
                        result["button_text"],
                        result["button_url"]
                    )
                else:
                    print(f"Error getting product info: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None, None, None
            except Exception as e:
                print(f"Exception getting product info: {str(e)}")
                return None, None, None
    
    async def get_location(self, ai_output):

        url = f"{BACKEND_URL}basemodel/wa/get-location-info/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"  
        }

        data = {
            "business_id": self.business_id,
            "ai_output": ai_output,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return (
                        result["latitude"],
                        result["longitude"],
                        result["name"],
                        result["address"]
                    )
                else:
                    print(f"Error getting location info: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None, None, None, None
            except Exception as e:
                print(f"Exception getting location info: {str(e)}")
                return None, None, None, None
            
    
                    
    async def get_cta_url(self, ai_output):

        url = f"{BACKEND_URL}basemodel/wa/get-cta-url/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "business_id": self.business_id,
            "ai_output": ai_output,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return result["cta_url"]
                else:
                    print(f"Error getting CTA URL: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
            except Exception as e:
                print(f"Exception getting CTA URL: {str(e)}")
                return None 





class DjangoAccess:
    def __init__(self, phone_number_id, business_id, phone_number):
        self.phone_number_id = phone_number_id
        self.business_id = business_id
        self.phone_number = phone_number
        self.token_manager = TokenManager()
        self.basemodel_id = None
        self.access_token = None

    async def get_service_token(self):
        """Get a valid service token"""
        token = await self.token_manager.get_valid_token()
        if not token:
            raise HTTPException(status_code=401, detail="Failed to get service token")
        return token

    async def get_modelID_and_conversation(self):
        # Get token first since we removed initialize
        self.access_token = await self.token_manager.get_valid_token()
        if not self.access_token:
            raise HTTPException(status_code=401, detail="Failed to get access token")
            
        url = f"{BACKEND_URL}wa/get-model-id/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        params = {
            "phone_number": self.phone_number,
            "business_id": self.business_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers, params=params)
            res = response.json()

            model_id = res["data"]["provider_model_id"]
            system_prompt = res["data"]["system_prompt"]
            thread_id = res["data"]["thread_id"]
            basemodel_id = res["data"]["basemodel_id"]

            return model_id, system_prompt, thread_id, self.access_token, basemodel_id