def __init__(self, weaviate_url: str = "http://localhost:8080"):
    """Initialize content ingester with paths and Weaviate v4 connection."""
    self.client = weaviate.connect_to_local(port=8080, grpc_port=50051)
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

# Update the ingest_single_file method's Weaviate insertion part:
def ingest_single_file(self, filepath: Path, state: Dict) -> bool:
    """Ingest a single markdown file with comprehensive error handling."""
    file_key = str(filepath)
    
    try:
        current_hash = self.calculate_file_hash(filepath)
        if file_key in state and state[file_key].get('sha256') == current_hash:
            print(f"⏭️  Already processed (no changes): {filepath.name}")
            return False
        
        print(f"📄 Processing: {filepath.name}")
        
        metadata = self.parse_markdown_file(filepath)
        if not metadata:
            return False
        
        is_valid, errors = self.validate_metadata(metadata, filepath)
        if not is_valid:
            for error in errors:
                print(f"   ❌ {error}")
            self.log_error(filepath, f"Validation errors: {'; '.join(errors)}")
            return False
        
        normalized_metadata = self.normalize_metadata(metadata)
        class_name = normalized_metadata.pop('content_type')
        
        try:
            # v4 syntax for data insertion
            collection = self.client.collections.get(class_name)
            uuid = collection.data.insert(properties=normalized_metadata)
            
            if uuid:
                archive_path = self.archived_dir / filepath.name
                shutil.copy2(str(filepath), str(archive_path))
                
                state[file_key] = {
                    'sha256': current_hash,
                    'ingested_at': datetime.now().isoformat(),
                    'class_name': class_name,
                    'weaviate_id': str(uuid)
                }
                
                print(f"   ✅ Successfully ingested and archived")
                return True
            else:
                raise Exception("Weaviate returned empty result")
                
        except Exception as e:
            self.log_error(filepath, f"Weaviate ingestion error: {e}")
            print(f"   ❌ Weaviate ingestion failed: {e}")
            return False
            
    except Exception as e:
        self.log_error(filepath, f"Unexpected error: {e}")
        print(f"   ❌ Unexpected error: {e}")
        return False
