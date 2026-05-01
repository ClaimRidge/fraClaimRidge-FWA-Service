import networkx as nx
import pandas as pd
from typing import List, Dict, Any
from src.config import settings

class Layer3GraphDetector:
    def __init__(self):
        self.graph = nx.Graph()

    async def analyze_collusion(self, claims_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Builds a network and identifies suspicious structural patterns.
        """
        G = nx.Graph()
        
        # 1. Build the Graph
        # We use prefixes to distinguish between Member and Provider nodes
        for _, row in claims_df.iterrows():
            m_node = f"M_{row['Patient_Age']}_{row['Patient_Gender']}" # Mocking Member ID from features
            p_node = f"P_{row['Provider_ID']}"
            
            if G.has_edge(m_node, p_node):
                G[m_node][p_node]['weight'] += 1
                G[m_node][p_node]['amount'] += row['Claim_Amount']
            else:
                G.add_edge(m_node, p_node, weight=1, amount=row['Claim_Amount'])

        flags = []

        # 2. Identify Hub Providers (PageRank)
        # Higher PageRank = Provider is a major "hub" in the member network
        pagerank = nx.pagerank(G, weight='weight')
        
        # 3. Community Detection (Connected Components)
        components = list(nx.connected_components(G))
        
        # 4. Generate Flags for Hubs
        for node, score in pagerank.items():
            if node.startswith("P_") and score > (1.0 / len(G.nodes())): # Increased sensitivity
                flags.append({
                    "layer": "L3",
                    "type": "HUB_PROVIDER",
                    "entity_id": node[2:],
                    "score": float(score),
                    "severity": "HIGH" if score > (10.0 / len(G.nodes())) else "MEDIUM",
                    "description": f"Provider {node} identified as a high-centrality network hub."
                })

        # 5. Generate Flags for Suspicious Rings
        for comp in components:
            if 3 <= len(comp) <= 10: # Small, tight-knit groups are suspicious
                # Calculate "Density" of the sub-graph
                subgraph = G.subgraph(comp)
                density = nx.density(subgraph)
                if density > 0.5:
                    flags.append({
                        "layer": "L3",
                        "type": "COLLUSION_RING",
                        "entities": list(comp),
                        "score": float(density),
                        "severity": "CRITICAL",
                        "description": "High-density collusion ring detected among members and providers."
                    })

        return flags
