import argparse
import signal
import sys

# 导入下载图片的函数
from util import (
    download_images_from_gallery
)


# 定义一个回调函数，用于在命令行界面显示进度信息
def cli_progress_callback(message):
    print(message)


# 定义一个信号处理器，用于响应用户中断下载的请求
def signal_handler(sig, frame):
    global stop_download
    stop_download = True
    print("\n下载已取消")
    sys.exit(0)


# 主函数，负责处理命令行参数并启动图片下载过程
def main():
    # 设置信号处理器，以便能够响应中断信号
    signal.signal(signal.SIGINT, signal_handler)

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='图片下载器 CLI 版本')
    # 添加目标网页URL参数
    parser.add_argument('url', help='目标网页URL')
    # 添加画廊选择器值参数
    parser.add_argument('selector_value', help='画廊选择器值')
    # 添加选择器类型参数，默认为id
    parser.add_argument('--selector-type', choices=['id', 'class'], default='id',
                        help='选择器类型 (id 或 class), 默认为 id')
    # 添加图片保存目录参数
    parser.add_argument('--save-dir', help='图片保存目录, 默认为 downloaded_images')
    # 添加文件名命名方式参数，默认为original
    parser.add_argument('--naming', choices=['original', 'uuid', 'timestamp', 'custom'],
                        default='original', help='文件名命名方式, 默认为 original')
    # 添加自定义文件名前缀参数，仅在命名方式为custom时使用
    parser.add_argument('--prefix', help='自定义文件名前缀 (当命名方式为 custom 时使用)')
    # 添加下载超时时间参数，默认为15秒
    parser.add_argument('--timeout', type=int, default=15,
                        help='下载超时时间(秒), 默认为 15')
    # 添加下载失败重试次数参数，默认为3次
    parser.add_argument('--retries', type=int, default=3,
                        help='下载失败重试次数, 默认为 3')

    # 解析命令行参数
    args = parser.parse_args()

    # 检查参数有效性：当命名方式为custom且未提供前缀时，显示错误信息并退出
    if args.naming == 'custom' and not args.prefix:
        print("错误: 当使用 custom 命名方式时必须提供 --prefix 参数")
        sys.exit(1)

    # 打印下载信息
    print(f"开始下载: {args.url}")
    print(f"选择器: {args.selector_type}={args.selector_value}")
    print(f"保存目录: {args.save_dir or 'downloaded_images'}")
    print(f"命名方式: {args.naming}{' (前缀: ' + args.prefix + ')' if args.naming == 'custom' else ''}")
    print(f"超时: {args.timeout}秒, 重试: {args.retries}次")
    print("按 Ctrl+C 取消下载\n")

    # 调用函数执行图片下载
    download_images_from_gallery(
        url=args.url,
        gallery_selector=args.selector_value,
        selector_type=args.selector_type,
        save_dir=args.save_dir,
        naming_option=args.naming,
        custom_prefix=args.prefix,
        timeout=args.timeout,
        max_retries=args.retries,
        progress_callback=cli_progress_callback
    )

    # 下载完成后，显示完成信息
    print("\n下载完成!")


# 当脚本直接执行时，调用主函数
if __name__ == "__main__":
    main()
