from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models.service_account import ServiceAccount
from models.user import User
from security.deps import get_current_user

router = APIRouter(prefix="/services", tags=["services"])


@router.get("")
def list_services(
    session: Session = Depends(get_session), current_user: User = Depends(get_current_user)
):
    statement = select(ServiceAccount).where(ServiceAccount.user_id == current_user.id)
    return list(session.exec(statement))


@router.get("/{service_id}")
def get_service(
    service_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = session.get(ServiceAccount, service_id)
    if not service or service.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
