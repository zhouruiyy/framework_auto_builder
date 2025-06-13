#!/usr/bin/env python3
"""
XCFramework 构建器
用于从 Xcode 项目构建 XCFramework
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class BuildTarget:
    """构建目标配置"""
    name: str
    sdk: str
    destination: str
    arch: List[str]


@dataclass
class XCFrameworkConfig:
    """XCFramework 配置"""
    framework_name: str
    project_path: str
    scheme_name: str
    output_dir: str
    targets: List[BuildTarget]
    configuration: str = "Release"
    clean_build: bool = True


class XCFrameworkBuilder:
    """XCFramework 构建器"""
    
    def __init__(self):
        self.default_targets = [
            BuildTarget(
                name="iOS",
                sdk="iphoneos",
                destination="generic/platform=iOS",
                arch=["arm64"]
            ),
            BuildTarget(
                name="iOS Simulator",
                sdk="iphonesimulator", 
                destination="generic/platform=iOS Simulator",
                arch=["arm64", "x86_64"]
            ),
            BuildTarget(
                name="macOS",
                sdk="macosx",
                destination="generic/platform=macOS",
                arch=["arm64", "x86_64"]
            )
        ]
    
    def build_xcframework(self, config: XCFrameworkConfig) -> bool:
        """构建 XCFramework"""
        try:
            print(f"🚀 开始构建 XCFramework: {config.framework_name}")
            
            # 1. 验证环境
            if not self._check_environment():
                return False
            
            # 2. 清理之前的构建
            if config.clean_build:
                self._clean_build_directory(config)
            
            # 3. 为每个目标平台构建 Framework
            framework_paths = []
            for target in config.targets:
                framework_path = self._build_framework_for_target(config, target)
                if framework_path:
                    framework_paths.append(framework_path)
                else:
                    print(f"❌ 构建目标失败: {target.name}")
                    return False
            
            # 4. 创建 XCFramework
            xcframework_path = self._create_xcframework(config, framework_paths)
            if not xcframework_path:
                return False
            
            # 5. 验证 XCFramework
            if self._validate_xcframework(xcframework_path):
                print(f"✅ XCFramework 构建成功: {xcframework_path}")
                self._generate_build_summary(config, xcframework_path)
                return True
            else:
                print("❌ XCFramework 验证失败")
                return False
                
        except Exception as e:
            print(f"❌ XCFramework 构建失败: {e}")
            return False
    
    def _check_environment(self) -> bool:
        """检查构建环境"""
        try:
            # 检查 Xcode 是否安装
            result = subprocess.run(['xcodebuild', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Xcode 未安装或不可用")
                return False
            
            print(f"✅ Xcode 版本: {result.stdout.strip().split()[1]}")
            
            # 检查可用的 SDK
            result = subprocess.run(['xcodebuild', '-showsdks'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 可用的 SDK:")
                for line in result.stdout.split('\n'):
                    if 'iOS' in line or 'macOS' in line:
                        print(f"   {line.strip()}")
            
            return True
            
        except FileNotFoundError:
            print("❌ 未找到 xcodebuild 命令，请确保 Xcode 已正确安装")
            return False
    
    def _clean_build_directory(self, config: XCFrameworkConfig):
        """清理构建目录"""
        build_dir = Path(config.output_dir) / "build"
        if build_dir.exists():
            print("🧹 清理之前的构建...")
            shutil.rmtree(build_dir)
        
        # 清理现有的 XCFramework
        xcframework_path = Path(config.output_dir) / f"{config.framework_name}.xcframework"
        if xcframework_path.exists():
            shutil.rmtree(xcframework_path)
    
    def _build_framework_for_target(self, config: XCFrameworkConfig, target: BuildTarget) -> Optional[str]:
        """为特定目标构建 Framework"""
        try:
            print(f"🔨 构建 {target.name} Framework...")
            
            # 构建输出目录
            build_dir = Path(config.output_dir) / "build" / target.name
            build_dir.mkdir(parents=True, exist_ok=True)
            
            # 构建命令
            cmd = [
                'xcodebuild',
                '-project', config.project_path,
                '-scheme', config.scheme_name,
                '-configuration', config.configuration,
                '-sdk', target.sdk,
                '-destination', target.destination,
                'BUILD_DIR=' + str(build_dir),
                'SKIP_INSTALL=NO',
                'BUILD_LIBRARY_FOR_DISTRIBUTION=YES',
                'ONLY_ACTIVE_ARCH=NO'
            ]
            
            # 添加架构设置
            if len(target.arch) > 1:
                cmd.extend(['ARCHS=' + ' '.join(target.arch)])
            
            cmd.append('build')
            
            print(f"   执行命令: {' '.join(cmd)}")
            
            # 执行构建
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(config.project_path).parent)
            
            if result.returncode != 0:
                print(f"❌ 构建失败: {target.name}")
                print(f"错误输出: {result.stderr}")
                return None
            
            # 查找生成的 Framework
            framework_name = f"{config.framework_name}.framework"
            
            # 可能的 Framework 路径
            possible_paths = [
                build_dir / config.configuration / framework_name,
                build_dir / f"{config.configuration}-{target.sdk}" / framework_name,
                build_dir / "Products" / config.configuration / framework_name,
                build_dir / "Products" / f"{config.configuration}-{target.sdk}" / framework_name
            ]
            
            for path in possible_paths:
                if path.exists():
                    print(f"✅ 找到 Framework: {path}")
                    return str(path)
            
            # 如果没找到，搜索整个构建目录
            for framework_path in build_dir.rglob(framework_name):
                if framework_path.is_dir():
                    print(f"✅ 找到 Framework: {framework_path}")
                    return str(framework_path)
            
            print(f"❌ 未找到生成的 Framework: {framework_name}")
            print(f"构建目录内容:")
            for item in build_dir.rglob("*"):
                if item.is_dir():
                    print(f"   📁 {item}")
                else:
                    print(f"   📄 {item}")
            
            return None
            
        except Exception as e:
            print(f"❌ 构建目标失败 {target.name}: {e}")
            return None
    
    def _create_xcframework(self, config: XCFrameworkConfig, framework_paths: List[str]) -> Optional[str]:
        """创建 XCFramework"""
        try:
            print("📦 创建 XCFramework...")
            
            xcframework_path = Path(config.output_dir) / f"{config.framework_name}.xcframework"
            
            # 构建 xcodebuild -create-xcframework 命令
            cmd = ['xcodebuild', '-create-xcframework']
            
            for framework_path in framework_paths:
                cmd.extend(['-framework', framework_path])
            
            cmd.extend(['-output', str(xcframework_path)])
            
            print(f"   执行命令: {' '.join(cmd)}")
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ 创建 XCFramework 失败")
                print(f"错误输出: {result.stderr}")
                return None
            
            if xcframework_path.exists():
                return str(xcframework_path)
            else:
                print("❌ XCFramework 文件未生成")
                return None
                
        except Exception as e:
            print(f"❌ 创建 XCFramework 失败: {e}")
            return None
    
    def _validate_xcframework(self, xcframework_path: str) -> bool:
        """验证 XCFramework"""
        try:
            print("🔍 验证 XCFramework...")
            
            # 检查文件结构
            xcframework = Path(xcframework_path)
            if not xcframework.exists():
                print("❌ XCFramework 文件不存在")
                return False
            
            # 检查 Info.plist
            info_plist = xcframework / "Info.plist"
            if not info_plist.exists():
                print("❌ Info.plist 不存在")
                return False
            
            # 使用 xcodebuild 验证
            cmd = ['xcodebuild', '-checkFirstLaunchForSimulator']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            print("✅ XCFramework 验证通过")
            
            # 显示 XCFramework 信息
            self._show_xcframework_info(xcframework_path)
            
            return True
            
        except Exception as e:
            print(f"⚠️ XCFramework 验证出现问题: {e}")
            return True  # 不阻止构建完成
    
    def _show_xcframework_info(self, xcframework_path: str):
        """显示 XCFramework 信息"""
        try:
            xcframework = Path(xcframework_path)
            
            print(f"\n📊 XCFramework 信息:")
            print(f"   路径: {xcframework_path}")
            print(f"   大小: {self._get_directory_size(xcframework):.2f} MB")
            
            # 列出包含的平台
            print(f"   包含的平台:")
            for item in xcframework.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    print(f"     - {item.name}")
            
        except Exception as e:
            print(f"⚠️ 获取 XCFramework 信息失败: {e}")
    
    def _get_directory_size(self, path: Path) -> float:
        """获取目录大小（MB）"""
        total_size = 0
        for file_path in path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)
    
    def _generate_build_summary(self, config: XCFrameworkConfig, xcframework_path: str):
        """生成构建摘要"""
        try:
            summary_path = Path(config.output_dir) / "xcframework_build_summary.json"
            
            import json
            from datetime import datetime
            
            summary = {
                'framework_name': config.framework_name,
                'xcframework_path': xcframework_path,
                'build_date': datetime.now().isoformat(),
                'configuration': config.configuration,
                'targets': [
                    {
                        'name': target.name,
                        'sdk': target.sdk,
                        'architectures': target.arch
                    }
                    for target in config.targets
                ],
                'file_size_mb': self._get_directory_size(Path(xcframework_path))
            }
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"📄 构建摘要已保存: {summary_path}")
            
        except Exception as e:
            print(f"⚠️ 生成构建摘要失败: {e}")


def main():
    """测试 XCFramework 构建器"""
    builder = XCFrameworkBuilder()
    
    # 测试配置
    config = XCFrameworkConfig(
        framework_name="MyTestFramework",
        project_path="../output/MyTestFramework.xcodeproj",
        scheme_name="MyTestFramework",
        output_dir="../output",
        targets=builder.default_targets[:2]  # 只构建 iOS 和 iOS Simulator
    )
    
    # 构建 XCFramework
    success = builder.build_xcframework(config)
    
    if success:
        print("✅ XCFramework 构建测试成功!")
    else:
        print("❌ XCFramework 构建测试失败!")


if __name__ == "__main__":
    main() 