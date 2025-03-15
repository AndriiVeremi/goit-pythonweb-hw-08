import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.contacts import ContactService
from src.schemas.contact import (
    ContactResponse,
    ContactSchema,
    ContactUpdateSchema,
)

router = APIRouter(prefix="/contacts", tags=["contacts"])
logger = logging.getLogger("uvicorn.error")


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    limit: int = Query(10, ge=10, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    cont_service = ContactService(db)
    return await cont_service.get_contacts(limit, offset)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    cont_service = ContactService(db)
    contact = await cont_service.get_contact(contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    try:
        cont_service = ContactService(db)
        return await cont_service.create_contact(body)
    except Exception as e:
        logger.error(f"Error creating contact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession = Depends(get_db)
):
    cont_service = ContactService(db)
    contact = await cont_service.update_contact(contact_id, body)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    cont_service = ContactService(db)
    await cont_service.remove_contact(contact_id)
    return None


@router.get("/search/", response_model=list[ContactResponse])
async def search_contacts(
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    cont_service = ContactService(db)
    contacts = await cont_service.search_contacts(first_name, last_name, email)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found"
        )
    return contacts


@router.get("/birthdays/", response_model=list[ContactResponse])
async def upcoming_birthdays(days: int = 7, db: AsyncSession = Depends(get_db)):
    cont_service = ContactService(db)
    contacts = await cont_service.get_upcoming_birthdays(days)
    return contacts
