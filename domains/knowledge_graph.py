# routers/knowledge.py

from fastapi import APIRouter, HTTPException, Depends
from core.database import get_db
from core.models import KnowledgeUpload, KnowledgeOut
from typing import List
import mysql.connector
import json

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.post("/", response_model=dict)
def upload_knowledge_entry(data: KnowledgeUpload, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO Knowledge_Graph (user_id, json_data) VALUES (%s, %s)",
            (data.user_id, json.dumps(data.json_data))
        )
        db.commit()
        return {"message": "Knowledge graph entry uploaded successfully"}
    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/", response_model=List[KnowledgeOut])
def get_all_knowledge_entries(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Knowledge_Graph")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/{knowledge_graph_id}", response_model=KnowledgeOut)
def get_knowledge_entry(knowledge_graph_id: int, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Knowledge_Graph WHERE knowledge_graph_id = %s", (knowledge_graph_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
        return result
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.put("/{knowledge_graph_id}", response_model=dict)
def update_knowledge_entry(knowledge_graph_id: int, data: KnowledgeUpload, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        # Check if entry exists
        cursor.execute("SELECT * FROM Knowledge_Graph WHERE knowledge_graph_id = %s", (knowledge_graph_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")

        cursor.execute("""
            UPDATE Knowledge_Graph
            SET user_id = %s, json_data = %s
            WHERE knowledge_graph_id = %s
        """, (data.user_id, json.dumps(data.json_data), knowledge_graph_id))
        db.commit()

        return {"message": "Knowledge graph entry updated successfully"}
    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.delete("/{knowledge_graph_id}", response_model=dict)
def delete_knowledge_entry(knowledge_graph_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Knowledge_Graph WHERE knowledge_graph_id = %s", (knowledge_graph_id,))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
        return {"message": "Knowledge entry deleted successfully"}
    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
