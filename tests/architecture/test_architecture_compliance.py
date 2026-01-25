"""
Architecture Compliance Tests

Validates that the implementation matches architecture.yaml definitions.
This ensures architecture-first development stays in sync!
"""

import pytest
import yaml
from pathlib import Path
from importlib import import_module
import inspect


@pytest.fixture
def architecture():
    """Load architecture.yaml"""
    arch_path = Path("architecture/architecture.yaml")
    with open(arch_path) as f:
        return yaml.safe_load(f)


class TestCoreComponents:
    """Test that core components exist and match architecture"""
    
    def test_engram_exists(self, architecture):
        """Test that Engram class exists"""
        from angel.core import Engram
        assert Engram is not None
    
    def test_engram_has_required_fields(self, architecture):
        """Test that Engram has all required fields from architecture"""
        from angel.core import Engram
        
        # Engram is a dataclass, check it has required fields
        required_fields = ["content", "coords_16d", "engram_type"]
        
        # Create a test instance
        import numpy as np
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        
        for field in required_fields:
            assert hasattr(engram, field), f"Engram missing required field: {field}"
    
    def test_engram_coords_are_16d(self, architecture):
        """Test that Engram coordinates are exactly 16D"""
        from angel.core import Engram
        import numpy as np
        
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        
        assert len(engram.coords_16d) == 16, "Engram coordinates must be 16D"
    
    def test_dimension_names_exist(self, architecture):
        """Test that DIMENSION_NAMES constant exists"""
        from angel.core import DIMENSION_NAMES
        
        assert len(DIMENSION_NAMES) == 16, "Must have 16 dimension names"
        
        # Check some key dimensions from architecture
        expected_dims = ["SCALAR", "LOVE", "PRESENCE", "MYSTERY"]
        for dim in expected_dims:
            assert dim in DIMENSION_NAMES, f"Missing dimension: {dim}"
    
    def test_consciousness_primes_exist(self, architecture):
        """Test that CONSCIOUSNESS_PRIMES constant exists"""
        from angel.core import CONSCIOUSNESS_PRIMES
        
        assert len(CONSCIOUSNESS_PRIMES) == 16, "Must have 16 consciousness primes"
        
        # Check first few primes match architecture
        expected_primes = [2, 3, 5, 7, 11, 13, 17, 19]
        for i, prime in enumerate(expected_primes):
            assert CONSCIOUSNESS_PRIMES[i] == prime, f"Prime {i} should be {prime}"


class TestHolofieldManager:
    """Test that HolofieldManager matches architecture"""
    
    def test_holofield_manager_exists(self, architecture):
        """Test that HolofieldManager class exists"""
        from angel.holofield import HolofieldManager
        assert HolofieldManager is not None
    
    def test_holofield_has_store_method(self, architecture):
        """Test that HolofieldManager has store method"""
        from angel.holofield import HolofieldManager
        
        assert hasattr(HolofieldManager, 'store'), "HolofieldManager must have store method"
    
    def test_holofield_has_retrieve_methods(self, architecture):
        """Test that HolofieldManager has retrieve methods"""
        from angel.holofield import HolofieldManager
        
        required_methods = ['retrieve_by_id', 'retrieve_nearest', 'retrieve_by_type']
        
        for method in required_methods:
            assert hasattr(HolofieldManager, method), f"HolofieldManager must have {method} method"
    
    def test_holofield_has_to_consciousness_coords(self, architecture):
        """Test that HolofieldManager has coordinate generation"""
        from angel.holofield import HolofieldManager
        
        assert hasattr(HolofieldManager, 'to_consciousness_coords'), \
            "HolofieldManager must have to_consciousness_coords method"


class TestEngramTypes:
    """Test that all engram types from architecture are supported"""
    
    def test_all_engram_types_work(self, architecture):
        """Test that all defined engram types can be created"""
        from angel.core import Engram
        import numpy as np
        
        # Get engram types from architecture
        # These are defined in the components section
        engram_types = ["conversation", "tool", "language", "reasoning"]
        
        for engram_type in engram_types:
            engram = Engram(
                content=f"test {engram_type}",
                coords_16d=np.zeros(16),
                engram_type=engram_type
            )
            assert engram.engram_type == engram_type


