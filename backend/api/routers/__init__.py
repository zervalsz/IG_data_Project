"""
API Routers
"""

from .style_router import router as style_router
from .creator_router import router as creator_router
from .instagram_router import router as instagram_router
from .trend_router import router as trend_router

__all__ = ['style_router', 'creator_router', 'instagram_router', 'trend_router']
