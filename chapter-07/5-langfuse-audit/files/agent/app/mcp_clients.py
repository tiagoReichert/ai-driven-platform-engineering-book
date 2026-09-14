"""Connect the runtime to the two MCP servers used by the specialists.

This module starts both agent-owned connections once at runtime and exposes the
discovered tool lists to the coordinator. The connection details live beside
each agent in ``diagnostics_agent.py`` and ``gitops_agent.py``.
"""

from __future__ import annotations

import os
import logging

from strands.tools.mcp import MCPClient

from .settings import settings
from .diagnostics_agent import connect as connect_cluster
from .gitops_agent import connect as connect_gitops

logger = logging.getLogger("agent.mcp")

_cluster_client: MCPClient | None = None
_cluster_tools: list = []
_gitops_client: MCPClient | None = None
_gitops_tools: list = []


def start_clients() -> None:
    """Connect once at startup and cache each server's tool list."""
    global _gitops_client, _gitops_tools, _cluster_client, _cluster_tools
    # The Diagnostics Agent owns the upstream Kubernetes MCP connection.
    _cluster_client, _cluster_tools = connect_cluster(os.environ['MCP_CLUSTER_URL'])

    # GitOps is optional until Lab 3's gateway is deployed.
    if not settings.mcp_gitops_url:
        return

    # The GitOps Agent owns the GitOps MCP connection.
    token = os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']
    _gitops_client, _gitops_tools = connect_gitops(settings.mcp_gitops_url, token)


def stop_clients() -> None:
    """Stop all MCP clients. Called at shutdown."""
    global _gitops_client, _cluster_client
    if _cluster_client is not None:
        _cluster_client.stop(None, None, None)
        _cluster_client = None
    if _gitops_client is not None:
        try:
            _gitops_client.stop(None, None, None)
        except Exception as e:
            logger.warning("error stopping gitops client: %s", e)
        _gitops_client = None


def gitops_tools() -> list:
    """Return the list of MCPAgentTool instances exposed by gitops-mcp."""
    return list(_gitops_tools)


def cluster_tools() -> list:
    return list(_cluster_tools)
