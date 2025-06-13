#!/usr/bin/env python3
"""
头文件解析器
解析Objective-C头文件，提取类、方法、属性等API信息
"""

import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MethodInfo:
    """方法信息"""
    name: str
    signature: str
    return_type: str
    parameters: List[Dict[str, str]]
    is_class_method: bool
    description: str = ""


@dataclass
class PropertyInfo:
    """属性信息"""
    name: str
    type: str
    attributes: List[str]
    description: str = ""


@dataclass
class ClassInfo:
    """类信息"""
    name: str
    superclass: str
    protocols: List[str]
    methods: List[MethodInfo]
    properties: List[PropertyInfo]
    description: str = ""


@dataclass
class EnumInfo:
    """枚举信息"""
    name: str
    values: List[Dict[str, Any]]
    description: str = ""


@dataclass
class APIInfo:
    """完整的API信息"""
    classes: List[ClassInfo]
    enums: List[EnumInfo]
    constants: List[Dict[str, str]]
    functions: List[MethodInfo]
    imports: List[str]


class HeaderParser:
    """头文件解析器"""
    
    def __init__(self):
        self.api_info = APIInfo([], [], [], [], [])
        
        # 正则表达式模式
        self.patterns = {
            'import': r'#import\s+[<"]([^>"]+)[>"]',
            'interface': r'@interface\s+(\w+)\s*(?::\s*(\w+))?\s*(?:<([^>]+)>)?\s*\{?',
            'property': r'@property\s*\(([^)]*)\)\s*([^;]+?)\s*(\w+)\s*;',
            'method': r'([-+])\s*\(([^)]+)\)\s*([^;{]+)',
            'enum': r'typedef\s+(?:NS_)?enum\s*(?:\w+\s*)?\{([^}]+)\}\s*(\w+)\s*;',
            'constant': r'(?:extern\s+)?(?:const\s+)?(\w+\s*\*?)\s+(\w+)\s*(?:=\s*[^;]+)?;',
            'function': r'(\w+\s*\*?)\s+(\w+)\s*\(([^)]*)\)\s*;'
        }
    
    def parse_directory(self, headers_dir: str) -> APIInfo:
        """解析整个头文件目录"""
        headers_path = Path(headers_dir)
        if not headers_path.exists():
            raise FileNotFoundError(f"头文件目录不存在: {headers_dir}")
        
        print(f"📋 解析头文件目录: {headers_dir}")
        
        # 查找所有.h文件
        header_files = list(headers_path.glob("*.h"))
        if not header_files:
            raise ValueError(f"在目录 {headers_dir} 中未找到头文件")
        
        print(f"   找到 {len(header_files)} 个头文件")
        
        # 解析每个头文件
        for header_file in header_files:
            print(f"   解析: {header_file.name}")
            self.parse_header_file(str(header_file))
        
        print(f"✅ 解析完成: {len(self.api_info.classes)} 个类, {len(self.api_info.enums)} 个枚举")
        return self.api_info
    
    def parse_header_file(self, header_path: str) -> Optional[Dict[str, Any]]:
        """解析单个头文件"""
        try:
            with open(header_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(header_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # 创建临时API信息对象
        temp_api = APIInfo([], [], [], [], [])
        original_api = self.api_info
        self.api_info = temp_api
        
        try:
            # 移除注释
            content = self._remove_comments(content)
            
            # 解析各种元素
            self._parse_imports(content)
            self._parse_classes(content)
            self._parse_enums(content)
            self._parse_constants(content)
            self._parse_functions(content)
            
            # 转换为字典格式
            result = {
                'classes': [self._class_info_to_dict(cls) for cls in temp_api.classes],
                'protocols': [],  # 协议解析需要单独实现
                'enums': [self._enum_info_to_dict(enum) for enum in temp_api.enums],
                'constants': temp_api.constants,
                'functions': [self._method_info_to_dict(func) for func in temp_api.functions],
                'imports': temp_api.imports
            }
            
            return result if (result['classes'] or result['enums'] or result['constants']) else None
            
        finally:
            # 恢复原始API信息
            self.api_info = original_api
    
    def _remove_comments(self, content: str) -> str:
        """移除C风格注释"""
        # 移除单行注释
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        # 移除多行注释
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _parse_imports(self, content: str) -> None:
        """解析import语句"""
        matches = re.findall(self.patterns['import'], content)
        for match in matches:
            if match not in self.api_info.imports:
                self.api_info.imports.append(match)
    
    def _parse_classes(self, content: str) -> None:
        """解析类定义"""
        # 查找@interface...@end块
        interface_pattern = r'@interface\s+(\w+).*?@end'
        interface_matches = re.finditer(interface_pattern, content, re.DOTALL)
        
        for match in interface_matches:
            interface_content = match.group(0)
            class_info = self._parse_single_class(interface_content)
            if class_info:
                self.api_info.classes.append(class_info)
    
    def _parse_single_class(self, interface_content: str) -> Optional[ClassInfo]:
        """解析单个类"""
        # 解析类声明行
        header_match = re.search(self.patterns['interface'], interface_content)
        if not header_match:
            return None
        
        class_name = header_match.group(1)
        superclass = header_match.group(2) or "NSObject"
        protocols_str = header_match.group(3) or ""
        protocols = [p.strip() for p in protocols_str.split(',')] if protocols_str else []
        
        # 解析属性
        properties = self._parse_properties(interface_content)
        
        # 解析方法
        methods = self._parse_methods(interface_content)
        
        return ClassInfo(
            name=class_name,
            superclass=superclass,
            protocols=protocols,
            methods=methods,
            properties=properties
        )
    
    def _parse_properties(self, content: str) -> List[PropertyInfo]:
        """解析属性"""
        properties = []
        matches = re.finditer(self.patterns['property'], content)
        
        for match in matches:
            attributes_str = match.group(1)
            type_str = match.group(2).strip()
            name = match.group(3)
            
            attributes = [attr.strip() for attr in attributes_str.split(',')]
            
            properties.append(PropertyInfo(
                name=name,
                type=type_str,
                attributes=attributes
            ))
        
        return properties
    
    def _parse_methods(self, content: str) -> List[MethodInfo]:
        """解析方法"""
        methods = []
        matches = re.finditer(self.patterns['method'], content)
        
        for match in matches:
            method_type = match.group(1)  # - 或 +
            return_type = match.group(2).strip()
            signature = match.group(3).strip()
            
            # 解析方法名和参数
            method_name, parameters = self._parse_method_signature(signature)
            
            methods.append(MethodInfo(
                name=method_name,
                signature=f"{method_type} ({return_type}){signature}",
                return_type=return_type,
                parameters=parameters,
                is_class_method=(method_type == '+')
            ))
        
        return methods
    
    def _parse_method_signature(self, signature: str) -> tuple:
        """解析方法签名"""
        # 简单的方法名提取
        if ':' not in signature:
            # 无参数方法
            return signature.strip(), []
        
        # 有参数的方法
        parts = signature.split(':')
        method_name = parts[0].strip()
        
        parameters = []
        for i, part in enumerate(parts[1:], 1):
            if i < len(parts) - 1:
                # 提取参数类型和名称
                param_match = re.search(r'\(([^)]+)\)\s*(\w+)', part)
                if param_match:
                    param_type = param_match.group(1)
                    param_name = param_match.group(2)
                    parameters.append({
                        'type': param_type,
                        'name': param_name
                    })
        
        return method_name, parameters
    
    def _parse_enums(self, content: str) -> None:
        """解析枚举"""
        matches = re.finditer(self.patterns['enum'], content)
        
        for match in matches:
            enum_body = match.group(1)
            enum_name = match.group(2)
            
            # 解析枚举值
            values = []
            enum_values = re.findall(r'(\w+)(?:\s*=\s*([^,}]+))?', enum_body)
            
            for value_name, value_expr in enum_values:
                values.append({
                    'name': value_name.strip(),
                    'value': value_expr.strip() if value_expr else None
                })
            
            self.api_info.enums.append(EnumInfo(
                name=enum_name,
                values=values
            ))
    
    def _parse_constants(self, content: str) -> None:
        """解析常量"""
        matches = re.finditer(self.patterns['constant'], content)
        
        for match in matches:
            const_type = match.group(1).strip()
            const_name = match.group(2)
            
            self.api_info.constants.append({
                'name': const_name,
                'type': const_type
            })
    
    def _parse_functions(self, content: str) -> None:
        """解析函数"""
        matches = re.finditer(self.patterns['function'], content)
        
        for match in matches:
            return_type = match.group(1).strip()
            func_name = match.group(2)
            params_str = match.group(3)
            
            # 解析参数
            parameters = []
            if params_str.strip() and params_str.strip() != 'void':
                param_matches = re.findall(r'([^,]+)', params_str)
                for param in param_matches:
                    param = param.strip()
                    if param:
                        # 简单的参数解析
                        param_parts = param.split()
                        if len(param_parts) >= 2:
                            param_type = ' '.join(param_parts[:-1])
                            param_name = param_parts[-1]
                            parameters.append({
                                'type': param_type,
                                'name': param_name
                            })
            
            self.api_info.functions.append(MethodInfo(
                name=func_name,
                signature=f"{return_type} {func_name}({params_str})",
                return_type=return_type,
                parameters=parameters,
                is_class_method=False
            ))
    
    def _class_info_to_dict(self, class_info: ClassInfo) -> Dict[str, Any]:
        """将ClassInfo转换为字典"""
        return {
            'name': class_info.name,
            'superclass': class_info.superclass,
            'protocols': class_info.protocols,
            'methods': [self._method_info_to_dict(method) for method in class_info.methods],
            'properties': [self._property_info_to_dict(prop) for prop in class_info.properties],
            'description': class_info.description
        }
    
    def _method_info_to_dict(self, method_info: MethodInfo) -> Dict[str, Any]:
        """将MethodInfo转换为字典"""
        return {
            'name': method_info.name,
            'signature': method_info.signature,
            'return_type': method_info.return_type,
            'parameters': method_info.parameters,
            'is_class_method': method_info.is_class_method,
            'description': method_info.description
        }
    
    def _property_info_to_dict(self, prop_info: PropertyInfo) -> Dict[str, Any]:
        """将PropertyInfo转换为字典"""
        return {
            'name': prop_info.name,
            'type': prop_info.type,
            'attributes': prop_info.attributes,
            'description': prop_info.description
        }
    
    def _enum_info_to_dict(self, enum_info: EnumInfo) -> Dict[str, Any]:
        """将EnumInfo转换为字典"""
        return {
            'name': enum_info.name,
            'values': [value['name'] for value in enum_info.values],
            'description': enum_info.description
        }
    
    def get_framework_info(self) -> Dict[str, Any]:
        """获取Framework信息摘要"""
        return {
            'total_classes': len(self.api_info.classes),
            'total_methods': sum(len(cls.methods) for cls in self.api_info.classes),
            'total_properties': sum(len(cls.properties) for cls in self.api_info.classes),
            'total_enums': len(self.api_info.enums),
            'total_constants': len(self.api_info.constants),
            'total_functions': len(self.api_info.functions),
            'imports': self.api_info.imports,
            'class_names': [cls.name for cls in self.api_info.classes]
        }


def main():
    """测试头文件解析器"""
    parser = HeaderParser()
    
    # 测试解析
    try:
        api_info = parser.parse_directory("../examples/MyFramework/Headers")
        
        print("\n📊 解析结果:")
        framework_info = parser.get_framework_info()
        for key, value in framework_info.items():
            print(f"   {key}: {value}")
        
        # 显示详细信息
        print("\n📋 类详情:")
        for cls in api_info.classes:
            print(f"   {cls.name} : {cls.superclass}")
            print(f"      属性: {len(cls.properties)}")
            print(f"      方法: {len(cls.methods)}")
    
    except Exception as e:
        print(f"❌ 解析失败: {e}")


if __name__ == "__main__":
    main() 