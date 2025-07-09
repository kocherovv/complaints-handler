import asyncio
import time
import logging
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pkg.models import ComplaintRequest, ComplaintResponse, ComplaintDetailResponse, CloseComplaintRequest, GetComplaintsRequest
from pkg.repository import init_db, fetch_complaints_from_db, save_complaint_to_db, update_category_in_db, mark_complaint_as_closed
from pkg.service import get_sentiment_async, get_category_async

logging.basicConfig(
    level=logging.DEBUG,
)
log = logging.getLogger("default")

app = FastAPI()
openai_client = AsyncOpenAI()

init_db()


@app.post("/complaint", response_model=ComplaintResponse)
async def handle_complaint(complaint_request: ComplaintRequest):
    complaint_text = complaint_request.text

    try:
        sentiment = await get_sentiment_async(complaint_text)
    except Exception as e:
        log.warning(f"[WARNING] Не удалось определить sentiment: {e}")
        sentiment = "unknown"

    try:
        complaint_id = await asyncio.to_thread(save_complaint_to_db, complaint_text, sentiment)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при сохранении в базу данных")

    try:
        category = await get_category_async(complaint_text)
        log.debug(f"[DEBUG] category: {category}")
        await asyncio.to_thread(update_category_in_db, category, complaint_id)
    except Exception as e:
        log.warning(f"[WARNING] Не удалось определить категорию: {e}")
        category = "другое"

    return ComplaintResponse(id=complaint_id, status="open", sentiment=sentiment, category=category)


@app.get("/complaints")
async def get_complaints(getComplaintsRequest: GetComplaintsRequest):
    try:
        from_time = int(time.time()) - getComplaintsRequest.hours * 3600

        valid_statuses = {"open", "closed"}
        if getComplaintsRequest.status in valid_statuses:
            rows = await asyncio.to_thread(fetch_complaints_from_db, getComplaintsRequest.status, from_time)

            complaints = [
                ComplaintDetailResponse(
                    id=row["id"],
                    text=row["text"],
                    status=row["status"],
                    timestamp=row["timestamp"],
                    sentiment=row["sentiment"],
                    category=row["category"]
                )
                for row in rows
            ]

            return complaints
        else:
            raise HTTPException(detail="BAD_REQUEST: Статус может быть только: open или closed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении жалоб: {str(e)}")


@app.post("/closeComplaint")
async def close_complaint(request: CloseComplaintRequest):
    complaint_id = request.complaint_id
    try:
        result = await asyncio.to_thread(mark_complaint_as_closed, complaint_id)
        if not result:
            raise HTTPException(status_code=404, detail="Жалоба не найдена")
        return {"message": f"Жалоба с ID {complaint_id} успешно закрыта"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при закрытии жалобы: {str(e)}")