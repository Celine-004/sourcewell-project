"""
Medical Content Ingestion System

Processes curated medical content from markdown files with YAML frontmatter,
validates metadata, generates Vancouver-style citations, and ingests approved
content into Weaviate knowledge base with complete audit trail.
"""
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="<frozen runpy>")

import os
import sys
import yaml
import json
import shutil
import hashlib
import weaviate
from pathlib import Path
from datetime import datetime
import weaviate.classes as wvc
from typing import Dict, List, Optional, Tuple
from .config import WEAVIATE_HTTP_PORT, WEAVIATE_GRPC_PORT

class MedicalContentIngester:
    
    def __init__(self):
        """Initialize content ingester with paths and Weaviate v4 connection."""
        self.client = weaviate.connect_to_local(port=WEAVIATE_HTTP_PORT, grpc_port=WEAVIATE_GRPC_PORT)
        self.root_path = Path(__file__).resolve().parents[1]
        self.medical_content_base = self.root_path / "data" / "medical_content"
        self.guidelines_dir = self.medical_content_base / "guidelines"
        self.abstracts_dir = self.medical_content_base / "research_abstracts"
        self.archived_dir = self.medical_content_base / "processed" / "archived"
        self.validation_reports_dir = self.medical_content_base / "processed" / "validation_reports"
        self.state_file = self.validation_reports_dir / "ingestion_state.json"
        
        # Ensure processing directories exist
        self.archived_dir.mkdir(parents=True, exist_ok=True)
        self.validation_reports_dir.mkdir(parents=True, exist_ok=True)
    
    def close(self):
        """Close Weaviate connection."""
        try:
            self.client.close()
        except Exception:
            pass
    
    def load_ingestion_state(self) -> Dict:
        """Load previous ingestion state to avoid re-processing unchanged files."""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Warning: Could not load ingestion state: {e}")
            return {}
    
    def save_ingestion_state(self, state: Dict) -> None:
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save ingestion state: {e}")
    
    def calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file content for change detection."""
        try:
            return hashlib.sha256(filepath.read_bytes()).hexdigest()
        except Exception as e:
            print(f"Warning: Could not calculate hash for {filepath}: {e}")
            return ""
    
    def generate_vancouver_citation(self, metadata: Dict) -> str:
        content_type = metadata.get('content_type', '')
        
        if content_type == 'MedicalGuideline':
            parts = []
            if metadata.get('organization'): 
                parts.append(metadata['organization'])
            if metadata.get('title'): 
                parts.append(metadata['title'])
            if metadata.get('publication_year'): 
                parts.append(str(metadata['publication_year']))
            if metadata.get('section'): 
                parts.append(f"Section: {metadata['section']}")
            if metadata.get('page_reference'): 
                parts.append(f"pp. {metadata['page_reference']}")
            if metadata.get('url'): 
                parts.append(f"Available from: {metadata['url']}")
            if metadata.get('accessed_date'): 
                parts.append(f"[accessed {metadata['accessed_date']}]")
            
            return ". ".join(parts) + "."
            
        elif content_type == 'ResearchAbstract':
            parts = []
            authors = metadata.get('authors', [])
            if authors: 
                if len(authors) <= 6:
                    parts.append(", ".join(authors))
                else:
                    parts.append(", ".join(authors[:6]) + ", et al")
            
            if metadata.get('title'): 
                parts.append(metadata['title'])
            if metadata.get('journal'): 
                parts.append(metadata['journal'])
            if metadata.get('publication_year'): 
                parts.append(str(metadata['publication_year']))
            
            citation_end = []
            if metadata.get('pmid'): 
                citation_end.append(f"PMID: {metadata['pmid']}")
            if metadata.get('doi'): 
                citation_end.append(f"doi: {metadata['doi']}")
            
            citation = ". ".join(parts)
            if citation_end:
                citation += ". " + ". ".join(citation_end)
            
            return citation + "."
        
        return "Citation format not supported for this content type."
    
    def parse_markdown_file(self, filepath: Path) -> Optional[Dict]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                raise ValueError("Missing YAML frontmatter (requires --- delimiters)")
            
            try:
                metadata = yaml.safe_load(parts[1])
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML frontmatter: {e}")
            
            if not isinstance(metadata, dict):
                raise ValueError("YAML frontmatter must be a dictionary")
            
            text_content = parts[2].strip()
            if not text_content:
                raise ValueError("Empty content section")
            
            metadata['content'] = text_content
            metadata['citation'] = self.generate_vancouver_citation(metadata)
            
            return metadata
            
        except Exception as e:
            self.log_error(filepath, f"Parse error: {e}")
            return None
    
    def validate_metadata(self, metadata: Dict, filepath: Path) -> Tuple[bool, List[str]]:
        errors = []
        
        content_type = metadata.get('content_type')
        if not content_type:
            errors.append("Missing required field: content_type")
        elif content_type not in ['MedicalGuideline', 'ResearchAbstract']:
            errors.append(f"Invalid content_type: {content_type}")
        
        review_status = metadata.get('review_status')
        if review_status != 'approved':
            errors.append(f"Content not approved for ingestion (status: {review_status})")
        
        universal_required = ['publication_year', 'calculator_support', 'medical_domain', 'accessed_date']
        for field in universal_required:
            if field not in metadata or metadata[field] is None:
                errors.append(f"Missing required field: {field}")
        
        if content_type == 'MedicalGuideline':
            guideline_required = ['organization', 'title', 'section', 'url']
            for field in guideline_required:
                if field not in metadata or not metadata[field]:
                    errors.append(f"Missing required MedicalGuideline field: {field}")
        
        elif content_type == 'ResearchAbstract':
            abstract_required = ['title', 'journal', 'authors']
            for field in abstract_required:
                if field not in metadata or not metadata[field]:
                    errors.append(f"Missing required ResearchAbstract field: {field}")
        
        return len(errors) == 0, errors
    
    def normalize_metadata(self, metadata: Dict) -> Dict:
        normalized = metadata.copy()
        
        list_fields = ['authors', 'calculator_support', 'medical_domain']
        for field in list_fields:
            if field in normalized:
                if not isinstance(normalized[field], list):
                    if isinstance(normalized[field], str) and normalized[field]:
                        normalized[field] = [normalized[field]]
                    else:
                        normalized[field] = []
        
        if 'publication_year' in normalized and normalized['publication_year']:
            try:
                normalized['publication_year'] = int(normalized['publication_year'])
            except (ValueError, TypeError):
                normalized['publication_year'] = None
        
        for key, value in list(normalized.items()):
            if isinstance(value, str) and value.strip() == "":
                normalized[key] = None
        
        if 'pmid' not in normalized:
            normalized['pmid'] = None
        if 'doi' not in normalized:
            normalized['doi'] = None
        
        return normalized
    
    def ingest_single_file(self, filepath: Path, state: Dict) -> bool:
        file_key = str(filepath)
        
        try:
            current_hash = self.calculate_file_hash(filepath)
            
            # File-level check (first layer of deduplication)
            if file_key in state and state[file_key].get('sha256') == current_hash:
                print(f"  Already processed (no changes): {filepath.name}")
                return False
            
            print(f"\n Processing: {filepath.name}")
            
            metadata = self.parse_markdown_file(filepath)
            if not metadata:
                return False
            
            is_valid, errors = self.validate_metadata(metadata, filepath)
            if not is_valid:
                for error in errors:
                    print(f"    {error}")
                self.log_error(filepath, f"Validation errors: {'; '.join(errors)}")
                return False
            
            normalized_metadata = self.normalize_metadata(metadata)
            normalized_metadata['content_hash'] = current_hash  # Add hash to database record
            class_name = normalized_metadata.pop('content_type')
            
            try:
                collection = self.client.collections.get(class_name)
                
                # Database-level check (second layer of deduplication)
                # This ensures no duplicates even if state file is lost or corrupted
                try:
                    existing = collection.query.fetch_objects(
                        filters=wvc.query.Filter.by_property("content_hash").equal(current_hash),
                        limit=1,
                        return_properties=["content_hash", "title"]
                    )
                    
                    if existing.objects:
                        # Duplicate detected at database level - update existing record
                        existing_uuid = existing.objects[0].uuid
                        collection.data.replace(uuid=existing_uuid, properties=normalized_metadata)
                        
                        archive_path = self.archived_dir / filepath.name
                        shutil.copy2(str(filepath), str(archive_path))
                        
                        state[file_key] = {
                            'sha256': current_hash,
                            'ingested_at': datetime.now().isoformat(),
                            'class_name': class_name,
                            'weaviate_id': str(existing_uuid),
                            'action': 'duplicate_updated'
                        }
                        
                        print(f"    Database-level duplicate detected: updated existing record")
                        return False  # Not counted as new ingestion
                        
                except Exception as query_error:
                    # If content_hash property doesn't exist yet, proceed with normal insertion
                    print(f"    Database-level check skipped (legacy schema): {query_error}")
                
                # Insert new record
                uuid = collection.data.insert(properties=normalized_metadata)
                
                if uuid:
                    archive_path = self.archived_dir / filepath.name
                    shutil.copy2(str(filepath), str(archive_path))
                    
                    state[file_key] = {
                        'sha256': current_hash,
                        'ingested_at': datetime.now().isoformat(),
                        'class_name': class_name,
                        'weaviate_id': str(uuid),
                        'action': 'newly_inserted'
                    }
                    
                    print(f"    Successfully ingested and archived")
                    return True
                else:
                    raise Exception("Weaviate returned empty result")
                    
            except Exception as e:
                self.log_error(filepath, f"Weaviate ingestion error: {e}")
                print(f"    Weaviate ingestion failed: {e}")
                return False
                
        except Exception as e:
            self.log_error(filepath, f"Unexpected error: {e}")
            print(f"    Unexpected error: {e}")
            return False

    def log_error(self, filepath: Path, error_msg: str) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = self.validation_reports_dir / f"error_{filepath.stem}_{timestamp}.log"
        
        try:
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"Medical Content Ingestion Error Report\n")
                f.write(f"=" * 50 + "\n")
                f.write(f"File: {filepath}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Error: {error_msg}\n")
                f.write(f"\nFile exists: {filepath.exists()}\n")
                if filepath.exists():
                    f.write(f"File size: {filepath.stat().st_size} bytes\n")
        except Exception as e:
            print(f"Warning: Could not write error log: {e}")
        
    def ingest_all_approved_content(self) -> Dict:
        """Ingest all approved medical content with comprehensive reporting."""
        print("Medical Content Ingestion")
        print("=" * 50)
        
        state = self.load_ingestion_state()
        
        stats = {
            'total_processed': 0,
            'successfully_ingested': 0,
            'by_type': {'MedicalGuideline': 0, 'ResearchAbstract': 0}
        }
        
        for content_dir in [self.guidelines_dir, self.abstracts_dir]:
            if not content_dir.exists():
                print(f"  Warning: Directory {content_dir} does not exist")
                continue
            
            dir_name = content_dir.name
            print(f"\n\\ Processing {dir_name} /")
            
            md_files = list(content_dir.glob("*.md"))
            template_files = [f for f in md_files if f.name.startswith('_TEMPLATE_')]
            content_files = [f for f in md_files if not f.name.startswith('_TEMPLATE_')]
            
            if template_files:
                print(f"     Skipping {len(template_files)} template files")
            
            for md_file in content_files:
                stats['total_processed'] += 1
                
                if self.ingest_single_file(md_file, state):
                    stats['successfully_ingested'] += 1
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            metadata = yaml.safe_load(parts[1])
                            content_type = metadata.get('content_type', 'Unknown')
                            if content_type in stats['by_type']:
                                stats['by_type'][content_type] += 1
                    except:
                        pass
        
        self.save_ingestion_state(state)
        
        print(f"\nIngestion Summary")
        print("=" * 40)
        print(f"   Files processed: {stats['total_processed']}")
        print(f"   Successfully ingested: {stats['successfully_ingested']}")
        print(f"   Medical Guidelines: {stats['by_type']['MedicalGuideline']}")
        print(f"   Research Abstracts: {stats['by_type']['ResearchAbstract']}")
        print(f"\n Archive location: {self.archived_dir}")
        print(f" Reports location: {self.validation_reports_dir}")
        print(f" Original files preserved in: guidelines/ and research_abstracts/")
        
        if stats['successfully_ingested'] > 0:
            print(f"\n Knowledge base ready for semantic search and AI integration!")
        else:
            print(f"\n  No content was ingested. Check file review_status and error logs.")
        
        return stats

def main():
    """Command-line interface for content ingestion."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "status":
            ingester = MedicalContentIngester()
            try:
                state = ingester.load_ingestion_state()
                print(f" Ingestion state: {len(state)} files tracked")
                for file_path, info in list(state.items())[:10]:
                    print(f"  {Path(file_path).name}: {info.get('ingested_at', 'Unknown')}")
            finally:
                ingester.close()
            return
        elif command == "reset":
            ingester = MedicalContentIngester()
            try:
                if ingester.state_file.exists():
                    ingester.state_file.unlink()
                    print(" Ingestion state reset.")
                else:
                    print("  No state file to reset.")
            finally:
                ingester.close()
            return
    
    # Main ingestion process
    ingester = MedicalContentIngester()
    try:
        stats = ingester.ingest_all_approved_content()
    finally:
        ingester.close()

if __name__ == "__main__":
    main()
