"""
Account Manager — Credential handling via 1Password or local fallback.

Provides warmup and keepalive patterns for auth context.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AccountManager:
    """Manages credentials from 1Password or local accounts.json."""
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        """
        Initialize account manager.
        
        Args:
            config: Configuration dict with credential_vault, use_1password, accounts_fallback_path
            base_path: Base path to job-agent directory
        """
        self.config = config
        self.base_path = base_path
        self.use_1password = config.get("use_1password", True)
        self.vault_name = config.get("credential_vault", "Agent Vault")
        self.fallback_path = base_path / config.get("accounts_fallback_path", "accounts.json")
        self._local_accounts = None
    
    def get_credential(self, account_type: str, field: str) -> Optional[str]:
        """
        Fetch a credential from 1Password or local fallback.
        
        Args:
            account_type: Type of account (linkedin, gmail, workday, etc)
            field: Field name (username, password, api_key, etc)
        
        Returns:
            Credential value or None if not found
        """
        if self.use_1password:
            return self._get_from_1password(account_type, field)
        else:
            return self._get_from_local(account_type, field)
    
    def _get_from_1password(self, account_type: str, field: str) -> Optional[str]:
        """Fetch credential from 1Password vault."""
        try:
            item_name = f"ApplyFlow_{account_type}"
            cmd = [
                "op",
                "read",
                f"op://{self.vault_name}/{item_name}/{field}",
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            
            return result.stdout.strip()
        
        except subprocess.CalledProcessError as e:
            logger.warning(
                f"Failed to fetch {account_type}.{field} from 1Password: {e}"
            )
            return None
        except FileNotFoundError:
            logger.warning("1Password CLI (op) not found. Install via: brew install 1password-cli")
            return None
    
    def _get_from_local(self, account_type: str, field: str) -> Optional[str]:
        """Fetch credential from local accounts.json."""
        accounts = self._load_local_accounts()
        
        if not accounts or account_type not in accounts:
            logger.warning(f"Account type '{account_type}' not found in {self.fallback_path}")
            return None
        
        account = accounts[account_type]
        if field not in account:
            logger.warning(f"Field '{field}' not found for account '{account_type}'")
            return None
        
        return account[field]
    
    def _load_local_accounts(self) -> Optional[Dict]:
        """Load accounts from local JSON file."""
        if self._local_accounts is not None:
            return self._local_accounts
        
        if not self.fallback_path.exists():
            logger.warning(f"Accounts file not found: {self.fallback_path}")
            return None
        
        try:
            with open(self.fallback_path) as f:
                self._local_accounts = json.load(f)
            return self._local_accounts
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load accounts file: {e}")
            return None
    
    def warmup_1password(self) -> bool:
        """
        Warmup 1Password session.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.use_1password:
            return True
        
        try:
            subprocess.run(
                ["op", "user", "get", "email"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            logger.info("1Password session warmed up")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning(f"1Password warmup failed: {e}")
            return False
    
    def keepalive_1password(self) -> bool:
        """
        Keep 1Password session alive (prevents timeout).
        
        Returns:
            True if successful, False otherwise
        """
        if not self.use_1password:
            return True
        
        try:
            subprocess.run(
                ["op", "vault", "list"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            logger.debug("1Password session kept alive")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning(f"1Password keepalive failed: {e}")
            return False


def create_accounts_template(path: Path) -> None:
    """Create a template accounts.json file."""
    template = {
        "linkedin": {
            "username": "your.email@gmail.com",
            "password": "your_password_here"
        },
        "gmail": {
            "username": "your.email@gmail.com",
            "password": "your_app_password_here"
        },
        "workday_company": {
            "username": "your_workday_username",
            "password": "your_workday_password"
        }
    }
    
    with open(path, "w") as f:
        json.dump(template, f, indent=2)
    
    logger.info(f"Created template accounts.json at {path}")
    logger.info("Fill in your credentials and ensure file permissions are 600")
