import os
import json
from runwisper import transcribe_audio_local
import mysql.connector
from fastapi.responses import JSONResponse
from datetime import datetime
from mysql.connector import Error as MySQLError
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional

# ========== CONFIGURATION ==========
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SunshineCascade89")
DB_NAME = os.getenv("DB_NAME", "call_audit_db")
DB_PORT = int(os.getenv("DB_PORT", 3306))
UPLOAD_DIR = os.path.join(os.getcwd(), "calls")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== FASTAPI SETUP ==========
app = FastAPI(
    title="Call Audit API",
    description="FastAPI with MySQL for AI Call Audit System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== DATABASE FUNCTIONS ==========
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, 
            password=DB_PASSWORD, database=DB_NAME, 
            port=DB_PORT
        )
        if conn.is_connected():
            return conn
    except MySQLError as e:
        print(f"MySQL error: {e}")
    return None

# ========== MODELS ==========
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class AgentCreate(BaseModel):
    agent_name: str
    email: str
    agent_code: str

class CallCreate(BaseModel):
    agent_id: int
    user_id: int
    caller_number: str
    call_date: str
    duration: float
    audio_file: str
    upload_date: str
    transcription_text: Optional[str]
    ai_summary: Optional[str]

class CallScoreUpdate(BaseModel):
    greeting_score: float
    compliance_score: float
    knowledge_score: float
    empathy_score: float
    script_adherence_score: float
    overall_score: float
    remarks: Optional[str] = None

class KnowledgeUpload(BaseModel):
    user_id: int
    json_data: dict

# ========== HEALTH CHECK ==========
@app.get("/")
def health_check():
    return {"message": "FASTAPI is running successfully."}

