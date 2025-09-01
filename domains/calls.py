from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from core.database import get_db
from core.models import CallCreate, CallResponse, CallScoreUpdate
from utils.audio_processor import save_audio_file
from typing import List
import os

router = APIRouter(prefix="/calls", tags=["calls"])

@router.post("/upload", response_model=CallResponse)
async def upload_call(
    agent_id: int = Form(...),
    user_id: int = Form(...),
    caller_number: str = Form(...),
    duration: float = Form(...),
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)
    try:
        filepath = save_audio_file(file)
        cursor.execute(
            """INSERT INTO Calls 
            (agent_id, user_id, caller_number, duration, audio_file) 
            VALUES (%s, %s, %s, %s, %s)""",
            (agent_id, user_id, caller_number, duration, filepath)
        )
        db.commit()
        call_id = cursor.lastrowid

        return {
            "id": call_id,
            "agent_id": agent_id,
            "user_id": user_id,
            "caller_number": caller_number,
            "audio_file": filepath
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.post("/{call_id}/score", response_model=CallResponse)
def score_call(
    call_id: int, 
    scores: CallScoreUpdate,
    db = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            """UPDATE Calls SET
            greeting_score = %s,
            compliance_status = %s,
            knowledge_score = %s,
            empathy_score = %s,
            script_adherence_score = %s,
            overall_score = %s,
            remarks = %s
            WHERE id = %s""",
            (
                scores.greeting_score,
                scores.compliance_status,
                scores.knowledge_score,
                scores.empathy_score,
                scores.script_adherence_score,
                scores.overall_score,
                scores.remarks,
                call_id
            )
        )
        db.commit()
        return {"message": "Call scored successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
