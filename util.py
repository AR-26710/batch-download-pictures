import os
import requests
import uuid
import time
import random
import string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# 全局变量
DOWNLOADED_FILES = set()
is_paused = False
stop_download = False


def load_downloaded_files(save_dir):
    """加载已下载的文件列表"""
    if os.path.exists(os.path.join(save_dir, "downloaded.txt")):
        with open(os.path.join(save_dir, "downloaded.txt"), "r") as f:
            return set(line.strip() for line in f)
    return set()


def save_downloaded_file(save_dir, filename):
    """保存已下载的文件名"""
    with open(os.path.join(save_dir, "downloaded.txt"), "a") as f:
        f.write(f"{filename}\n")


def generate_filename(img_url, naming_option="original", custom_prefix=""):
    """生成文件名"""
    original_name = os.path.basename(img_url)
    name, ext = os.path.splitext(original_name)

    if naming_option == "original":
        return original_name if original_name else f"image_{hash(img_url)}{ext}"
    elif naming_option == "uuid":
        return f"{uuid.uuid4()}{ext}"
    elif naming_option == "timestamp":
        return f"{int(time.time())}{ext}"
    elif naming_option == "custom":
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        return f"{custom_prefix}_{random_str}{ext}"
    else:
        raise ValueError("Invalid naming option.")


def download_images_from_gallery(
        url,
        gallery_selector,
        selector_type="id",
        save_dir=None,
        naming_option="original",
        custom_prefix="",
        timeout=10,
        max_retries=3,
        progress_callback=None
):
    """下载画廊图片，支持暂停和继续"""
    global is_paused, stop_download, DOWNLOADED_FILES

    if save_dir is None:
        save_dir = "downloaded_images"
    # 解析域名和生成时间戳
    parsed_url = urlparse(url)
    domain = parsed_url.netloc if parsed_url.netloc else "unknown_domain"
    timestamp = time.strftime("%Y-%m-%d-%H%M")
    new_save_dir = os.path.join(save_dir, domain, timestamp)
    os.makedirs(new_save_dir, exist_ok=True)

    DOWNLOADED_FILES = load_downloaded_files(new_save_dir)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if progress_callback:
            progress_callback(f"无法访问网页: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    if selector_type == "id":
        gallery = soup.find(id=gallery_selector)
    elif selector_type == "class":
        gallery = soup.find(class_=gallery_selector)
    else:
        if progress_callback:
            progress_callback("无效的选择器类型，请使用 'id' 或 'class'")
        return

    if not gallery:
        if progress_callback:
            progress_callback(f"未找到 {selector_type} 为 '{gallery_selector}' 的画廊")
        return

    img_tags = gallery.find_all('img')
    if not img_tags:
        if progress_callback:
            progress_callback("画廊中没有找到图片")
        return

    total_images = len(img_tags)
    for idx, img in enumerate(img_tags):
        if stop_download:
            if progress_callback:
                progress_callback("用户取消下载，程序退出。")
            return

        while is_paused:
            if stop_download:
                return
            time.sleep(0.5)

        img_url = img.get('src')
        if not img_url:
            continue

        img_url = urljoin(url, img_url)
        try:
            img_name = generate_filename(img_url, naming_option, custom_prefix)
        except ValueError as e:
            if progress_callback:
                progress_callback(f"文件名生成失败: {e}")
            continue

        if img_name in DOWNLOADED_FILES:
            if progress_callback:
                progress_callback(f"跳过已下载: {img_name}")
            continue

        for attempt in range(max_retries):
            if stop_download:
                return

            while is_paused:
                if stop_download:
                    return
                time.sleep(0.5)

            try:
                img_data = requests.get(img_url, headers=headers, timeout=timeout).content
                img_path = os.path.join(new_save_dir, img_name)

                counter = 1
                while os.path.exists(img_path):
                    name, ext = os.path.splitext(img_name)
                    img_path = os.path.join(save_dir, f"{name}_{counter}{ext}")
                    counter += 1

                with open(img_path, 'wb') as f:
                    f.write(img_data)
                save_downloaded_file(new_save_dir, img_name)
                if progress_callback:
                    progress_callback(f"下载成功 ({idx + 1}/{total_images}): {img_path}")
                break
            except (requests.exceptions.RequestException, KeyboardInterrupt) as e:
                if isinstance(e, KeyboardInterrupt):
                    if progress_callback:
                        progress_callback("\n用户中断下载，程序退出。")
                    return
                if attempt == max_retries - 1:
                    if progress_callback:
                        progress_callback(f"下载失败（重试 {max_retries} 次）: {img_url}, 错误: {e}")
                else:
                    if progress_callback:
                        progress_callback(f"下载失败（第 {attempt + 1} 次重试）: {img_url}, 错误: {e}")
                    time.sleep(1)
