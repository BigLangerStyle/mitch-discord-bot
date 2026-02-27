"""
Health monitoring endpoint for Mitch Discord Bot.

Provides HTTP endpoint for external monitoring systems (HomeSentry)
to check bot status, Ollama connectivity, and activity metrics.

Endpoint: http://localhost:8001/health
Response: JSON

Configuration (config.yaml):
    health.enabled: bool (default: true)
    health.host: str (default: "127.0.0.1")
    health.port: int (default: 8001)
"""

import os
import time
from datetime import datetime
from aiohttp import web
from logger import get_logger

logger = get_logger(__name__)


class HealthServer:
    """
    Lightweight HTTP health endpoint for external monitoring.

    Used by HomeSentry (and anything else) to check Mitch's status
    without relying on systemd alone.
    """

    def __init__(self, bot, ollama_client, config):
        """
        Initialize health server.

        Args:
            bot: discord.commands.Bot instance (i.e., MitchBot.bot)
            ollama_client: OllamaClient instance (reuses its health_check method)
            config: Full config dict
        """
        self.bot = bot
        self.ollama_client = ollama_client
        self.config = config
        self.start_time = time.time()
        self.runner = None

    async def start(self):
        """Start the health HTTP server."""
        health_config = self.config.get('health', {})

        if not health_config.get('enabled', True):
            logger.info("Health endpoint disabled in config, skipping")
            return

        host = health_config.get('host', '127.0.0.1')
        port = health_config.get('port', 8001)

        app = web.Application()
        app.router.add_get('/health', self.health_handler)

        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host, port)
        await site.start()

        logger.info(f"Health endpoint started on http://{host}:{port}/health")

    async def stop(self):
        """Stop the health HTTP server."""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Health endpoint stopped")

    async def health_handler(self, request):
        """
        Handle GET /health requests.

        Returns JSON with bot status, Discord connection, Ollama health,
        database info, and memory usage.
        """
        db_path = self.config.get('database', {}).get('path', 'data/mitch.db')

        # Database size
        try:
            db_size_mb = round(os.path.getsize(db_path) / 1024 / 1024, 2) if os.path.exists(db_path) else 0
        except Exception:
            db_size_mb = 0

        # Memory usage (Linux only via /proc/self/status)
        memory_mb = 0
        try:
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        # Format: "VmRSS:    12345 kB"
                        kb = int(line.split()[1])
                        memory_mb = round(kb / 1024, 2)
                        break
        except Exception:
            pass  # Windows dev machine or other non-Linux — default stays 0

        # Ollama health
        ollama_responsive = await self.ollama_client.health_check()

        response = {
            "status": "ok" if self.bot.is_ready() else "starting",
            "version": "1.2.4",
            "uptime_seconds": int(time.time() - self.start_time),
            "discord": {
                "connected": self.bot.is_ready(),
                "latency_ms": round(self.bot.latency * 1000) if self.bot.is_ready() else 0
            },
            "ollama": {
                "responsive": ollama_responsive,
                "last_check": datetime.utcnow().isoformat() + "Z",
                "model": self.config.get('ollama', {}).get('model', 'unknown')
            },
            "database": {
                "size_mb": db_size_mb,
                "path": db_path
            },
            "memory_mb": memory_mb
        }

        return web.json_response(response)
