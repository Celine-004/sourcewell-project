"""
Citation Viewer
"""
import streamlit as st
from typing import List, Dict, Any, Optional

class CitationViewer:
    """Component for viewing and managing citations"""
    
    def __init__(self):
        """Initialize the citation viewer component"""
        pass
    
    def render(self, citations: Optional[List[Dict[str, Any]]] = None):
        """Render citations"""
        if not citations:
            st.info("No citations available")
            return
        
        st.subheader("📚 Evidence & Citations")
        
        for i, citation in enumerate(citations, 1):
            with st.expander(f"Citation {i}: {citation.get('title', 'Unknown')}"):
                if citation.get('organization'):
                    st.markdown(f"**Organization:** {citation['organization']}")
                if citation.get('journal'):
                    st.markdown(f"**Journal:** {citation['journal']}")
                if citation.get('year'):
                    st.markdown(f"**Year:** {citation['year']}")
                if citation.get('citation'):
                    st.markdown(f"**Full Citation:** {citation['citation']}")