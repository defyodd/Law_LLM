"""
法律相关API路由 - 使用 PyMySQL
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
import pymysql
from routes.database.database import get_db
from routes.database.models import Law
from routes.database.dao import LawDAO
from routes.database.schemas import Result, LawInfo, LawItem, SearchLawItem
from typing import List
import json
import aiofiles

router = APIRouter(prefix="/law", tags=["法律法规"])


@router.post("/upload", response_model=Result)
async def upload_law(
    file: UploadFile = File(...),
    db: pymysql.Connection = Depends(get_db)
):
    """上传法律法规"""
    try:
        # 检查文件类型
        if not file.filename.endswith('.json'):
            return Result.error("只支持JSON格式文件")
        
        # 读取文件内容
        content = await file.read()
        law_data = json.loads(content.decode('utf-8'))
        
        # 验证数据格式
        if 'title' not in law_data or 'parts' not in law_data:
            return Result.error("文件格式不正确，缺少必要字段")
        
        # 检查法律是否已存在
        existing_law = LawDAO.get_law_by_title(law_data['title'])
        if existing_law:
            return Result.error("该法律已存在")
        
        # 创建新法律记录
        law_id = LawDAO.create_law(law_data['title'], law_data['parts'])
        
        if law_id:
            return Result.success()
        else:
            return Result.error("法律创建失败")
        
    except json.JSONDecodeError:
        return Result.error("JSON文件格式错误")
    except Exception as e:
        return Result.error(f"上传失败: {str(e)}")


@router.get("/getAllLaws", response_model=Result)
def get_all_laws(db: pymysql.Connection = Depends(get_db)):
    """获取法律法规列表"""
    try:
        # 使用轻量级查询，只获取 ID 和标题
        law_titles = LawDAO.get_law_titles()
        
        law_list = [
            LawItem(lawId=law['law_id'], title=law['title'])
            for law in law_titles
        ]
        
        return Result.success(data=law_list)
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1038:  # Out of sort memory error
            return Result.error("数据库内存不足，请联系管理员优化数据库配置")
        else:
            return Result.error(f"数据库操作失败: {str(e)}")
    except Exception as e:
        return Result.error(f"获取法律列表失败: {str(e)}")


@router.get("/getLawInfo", response_model=Result)
def get_law_info(
    lawId: int = Query(...),
    db: pymysql.Connection = Depends(get_db)
):
    """获取法律详细内容"""
    law = LawDAO.get_law_by_id(lawId)
    
    if not law:
        return Result.error("法律不存在")
    
    law_info = LawInfo(title=law.title, parts=law.parts)
    
    return Result.success(data=law_info)


@router.get("/search", response_model=Result)
def search_laws(
    keyword: str = Query(...),
    db: pymysql.Connection = Depends(get_db)
):
    """搜索法律法规"""
    try:
        # 首先按标题搜索
        laws = LawDAO.search_laws(keyword)
        
        search_results = []
        
        for law in laws:
            # 在法律内容中搜索关键字
            parts = law.parts
            if isinstance(parts, list):
                for part in parts:
                    if 'chapters' in part and isinstance(part['chapters'], list):
                        for chapter in part['chapters']:
                            chapter_title = chapter.get('chapter_title', '')
                            if 'articles' in chapter and isinstance(chapter['articles'], list):
                                for article in chapter['articles']:
                                    article_no = article.get('article_no', '')
                                    article_content = article.get('article_content', '')
                                    
                                    # 检查是否包含关键字
                                    if (keyword in chapter_title or 
                                        keyword in article_no or 
                                        keyword in article_content):
                                        
                                        search_results.append(SearchLawItem(
                                            lawId=law.law_id,
                                            title=law.title,
                                            chapterTitle=chapter_title,
                                            articleNo=article_no,
                                            articleContent=article_content
                                        ))
        
        return Result.success(data=search_results)
        
    except Exception as e:
        return Result.error(f"搜索失败: {str(e)}")