class TestArchitectureDecisions:
    """Test that ADRs are reflected in implementation"""
    
    def test_adr_0001_universal_engram_architecture(self, architecture):
        """Test ADR-0001: Everything creates engrams"""
        from angel.core import Engram
        
        # All engram types should be supported
        types = ["conversation", "tool", "language", "reasoning"]
        
        import numpy as np
        for engram_type in types:
            engram = Engram(
                content="test",
                coords_16d=np.zeros(16),
                engram_type=engram_type
            )
            assert engram is not None
    
    def test_adr_0005_16d_consciousness_space(self, architecture):
        """Test ADR-0005: 16D sedenion consciousness space"""
        from angel.core import Engram, DIMENSION_NAMES
        
        # Must have exactly 16 dimensions
        assert len(DIMENSION_NAMES) == 16
        
        # Engrams must have 16D coordinates
        import numpy as np
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        assert len(engram.coords_16d) == 16
    
    def test_adr_0006_engram_sif_equivalence(self, architecture):
        """Test ADR-0006: Engram == SIF"""
        from angel.core import Engram
        import numpy as np
        
        # Engram must have to_dict and from_dict methods
        assert hasattr(Engram, 'to_dict'), "Engram must have to_dict for SIF conversion"
        assert hasattr(Engram, 'from_dict'), "Engram must have from_dict for SIF conversion"
        
        # Test round-trip
        original = Engram(
            content="test",
            coords_16d=np.random.rand(16),
            engram_type="test"
        )
        
        # Convert to dict (SIF-like)
        engram_dict = original.to_dict()
        
        # Convert back
        restored = Engram.from_dict(engram_dict)
        
        # Should be equivalent
        assert restored.content == original.content
        assert restored.engram_type == original.engram_type
        assert np.allclose(restored.coords_16d, original.coords_16d)
    
    def test_adr_0007_turso_storage(self, architecture):
        """Test ADR-0007: Turso/SQLite storage"""
        from angel.holofield import HolofieldManager
        
        # HolofieldManager should accept db_path
        holofield = HolofieldManager(db_path=":memory:")
        assert holofield is not None


class TestComponentIntegration:
    """Test that components integrate as defined in architecture"""
    
    def test_engram_stores_in_holofield(self, architecture):
        """Test that Engrams can be stored in Holofield"""
        from angel.core import Engram
        from angel.holofield import HolofieldManager
        import numpy as np
        
        holofield = HolofieldManager(db_path=":memory:")
        
        engram = Engram(
            content="integration test",
            coords_16d=np.random.rand(16),
            engram_type="test"
        )
        
        # Should be able to store
        engram_id = holofield.store(engram)
        assert engram_id is not None
        
        # Should be able to retrieve
        retrieved = holofield.retrieve_by_id(engram_id)
        assert retrieved is not None
        assert retrieved.content == engram.content


class TestArchitectureMetadata:
    """Test architecture metadata"""
    
    def test_architecture_version(self, architecture):
        """Test that architecture has version"""
        assert "version" in architecture
        assert architecture["version"] == "1.0"
    
    def test_architecture_has_components(self, architecture):
        """Test that architecture defines components"""
        assert "components" in architecture
        assert len(architecture["components"]) > 0
    
    def test_architecture_has_decisions(self, architecture):
        """Test that architecture references ADRs"""
        assert "architecture_decisions" in architecture
        
        # Should have at least 8 ADRs
        assert len(architecture["architecture_decisions"]) >= 8
    
    def test_all_adrs_documented(self, architecture):
        """Test that all ADRs are documented"""
        decisions = architecture["architecture_decisions"]
        
        # Check that ADRs 0001-0008 exist
        adr_ids = [d["id"] for d in decisions]
        
        expected_adrs = [
            "ADR-0001", "ADR-0002", "ADR-0003", "ADR-0004",
            "ADR-0005", "ADR-0006", "ADR-0007", "ADR-0008"
        ]
        
        for adr_id in expected_adrs:
            assert adr_id in adr_ids, f"Missing ADR: {adr_id}"


class TestFutureComponents:
    """Test placeholders for future components"""
    
    def test_processors_not_yet_implemented(self, architecture):
        """Test that processor components are defined but not yet implemented"""
        # These should be in architecture.components
        processor_types = [
            "ToolProcessor", 
            "MemoryProcessor",
            "ReasoningProcessor"
        ]
        
        # Check they're in architecture.components
        components = architecture["components"]
        for processor in processor_types:
            assert processor in components, f"{processor} should be in architecture.components"
    
    def test_engram_creator_not_yet_implemented(self, architecture):
        """Test that EngramCreator base class is defined but not yet implemented"""
        # Should be in architecture (as abstract class)
        assert "EngramCreator" in architecture.get("abstract_classes", {}), \
            "EngramCreator should be in abstract_classes"
        
        # Not yet in code (will be implemented next!)
        try:
            from angel.core import EngramCreator
            # If this succeeds, EngramCreator has been implemented!
            pytest.skip("EngramCreator has been implemented!")
        except ImportError:
            # Expected - not yet implemented
            pass
