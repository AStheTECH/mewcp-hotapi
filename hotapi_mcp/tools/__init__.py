"""MewCP HotAPI tool registration."""

from fastmcp import FastMCP

from .face_assets_tools import register_face_assets_tools
from .image_generation_tools import register_image_generation_tools
from .models_tools import register_models_tools
from .tasks_tools import register_tasks_tools
from .usage_tools import register_usage_tools
from .video_generation_tools import register_video_generation_tools


def register_tools(mcp: FastMCP) -> None:
    register_face_assets_tools(mcp)
    register_image_generation_tools(mcp)
    register_models_tools(mcp)
    register_tasks_tools(mcp)
    register_usage_tools(mcp)
    register_video_generation_tools(mcp)
