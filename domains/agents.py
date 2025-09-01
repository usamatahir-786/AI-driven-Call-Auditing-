# routers/agent.py

from fastapi import APIRouter, HTTPException, Depends
from core.database import get_db
from core.models import AgentCreate, AgentUpdate, AgentOut
from typing import List
import mysql.connector

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/", response_model=AgentOut)
def create_agent(agent: AgentCreate, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO Agent (name, department) VALUES (%s, %s)",
            (agent.name, agent.department)
        )
        db.commit()
        return {
            "agent_id": cursor.lastrowid,
            "name": agent.name,
            "department": agent.department
        }
    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/", response_model=List[AgentOut])
def get_all_agents(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Agent")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/{agent_id}", response_model=AgentOut)
def get_agent_by_id(agent_id: int, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Agent WHERE agent_id = %s", (agent_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Agent not found")
        return result
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.put("/{agent_id}", response_model=AgentOut)
def update_agent(agent_id: int, agent: AgentUpdate, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "UPDATE Agent SET name = %s, department = %s WHERE agent_id = %s",
            (agent.name, agent.department, agent_id)
        )
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {
            "agent_id": agent_id,
            "name": agent.name,
            "department": agent.department
        }
    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Agent WHERE agent_id = %s", (agent_id,))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent deleted successfully"}
    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
