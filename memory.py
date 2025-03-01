# memory.py
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class MemoryConfig:
    base_address: int
    size: int
    word_size: int = 4  # 4 bytes per word

class MemoryError(Exception):
    """Custom exception for memory-related errors."""
    pass

class MIPSMemory:
    def __init__(self, base_address: int, size: int):
        self.config = MemoryConfig(base_address, size)
        self.memory: List[int] = [0] * (size // 2)  # 2 bytes per word for 16-bit
        self.data_section: Dict[str, int] = {}

    def _validate_address(self, address: int) -> None:
        """Validate memory address."""
        if address % self.config.word_size != 0:
            raise MemoryError(f"Unaligned memory access at address: 0x{address:08X}")
            
        relative_address = address - self.config.base_address
        index = relative_address // self.config.word_size
        
        if not (0 <= index < len(self.memory)):
            if not (0 <= address < self.config.base_address):
                raise MemoryError(f"Memory access out of bounds at address: 0x{address:08X}")

    def read_word(self, address: int) -> int:
        """Read a word from memory."""
        try:
            self._validate_address(address)
            index = (address - self.config.base_address) // self.config.word_size
            return self.memory[index]
        except MemoryError as e:
            # Try reading from absolute address
            if 0 <= address < self.config.base_address:
                index = address // self.config.word_size
                if 0 <= index < len(self.memory):
                    return self.memory[index]
            raise e

    def write_word(self, address: int, value: int):
        # Calculate relative address
        relative_address = address - self.config.base_address
        
        # Check if address is word-aligned
        if relative_address % self.config.word_size != 0:
            raise MemoryError(f"Unaligned memory access at address: 0x{address:08X}")
            
        # Convert to array index
        index = relative_address // self.config.word_size
        
        # Check bounds
        if 0 <= index < len(self.memory):
            self.memory[index] = value & 0xFFFF
        else:
            # For addresses below base_address, treat as regular memory access
            if 0 <= address < self.config.base_address:
                index = address // self.config.word_size
                if 0 <= index < len(self.memory):
                    self.memory[index] = value & 0xFFFF
                    return
            raise MemoryError(f"Memory access out of bounds at address: 0x{address:08X}")

    def is_valid_address(self, address: int) -> bool:
        # Check if address is within valid ranges
        relative_address = address - self.config.base_address
        
        # Check if address is word-aligned
        if relative_address % self.config.word_size != 0:
            return False
            
        # Convert to array index
        index = relative_address // self.config.word_size
        
        # Check primary range (relative to base address)
        if 0 <= index < len(self.memory):
            return True
            
        # Check secondary range (absolute addresses below base_address)
        if 0 <= address < self.config.base_address:
            index = address // self.config.word_size
            return 0 <= index < len(self.memory)
            
        return False

    def allocate_data(self, data_section: Dict[str, int]):
        self.data_section = data_section
        # Initialize memory locations for data section
        for i, value in enumerate(data_section.values()):
            if i < len(self.memory):
                self.memory[i] = value

    def update_data_memory(self, var_name: str, value: int):
        if var_name in self.data_section:
            variable_index = list(self.data_section.keys()).index(var_name)
            if 0 <= variable_index < len(self.memory):
                self.memory[variable_index] = value
                self.data_section[var_name] = value

    def get_data_memory_values(self) -> List[int]:
        return self.memory[:]