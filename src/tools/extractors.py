"""
内容提取器
提供各种内容提取和解析功能
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re


class ContentExtractor:
    """内容提取器类"""
    
    @staticmethod
    def extract_links(html: str) -> List[Dict[str, str]]:
        """提取页面中的所有链接
        
        Args:
            html: HTML 内容
            
        Returns:
            链接列表，每个链接包含 text 和 href
        """
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        for a in soup.find_all('a', href=True):
            links.append({
                'text': a.get_text(strip=True),
                'href': a['href']
            })
        
        return links
    
    @staticmethod
    def extract_images(html: str) -> List[Dict[str, str]]:
        """提取页面中的所有图片
        
        Args:
            html: HTML 内容
            
        Returns:
            图片列表，每个图片包含 src 和 alt
        """
        soup = BeautifulSoup(html, 'lxml')
        images = []
        
        for img in soup.find_all('img'):
            images.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', '')
            })
        
        return images
    
    @staticmethod
    def extract_headings(html: str) -> Dict[str, List[str]]:
        """提取页面中的标题
        
        Args:
            html: HTML 内容
            
        Returns:
            标题字典，按级别分组
        """
        soup = BeautifulSoup(html, 'lxml')
        headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        
        for level in headings:
            for h in soup.find_all(level):
                headings[level].append(h.get_text(strip=True))
        
        return headings
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """提取文本中的邮箱地址
        
        Args:
            text: 文本内容
            
        Returns:
            邮箱列表
        """
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """提取文本中的电话号码
        
        Args:
            text: 文本内容
            
        Returns:
            电话号码列表
        """
        phone_patterns = [
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US 格式
            r'\d{3}[-.\s]?\d{4}[-.\s]?\d{4}',  # 中国手机号
            r'\d{4}[-.\s]?\d{7,8}'  # 中国座机
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return list(set(phones))
    
    @staticmethod
    def extract_structured_data(html: str) -> List[Dict[str, Any]]:
        """提取结构化数据（JSON-LD）
        
        Args:
            html: HTML 内容
            
        Returns:
            结构化数据列表
        """
        soup = BeautifulSoup(html, 'lxml')
        structured_data = []
        
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                structured_data.append(data)
            except (json.JSONDecodeError, TypeError):
                continue
        
        return structured_data
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符（保留常用标点）
        text = re.sub(r'[^\w\s.,!?;:()\[\]{}"\'-]', '', text)
        return text.strip()
