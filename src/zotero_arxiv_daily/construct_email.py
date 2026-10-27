from .protocol import Paper
import math
from datetime import datetime


framework = """
<!DOCTYPE HTML>
<html>
<head>
  <style>
    .star-wrapper {
      font-size: 1.3em; /* 调整星星大小 */
      line-height: 1; /* 确保垂直对齐 */
      display: inline-flex;
      align-items: center; /* 保持对齐 */
    }
    .half-star {
      display: inline-block;
      width: 0.5em; /* 半颗星的宽度 */
      overflow: hidden;
      white-space: nowrap;
      vertical-align: middle;
    }
    .full-star {
      vertical-align: middle;
    }
  </style>
</head>
<body>

<div>
    __CONTENT__
</div>

<br><br>
<div>
To unsubscribe, remove your email in your Github Action setting.
</div>

</body>
</html>
"""

def get_empty_html():
  block_template = """
  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
  <tr>
    <td style="font-size: 20px; font-weight: bold; color: #333;">
        No Papers Today. Take a Rest!
    </td>
  </tr>
  </table>
  """
  return block_template

def get_block_html(title:str, authors:str, rate:str, tldr:str, pdf_url:str, affiliations:str=None):
    block_template = """
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
    <tr>
        <td style="font-size: 20px; font-weight: bold; color: #333;">
            {title}
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #666; padding: 8px 0;">
            {authors}
            <br>
            <i>{affiliations}</i>
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #333; padding: 8px 0;">
            <strong>Relevance:</strong> {rate}
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #333; padding: 8px 0;">
            <strong>TLDR:</strong> {tldr}
        </td>
    </tr>

    <tr>
        <td style="padding: 8px 0;">
            <a href="{pdf_url}" style="display: inline-block; text-decoration: none; font-size: 14px; font-weight: bold; color: #fff; background-color: #d9534f; padding: 8px 16px; border-radius: 4px;">PDF</a>
        </td>
    </tr>
</table>
"""
    return block_template.format(title=title, authors=authors,rate=rate, tldr=tldr, pdf_url=pdf_url, affiliations=affiliations)

def get_stars(score:float):
    full_star = '<span class="full-star">⭐</span>'
    half_star = '<span class="half-star">⭐</span>'
    low = 6
    high = 8
    if score <= low:
        return ''
    elif score >= high:
        return full_star * 5
    else:
        interval = (high-low) / 10
        star_num = math.ceil((score-low) / interval)
        full_star_num = int(star_num/2)
        half_star_num = star_num - full_star_num * 2
        return '<div class="star-wrapper">'+full_star * full_star_num + half_star * half_star_num + '</div>'


def _format_rate(score:float|None) -> str:
    return round(score, 1) if score is not None else 'Unknown'


def _format_authors(authors:list[str]) -> str:
    author_list = [a for a in authors]
    if len(author_list) <= 5:
        return ', '.join(author_list)
    return ', '.join(author_list[:3] + ['...'] + author_list[-2:])


def _format_affiliations(affiliations:list[str]|None) -> str:
    if affiliations is None:
        return 'Unknown Affiliation'
    shown = affiliations[:5]
    text = ', '.join(shown)
    if len(affiliations) > 5:
        text += ', ...'
    return text


def render_email(papers:list[Paper]) -> str:
    parts = []
    if len(papers) == 0 :
        return framework.replace('__CONTENT__', get_empty_html())

    for p in papers:
        #rate = get_stars(p.score)
        rate = _format_rate(p.score)
        authors = _format_authors(p.authors)
        affiliations = _format_affiliations(p.affiliations)
        parts.append(get_block_html(p.title, authors, rate, p.tldr, p.pdf_url, affiliations))

    content = '<br>' + '</br><br>'.join(parts) + '</br>'
    return framework.replace('__CONTENT__', content)


def render_markdown(papers:list[Paper]) -> str:
    """Render the daily digest as Markdown, for committing into the repo (no email needed).

    Produces a file like ``# Daily arXiv Digest - 2026-10-27`` followed by one section per paper,
    sorted by relevance (the order papers are given in). Mirrors render_email's content, in a
    format that renders nicely in GitHub's file browser.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    lines = [f"# Daily arXiv Digest - {today}", ""]

    if len(papers) == 0:
        lines.append("_No new papers today. Take a rest!_")
        return '\n'.join(lines) + '\n'

    for i, p in enumerate(papers, start=1):
        rate = _format_rate(p.score)
        authors = _format_authors(p.authors)
        affiliations = _format_affiliations(p.affiliations)
        lines.append(f"## {i}. {p.title}")
        lines.append("")
        lines.append(f"- **Authors:** {authors}")
        lines.append(f"- **Affiliations:** {affiliations}")
        lines.append(f"- **Relevance:** {rate}")
        lines.append(f"- **PDF:** [{p.pdf_url}]({p.pdf_url})")
        lines.append("")
        lines.append(f"**TLDR:** {p.tldr}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return '\n'.join(lines) + '\n'
