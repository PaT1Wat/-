"""
Test cases for the Supabase client module.

These tests verify that:
1. The client module loads correctly
2. Environment variable validation works
3. Client creation functions behave as expected

Note: These are unit tests that mock the Supabase client.
For integration tests against a real Supabase instance, 
set up proper environment variables and run separately.
"""

import pytest
from unittest.mock import patch, MagicMock
import os


class TestSupabaseClientModule:
    """Tests for the Supabase client configuration module."""
    
    def test_module_imports(self):
        """Test that the supabase_client module can be imported."""
        # Clear any cached imports
        import importlib
        import sys
        
        # Remove cached module if exists
        if 'app.config.supabase_client' in sys.modules:
            del sys.modules['app.config.supabase_client']
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-anon-key',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-service-role-key'
        }):
            # Import should not raise
            from app.config import supabase_client
            assert supabase_client is not None
    
    def test_missing_env_var_raises_error(self):
        """Test that missing required env vars raise ValueError."""
        import importlib
        import sys
        
        # Clear cache
        if 'app.config.supabase_client' in sys.modules:
            del sys.modules['app.config.supabase_client']
        
        # Remove any existing env vars
        with patch.dict(os.environ, {}, clear=True):
            from app.config.supabase_client import _get_env_var
            
            with pytest.raises(ValueError) as exc_info:
                _get_env_var("SUPABASE_URL", required=True)
            
            assert "SUPABASE_URL" in str(exc_info.value)
    
    def test_optional_env_var_returns_none(self):
        """Test that optional env vars return None when missing."""
        import importlib
        import sys
        
        # Clear cache
        if 'app.config.supabase_client' in sys.modules:
            del sys.modules['app.config.supabase_client']
        
        with patch.dict(os.environ, {}, clear=True):
            from app.config.supabase_client import _get_env_var
            
            result = _get_env_var("OPTIONAL_VAR", required=False)
            assert result is None
    
    def test_get_supabase_client_with_mock(self):
        """Test get_supabase_client with mocked supabase package."""
        import importlib
        import sys
        
        # Clear cache
        for mod in list(sys.modules.keys()):
            if 'supabase_client' in mod:
                del sys.modules[mod]
        
        # Mock the supabase package
        mock_client = MagicMock()
        mock_create_client = MagicMock(return_value=mock_client)
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-anon-key',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-service-role-key'
        }):
            with patch.dict(sys.modules, {'supabase': MagicMock(
                create_client=mock_create_client,
                Client=MagicMock
            )}):
                from app.config.supabase_client import get_supabase_client
                
                # Clear the lru_cache
                get_supabase_client.cache_clear()
                
                client = get_supabase_client()
                
                # Verify create_client was called with correct args
                mock_create_client.assert_called_once_with(
                    'https://test.supabase.co',
                    'test-anon-key'
                )
    
    def test_get_supabase_admin_client_with_mock(self):
        """Test get_supabase_admin_client with mocked supabase package."""
        import importlib
        import sys
        
        # Clear cache
        for mod in list(sys.modules.keys()):
            if 'supabase_client' in mod:
                del sys.modules[mod]
        
        # Mock the supabase package
        mock_client = MagicMock()
        mock_create_client = MagicMock(return_value=mock_client)
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-anon-key',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-service-role-key'
        }):
            with patch.dict(sys.modules, {'supabase': MagicMock(
                create_client=mock_create_client,
                Client=MagicMock
            )}):
                from app.config.supabase_client import get_supabase_admin_client
                
                # Clear the lru_cache
                get_supabase_admin_client.cache_clear()
                
                client = get_supabase_admin_client()
                
                # Verify create_client was called with service role key
                mock_create_client.assert_called_once_with(
                    'https://test.supabase.co',
                    'test-service-role-key'
                )


class TestSupabaseExampleFunctions:
    """Tests for the example Supabase operation functions."""
    
    def test_fetch_items_example(self):
        """Test the fetch_items_example function with mocked client."""
        import sys
        
        # Clear cache
        for mod in list(sys.modules.keys()):
            if 'supabase_client' in mod:
                del sys.modules[mod]
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.data = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]
        
        # Create mock client chain
        mock_table = MagicMock()
        mock_table.select.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = mock_response
        
        mock_client = MagicMock()
        mock_client.table.return_value = mock_table
        
        mock_create_client = MagicMock(return_value=mock_client)
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-anon-key',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-service-role-key'
        }):
            with patch.dict(sys.modules, {'supabase': MagicMock(
                create_client=mock_create_client,
                Client=MagicMock
            )}):
                from app.config.supabase_client import fetch_items_example, get_supabase_client
                
                # Clear cache
                get_supabase_client.cache_clear()
                
                result = fetch_items_example("items", 10)
                
                assert result == [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ]
                mock_client.table.assert_called_with("items")
    
    def test_insert_item_example(self):
        """Test the insert_item_example function with mocked client."""
        import sys
        
        # Clear cache
        for mod in list(sys.modules.keys()):
            if 'supabase_client' in mod:
                del sys.modules[mod]
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "name": "New Item"}]
        
        # Create mock client chain
        mock_table = MagicMock()
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = mock_response
        
        mock_client = MagicMock()
        mock_client.table.return_value = mock_table
        
        mock_create_client = MagicMock(return_value=mock_client)
        
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-anon-key',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-service-role-key'
        }):
            with patch.dict(sys.modules, {'supabase': MagicMock(
                create_client=mock_create_client,
                Client=MagicMock
            )}):
                from app.config.supabase_client import insert_item_example, get_supabase_client
                
                # Clear cache
                get_supabase_client.cache_clear()
                
                test_data = {"name": "New Item"}
                result = insert_item_example("items", test_data)
                
                assert result == [{"id": 1, "name": "New Item"}]
                mock_table.insert.assert_called_with(test_data)
