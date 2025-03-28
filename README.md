# 图片下载器

这是一个可以从网页画廊批量下载图片的工具，提供GUI界面和命令行两种使用方式。

## 功能特点

- 支持通过ID或class选择器定位网页中的图片画廊
- 提供多种图片命名方式：原始文件名、UUID、时间戳、自定义前缀
- 支持暂停/继续下载功能
- 支持断点续传（记录已下载文件）
- 可设置超时时间和重试次数
- 提供下载进度显示

## 安装要求

- Python 3.6+
- 依赖库：
  ```
  pip install requests beautifulsoup4 tkinterdnd2 pyinstaller
  ```

## 使用方法

### GUI版本

运行GUI界面：
```
python gui.py
```

界面参数说明：
- 目标URL：要下载的网页地址
- 选择器类型：id或class
- 选择器值：画廊元素的id或class值
- 保存目录：图片保存路径（默认为downloaded_images）
- 命名方式：图片文件名生成规则
- 超时时间：单张图片下载超时时间（秒）
- 最大重试次数：下载失败重试次数

### 命令行版本

基本用法：
```
python cli.py <url> <selector_value> [options]
```

选项参数：
```
--selector-type     选择器类型(id/class)，默认为id
--save-dir          保存目录，默认为downloaded_images
--naming            命名方式(original/uuid/timestamp/custom)，默认为original
--prefix            自定义前缀（当命名方式为custom时使用）
--timeout           超时时间(秒)，默认为15
--retries           重试次数，默认为3
```

示例：
```
python cli.py "https://example.com/gallery" "gallery-container" --selector-type class --naming timestamp
```

## 打包说明

将GUI版本打包为可执行文件：
```
pyinstaller gui.spec
```

打包后程序位于dist/gui目录

## 注意事项

1. 请遵守目标网站的robots.txt和使用条款
2. 大量下载时请设置合理的超时时间和间隔
3. 自定义前缀命名方式需要指定--prefix参数
4. 暂停功能会暂停下载但不会中断当前正在下载的图片
5. 打包时需要安装tkinterdnd2库
