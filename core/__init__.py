"""
Framework自动化构建工具 - 核心模块

提供以下功能：
- 头文件解析
- Xcode项目生成
- Framework构建
- XCFramework构建
"""

__version__ = "1.0.0"
__author__ = "Framework Auto Builder"

from .header_parser import HeaderParser
from .xcode_generator import XcodeProjectGenerator
from .xcframework_builder import XCFrameworkBuilder

__all__ = [
    'HeaderParser',
    'XcodeProjectGenerator',
    'XCFrameworkBuilder'
] 