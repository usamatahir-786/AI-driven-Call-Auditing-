from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime

# ===== USER MODELS =====
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# ===== AGENT MODELS =====
class AgentBase(BaseModel):
    email: EmailStr
    agent_name: str

class AgentCreate(AgentBase):
    agent_code: str

class AgentResponse(AgentBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# ===== CALL MODELS =====
class CallBase(BaseModel):
    agent_id: int
    user_id: int
    caller_number: str

class CallCreate(CallBase):
    duration: float

class CallResponse(CallBase):
    id: int
    call_date: datetime
    audio_file: str
    transcription_text: Optional[str]
    ai_summary: Optional[str]

    class Config:
        from_attributes = True

# ===== SCORING MODELS =====
class CallScoreUpdate(BaseModel):
    greeting_score: float = Field(..., ge=0, le=5)
    compliance_status: str
    knowledge_score: float = Field(..., ge=0, le=5)
    empathy_score: float = Field(..., ge=0, le=5)
    script_adherence_score: float = Field(..., ge=0, le=5)
    overall_score: float = Field(..., ge=0, le=5)
    remarks: Optional[str]

# ===== KNOWLEDGE GRAPH MODELS =====
class KnowledgeBase(BaseModel):
    user_id: int

class KnowledgeCreate(KnowledgeBase):
    json_data: Dict

class KnowledgeResponse(KnowledgeBase):
    id: int
    upload_time: datetime
    json_data: Dict

    class Config:
        from_attributes = True