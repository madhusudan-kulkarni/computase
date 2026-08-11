"""Computase MCP server and command-line entry point."""

import argparse
from collections.abc import Sequence

from mcp.server.mcpserver import MCPServer

from computase import __version__

server = MCPServer(
    "computase",
    title="Computase",
    description=(
        "Local DNA and RNA sequence utilities: sequence summaries, reverse complements, "
        "translation, candidate ORF enumeration, and motif scanning."
    ),
    version=__version__,
)


def _register_tools() -> None:
    from .tools import register_tools

    register_tools(server)


def build_parser() -> argparse.ArgumentParser:
    """Build the Computase server command-line parser."""
    parser = argparse.ArgumentParser(description="Computase MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="MCP transport (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP bind host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP bind port (default: 8000)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Run Computase over stdio or locally bound streamable HTTP."""
    args = build_parser().parse_args(argv)
    if args.transport == "streamable-http":
        server.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        server.run(transport="stdio")


_register_tools()


if __name__ == "__main__":
    main()
