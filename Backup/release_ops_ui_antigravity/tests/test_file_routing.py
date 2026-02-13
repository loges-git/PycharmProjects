
import unittest
from pathlib import Path
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestFileRouting(unittest.TestCase):
    def test_routing_logic(self):
        """
        Directly test the routing logic snippet.
        """
        routing_map = {
            ".prc": "prc",
            ".sql": "sql",
            ".vw": "vw",
            ".inc": "oneoff",
            ".trg": "trgall"
        }
        
        # Helper to simulate key release service logic
        def get_destination(rel_path_str):
            rel_path = Path(rel_path_str)
            if len(rel_path.parts) == 1 and rel_path.suffix in routing_map:
                target_folder = routing_map[rel_path.suffix]
                return Path(target_folder) / rel_path.name
            return rel_path

        # Case 1: .prc file in root
        res = get_destination("test.prc")
        self.assertEqual(str(res), os.path.join("prc", "test.prc"))

        # Case 2: .sql file in root
        res = get_destination("my_script.sql")
        self.assertEqual(str(res), os.path.join("sql", "my_script.sql"))
            
        # Case 3: nested file (should not move)
        res = get_destination("nested/file.prc")
        self.assertEqual(str(res), os.path.normpath("nested/file.prc"))

        # Case 4: unknown extension
        res = get_destination("readme.txt")
        self.assertEqual(str(res), "readme.txt")
        
        # Case 5: .trg -> trgall
        res = get_destination("trigger.trg")
        self.assertEqual(str(res), os.path.join("trgall", "trigger.trg"))

if __name__ == "__main__":
    unittest.main()
