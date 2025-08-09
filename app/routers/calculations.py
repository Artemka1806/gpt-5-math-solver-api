from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user
from ..models.calculation import Calculation
from ..models.user import User

router = APIRouter(prefix="/calculations", tags=["calculations"])


@router.get("")
async def list_calculations(user: User = Depends(get_current_user), page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    cursor = Calculation.find(Calculation.user_id == str(user.id)).sort(-Calculation.created_at).skip(skip).limit(limit)
    return [
        {
            "calculationId": str(c.id),
            "expression": c.expression,
            "resultPreview": c.result_text[:50],
            "timestamp": c.created_at.isoformat(),
        }
        async for c in cursor
    ]


@router.get("/{calc_id}")
async def get_calculation(calc_id: str, user: User = Depends(get_current_user)):
    calc = await Calculation.get(calc_id)
    if not calc or calc.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Not found")
    return calc


@router.delete("/{calc_id}")
async def delete_calculation(calc_id: str, user: User = Depends(get_current_user)):
    calc = await Calculation.get(calc_id)
    if not calc or calc.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Not found")
    await calc.delete()
    return {"message": "Deleted"}
