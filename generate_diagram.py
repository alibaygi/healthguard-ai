"""Generate a beautiful architecture diagram PNG for HealthGuard AI presentation."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(1, 1, figsize=(24, 16))
fig.patch.set_facecolor('#0f1923')
ax.set_xlim(0, 24)
ax.set_ylim(0, 16)
ax.set_aspect('equal')
ax.axis('off')

# ── Color Palette ──
C_BG = '#0f1923'
C_CARD = '#1a2733'
C_BORDER_BLUE = '#4a90d9'
C_BORDER_GREEN = '#48bb78'
C_BORDER_ORANGE = '#ed8936'
C_BORDER_PURPLE = '#9f7aea'
C_BORDER_RED = '#fc8181'
C_BORDER_TEAL = '#38b2ac'
C_TEXT_DIM = '#a0aec0'
C_HIGHLIGHT = '#63b3ed'

def draw_card(ax, x, y, w, h, title, items, border_color, icon=''):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                         facecolor=C_CARD, edgecolor=border_color, linewidth=2.5, alpha=0.95)
    ax.add_patch(box)
    title_text = f"{icon}  {title}" if icon else title
    ax.text(x + w/2, y + h - 0.35, title_text, ha='center', va='top',
            fontsize=12, fontweight='bold', color='white', family='sans-serif')
    for i, item in enumerate(items):
        ax.text(x + w/2, y + h - 0.8 - i*0.38, item, ha='center', va='top',
                fontsize=9, color=C_TEXT_DIM, family='sans-serif')

def draw_arrow(ax, x1, y1, x2, y2, color, style='-|>', lw=2.0, ls='-'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                              connectionstyle='arc3,rad=0', linestyle=ls))

def draw_label(ax, x, y, text, color=C_TEXT_DIM, fontsize=8):
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            color=color, family='sans-serif',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=C_BG, edgecolor='none', alpha=0.9))

# ══════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════
ax.text(12, 15.4, 'HealthGuard AI', ha='center', va='center',
        fontsize=32, fontweight='bold', color='white', family='sans-serif')
ax.text(12, 14.85, 'TikTok / YouTube Health Claims Auditor  —  Full Pipeline Architecture',
        ha='center', va='center', fontsize=13, color=C_TEXT_DIM, family='sans-serif')

# ══════════════════════════════════════════════════
# LEFT COLUMN: INPUT + FASTAPI (stacked vertically)
# ══════════════════════════════════════════════════
draw_card(ax, 0.4, 12.2, 3.2, 1.8, 'INPUT', ['TikTok / YouTube', 'Video URL'], C_BORDER_TEAL, '🎬')
draw_card(ax, 0.4, 9.0, 3.2, 2.5, 'FastAPI Server', ['POST /audit', 'Validate URL', 'Generate Session ID', 'Prepare Initial State'], C_BORDER_GREEN, '⚡')

# ══════════════════════════════════════════════════
# CENTER: LANGGRAPH WORKFLOW (big dashed box)
# ══════════════════════════════════════════════════
wf_box = FancyBboxPatch((4.0, 4.2), 9.5, 9.6, boxstyle="round,pad=0.25",
                         facecolor='none', edgecolor=C_BORDER_BLUE, linewidth=1.5, linestyle='--', alpha=0.4)
ax.add_patch(wf_box)
ax.text(8.75, 13.5, '🔄  LangGraph StateGraph Workflow', ha='center', va='center',
        fontsize=11, color=C_HIGHLIGHT, family='sans-serif', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor=C_BG, edgecolor=C_BORDER_BLUE, alpha=0.7))

# Node 1: Indexer
draw_card(ax, 4.5, 9.8, 4.0, 3.3, 'Node 1: Indexer', [
    '① Download Video (yt-dlp)',
    '② Upload → Azure Video Indexer',
    '③ Poll Until Processed',
    '④ Extract Transcript',
    '⑤ Extract OCR Text'
], C_BORDER_BLUE, '📥')

# Node 2: Auditor
draw_card(ax, 4.5, 5.5, 4.0, 3.5, 'Node 2: Auditor', [
    '① RAG → Azure AI Search',
    '② Retrieve Health Guidelines',
    '③ GPT-4o Analysis',
    '④ Parse Violations',
    '⑤ Generate Health Report'
], C_BORDER_BLUE, '🔍')

# State box
st_box = FancyBboxPatch((9.5, 6.5), 3.6, 5.5, boxstyle="round,pad=0.12",
                         facecolor='#1e3a4c', edgecolor=C_HIGHLIGHT, linewidth=1.5, alpha=0.7)
ax.add_patch(st_box)
ax.text(11.3, 11.7, '📦 VideoAuditState', ha='center', va='center',
        fontsize=10, fontweight='bold', color='white', family='sans-serif')
state_fields = [
    'video_url', 'video_id', 'transcript',
    'ocr_text', 'video_metadata',
    'compliance_results',
    'final_status', 'final_report',
    'errors'
]
for i, field in enumerate(state_fields):
    ax.text(11.3, 11.25 - i*0.45, f'• {field}', ha='center', va='center',
            fontsize=8, color=C_TEXT_DIM, family='sans-serif')

# ══════════════════════════════════════════════════
# RIGHT COLUMN: AZURE SERVICES (stacked)
# ══════════════════════════════════════════════════
az_x = 14.5
draw_card(ax, az_x, 12.0, 4.0, 1.8, 'Azure Identity', ['Service Principal', 'ARM Token Exchange'], C_BORDER_ORANGE, '🔐')
draw_card(ax, az_x, 9.5, 4.0, 2.0, 'Azure Video Indexer', ['Speech-to-Text', 'OCR Text Extraction', 'Video Processing'], C_BORDER_ORANGE, '🎥')
draw_card(ax, az_x, 7.0, 4.0, 2.0, 'Azure AI Search', ['Vector Store (RAG)', 'Semantic Search', 'Health Guidelines Index'], C_BORDER_ORANGE, '🔎')
draw_card(ax, az_x, 4.5, 4.0, 2.0, 'Azure OpenAI', ['GPT-4o (LLM Analysis)', 'text-embedding-3-small'], C_BORDER_ORANGE, '🧠')

# Far right column
az2_x = 19.2
draw_card(ax, az2_x, 10.5, 4.0, 2.0, 'Azure Monitor', ['OpenTelemetry', 'Application Insights', 'Request Tracing'], C_BORDER_ORANGE, '📊')
draw_card(ax, az2_x, 7.5, 4.0, 2.5, 'Knowledge Base', ['FTC Health Claims', 'Guidance (MD)', '', 'WHO/FDA Misinfo', 'Guidelines (MD)'], C_BORDER_PURPLE, '📚')

# ══════════════════════════════════════════════════
# BOTTOM: OUTPUT
# ══════════════════════════════════════════════════
draw_card(ax, 4.5, 0.8, 9.0, 2.8, 'Health Audit Report', [
    '✅ PASS  /  ❌ FAIL',
    'Violation Categories & Severity Ratings',
    'Evidence-Based Analysis with Source Citations',
    'Detailed Natural Language Summary'
], C_BORDER_RED, '📋')

# ══════════════════════════════════════════════════
# ARROWS — Main Flow (thick, solid)
# ══════════════════════════════════════════════════
# Input → FastAPI
draw_arrow(ax, 2.0, 12.2, 2.0, 11.55, C_BORDER_TEAL, '-|>', 3)

# FastAPI → Node 1
draw_arrow(ax, 3.6, 10.5, 4.5, 11.0, C_BORDER_GREEN, '-|>', 2.5)

# Node 1 → Node 2
draw_arrow(ax, 6.5, 9.8, 6.5, 9.05, C_BORDER_BLUE, '-|>', 3)
draw_label(ax, 7.6, 9.4, 'transcript + ocr_text', C_HIGHLIGHT, 8)

# Node 1 ↔ State
draw_arrow(ax, 8.5, 11.0, 9.5, 10.5, C_HIGHLIGHT, '-|>', 1.5, '--')

# Node 2 ↔ State
draw_arrow(ax, 8.5, 7.2, 9.5, 7.8, C_HIGHLIGHT, '-|>', 1.5, '--')

# Node 2 → Output
draw_arrow(ax, 6.5, 5.5, 7.5, 3.6, C_BORDER_BLUE, '-|>', 2.5)

# ══════════════════════════════════════════════════
# ARROWS — Azure connections (dashed)
# ══════════════════════════════════════════════════
# Indexer → Azure Identity
draw_arrow(ax, 8.5, 12.5, 14.5, 13.0, C_BORDER_ORANGE, '-|>', 1.3, '--')
draw_label(ax, 11.5, 13.0, 'auth token', C_BORDER_ORANGE, 7.5)

# Indexer → Video Indexer
draw_arrow(ax, 8.5, 10.5, 14.5, 10.5, C_BORDER_ORANGE, '-|>', 1.3, '--')
draw_label(ax, 11.5, 10.8, 'upload + extract', C_BORDER_ORANGE, 7.5)

# Auditor → AI Search
draw_arrow(ax, 8.5, 7.5, 14.5, 8.0, C_BORDER_ORANGE, '-|>', 1.3, '--')
draw_label(ax, 11.5, 8.1, 'RAG query', C_BORDER_ORANGE, 7.5)

# Auditor → OpenAI
draw_arrow(ax, 8.5, 6.2, 14.5, 5.5, C_BORDER_ORANGE, '-|>', 1.3, '--')
draw_label(ax, 11.5, 6.1, 'LLM analysis', C_BORDER_ORANGE, 7.5)

# KB → AI Search
draw_arrow(ax, 19.2, 8.5, 18.5, 8.2, C_BORDER_PURPLE, '-|>', 1.3, '--')
draw_label(ax, 18.85, 8.6, 'indexed chunks', C_BORDER_PURPLE, 7)

# Monitor dashed to API
draw_arrow(ax, 19.2, 11.5, 3.6, 10.5, C_BORDER_ORANGE, '-|>', 0.8, ':')
draw_label(ax, 12.0, 11.5, 'traces all HTTP requests', '#ed8936', 7)

# Output final
draw_arrow(ax, 9.0, 0.8, 9.0, 0.3, C_BORDER_RED, '-|>', 2.5)
ax.text(12, 0.15, '→  JSON API Response  /  CLI Report  /  Dashboard',
        ha='center', va='center', fontsize=10, color=C_BORDER_RED, family='sans-serif')

# ── Tech Stack Footer ──
ax.text(12, -0.3, 'Python 3.12  •  LangGraph  •  LangChain  •  FastAPI  •  yt-dlp  •  Azure Cloud  •  OpenTelemetry',
        ha='center', va='center', fontsize=9, color=C_TEXT_DIM, family='sans-serif', alpha=0.5)

plt.tight_layout()
output_path = '/Users/ali/Documents/Educational/nlp_langchain_llms_2026/llmops_with_Azure_Tiktok/ComplianceQAPipeline/healthguard_architecture.png'
fig.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=C_BG, pad_inches=0.4)
plt.close()
print(f"✅ Diagram saved to: {output_path}")
