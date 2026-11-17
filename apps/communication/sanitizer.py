import re
import html
from html.parser import HTMLParser
from urllib.parse import urlparse

ALLOWED_TAGS = {'b', 'strong', 'i', 'em', 'u', 'br', 'p', 'ul', 'ol', 'li', 'a', 'h3'}
VOID_TAGS = {'br'}
DISCARD_CONTENT_TAGS = {'script', 'style', 'iframe', 'object', 'embed', 'applet', 'noscript', 'svg'}

class SafeHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output = []
        self.open_tags = []
        self.discard_depth = 0

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower in DISCARD_CONTENT_TAGS:
            self.discard_depth += 1
            return

        if self.discard_depth > 0:
            return

        if tag_lower in ALLOWED_TAGS:
            if tag_lower == 'a':
                clean_attrs = []
                for attr_name, attr_val in attrs:
                    if attr_name.lower() == 'href' and attr_val:
                        val = attr_val.strip()
                        # Allow only http, https, mailto
                        val_lower = val.lower()
                        if val_lower.startswith(('http://', 'https://', 'mailto:')):
                            # Ensure no embedded javascript or null bytes
                            if 'javascript:' not in val_lower and '\x00' not in val:
                                clean_attrs.append(f'href="{html.escape(val, quote=True)}"')
                if clean_attrs:
                    self.output.append(f'<a {" ".join(clean_attrs)}>')
                    self.open_tags.append('a')
                else:
                    # If invalid href, omit the <a> tag but keep contents
                    pass
            elif tag_lower in VOID_TAGS:
                self.output.append(f'<{tag_lower}>')
            else:
                self.output.append(f'<{tag_lower}>')
                self.open_tags.append(tag_lower)

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in DISCARD_CONTENT_TAGS:
            if self.discard_depth > 0:
                self.discard_depth -= 1
            return

        if self.discard_depth > 0:
            return

        if tag_lower in ALLOWED_TAGS and tag_lower not in VOID_TAGS:
            if tag_lower in self.open_tags:
                # Close all open tags up to this tag
                while self.open_tags:
                    popped = self.open_tags.pop()
                    self.output.append(f'</{popped}>')
                    if popped == tag_lower:
                        break

    def handle_data(self, data):
        if self.discard_depth == 0:
            # Escape raw text to prevent raw characters from being parsed as markup
            self.output.append(html.escape(data))

    def handle_entityref(self, name):
        if self.discard_depth == 0:
            self.output.append(f'&{name};')

    def handle_charref(self, name):
        if self.discard_depth == 0:
            self.output.append(f'&#{name};')

    def close(self):
        super().close()
        # Close any unclosed tags
        while self.open_tags:
            popped = self.open_tags.pop()
            self.output.append(f'</{popped}>')
        return ''.join(self.output)


def sanitize_html(content):
    """
    Sanitizes HTML allowing only safe tags (b, strong, i, em, u, br, p, ul, ol, li, a[href], h3).
    Strips scripts, onclick, stylesheets, and dangerous schemes.
    If the content appears to be legacy plain text (contains newlines without HTML block tags),
    newlines are converted to <br> to ensure proper rendering.
    """
    if not content:
        return ""

    content_str = str(content)

    parser = SafeHTMLParser()
    parser.feed(content_str)
    sanitized = parser.close()

    # Check if this looks like plain text that lacks HTML markup
    has_html_tags = bool(re.search(r'<(?:p|br|b|i|strong|em|u|ul|ol|li|h3|a)\b', content_str, re.IGNORECASE))
    if not has_html_tags and '\n' in content_str:
        # Legacy plain text with newlines - convert newlines to <br>
        sanitized = sanitized.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br>')

    return sanitized


def html_to_plain_text(content):
    """
    Converts sanitized or raw HTML to clean plain text.
    Replaces line break and block tags with appropriate newlines,
    bullet points for list items, and strips all HTML tags.
    """
    if not content:
        return ""

    text = str(content)
    # Replace line breaks
    text = re.sub(r'<\s*br\s*/?\s*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<\s*/\s*p\s*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<\s*/\s*h3\s*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<\s*li\s*>', '• ', text, flags=re.IGNORECASE)
    text = re.sub(r'<\s*/\s*li\s*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<\s*/\s*(?:ul|ol)\s*>', '\n', text, flags=re.IGNORECASE)

    # Strip remaining tags
    text = re.sub(r'<[^>]+>', '', text)

    # Unescape HTML entities
    text = html.unescape(text)

    # Normalize whitespace
    lines = [line.strip() for line in text.split('\n')]
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    return cleaned
