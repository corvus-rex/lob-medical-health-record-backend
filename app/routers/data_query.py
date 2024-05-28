from typing import Annotated, Optional, Dict
from fastapi import Depends, FastAPI, HTTPException, status, Form, UploadFile
from pydantic import BaseModel, EmailStr, constr, Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import uuid
import json
import os
from dotenv import load_dotenv


from schema import *
from models import *


load_dotenv('.env')
ASSET_STORAGE = os.environ['ASSET_STORAGE']

## INITIALIZE ROUTER
router = APIRouter()

@router.get("/videos/preview")
async def get_preview_vids(
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    query_res = (
        db.query(Media_Unit, Template)
        .join(Template, Media_Unit.template_id == Template.template_id)
        .filter(Media_Unit.is_preview == True)
        .order_by(Media_Unit.media_unit_edited_datetime.asc())
        .all()
    )
    res = {"media_units": []}
    for unit, template in query_res:
        print(unit)
        if unit.video_edited_datetime == None:
            if unit.video_creation_datetime != None:
                video_last_edited = unit.video_creation_datetime
            else:
                video_last_edited = unit.media_unit_creation_datetime
        if unit.audio_edited_datetime == None:
            if unit.audio_creation_datetime != None:
                audio_last_edited = unit.audio_creation_datetime
            else:
                audio_last_edited = unit.media_unit_creation_datetime
        res_unit = Media_Unit_Response(
            id=str(unit.media_unit_id),
            caption=unit.caption,
            thumbnail=template.thumbnail,
            video_duration=unit.video_duration,
            audio_duration=unit.audio_duration,
            is_video_generated=unit.is_video_generated,
            is_audio_generated=unit.is_audio_generated,
            avatar_id=str(unit.avatar_id),
            template_id=str(unit.template_id),
            media_unit_last_edited=unit.media_unit_edited_datetime,
            video_last_edited=video_last_edited,
            audio_last_edited=audio_last_edited
        )
        res["media_units"].append(res_unit)
    return res


@router.get("/user")
async def get_user_info(
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    return {
        "name": user.user_name,
        "email": user.user_email,
        "image": user.user_img,
        "date_of_birth": user.date_of_birth,
        "gender": user.gender,
        "position": user.position,
        "company": user.company,
        "phone": user.phone
    }
    

@router.get("/videos/generated")
async def get_preview_vids(
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    # print(user.user_id)
    query_res = (
        db.query(Media_Unit, Template)
        .join(Template, Media_Unit.template_id == Template.template_id)
        .filter(Media_Unit.user_id == user.user_id, Media_Unit.media_unit_edited_datetime != None)
        .order_by(Media_Unit.media_unit_edited_datetime.desc())
        .all()
    )
    res = {"media_units": []}
    for unit, template in query_res:
        print(unit)
        video_last_edited = None
        audio_last_edited = None
        if unit.video_edited_datetime == None:
            if unit.video_creation_datetime != None:
                video_last_edited = unit.video_creation_datetime
            else:
                video_last_edited = unit.media_unit_creation_datetime
        if unit.audio_edited_datetime == None:
            if unit.audio_creation_datetime != None:
                audio_last_edited = unit.audio_creation_datetime
            else:
                audio_last_edited = unit.media_unit_creation_datetime
        res_unit = Media_Unit_Response(
            id=str(unit.media_unit_id),
            caption=unit.caption,
            thumbnail=template.thumbnail,
            video_duration=unit.video_duration,
            audio_duration=unit.audio_duration,
            is_video_generated=unit.is_video_generated,
            is_audio_generated=unit.is_audio_generated,
            avatar_id=str(unit.avatar_id),
            template_id=str(unit.template_id),
            media_unit_last_edited=unit.media_unit_edited_datetime,
            video_last_edited=video_last_edited,
            audio_last_edited=audio_last_edited
        )
        res["media_units"].append(res_unit)
    return res


@router.get("/videos/template")
async def get_preview_vids(
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    query_res = db.query(TemplateAvatar, Template).join(Template, TemplateAvatar.template_id == Template.template_id).all()
    res = {"media_units": []}
    for unit, template in query_res:
        res_unit = TemplateAvatar_Response(
            template_id=str(unit.template_id),
            avatar_id=str(unit.avatar_id),
            thumbnail=template.thumbnail,
            caption=template.template_name,
            duration=unit.duration,
            creation_datetime=unit.creation_datetime
        )
        res["media_units"].append(res_unit)
    return res

@router.get("/avatars")
async def get_preview_vids(
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    query_res = db.query(Avatar).all()
    return {'avatars': query_res}

@router.get("/products")
async def fetch_product_templates(
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    products = db.query(Product).all()

    res = {'products': []}

    for product in products:
        templates = [{
            "id": template.template_id, 
            "name": template.template_name, 
            "script": template.template_script,
            "thumbnail": template.thumbnail,
            "template_avatar": [{
                "id": template_avatar.avatar_id,
                "video_path": template_avatar.avatar_id,
                "creation_datetime": template_avatar.creation_datetime,
                "duration": template_avatar.duration,
                "avatar": template_avatar.avatar
            } for template_avatar in template.template_avatar]
        } for template in product.templates]
        product_info = {
            "id": product.product_id, 
            "name": product.product_name, 
            "templates": templates
        }
        res["products"].append(product_info)
    return res