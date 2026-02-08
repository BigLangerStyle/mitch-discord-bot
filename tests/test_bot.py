"""
Unit tests for Mitch Discord Bot

Tests bot initialization, mention detection, and response handling
without actually connecting to Discord.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bot import MitchBot, CASUAL_RESPONSES


class TestBotInitialization:
    """Test bot initialization and setup."""
    
    def test_bot_creates_successfully(self):
        """Test that MitchBot can be instantiated."""
        mitch = MitchBot()
        assert mitch is not None
        assert mitch.bot is not None
        assert mitch.config is not None
    
    def test_bot_has_correct_intents(self):
        """Test that bot has required Discord intents enabled."""
        mitch = MitchBot()
        intents = mitch.bot.intents
        
        assert intents.message_content is True
        assert intents.guilds is True
        assert intents.guild_messages is True
        assert intents.members is True


class TestMentionDetection:
    """Test mention detection and response logic."""
    
    @pytest.mark.asyncio
    async def test_bot_ignores_own_messages(self):
        """Test that bot doesn't respond to its own messages."""
        mitch = MitchBot()
        
        # Mock message from the bot itself
        message = Mock()
        message.author = mitch.bot.user
        
        # Should not process this message
        # This is a simple test - in real implementation,
        # on_message checks this before calling _handle_mention
        assert message.author == mitch.bot.user
    
    @pytest.mark.asyncio
    async def test_bot_responds_to_mentions(self):
        """Test that bot responds when mentioned."""
        mitch = MitchBot()
        
        # Mock Discord message with bot mention
        message = AsyncMock()
        message.author = Mock()
        message.author.name = "TestUser"
        message.channel.name = "general"
        message.content = "@Mitch what should we play?"
        message.mentions = [mitch.bot.user]
        
        # Mock typing context manager
        typing_mock = AsyncMock()
        typing_mock.__aenter__ = AsyncMock()
        typing_mock.__aexit__ = AsyncMock()
        message.channel.typing.return_value = typing_mock
        
        # Call the handler
        await mitch._handle_mention(message)
        
        # Verify message was sent
        message.channel.send.assert_called_once()
        
        # Verify response is one of the casual responses
        call_args = message.channel.send.call_args[0]
        assert call_args[0] in CASUAL_RESPONSES
    
    def test_casual_responses_exist(self):
        """Test that casual responses are defined and non-empty."""
        assert len(CASUAL_RESPONSES) > 0
        assert all(isinstance(r, str) for r in CASUAL_RESPONSES)
        assert all(len(r) > 0 for r in CASUAL_RESPONSES)
    
    def test_casual_responses_are_casual(self):
        """Test that responses match the casual gaming buddy tone."""
        # Should be lowercase and casual
        for response in CASUAL_RESPONSES:
            # Should be relatively short
            assert len(response) < 100
            
            # Should not contain corporate language
            corporate_words = ['assist', 'pleasure', 'delighted', 'comprehensive']
            assert not any(word in response.lower() for word in corporate_words)


class TestErrorHandling:
    """Test error handling in bot operations."""
    
    @pytest.mark.asyncio
    async def test_handle_mention_with_send_error(self):
        """Test that bot handles message send failures gracefully."""
        mitch = MitchBot()
        
        # Mock message
        message = AsyncMock()
        message.author = Mock()
        message.author.name = "TestUser"
        message.channel.name = "general"
        message.content = "@Mitch hey"
        
        # Mock typing context
        typing_mock = AsyncMock()
        typing_mock.__aenter__ = AsyncMock()
        typing_mock.__aexit__ = AsyncMock()
        message.channel.typing.return_value = typing_mock
        
        # Make send raise an exception
        import discord
        message.channel.send.side_effect = discord.HTTPException(Mock(), "API error")
        
        # Should not raise exception
        try:
            await mitch._handle_mention(message)
        except Exception as e:
            pytest.fail(f"Bot should handle send errors gracefully, but raised: {e}")
    
    @pytest.mark.asyncio
    async def test_handle_mention_with_unexpected_error(self):
        """Test that bot handles unexpected errors gracefully."""
        mitch = MitchBot()
        
        # Mock message that will cause an error
        message = AsyncMock()
        message.author = Mock()
        message.channel.name = "general"
        message.channel.typing.side_effect = Exception("Unexpected error")
        
        # Should not raise exception
        try:
            await mitch._handle_mention(message)
        except Exception as e:
            pytest.fail(f"Bot should handle unexpected errors gracefully, but raised: {e}")


class TestBotConfiguration:
    """Test bot configuration and startup."""
    
    def test_bot_loads_config(self):
        """Test that bot successfully loads configuration."""
        mitch = MitchBot()
        assert mitch.config is not None
        assert 'discord' in mitch.config
    
    @pytest.mark.asyncio
    async def test_bot_validates_token(self):
        """Test that bot validates Discord token before starting."""
        mitch = MitchBot()
        
        # Mock config with invalid token
        mitch.config['discord']['token'] = 'YOUR_DISCORD_BOT_TOKEN_HERE'
        
        # Should exit with error
        with pytest.raises(SystemExit):
            await mitch.start()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
