"""
Sent manager module for handling email workflow and archiving.
"""

import shutil
from pathlib import Path
from typing import Set, List

from src.config import (
    EBOOK_DIR,
    SENT_DIR,
    SENT_HISTORY_FILE,
)
from src.mailer import Mailer


class SentManager:
    """Manages sent EPUB history and archiving."""
    
    def __init__(self):
        self.ebook_dir = EBOOK_DIR
        self.sent_dir = SENT_DIR
        self.history_file = SENT_HISTORY_FILE
        self.mailer = Mailer()
        
        # Ensure directories exist
        self.ebook_dir.mkdir(parents=True, exist_ok=True)
        self.sent_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self) -> None:
        """Run the full sent management workflow."""
        print("=" * 60)
        print("STARTING SENT MANAGER")
        print("=" * 60)
        
        # Get history and available EPUBs
        sent_books = self._get_sent_history()
        all_epubs = self._get_available_epubs()
        
        if not all_epubs:
            print("No EPUB files found in the ebook directory.")
            return
        
        print(f"Checking {len(all_epubs)} files...")
        
        # Process each EPUB
        processed = 0
        failed = 0
        archived = 0
        
        for epub_path in all_epubs:
            filename = epub_path.name
            
            if filename in sent_books:
                # Already sent, just archive
                print(f"-> {filename} already in history. Moving to archive...")
                self._archive_epub(epub_path)
                archived += 1
            else:
                # New book, send and archive
                print(f"-> New book detected: {filename}. Sending...")
                
                if self._send_and_archive(epub_path):
                    processed += 1
                else:
                    failed += 1
        
        print(f"\n{'='*60}")
        print(f"SENT MANAGER COMPLETE")
        print(f"  Sent & Archived: {processed}")
        print(f"  Already Sent (archived): {archived}")
        print(f"  Failed: {failed}")
        print(f"{'='*60}")
    
    def _get_sent_history(self) -> Set[str]:
        """
        Read the list of already sent EPUBs.
        
        Returns:
            Set[str]: Set of sent filenames
        """
        if not self.history_file.exists():
            return set()
        
        try:
            content = self.history_file.read_text(encoding="utf-8")
            return set(line.strip() for line in content.splitlines() if line.strip())
        except Exception as e:
            print(f"Warning: Could not read history file: {e}")
            return set()
    
    def _save_to_history(self, filename: str) -> None:
        """
        Add a filename to the sent history.
        
        Args:
            filename: Name of the EPUB file
        """
        try:
            with open(self.history_file, "a", encoding="utf-8") as f:
                f.write(f"{filename}\n")
        except Exception as e:
            print(f"Warning: Could not save to history: {e}")
    
    def _get_available_epubs(self) -> List[Path]:
        """
        Get list of available EPUB files.
        
        Returns:
            List[Path]: List of EPUB file paths
        """
        return list(self.ebook_dir.glob("*.epub"))
    
    def _send_and_archive(self, epub_path: Path) -> bool:
        """
        Send an EPUB and archive it if successful.
        
        Args:
            epub_path: Path to the EPUB file
            
        Returns:
            bool: True if successful
        """
        success = self.mailer.send_epub(epub_path)
        
        if success:
            # Save to history
            self._save_to_history(epub_path.name)
            
            # Move to sent directory
            self._archive_epub(epub_path)
            print(f"✓ {epub_path.name} sent and archived.")
            return True
        else:
            print(f"X Failed to send {epub_path.name}. Keeping in ebook folder for retry.")
            return False
    
    def _archive_epub(self, epub_path: Path) -> None:
        """
        Move an EPUB file to the sent archive.
        
        Args:
            epub_path: Path to the EPUB file
        """
        try:
            destination = self.sent_dir / epub_path.name
            
            # If file already exists in sent, remove it first
            if destination.exists():
                destination.unlink()
            
            shutil.move(str(epub_path), str(destination))
        except Exception as e:
            print(f"  ! Warning: Could not archive {epub_path.name}: {e}")


# Convenience function
def run_sent_manager() -> None:
    """Run the sent manager workflow."""
    manager = SentManager()
    manager.run()
