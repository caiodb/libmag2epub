"""
EPUB builder module for converting scraped magazine content to Kindle format.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from io import BytesIO
from datetime import datetime
from typing import List, Optional
import httpx
from PIL import Image

from src.config import (
    RAW_DIR,
    EBOOK_DIR,
    PROJECT_ROOT,
    AUTHOR_NAME,
    LANGUAGE,
    COVER_MAX_WIDTH,
    COVER_MAX_HEIGHT,
    COVER_QUALITY,
    IMAGE_QUALITY,
    HTTP_TIMEOUT,
)

# Path to custom CSS stylesheet
EPUB_CSS_PATH = PROJECT_ROOT / "epub_styles.css"


class EpubBuilder:
    """Builds EPUB files from scraped magazine content."""
    
    def __init__(self, issue_name: str):
        self.issue_name = issue_name
        self.raw_dir = RAW_DIR / issue_name
        self.build_dir = RAW_DIR / f"{issue_name}_build_temp"
        self.cover_path = self.build_dir / "cover.jpg"
        self.output_file: Optional[Path] = None
    
    def build(self) -> Optional[Path]:
        """
        Build the EPUB file from scraped content.
        
        Returns:
            Optional[Path]: Path to the generated EPUB file, or None if build failed
        """
        # Validation: Check if scraper actually ran
        if not self.raw_dir.exists():
            print(f"ERROR: Raw directory not found at {self.raw_dir}. Did you run the scrape script?")
            return None
        
        # Check if output already exists
        clean_title = self._get_clean_title()
        self.output_file = EBOOK_DIR / f"{clean_title} ({AUTHOR_NAME}).epub"
        
        if self.output_file.exists():
            print(f"WARNING: EPUB already exists at {self.output_file}. Will overwrite.")
        
        try:
            # Clean and create build directory
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            self.build_dir.mkdir(parents=True)
            
            # Process cover image
            self._process_cover()
            
            # Process articles
            self._process_articles()
            
            # Build EPUB with pandoc
            success = self._build_epub(clean_title)
            
            if success:
                print(f"SUCCESS! EPUB generated: {self.output_file}")
                return self.output_file
            else:
                return None
                
        except Exception as e:
            print(f"ERROR building EPUB: {e}")
            return None
        finally:
            # Always cleanup
            self._cleanup()
    
    def _get_clean_title(self) -> str:
        """Generate a clean title from the issue name."""
        return self.issue_name.replace('-', ' ').title().replace('Edicao', 'Edição')
    
    def _process_cover(self) -> None:
        """Optimize cover image for Kindle."""
        cover_source = self.raw_dir / "cover.jpg"
        
        if not cover_source.exists():
            print("WARNING: No cover image found")
            return
        
        try:
            with Image.open(cover_source) as img:
                img = img.convert("RGB")
                img.thumbnail((COVER_MAX_WIDTH, COVER_MAX_HEIGHT), Image.Resampling.LANCZOS)
                img.save(self.cover_path, "JPEG", quality=COVER_QUALITY, optimize=True)
            print("✓ Cover optimized")
        except Exception as e:
            print(f"Cover optimization error: {e}")
            # Fallback: copy original
            shutil.copy(cover_source, self.cover_path)
    
    def _process_articles(self) -> None:
        """Process markdown articles and convert WebP images."""
        print(f"--- Processing Articles from {self.raw_dir.name} ---")
        
        md_files = sorted(self.raw_dir.glob("*.md"))
        
        for md_path in md_files:
            try:
                content = md_path.read_text(encoding="utf-8")
                
                # Download and convert WebP images
                content = self._convert_webp_images(content)
                
                # Save processed content to build directory
                (self.build_dir / md_path.name).write_text(content, encoding="utf-8")
                print(f"✓ Processed: {md_path.name}")
                
            except Exception as e:
                print(f"  ! Error processing {md_path.name}: {e}")
    
    def _convert_webp_images(self, content: str) -> str:
        """
        Find WebP images in markdown and convert to JPEG.
        
        Args:
            content: Markdown content
            
        Returns:
            str: Content with WebP URLs replaced by local JPEG paths
        """
        urls = re.findall(r'\((https?://[^\s)]+\.webp)\)', content)
        
        for url in urls:
            try:
                local_name = f"img_{hash(url) & 0xffffffff}.jpg"
                local_path = self.build_dir / local_name
                
                # Download with timeout
                resp = httpx.get(url, timeout=HTTP_TIMEOUT)
                resp.raise_for_status()
                
                # Convert WebP to JPEG
                with Image.open(BytesIO(resp.content)) as img:
                    img.convert("RGB").save(local_path, "JPEG", quality=IMAGE_QUALITY)
                
                # Replace URL in content
                content = content.replace(url, local_name)
                print(f"  ✓ Converted WebP: {url[:50]}...")
                
            except httpx.TimeoutException:
                print(f"  ! Timeout downloading image: {url[:50]}...")
            except Exception as e:
                print(f"  ! Failed to process image {url[:50]}...: {e}")
        
        return content
    
    def _build_epub(self, clean_title: str) -> bool:
        """
        Run pandoc to build the EPUB file.
        
        Args:
            clean_title: Cleaned title for metadata
            
        Returns:
            bool: True if build succeeded, False otherwise
        """
        print("--- Executing Pandoc ---")
        
        # Ensure ebook directory exists
        EBOOK_DIR.mkdir(parents=True, exist_ok=True)
        
        # Copy CSS file to build directory if it exists
        css_in_build = None
        if EPUB_CSS_PATH.exists():
            css_in_build = self.build_dir / "epub_styles.css"
            shutil.copy(EPUB_CSS_PATH, css_in_build)
            print("✓ Custom CSS stylesheet added")
        else:
            print("! Custom CSS not found, using default pandoc styles")
        
        # Build pandoc command
        cmd = [
            "pandoc",
            "-f", "commonmark",
            "-t", "epub3",
            "--toc", "--toc-depth=1",
            "--epub-chapter-level=1",
            "--standalone",
            "-o", str(self.output_file),
            "--metadata", f"title={clean_title}",
            "--metadata", f"author={AUTHOR_NAME}",
            "--metadata", f"language={LANGUAGE}",
            "--metadata", f"date={datetime.now().strftime('%Y-%m-%d')}",
            "--metadata", "cover-image=cover.jpg",
            f"--resource-path={self.build_dir}"
        ]
        
        # Add CSS stylesheet if available
        if css_in_build and css_in_build.exists():
            cmd.extend(["--css", "epub_styles.css"])
        
        # Add cover image if exists
        if self.cover_path.exists():
            cmd.append("--epub-cover-image=cover.jpg")
        
        # Add markdown files
        md_files = sorted([f.name for f in self.build_dir.glob("*.md")])
        if not md_files:
            print("ERROR: No markdown files to build")
            return False
        
        cmd.extend(md_files)
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                cwd=str(self.build_dir)
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"PANDOC ERROR: {e.stderr}")
            return False
        except FileNotFoundError:
            print("ERROR: pandoc not found. Please install pandoc.")
            return False
    
    def _cleanup(self) -> None:
        """Clean up temporary build directory."""
        if self.build_dir.exists():
            try:
                shutil.rmtree(self.build_dir)
                print("✓ Cleanup complete")
            except Exception as e:
                print(f"  ! Cleanup warning: {e}")


# Convenience function
def build_epub(issue_name: str) -> Optional[Path]:
    """
    Build an EPUB from scraped magazine content.
    
    Args:
        issue_name: The edition slug (e.g., 'edicao-18')
        
    Returns:
        Optional[Path]: Path to the generated EPUB file, or None if build failed
    """
    builder = EpubBuilder(issue_name)
    return builder.build()
