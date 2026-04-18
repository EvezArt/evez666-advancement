# Skill: quantum-ez-productivity
# Description: Quantum-enhanced productivity suite for faster, smarter, harder work
# Category: productivity/quantum

## Overview
This skill integrates quantum computing capabilities into every workflow - code execution, research, decision making, scheduling, and analysis.

## Capabilities
- **Code Execution** - Run code with quantum-enhanced analysis and optimization
- **Quantum Search** - Search with superposition-based query expansion  
- **Data Analysis** - Pattern recognition using quantum state analysis
- **Decision Making** - Choose between options using quantum superposition
- **Task Scheduling** - Optimize workflows with quantum algorithms
- **Code Optimization** - Analyze and suggest improvements using quantum patterns

## Commands
```bash
run.sh metrics                 # System metrics
run.sh search <query>         # Quantum-enhanced search
run.sh decide <options...>    # Quantum decision making
run.sh analyze <data>         # Quantum data analysis
run.sh schedule <json>       # Quantum task scheduling
run.sh optimize <code>        # Code optimization suggestions
run.sh execute <code> [lang] # Execute with quantum analysis
```

## Quantum Features
- Grover operator for search optimization
- Bell state generation for decision making
- GHZ states for parallel task processing
- QFT for frequency-based analysis
- Real circuit execution via Qiskit Aer

## Configuration
```json
{
  "quantum": {
    "backend": "aer",
    "shots": 100
  },
  "features": {
    "code_execution": true,
    "search": true,
    "decision_making": true,
    "scheduling": true
  }
}
```

## Integration
All quantum operations are tracked in metrics.json and can be used to optimize future operations based on historical performance.