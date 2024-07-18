import json
import sys
import os
from jinja2 import Environment, FileSystemLoader
import plotly.graph_objects as go
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import whois
from datetime import datetime
import ssl
import socket
import re

class WebsiteAnalyzer:

    def __init__(self, url):
        self.url = url
        self.data = {'url': url}

    def fetch_content(self):
        try:
            response = requests.get(self.url, timeout=10)
            self.data['html_content'] = response.text
            self.data['status_code'] = response.status_code
            return True
        except requests.RequestException:
            self.data['html_content'] = ''
            self.data['status_code'] = None
            return False

    def check_responsiveness(self):
        soup = BeautifulSoup(self.data['html_content'], 'html.parser')
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        self.data['responsive'] = 1 if viewport else 0

    def identify_technologies(self):
        self.data['technologies'] = []
        if 'WordPress' in self.data['html_content']:
            self.data['technologies'].append('WordPress')
        if 'jQuery' in self.data['html_content']:
            self.data['technologies'].append('jQuery')

    def check_seo(self):
        soup = BeautifulSoup(self.data['html_content'], 'html.parser')
        self.data['seo_score'] = 0
        if soup.find('title'):
            self.data['seo_score'] += 0.2
        if soup.find('meta', attrs={'name': 'description'}):
            self.data['seo_score'] += 0.2
        if soup.find('h1'):
            self.data['seo_score'] += 0.2
        if soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
            self.data['seo_score'] += 0.2
        if soup.find_all('img', alt=True):
            self.data['seo_score'] += 0.2

    def check_https(self):
        self.data['uses_https'] = 1 if self.url.startswith('https://') else 0

    def check_content_freshness(self):
        try:
            domain = urlparse(self.url).netloc
            whois_info = whois.whois(domain)
            if isinstance(whois_info.expiration_date, list):
                expiration_date = whois_info.expiration_date[0]
            else:
                expiration_date = whois_info.expiration_date

            if expiration_date:
                days_to_expire = (expiration_date - datetime.now()).days
                self.data['content_freshness'] = 1 if days_to_expire > 30 else 0
            else:
                self.data['content_freshness'] = 0
        except Exception:
            self.data['content_freshness'] = 0

    def check_security(self):
        self.data['security_score'] = 0
        try:
            context = ssl.create_default_context()
            with socket.create_connection((urlparse(self.url).netloc, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=urlparse(self.url).netloc) as ssock:
                    certificate = ssock.getpeercert()
                    self.data['security_score'] = 1 if certificate else 0
        except Exception:
            self.data['security_score'] = 0

    def check_accessibility(self):
        soup = BeautifulSoup(self.data['html_content'], 'html.parser')
        self.data['accessibility_score'] = 0
        if soup.find_all('img', alt=True):
            self.data['accessibility_score'] += 0.25
        if soup.find_all('label'):
            self.data['accessibility_score'] += 0.25
        if soup.find_all(attrs={"role": True}):
            self.data['accessibility_score'] += 0.25
        if soup.find(attrs={"role": "main"}):
            self.data['accessibility_score'] += 0.25

    def check_performance(self):
        self.data['page_size'] = len(self.data['html_content'])
        self.data['http_requests'] = len(re.findall(r'<(script|link|img)', self.data['html_content']))

    def analyze_content(self):
        soup = BeautifulSoup(self.data['html_content'], 'html.parser')
        text_content = soup.get_text()
        self.data['content_to_html_ratio'] = len(text_content) / len(self.data['html_content'])
        
        # Keyword density (simple implementation)
        words = re.findall(r'\w+', text_content.lower())
        word_count = len(words)
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        self.data['keyword_density'] = {word: count/word_count for word, count in word_freq.items() if len(word) > 3}

    def check_social_media_tags(self):
        soup = BeautifulSoup(self.data['html_content'], 'html.parser')
        self.data['social_media_tags'] = {
            'og:title': bool(soup.find('meta', property='og:title')),
            'og:description': bool(soup.find('meta', property='og:description')),
            'og:image': bool(soup.find('meta', property='og:image')),
            'twitter:card': bool(soup.find('meta', attrs={'name': 'twitter:card'})),
        }

    def check_technical_seo(self):
        soup = BeautifulSoup(self.data['html_content'], 'html.parser')
        self.data['has_sitemap'] = 1 if 'sitemap' in self.data['html_content'].lower() else 0
        self.data['has_robots_txt'] = 1 if 'robots.txt' in self.data['html_content'].lower() else 0
        self.data['has_structured_data'] = 1 if soup.find('script', attrs={'type': 'application/ld+json'}) else 0

    def check_mobile_friendliness(self):
        soup = BeautifulSoup(self.data['html_content'], 'html.parser')
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        self.data['mobile_friendly_score'] = 0
        if viewport and 'width=device-width' in viewport.get('content', ''):
            self.data['mobile_friendly_score'] += 0.5
        if viewport and 'initial-scale=1' in viewport.get('content', ''):
            self.data['mobile_friendly_score'] += 0.5

    def check_aesthetic_quality(self):
        soup = BeautifulSoup(self.data['html_content'], 'html.parser')
        self.data['aesthetic_score'] = 0

        if soup.find('link', href=re.compile(r'fonts\.googleapis\.com|fonts\.gstatic\.com')):
            self.data['aesthetic_score'] += 0.2

        if soup.find('style') or soup.find('link', rel='stylesheet'):
            self.data['aesthetic_score'] += 0.2

        if soup.find_all('img'):
            self.data['aesthetic_score'] += 0.2

        colors = re.findall(r'#[0-9a-fA-F]{6}', self.data['html_content'])
        if len(set(colors)) > 3:
            self.data['aesthetic_score'] += 0.2

        modern_tags = ['header', 'nav', 'main', 'footer', 'article', 'section']
        if any(soup.find(tag) for tag in modern_tags):
            self.data['aesthetic_score'] += 0.2

    def check_site_age(self):
        try:
            domain = urlparse(self.url).netloc
            whois_info = whois.whois(domain)
            creation_date = whois_info.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            age = (datetime.now() - creation_date).days / 365.25  # age in years
            self.data['site_age'] = min(age / 10, 1)  # Normalize to 0-1, max at 10 years
        except Exception:
            self.data['site_age'] = 0

    def calculate_visual_outdatedness(self):
        self.data['visual_outdatedness'] = (self.data['site_age'] + (1 - self.data['aesthetic_score'])) / 2

    def analyze(self):
        if not self.fetch_content():
            return False
        self.check_responsiveness()
        self.identify_technologies()
        self.check_seo()
        self.check_https()
        self.check_content_freshness()
        self.check_security()
        self.check_accessibility()
        self.check_performance()
        self.analyze_content()
        self.check_social_media_tags()
        self.check_technical_seo()
        self.check_mobile_friendliness()
        self.check_aesthetic_quality()
        self.check_site_age()
        self.calculate_visual_outdatedness()
        return True

    def calculate_score(self):
        score = 0
        score += (self.data['responsive'] + self.data['mobile_friendly_score']) / 2 * 0.2  # Responsiveness
        score += self.data['seo_score'] * 0.1
        score += (self.data['uses_https'] + self.data['security_score']) / 2 * 0.2  # Security
        score += self.data['accessibility_score'] * 0.1
        score += (1 - self.data['visual_outdatedness']) * 0.2  # Visual freshness
        score += (1 - min(self.data['page_size'] / 5000000, 1)) * 0.1  # Performance (simplified)
        score += sum(self.data['social_media_tags'].values()) / len(self.data['social_media_tags']) * 0.05
        score += (self.data['has_sitemap'] + self.data['has_robots_txt'] + self.data['has_structured_data']) / 3 * 0.05
        self.data['overall_score'] = score

# ... (previous code remains the same)

def create_gauge_chart(value, title):
    color = '#4CAF50' if value >= 0.7 else '#FFC107' if value >= 0.4 else '#F44336'
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 100], 'color': 'lightgray'}
            ],
        }
    ))
    
    fig.update_layout(
        height=250,
        width=250,
        paper_bgcolor="white",
        font={'color': "darkblue", 'family': "Exo"}
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def generate_report(url_data, template_file, output_file):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_file)
    
    charts = {
        'responsiveness': create_gauge_chart((url_data['responsive'] + url_data['mobile_friendly_score']) / 2, 'Responsiveness'),
        'seo': create_gauge_chart(url_data['seo_score'], 'SEO Score'),
        'security': create_gauge_chart((url_data['uses_https'] + url_data['security_score']) / 2, 'Security'),
        'accessibility': create_gauge_chart(url_data['accessibility_score'], 'Accessibility'),
        'visual_outdatedness': create_gauge_chart(1 - url_data['visual_outdatedness'], 'Visual Freshness'),
        'performance': create_gauge_chart(1 - min(url_data['page_size'] / 5000000, 1), 'Performance'),
    }
    
    rendered_html = template.render(url=url_data['url'], charts=charts, data=url_data)
    
    with open(output_file, 'w') as f:
        f.write(rendered_html)

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_report.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    template_file = 'report_template.html'
    
    # Create 'reports' folder if it doesn't exist
    reports_folder = 'reports'
    if not os.path.exists(reports_folder):
        os.makedirs(reports_folder)
    
    # Extract domain name from URL
    domain = urlparse(url).netloc
    
    # Generate output file names with domain
    output_file = os.path.join(reports_folder, f'{domain}_report.html')
    json_output_file = os.path.join(reports_folder, f'{domain}_record.json')
    
    analyzer = WebsiteAnalyzer(url)
    if analyzer.analyze():
        analyzer.calculate_score()
        
        with open(json_output_file, 'w') as f:
            json.dump(analyzer.data, f, indent=2)

        generate_report(analyzer.data, template_file, output_file)
        print(f"Report generated: {output_file}")
        print(f"JSON record generated: {json_output_file}")
    else:
        print(f"Failed to analyze the website: {url}")

if __name__ == "__main__":
    main()