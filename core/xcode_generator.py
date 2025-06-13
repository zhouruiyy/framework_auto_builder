"""
Xcode项目生成器
用于生成Framework项目的.xcodeproj文件和相关配置
"""

import os
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class XcodeTarget:
    """Xcode目标配置"""
    name: str
    product_name: str
    product_type: str
    build_configurations: Dict[str, Dict[str, Any]]
    build_phases: List[Dict[str, Any]]
    dependencies: List[str] = None


@dataclass
class XcodeProject:
    """Xcode项目配置"""
    name: str
    organization_name: str
    development_team: str
    targets: List[XcodeTarget]
    build_configurations: Dict[str, Dict[str, Any]]


class XcodeProjectGenerator:
    """Xcode项目生成器"""
    
    def __init__(self):
        pass
    
    def generate_project(self, config: Dict[str, Any], output_dir: str) -> bool:
        """生成Xcode项目"""
        try:
            project_name = config['framework_name']
            project_dir = Path(output_dir) / f"{project_name}.xcodeproj"
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # 自动复制 Info.plist
            src_info_plist = Path(__file__).parent.parent / 'src' / project_name / 'Info.plist'
            dst_info_plist = Path(output_dir) / 'Info.plist'
            if src_info_plist.exists():
                import shutil
                shutil.copy2(src_info_plist, dst_info_plist)
                print(f"✅ 已复制 Info.plist 到 {dst_info_plist}")
            else:
                print(f"⚠️ 未找到 Info.plist: {src_info_plist}")
            
            print(f"📦 生成Xcode项目: {project_name}")
            
            # 查找源文件
            source_files = self._find_source_files(output_dir, project_name)
            
            # 写入project.pbxproj文件
            pbxproj_path = project_dir / "project.pbxproj"
            with open(pbxproj_path, 'w', encoding='utf-8') as f:
                self._write_pbxproj_template(f, project_name, source_files, config.get('info_plist_path'))
            
            # 生成xcscheme文件
            self._generate_schemes(project_dir, config)
            
            # 生成xcworkspacedata文件
            self._generate_workspace_data(project_dir, config)
            
            print(f"✅ Xcode项目生成完成: {project_dir}")
            return True
            
        except Exception as e:
            print(f"❌ 生成Xcode项目失败: {e}")
            return False
    
    def _find_source_files(self, output_dir: str, framework_name: str) -> Dict[str, List[Path]]:
        """查找源文件"""
        framework_dir = Path(output_dir) / framework_name
        
        source_files = {
            'headers': [],
            'sources': []
        }
        
        if framework_dir.exists():
            # 查找头文件
            for header_file in framework_dir.glob("*.h"):
                source_files['headers'].append(header_file)
            
            # 查找源文件
            for source_file in framework_dir.glob("*.m"):
                source_files['sources'].append(source_file)
            
            # 递归查找子目录中的源文件
            for subdir in framework_dir.iterdir():
                if subdir.is_dir():
                    for source_file in subdir.rglob("*.m"):
                        source_files['sources'].append(source_file)
        
        print(f"📄 找到头文件: {len(source_files['headers'])} 个")
        print(f"📄 找到源文件: {len(source_files['sources'])} 个")
        
        return source_files
    
    def _write_pbxproj_template(self, file, framework_name: str, source_files: Dict[str, List[Path]], info_plist_path: str = None):
        """使用模板写入pbxproj文件"""
        
        # 生成UUID
        project_uuid = self._generate_uuid()
        target_uuid = self._generate_uuid()
        main_group_uuid = self._generate_uuid()
        framework_group_uuid = self._generate_uuid()
        products_group_uuid = self._generate_uuid()
        product_ref_uuid = self._generate_uuid()
        headers_phase_uuid = self._generate_uuid()
        sources_phase_uuid = self._generate_uuid()
        frameworks_phase_uuid = self._generate_uuid()
        project_config_list_uuid = self._generate_uuid()
        target_config_list_uuid = self._generate_uuid()
        project_debug_uuid = self._generate_uuid()
        project_release_uuid = self._generate_uuid()
        target_debug_uuid = self._generate_uuid()
        target_release_uuid = self._generate_uuid()
        
        # 为每个文件生成UUID
        header_uuids = {}
        source_uuids = {}
        header_build_uuids = {}
        source_build_uuids = {}
        
        for header in source_files['headers']:
            header_uuids[header.name] = self._generate_uuid()
            header_build_uuids[header.name] = self._generate_uuid()
        
        for source in source_files['sources']:
            source_uuids[source.name] = self._generate_uuid()
            source_build_uuids[source.name] = self._generate_uuid()
        
        # 写入文件头
        file.write("// !$*UTF8*$!\n")
        file.write("{\n")
        file.write("\tarchiveVersion = 1;\n")
        file.write("\tclasses = {\n\t};\n")
        file.write("\tobjectVersion = 56;\n")
        file.write("\tobjects = {\n")
        
        # PBXBuildFile section
        file.write("\n/* Begin PBXBuildFile section */\n")
        for header_name, build_uuid in header_build_uuids.items():
            file_uuid = header_uuids[header_name]
            file.write(f"\t\t{build_uuid} /* {header_name} in Headers */ = {{isa = PBXBuildFile; fileRef = {file_uuid} /* {header_name} */; settings = {{ATTRIBUTES = (Public, ); }}; }};\n")
        
        for source_name, build_uuid in source_build_uuids.items():
            file_uuid = source_uuids[source_name]
            file.write(f"\t\t{build_uuid} /* {source_name} in Sources */ = {{isa = PBXBuildFile; fileRef = {file_uuid} /* {source_name} */; }};\n")
        file.write("/* End PBXBuildFile section */\n")
        
        # PBXFileReference section
        file.write("\n/* Begin PBXFileReference section */\n")
        file.write(f"\t\t{product_ref_uuid} /* {framework_name}.framework */ = {{isa = PBXFileReference; explicitFileType = wrapper.framework; includeInIndex = 0; path = {framework_name}.framework; sourceTree = BUILT_PRODUCTS_DIR; }};\n")
        
        for header_name, file_uuid in header_uuids.items():
            file.write(f"\t\t{file_uuid} /* {header_name} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.c.h; path = {header_name}; sourceTree = \"<group>\"; }};\n")
        
        for source_name, file_uuid in source_uuids.items():
            file.write(f"\t\t{file_uuid} /* {source_name} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.c.objc; path = {source_name}; sourceTree = \"<group>\"; }};\n")
        file.write("/* End PBXFileReference section */\n")
        
        # PBXFrameworksBuildPhase section
        file.write("\n/* Begin PBXFrameworksBuildPhase section */\n")
        file.write(f"\t\t{frameworks_phase_uuid} /* Frameworks */ = {{\n")
        file.write("\t\t\tisa = PBXFrameworksBuildPhase;\n")
        file.write("\t\t\tbuildActionMask = 2147483647;\n")
        file.write("\t\t\tfiles = (\n")
        file.write("\t\t\t);\n")
        file.write("\t\t\trunOnlyForDeploymentPostprocessing = 0;\n")
        file.write("\t\t};\n")
        file.write("/* End PBXFrameworksBuildPhase section */\n")
        
        # PBXGroup section
        file.write("\n/* Begin PBXGroup section */\n")
        file.write(f"\t\t{main_group_uuid} = {{\n")
        file.write("\t\t\tisa = PBXGroup;\n")
        file.write("\t\t\tchildren = (\n")
        file.write(f"\t\t\t\t{framework_group_uuid} /* {framework_name} */,\n")
        file.write(f"\t\t\t\t{products_group_uuid} /* Products */,\n")
        file.write("\t\t\t);\n")
        file.write("\t\t\tsourceTree = \"<group>\";\n")
        file.write("\t\t};\n")
        
        file.write(f"\t\t{products_group_uuid} /* Products */ = {{\n")
        file.write("\t\t\tisa = PBXGroup;\n")
        file.write("\t\t\tchildren = (\n")
        file.write(f"\t\t\t\t{product_ref_uuid} /* {framework_name}.framework */,\n")
        file.write("\t\t\t);\n")
        file.write("\t\t\tname = Products;\n")
        file.write("\t\t\tsourceTree = \"<group>\";\n")
        file.write("\t\t};\n")
        
        file.write(f"\t\t{framework_group_uuid} /* {framework_name} */ = {{\n")
        file.write("\t\t\tisa = PBXGroup;\n")
        file.write("\t\t\tchildren = (\n")
        for header_name, file_uuid in header_uuids.items():
            file.write(f"\t\t\t\t{file_uuid} /* {header_name} */,\n")
        for source_name, file_uuid in source_uuids.items():
            file.write(f"\t\t\t\t{file_uuid} /* {source_name} */,\n")
        file.write("\t\t\t);\n")
        file.write(f"\t\t\tpath = {framework_name};\n")
        file.write("\t\t\tsourceTree = \"<group>\";\n")
        file.write("\t\t};\n")
        file.write("/* End PBXGroup section */\n")
        
        # PBXHeadersBuildPhase section
        file.write("\n/* Begin PBXHeadersBuildPhase section */\n")
        file.write(f"\t\t{headers_phase_uuid} /* Headers */ = {{\n")
        file.write("\t\t\tisa = PBXHeadersBuildPhase;\n")
        file.write("\t\t\tbuildActionMask = 2147483647;\n")
        file.write("\t\t\tfiles = (\n")
        for header_name, build_uuid in header_build_uuids.items():
            file.write(f"\t\t\t\t{build_uuid} /* {header_name} in Headers */,\n")
        file.write("\t\t\t);\n")
        file.write("\t\t\trunOnlyForDeploymentPostprocessing = 0;\n")
        file.write("\t\t};\n")
        file.write("/* End PBXHeadersBuildPhase section */\n")
        
        # PBXNativeTarget section
        file.write("\n/* Begin PBXNativeTarget section */\n")
        file.write(f"\t\t{target_uuid} /* {framework_name} */ = {{\n")
        file.write("\t\t\tisa = PBXNativeTarget;\n")
        file.write(f"\t\t\tbuildConfigurationList = {target_config_list_uuid} /* Build configuration list for PBXNativeTarget \"{framework_name}\" */;\n")
        file.write("\t\t\tbuildPhases = (\n")
        file.write(f"\t\t\t\t{headers_phase_uuid} /* Headers */,\n")
        file.write(f"\t\t\t\t{sources_phase_uuid} /* Sources */,\n")
        file.write(f"\t\t\t\t{frameworks_phase_uuid} /* Frameworks */,\n")
        file.write("\t\t\t);\n")
        file.write("\t\t\tbuildRules = (\n")
        file.write("\t\t\t);\n")
        file.write("\t\t\tdependencies = (\n")
        file.write("\t\t\t);\n")
        file.write(f"\t\t\tname = {framework_name};\n")
        file.write(f"\t\t\tproductName = {framework_name};\n")
        file.write(f"\t\t\tproductReference = {product_ref_uuid} /* {framework_name}.framework */;\n")
        file.write("\t\t\tproductType = \"com.apple.product-type.framework\";\n")
        file.write("\t\t};\n")
        file.write("/* End PBXNativeTarget section */\n")
        
        # PBXProject section
        file.write("\n/* Begin PBXProject section */\n")
        file.write(f"\t\t{project_uuid} /* Project object */ = {{\n")
        file.write("\t\t\tisa = PBXProject;\n")
        file.write("\t\t\tattributes = {\n")
        file.write("\t\t\t\tBuildIndependentTargetsInParallel = 1;\n")
        file.write("\t\t\t\tLastUpgradeCheck = 1500;\n")
        file.write("\t\t\t\tTargetAttributes = {\n")
        file.write(f"\t\t\t\t\t{target_uuid} = {{\n")
        file.write("\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;\n")
        file.write("\t\t\t\t\t};\n")
        file.write("\t\t\t\t};\n")
        file.write("\t\t\t};\n")
        file.write(f"\t\t\tbuildConfigurationList = {project_config_list_uuid} /* Build configuration list for PBXProject \"{framework_name}\" */;\n")
        file.write("\t\t\tcompatibilityVersion = \"Xcode 14.0\";\n")
        file.write("\t\t\tdevelopmentRegion = en;\n")
        file.write("\t\t\thasScannedForEncodings = 0;\n")
        file.write("\t\t\tknownRegions = (\n")
        file.write("\t\t\t\ten,\n")
        file.write("\t\t\t\tBase,\n")
        file.write("\t\t\t);\n")
        file.write(f"\t\t\tmainGroup = {main_group_uuid};\n")
        file.write(f"\t\t\tproductRefGroup = {products_group_uuid} /* Products */;\n")
        file.write("\t\t\tprojectDirPath = \"\";\n")
        file.write("\t\t\tprojectRoot = \"\";\n")
        file.write("\t\t\ttargets = (\n")
        file.write(f"\t\t\t\t{target_uuid} /* {framework_name} */,\n")
        file.write("\t\t\t);\n")
        file.write("\t\t};\n")
        file.write("/* End PBXProject section */\n")
        
        # PBXSourcesBuildPhase section
        file.write("\n/* Begin PBXSourcesBuildPhase section */\n")
        file.write(f"\t\t{sources_phase_uuid} /* Sources */ = {{\n")
        file.write("\t\t\tisa = PBXSourcesBuildPhase;\n")
        file.write("\t\t\tbuildActionMask = 2147483647;\n")
        file.write("\t\t\tfiles = (\n")
        for source_name, build_uuid in source_build_uuids.items():
            file.write(f"\t\t\t\t{build_uuid} /* {source_name} in Sources */,\n")
        file.write("\t\t\t);\n")
        file.write("\t\t\trunOnlyForDeploymentPostprocessing = 0;\n")
        file.write("\t\t};\n")
        file.write("/* End PBXSourcesBuildPhase section */\n")
        
        # XCBuildConfiguration section
        file.write("\n/* Begin XCBuildConfiguration section */\n")
        
        # Project Debug配置
        file.write(f"\t\t{project_debug_uuid} /* Debug */ = {{\n")
        file.write("\t\t\tisa = XCBuildConfiguration;\n")
        file.write("\t\t\tbuildSettings = {\n")
        file.write(f"\t\t\t\tINFOPLIST_FILE = \"{info_plist_path or '$(SRCROOT)/Info.plist'}\";\n")
        file.write("\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;\n")
        file.write("\t\t\t\tBUILD_LIBRARY_FOR_DISTRIBUTION = YES;\n")
        file.write("\t\t\t\tCLANG_ANALYZER_NONNULL = YES;\n")
        file.write("\t\t\t\tCLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE;\n")
        file.write("\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = \"gnu++20\";\n")
        file.write("\t\t\t\tCLANG_ENABLE_MODULES = YES;\n")
        file.write("\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;\n")
        file.write("\t\t\t\tCLANG_ENABLE_OBJC_WEAK = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_BOOL_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_COMMA = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_CONSTANT_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;\n")
        file.write("\t\t\t\tCLANG_WARN_DOCUMENTATION_COMMENTS = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_EMPTY_BODY = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_ENUM_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_INFINITE_RECURSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_INT_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_OBJC_LITERAL_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;\n")
        file.write("\t\t\t\tCLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_RANGE_LOOP_ANALYSIS = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_STRICT_PROTOTYPES = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_SUSPICIOUS_MOVE = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;\n")
        file.write("\t\t\t\tCLANG_WARN_UNREACHABLE_CODE = YES;\n")
        file.write("\t\t\t\tCLANG_WARN__DUPLICATE_METHOD_MATCH = YES;\n")
        file.write("\t\t\t\tCOPY_PHASE_STRIP = NO;\n")
        file.write("\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;\n")
        file.write("\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;\n")
        file.write("\t\t\t\tENABLE_TESTABILITY = YES;\n")
        file.write("\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu11;\n")
        file.write("\t\t\t\tGCC_DYNAMIC_NO_PIC = NO;\n")
        file.write("\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;\n")
        file.write("\t\t\t\tGCC_OPTIMIZATION_LEVEL = 0;\n")
        file.write("\t\t\t\tGCC_PREPROCESSOR_DEFINITIONS = (\n")
        file.write("\t\t\t\t\t\"DEBUG=1\",\n")
        file.write("\t\t\t\t\t\"$(inherited)\",\n")
        file.write("\t\t\t\t);\n")
        file.write("\t\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;\n")
        file.write("\t\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;\n")
        file.write("\t\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;\n")
        file.write("\t\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;\n")
        file.write("\t\t\t\tGCC_WARN_UNUSED_FUNCTION = YES;\n")
        file.write("\t\t\t\tGCC_WARN_UNUSED_VARIABLE = YES;\n")
        file.write("\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 12.0;\n")
        file.write("\t\t\t\tMTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;\n")
        file.write("\t\t\t\tMTL_FAST_MATH = YES;\n")
        file.write("\t\t\t\tONLY_ACTIVE_ARCH = YES;\n")
        file.write("\t\t\t\tSDKROOT = iphoneos;\n")
        file.write("\t\t\t\tSKIP_INSTALL = NO;\n")
        file.write("\t\t\t};\n")
        file.write("\t\t\tname = Debug;\n")
        file.write("\t\t};\n")
        
        # Project Release配置
        file.write(f"\t\t{project_release_uuid} /* Release */ = {{\n")
        file.write("\t\t\tisa = XCBuildConfiguration;\n")
        file.write("\t\t\tbuildSettings = {\n")
        file.write(f"\t\t\t\tINFOPLIST_FILE = \"{info_plist_path or '$(SRCROOT)/Info.plist'}\";\n")
        file.write("\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;\n")
        file.write("\t\t\t\tBUILD_LIBRARY_FOR_DISTRIBUTION = YES;\n")
        file.write("\t\t\t\tCLANG_ANALYZER_NONNULL = YES;\n")
        file.write("\t\t\t\tCLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE;\n")
        file.write("\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = \"gnu++20\";\n")
        file.write("\t\t\t\tCLANG_ENABLE_MODULES = YES;\n")
        file.write("\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;\n")
        file.write("\t\t\t\tCLANG_ENABLE_OBJC_WEAK = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_BOOL_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_COMMA = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_CONSTANT_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;\n")
        file.write("\t\t\t\tCLANG_WARN_DOCUMENTATION_COMMENTS = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_EMPTY_BODY = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_ENUM_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_INFINITE_RECURSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_INT_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_OBJC_LITERAL_CONVERSION = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;\n")
        file.write("\t\t\t\tCLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_RANGE_LOOP_ANALYSIS = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_STRICT_PROTOTYPES = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_SUSPICIOUS_MOVE = YES;\n")
        file.write("\t\t\t\tCLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;\n")
        file.write("\t\t\t\tCLANG_WARN_UNREACHABLE_CODE = YES;\n")
        file.write("\t\t\t\tCLANG_WARN__DUPLICATE_METHOD_MATCH = YES;\n")
        file.write("\t\t\t\tCOPY_PHASE_STRIP = NO;\n")
        file.write("\t\t\t\tDEBUG_INFORMATION_FORMAT = \"dwarf-with-dsym\";\n")
        file.write("\t\t\t\tENABLE_NS_ASSERTIONS = NO;\n")
        file.write("\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;\n")
        file.write("\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu11;\n")
        file.write("\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;\n")
        file.write("\t\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;\n")
        file.write("\t\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;\n")
        file.write("\t\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;\n")
        file.write("\t\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;\n")
        file.write("\t\t\t\tGCC_WARN_UNUSED_FUNCTION = YES;\n")
        file.write("\t\t\t\tGCC_WARN_UNUSED_VARIABLE = YES;\n")
        file.write("\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 12.0;\n")
        file.write("\t\t\t\tMTL_ENABLE_DEBUG_INFO = NO;\n")
        file.write("\t\t\t\tMTL_FAST_MATH = YES;\n")
        file.write("\t\t\t\tSDKROOT = iphoneos;\n")
        file.write("\t\t\t\tSKIP_INSTALL = NO;\n")
        file.write("\t\t\t\tVALIDATE_PRODUCT = YES;\n")
        file.write("\t\t\t};\n")
        file.write("\t\t\tname = Release;\n")
        file.write("\t\t};\n")
        
        # Target Debug配置
        file.write(f"\t\t{target_debug_uuid} /* Debug */ = {{\n")
        file.write("\t\t\tisa = XCBuildConfiguration;\n")
        file.write("\t\t\tbuildSettings = {\n")
        file.write(f"\t\t\t\tINFOPLIST_FILE = \"{info_plist_path or '$(SRCROOT)/Info.plist'}\";\n")
        file.write("\t\t\t\tCODE_SIGN_STYLE = Automatic;\n")
        file.write("\t\t\t\tCURRENT_PROJECT_VERSION = 1;\n")
        file.write("\t\t\t\tDEFINES_MODULE = YES;\n")
        file.write("\t\t\t\tDYLIB_COMPATIBILITY_VERSION = 1;\n")
        file.write("\t\t\t\tDYLIB_CURRENT_VERSION = 1;\n")
        file.write("\t\t\t\tDYLIB_INSTALL_NAME_BASE = \"@rpath\";\n")
        file.write("\t\t\t\tINFOPLIST_KEY_NSHumanReadableCopyright = \"\";\n")
        file.write("\t\t\t\tINSTALL_PATH = \"$(LOCAL_LIBRARY_DIR)/Frameworks\";\n")
        file.write("\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (\n")
        file.write("\t\t\t\t\t\"$(inherited)\",\n")
        file.write("\t\t\t\t\t\"@executable_path/Frameworks\",\n")
        file.write("\t\t\t\t\t\"@loader_path/Frameworks\",\n")
        file.write("\t\t\t\t);\n")
        file.write("\t\t\t\tMARKETING_VERSION = 1.0;\n")
        file.write(f"\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = \"com.example.{framework_name}\";\n")
        file.write("\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME:c99extidentifier)\";\n")
        file.write("\t\t\t\tSKIP_INSTALL = YES;\n")
        file.write("\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;\n")
        file.write("\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";\n")
        file.write("\t\t\t\tVERSIONING_SYSTEM = \"apple-generic\";\n")
        file.write("\t\t\t};\n")
        file.write("\t\t\tname = Debug;\n")
        file.write("\t\t};\n")
        
        # Target Release配置
        file.write(f"\t\t{target_release_uuid} /* Release */ = {{\n")
        file.write("\t\t\tisa = XCBuildConfiguration;\n")
        file.write("\t\t\tbuildSettings = {\n")
        file.write(f"\t\t\t\tINFOPLIST_FILE = \"{info_plist_path or '$(SRCROOT)/Info.plist'}\";\n")
        file.write("\t\t\t\tCODE_SIGN_STYLE = Automatic;\n")
        file.write("\t\t\t\tCURRENT_PROJECT_VERSION = 1;\n")
        file.write("\t\t\t\tDEFINES_MODULE = YES;\n")
        file.write("\t\t\t\tDYLIB_COMPATIBILITY_VERSION = 1;\n")
        file.write("\t\t\t\tDYLIB_CURRENT_VERSION = 1;\n")
        file.write("\t\t\t\tDYLIB_INSTALL_NAME_BASE = \"@rpath\";\n")
        file.write("\t\t\t\tINFOPLIST_KEY_NSHumanReadableCopyright = \"\";\n")
        file.write("\t\t\t\tINSTALL_PATH = \"$(LOCAL_LIBRARY_DIR)/Frameworks\";\n")
        file.write("\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (\n")
        file.write("\t\t\t\t\t\"$(inherited)\",\n")
        file.write("\t\t\t\t\t\"@executable_path/Frameworks\",\n")
        file.write("\t\t\t\t\t\"@loader_path/Frameworks\",\n")
        file.write("\t\t\t\t);\n")
        file.write("\t\t\t\tMARKETING_VERSION = 1.0;\n")
        file.write(f"\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = \"com.example.{framework_name}\";\n")
        file.write("\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME:c99extidentifier)\";\n")
        file.write("\t\t\t\tSKIP_INSTALL = YES;\n")
        file.write("\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;\n")
        file.write("\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";\n")
        file.write("\t\t\t\tVERSIONING_SYSTEM = \"apple-generic\";\n")
        file.write("\t\t\t};\n")
        file.write("\t\t\tname = Release;\n")
        file.write("\t\t};\n")
        file.write("/* End XCBuildConfiguration section */\n")
        
        # XCConfigurationList section
        file.write("\n/* Begin XCConfigurationList section */\n")
        file.write(f"\t\t{project_config_list_uuid} /* Build configuration list for PBXProject \"{framework_name}\" */ = {{\n")
        file.write("\t\t\tisa = XCConfigurationList;\n")
        file.write("\t\t\tbuildConfigurations = (\n")
        file.write(f"\t\t\t\t{project_debug_uuid} /* Debug */,\n")
        file.write(f"\t\t\t\t{project_release_uuid} /* Release */,\n")
        file.write("\t\t\t);\n")
        file.write("\t\t\tdefaultConfigurationIsVisible = 0;\n")
        file.write("\t\t\tdefaultConfigurationName = Release;\n")
        file.write("\t\t};\n")
        
        file.write(f"\t\t{target_config_list_uuid} /* Build configuration list for PBXNativeTarget \"{framework_name}\" */ = {{\n")
        file.write("\t\t\tisa = XCConfigurationList;\n")
        file.write("\t\t\tbuildConfigurations = (\n")
        file.write(f"\t\t\t\t{target_debug_uuid} /* Debug */,\n")
        file.write(f"\t\t\t\t{target_release_uuid} /* Release */,\n")
        file.write("\t\t\t);\n")
        file.write("\t\t\tdefaultConfigurationIsVisible = 0;\n")
        file.write("\t\t\tdefaultConfigurationName = Release;\n")
        file.write("\t\t};\n")
        file.write("/* End XCConfigurationList section */\n")
        
        # 文件结尾
        file.write("\t};\n")
        file.write(f"\trootObject = {project_uuid} /* Project object */;\n")
        file.write("}\n")
    
    def _generate_schemes(self, project_dir: Path, config: Dict[str, Any]):
        """生成Scheme文件"""
        schemes_dir = project_dir / "xcshareddata" / "xcschemes"
        schemes_dir.mkdir(parents=True, exist_ok=True)
        
        framework_name = config['framework_name']
        scheme_path = schemes_dir / f"{framework_name}.xcscheme"
        
        scheme_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion = "1500"
   version = "1.3">
   <BuildAction
      parallelizeBuildables = "YES"
      buildImplicitDependencies = "YES">
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting = "YES"
            buildForRunning = "YES"
            buildForProfiling = "YES"
            buildForArchiving = "YES"
            buildForAnalyzing = "YES">
            <BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "{self._generate_uuid()}"
               BuildableName = "{framework_name}.framework"
               BlueprintName = "{framework_name}"
               ReferencedContainer = "container:{framework_name}.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      shouldUseLaunchSchemeArgsEnv = "YES">
      <Testables>
      </Testables>
   </TestAction>
   <LaunchAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      launchStyle = "0"
      useCustomWorkingDirectory = "NO"
      ignoresPersistentStateOnLaunch = "NO"
      debugDocumentVersioning = "YES"
      debugServiceExtension = "internal"
      allowLocationSimulation = "YES">
   </LaunchAction>
   <ProfileAction
      buildConfiguration = "Release"
      shouldUseLaunchSchemeArgsEnv = "YES"
      savedToolIdentifier = ""
      useCustomWorkingDirectory = "NO"
      debugDocumentVersioning = "YES">
   </ProfileAction>
   <AnalyzeAction
      buildConfiguration = "Debug">
   </AnalyzeAction>
   <ArchiveAction
      buildConfiguration = "Release"
      revealArchiveInOrganizer = "YES">
   </ArchiveAction>
</Scheme>'''
        
        with open(scheme_path, 'w', encoding='utf-8') as f:
            f.write(scheme_content)
    
    def _generate_workspace_data(self, project_dir: Path, config: Dict[str, Any]):
        """生成workspace数据"""
        workspace_dir = project_dir / "project.xcworkspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # contents.xcworkspacedata
        contents_path = workspace_dir / "contents.xcworkspacedata"
        framework_name = config['framework_name']
        
        workspace_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "self:{framework_name}.xcodeproj">
   </FileRef>
</Workspace>'''
        
        with open(contents_path, 'w', encoding='utf-8') as f:
            f.write(workspace_content)
    
    def _generate_uuid(self) -> str:
        """生成24位UUID（Xcode格式）"""
        return uuid.uuid4().hex[:24].upper()


def main():
    """测试Xcode项目生成器"""
    generator = XcodeProjectGenerator()
    
    # 测试配置
    test_config = {
        'framework_name': 'MyTestFramework',
        'version': '1.0.0',
        'author': 'Test Author',
        'description': 'A test framework',
        'minimum_ios_version': '12.0'
    }
    
    # 生成项目
    success = generator.generate_project(test_config, "../output")
    
    if success:
        print("✅ 测试成功!")
    else:
        print("❌ 测试失败!")


if __name__ == "__main__":
    main() 