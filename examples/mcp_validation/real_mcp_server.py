"""
Real MCP Server Example

This demonstrates a working MCP server using the official SDK to validate
actual MCP protocol behavior and message formats.
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP

# Create FastMCP server
mcp_server = FastMCP("OpenMAS Validation Server")


@mcp_server.tool()
def analyze_text(text: str, analysis_type: str = "sentiment") -> Dict[str, Any]:
    """
    Analyze text using various analysis types.

    Args:
        text: The text to analyze
        analysis_type: Type of analysis (sentiment, length, words)
    """
    if analysis_type == "sentiment":
        # Simulate sentiment analysis
        score = 0.8 if "good" in text.lower() or "great" in text.lower() else 0.3
        return {
            "analysis_type": "sentiment",
            "score": score,
            "sentiment": "positive" if score > 0.5 else "negative",
            "confidence": 0.95,
            "text": text,
        }
    elif analysis_type == "length":
        return {
            "analysis_type": "length",
            "character_count": len(text),
            "word_count": len(text.split()),
            "text": text,
        }
    elif analysis_type == "words":
        words = text.split()
        return {
            "analysis_type": "words",
            "words": words,
            "unique_words": list(set(words)),
            "most_common": max(set(words), key=words.count) if words else "",
            "text": text,
        }
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")


@mcp_server.tool()
async def create_document(
    title: str, content: str, format: str = "txt"
) -> Dict[str, str]:
    """
    Create a temporary document with given content.

    Args:
        title: Document title
        content: Document content
        format: Document format (txt, md, json)
    """
    # Create temporary directory for documents
    temp_dir = Path(tempfile.gettempdir()) / "openmas_validation"
    temp_dir.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title}_{timestamp}.{format}"
    file_path = temp_dir / filename

    # Write content based on format
    if format == "json":
        import json

        content_data = {"title": title, "content": content, "created": timestamp}
        file_path.write_text(json.dumps(content_data, indent=2))
    elif format == "md":
        md_content = f"# {title}\n\n{content}\n\n*Created: {timestamp}*"
        file_path.write_text(md_content)
    else:  # txt
        txt_content = (
            f"{title}\n{'=' * len(title)}\n\n{content}\n\nCreated: {timestamp}"
        )
        file_path.write_text(txt_content)

    return {
        "status": "success",
        "file_path": str(file_path),
        "title": title,
        "format": format,
        "size_bytes": file_path.stat().st_size,
        "created": timestamp,
    }


@mcp_server.resource("config://server/info")
def get_server_info() -> str:
    """Get server configuration and capabilities."""
    info = {
        "name": "OpenMAS Validation Server",
        "version": "1.0.0",
        "protocol": "MCP",
        "capabilities": {
            "tools": ["analyze_text", "create_document"],
            "resources": ["config://server/info", "docs://list"],
            "prompts": ["analyze_prompt", "document_prompt"],
        },
        "supported_formats": ["txt", "md", "json"],
        "created": datetime.now().isoformat(),
    }
    import json

    return json.dumps(info, indent=2)


@mcp_server.resource("docs://list")
def list_documents() -> str:
    """List all created documents."""
    temp_dir = Path(tempfile.gettempdir()) / "openmas_validation"

    if not temp_dir.exists():
        return json.dumps({"documents": [], "count": 0})

    documents = []
    for file_path in temp_dir.glob("*"):
        if file_path.is_file():
            documents.append(
                {
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "path": str(file_path),
                }
            )

    result = {
        "documents": sorted(documents, key=lambda x: x["modified"], reverse=True),
        "count": len(documents),
        "directory": str(temp_dir),
    }

    import json

    return json.dumps(result, indent=2)


@mcp_server.prompt()
def analyze_prompt(text: str, focus: str = "general") -> str:
    """
    Generate a prompt for text analysis.

    Args:
        text: Text to analyze
        focus: Analysis focus (general, sentiment, style, content)
    """
    if focus == "sentiment":
        return f"""Please analyze the sentiment of the following text:

Text: "{text}"

Provide:
1. Overall sentiment (positive/negative/neutral)
2. Confidence score (0-1)
3. Key emotional indicators
4. Tone assessment
"""
    elif focus == "style":
        return f"""Please analyze the writing style of the following text:

Text: "{text}"

Analyze:
1. Writing style and tone
2. Target audience
3. Formality level
4. Key stylistic features
"""
    elif focus == "content":
        return f"""Please analyze the content and themes of the following text:

Text: "{text}"

Identify:
1. Main themes and topics
2. Key concepts mentioned
3. Subject matter expertise level
4. Content structure and organization
"""
    else:  # general
        return f"""Please provide a comprehensive analysis of the following text:

Text: "{text}"

Include analysis of:
1. Content and themes
2. Sentiment and tone
3. Writing style
4. Key insights or takeaways
"""


@mcp_server.prompt()
def document_prompt(title: str, purpose: str = "general") -> str:
    """
    Generate a prompt for document creation.

    Args:
        title: Document title
        purpose: Document purpose (report, summary, analysis, creative)
    """
    if purpose == "report":
        return f"""Create a structured report titled "{title}":

Structure:
1. Executive Summary
2. Introduction
3. Main Content (with subsections)
4. Conclusions
5. Recommendations

Requirements:
- Professional tone
- Clear headings and organization
- Factual and objective content
- Actionable insights
"""
    elif purpose == "summary":
        return f"""Create a concise summary document titled "{title}":

Include:
1. Key points overview
2. Main findings or insights
3. Critical information
4. Next steps or implications

Keep it:
- Brief but comprehensive
- Easy to scan and read
- Focused on essentials
"""
    elif purpose == "analysis":
        return f"""Create an analytical document titled "{title}":

Structure:
1. Analysis framework
2. Data or information examined
3. Methodology used
4. Findings and insights
5. Implications and recommendations

Approach:
- Systematic and thorough
- Evidence-based conclusions
- Clear reasoning process
"""
    else:  # creative
        return f"""Create a creative document titled "{title}":

Elements to include:
1. Engaging introduction
2. Creative content structure
3. Unique perspective or approach
4. Compelling narrative or flow

Style:
- Creative and engaging
- Original perspective
- Accessible language
- Memorable content
"""


# Export for use in integration examples
def get_mcp_server() -> FastMCP:
    """Get the configured MCP server instance."""
    return mcp_server


if __name__ == "__main__":
    print("Starting OpenMAS MCP Validation Server...")
    print("Available tools: analyze_text, create_document")
    print("Available resources: config://server/info, docs://list")
    print("Available prompts: analyze_prompt, document_prompt")

    # Run the server
    mcp_server.run()