# ========== USER ENDPOINTS ==========
@app.post("/users/create")
def create_user(user: UserCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO User (username, email, password) VALUES (%s, %s, %s)",
            (user.username, user.email, user.password)
        )
        conn.commit()
        return {"message": "User created successfully"}
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/users")
def get_users():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM user")
        return cur.fetchall()
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.put("/users/{user_id}")
def update_user(user_id: int, updated_user: UserCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE User 
            SET username = %s, email = %s, password = %s 
            WHERE user_id = %s
        """, (updated_user.username, updated_user.email, updated_user.password, user_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User updated successfully"}
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM User WHERE user_id = %s", (user_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ========== AGENT ENDPOINTS ==========
@app.post("/agents/create")
def create_agent(agent: AgentCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Agent (agent_name, email, agent_code) VALUES (%s, %s, %s)",
            (agent.agent_name, agent.email, agent.agent_code)
        )
        conn.commit()
        return {"message": "Agent created successfully"}
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/agents")
def get_agents():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM Agent")
        return cur.fetchall()
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/agents/{agent_id}")
def get_agent_by_id(agent_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM Agent WHERE agent_id = %s", (agent_id,))
        agent = cur.fetchone()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    finally:
        cur.close()
        conn.close()

@app.put("/agents/{agent_id}")
def update_agent(agent_id: int, updated_agent: AgentCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE Agent 
            SET agent_name = %s, email = %s, agent_code = %s 
            WHERE agent_id = %s
        """, (updated_agent.agent_name, updated_agent.email, updated_agent.agent_code, agent_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent updated successfully"}
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # First delete dependent records
        cur.execute("DELETE FROM Agent_Performance WHERE agent_id = %s", (agent_id,))
        # Then delete the agent
        cur.execute("DELETE FROM Agent WHERE agent_id = %s", (agent_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent deleted successfully"}
    except MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ========== CALL ENDPOINTS ==========
@app.post("/calls/upload-audio")
async def upload_call(
    agent_id: int = Form(...),
    user_id: int = Form(...),
    caller_number: str = Form(...),
    duration: float = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Save audio file
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"call_{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as f:
            f.write(await file.read())

        # Insert basic call data
        conn = get_db_connection()
        cur = conn.cursor()
        query = """
        INSERT INTO Calls (
            agent_id, user_id, caller_number, call_date, 
            duration, audio_file, upload_date
        ) VALUES (%s, %s, %s, NOW(), %s, %s, NOW())
        """
        cur.execute(query, (agent_id, user_id, caller_number, duration, filepath))
        conn.commit()
        call_id = cur.lastrowid
        cur.close()
        conn.close()

        return {
            "message": "Call uploaded successfully",
            "call_id": call_id,
            "audio_path": filepath
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/calls/get-transcription")
def get_transcription(call_id: int):
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed.")
        cur = conn.cursor()

        # Fetch audio file path
        cur.execute("SELECT audio_file FROM Calls WHERE call_id = %s", (call_id,))
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Call not found.")

        audio_path = result[0]
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found.")

        # Transcribe using Whisper
        transcription = transcribe_audio_local(audio_path)

        # Update transcription_text in DB
        cur.execute(
            "UPDATE Calls SET transcription_text = %s WHERE call_id = %s",
            (transcription, call_id)
        )
        conn.commit()
        cur.close()
        conn.close()

        return {
            "message": "Transcription generated successfully.",
            "call_id": call_id,
            "transcription": transcription
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.get("/calls")
def get_all_calls():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM Calls")
        return cur.fetchall()
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/calls/{call_id}")
def get_call_by_id(call_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM Calls WHERE call_id = %s", (call_id,))
        call = cur.fetchone()
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        return call
    finally:
        cur.close()
        conn.close()

@app.get("/calls/by-user/{user_id}")
def get_calls_by_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM Calls WHERE user_id = %s", (user_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()
@app.get("/calls/scores/all")  # Changed endpoint path to avoid conflict
def get_all_call_scores():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
            
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                call_id, 
                agent_id, 
                greeting_score, 
                compliance_status, 
                knowledge_score, 
                empathy_score, 
                script_adherence_score, 
                overall_score, 
                remarks
            FROM calls
            WHERE overall_score IS NOT NULL
            ORDER BY call_id DESC
        """)
        results = cur.fetchall()
        
        # Convert numeric fields to proper types
        for row in results:
            for field in ['call_id', 'agent_id']:
                if field in row and row[field] is not None:
                    row[field] = int(row[field])
            for field in ['greeting_score', 'knowledge_score', 'empathy_score', 
                         'script_adherence_score', 'overall_score']:
                if field in row and row[field] is not None:
                    row[field] = float(row[field])
        
        return results
        
    except MySQLError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
@app.delete("/calls/{call_id}")
def delete_call(call_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Calls WHERE call_id = %s", (call_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Call not found")
        return {"message": "Call deleted successfully"}
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ========== SCORING ENDPOINTS ==========

@app.get("/calls/scores/agent/{agent_id}")
def get_scores_by_agent(agent_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT call_id, greeting_score, compliance_status, knowledge_score,
                   empathy_score, script_adherence_score, overall_score, remarks
            FROM Calls
            WHERE agent_id = %s AND overall_score IS NOT NULL
        """, (agent_id,))
        return cur.fetchall()
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ========== KNOWLEDGE GRAPH ENDPOINTS ==========
@app.post("/knowledge/upload")
def upload_knowledge_graph(data: KnowledgeUpload):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Knowledge_Graph (user_id, json_data) VALUES (%s, %s)",
            (data.user_id, json.dumps(data.json_data))
        )
        conn.commit()
        return {"message": "Knowledge graph uploaded successfully"}
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/knowledge")
def get_all_knowledge_entries():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM Knowledge_Graph")
        return cur.fetchall()
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/knowledge/{entry_id}")
def get_knowledge_entry(entry_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT * FROM Knowledge_Graph WHERE knowledge_graph_id = %s", 
            (entry_id,)
        )
        entry = cur.fetchone()
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return entry
    finally:
        cur.close()
        conn.close()

@app.put("/knowledge/{entry_id}")
def update_knowledge_entry(entry_id: int, data: KnowledgeUpload):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE Knowledge_Graph
            SET user_id = %s, json_data = %s
            WHERE knowledge_graph_id = %s
        """, (data.user_id, json.dumps(data.json_data), entry_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entry not found")
        return {"message": "Knowledge graph entry updated successfully"}
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.delete("/knowledge/{entry_id}")
def delete_knowledge_entry(entry_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM Knowledge_Graph WHERE knowledge_graph_id = %s", 
            (entry_id,)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entry not found")
        return {"message": "Knowledge graph entry deleted successfully"}
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()