# XCFramework 自动构建工具

这是一个用于自动构建多架构 XCFramework 的工具，支持从源代码目录生成完整的 XCFramework。

## 功能特点

- 支持多平台构建（iOS、iOS Simulator、macOS、Mac Catalyst）
- 自动处理头文件依赖关系
- 自动生成主头文件
- 自动修复重复符号问题
- 支持自定义配置
- 生成详细的构建摘要

## 目录结构

```
.
├── src/                    # 源代码目录
│   ├── Headers/           # 头文件目录
│   │   ├── *.h           # 公共头文件
│   └── Sources/          # 源文件目录
│       └── *.m           # 实现文件
├── output_xcframework/    # 输出目录
├── build_xcframework.py   # 构建脚本
└── core/                 # 核心模块
    ├── header_parser.py  # 头文件解析器
    └── xcode_generator.py # Xcode项目生成器
```

## 使用方法

### 基本用法

```bash
python3 build_xcframework.py --name YourFrameworkName
```

### 完整参数

```bash
python3 build_xcframework.py [选项]

选项:
  --src, -s DIR           源码目录路径 (默认: src)
  --output, -o DIR        输出目录路径 (默认: output_xcframework)
  --name, -n NAME         Framework名称
  --platforms, -p PLAT   目标平台 (默认: ios ios-simulator)
                          可选值: ios, ios-simulator, macos, mac-catalyst
  --config, -c FILE      配置文件路径 (可选)
```

### 示例

1. 构建 iOS 和 iOS Simulator 版本：
```bash
python3 build_xcframework.py --name MyFramework
```

2. 指定输出目录：
```bash
python3 build_xcframework.py --name MyFramework --output ./build
```

3. 构建所有支持的平台：
```bash
python3 build_xcframework.py --name MyFramework --platforms ios ios-simulator macos mac-catalyst
```

## 源代码要求

### 目录结构

源代码目录应遵循以下结构：

```
src/
├── Headers/              # 公共头文件
│   ├── ClassA.h
│   └── ClassB.h
└── Sources/             # 实现文件
    ├── ClassA.m
    └── ClassB.m
```

### 头文件规范

1. 所有公共头文件应放在 `Headers` 目录下
2. 所有实现文件应放在 `Sources` 目录下
3. 头文件应使用标准的 Objective-C 语法
4. 建议使用模块化设计，每个类一个头文件

## 输出

构建完成后，将在输出目录生成：

1. XCFramework 文件
2. 构建摘要（JSON格式）
3. 构建日志

### 构建摘要示例

```json
{
  "framework_name": "MyFramework",
  "source_directory": "/path/to/src",
  "output_directory": "/path/to/output",
  "xcframework_path": "/path/to/output/MyFramework.xcframework",
  "platforms": ["ios", "ios-simulator"],
  "headers_count": 5,
  "sources_count": 5,
  "classes_count": 5,
  "build_status": "success"
}
```

## 注意事项

1. 确保已安装 Xcode 和命令行工具
2. 确保有足够的磁盘空间
3. 构建过程中会自动清理输出目录
4. 如果遇到重复符号问题，工具会自动处理

## 故障排除

1. 如果遇到构建失败，请检查：
   - Xcode 是否正确安装
   - 源代码目录结构是否正确
   - 是否有足够的磁盘空间

2. 如果遇到头文件问题，请检查：
   - 头文件是否放在正确的目录
   - 头文件语法是否正确
   - 是否有循环引用

## 贡献

欢迎提交 Issue 和 Pull Request。

## 许可证

MIT License 